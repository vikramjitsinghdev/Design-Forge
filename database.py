import sqlite3
import json
from pathlib import Path
from datetime import datetime


# ============================================================
# DESIGNFORGE DATABASE
# ============================================================
#
# Purpose:
#   - Maintain the SQLite database
#   - Store user information
#   - Store DesignForge searches
#   - Store filtered image references
#   - Store search tags
#
# This file does NOT:
#   - Run AI models
#   - Call APIs
#   - Search the web
#   - Process images
#   - Control Flask
#   - Modify the DesignForge workflow
#
# The authentication database has its own user IDs.
# This database keeps a small mapping to that authenticated
# user so search records can safely use this database's own
# user ID without violating foreign-key constraints.
# ============================================================


# ============================================================
# DATABASE LOCATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "database.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    """
    Create and return a connection to the DesignForge SQLite
    database.

    Foreign keys are enabled for every connection.
    """

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    connection.execute(
        "PRAGMA foreign_keys = ON"
    )

    return connection


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

def initialize_database():
    """
    Create all required DesignForge tables if they do not exist.

    Safe to call multiple times.
    Existing data is preserved.
    """

    connection = get_connection()

    try:
        cursor = connection.cursor()

        # ----------------------------------------------------
        # USERS
        # ----------------------------------------------------

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                username TEXT,
                email TEXT,
                auth_user_id INTEGER,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        # ----------------------------------------------------
        # SEARCHES
        # ----------------------------------------------------

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS searches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                user_description TEXT NOT NULL,
                ai_description TEXT,
                search_components TEXT,
                tags TEXT,
                created_at TEXT NOT NULL,

                FOREIGN KEY (user_id)
                    REFERENCES users(id)
                    ON DELETE SET NULL
            )
            """
        )

        # ----------------------------------------------------
        # SEARCH IMAGES
        # ----------------------------------------------------

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS search_images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                search_id INTEGER NOT NULL,
                image_url TEXT NOT NULL,
                source TEXT,
                position INTEGER,
                created_at TEXT NOT NULL,

                FOREIGN KEY (search_id)
                    REFERENCES searches(id)
                    ON DELETE CASCADE
            )
            """
        )

        # ----------------------------------------------------
        # BACKWARD-COMPATIBLE MIGRATION
        # ----------------------------------------------------
        #
        # Older database.py versions created users with only:
        #   id, name, email, created_at, updated_at
        #
        # Add the new authentication-mapping columns if the
        # existing database does not have them.
        # ----------------------------------------------------

        user_columns = {
            row["name"]
            for row in cursor.execute(
                "PRAGMA table_info(users)"
            ).fetchall()
        }

        if "username" not in user_columns:
            cursor.execute(
                "ALTER TABLE users ADD COLUMN username TEXT"
            )

        if "auth_user_id" not in user_columns:
            cursor.execute(
                "ALTER TABLE users ADD COLUMN auth_user_id INTEGER"
            )

        # ----------------------------------------------------
        # INDEXES
        # ----------------------------------------------------

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_searches_user_id
            ON searches(user_id)
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_search_images_search_id
            ON search_images(search_id)
            """
        )

        cursor.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS
            idx_users_auth_user_id
            ON users(auth_user_id)
            WHERE auth_user_id IS NOT NULL
            """
        )

        cursor.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS
            idx_users_username
            ON users(username)
            WHERE username IS NOT NULL
            """
        )

        connection.commit()

    finally:
        connection.close()


# ============================================================
# AUTHENTICATED USER MAPPING
# ============================================================

def sync_authenticated_user(
    auth_user_id,
    name,
    username,
    email=None
):
    """
    Create or update the DesignForge database user that
    corresponds to the authenticated user in user_database.py.

    Returns:
        int:
            The LOCAL user ID from database.db.

    Important:
        auth_user_id belongs to the authentication database.
        The returned value belongs to database.db.
    """

    if auth_user_id is None:
        raise ValueError(
            "auth_user_id cannot be empty."
        )

    if not isinstance(name, str):
        raise TypeError(
            "name must be a string."
        )

    if not isinstance(username, str):
        raise TypeError(
            "username must be a string."
        )

    name = name.strip()
    username = username.strip()

    if not name:
        raise ValueError(
            "name cannot be empty."
        )

    if not username:
        raise ValueError(
            "username cannot be empty."
        )

    connection = get_connection()

    try:
        cursor = connection.cursor()
        now = datetime.utcnow().isoformat()

        # First look for the exact authentication user.
        row = cursor.execute(
            """
            SELECT id
            FROM users
            WHERE auth_user_id = ?
            """,
            (auth_user_id,)
        ).fetchone()

        if row is not None:

            cursor.execute(
                """
                UPDATE users
                SET
                    name = ?,
                    username = ?,
                    email = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    name,
                    username,
                    email,
                    now,
                    row["id"]
                )
            )

            connection.commit()
            return row["id"]

        # If an older local record already has this username,
        # attach the authentication ID to that record.
        row = cursor.execute(
            """
            SELECT id
            FROM users
            WHERE username = ?
            """,
            (username,)
        ).fetchone()

        if row is not None:

            cursor.execute(
                """
                UPDATE users
                SET
                    auth_user_id = ?,
                    name = ?,
                    email = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    auth_user_id,
                    name,
                    email,
                    now,
                    row["id"]
                )
            )

            connection.commit()
            return row["id"]

        # Otherwise create the local search-database user.
        cursor.execute(
            """
            INSERT INTO users (
                name,
                username,
                email,
                auth_user_id,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                name,
                username,
                email,
                auth_user_id,
                now,
                now
            )
        )

        local_user_id = cursor.lastrowid

        connection.commit()

        return local_user_id

    finally:
        connection.close()


# ============================================================
# GENERIC USER FUNCTIONS
# ============================================================

def create_user(name, email=None):
    """
    Create a new generic DesignForge user.

    Returns:
        int:
            Newly created local user ID.
    """

    if not isinstance(name, str):
        raise TypeError(
            "name must be a string."
        )

    name = name.strip()

    if not name:
        raise ValueError(
            "name cannot be empty."
        )

    now = datetime.utcnow().isoformat()

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO users (
                name,
                email,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                name,
                email,
                now,
                now
            )
        )

        user_id = cursor.lastrowid

        connection.commit()

        return user_id

    finally:
        connection.close()


def get_user(user_id):
    """
    Retrieve one local database user by ID.

    Returns:
        dict | None
    """

    connection = get_connection()

    try:
        row = connection.execute(
            """
            SELECT
                id,
                name,
                username,
                email,
                auth_user_id,
                created_at,
                updated_at
            FROM users
            WHERE id = ?
            """,
            (user_id,)
        ).fetchone()

        if row is None:
            return None

        return dict(row)

    finally:
        connection.close()


def get_authenticated_database_user(auth_user_id):
    """
    Return the local database user associated with an
    authenticated user ID.

    Returns:
        dict | None
    """

    connection = get_connection()

    try:
        row = connection.execute(
            """
            SELECT
                id,
                name,
                username,
                email,
                auth_user_id,
                created_at,
                updated_at
            FROM users
            WHERE auth_user_id = ?
            """,
            (auth_user_id,)
        ).fetchone()

        if row is None:
            return None

        return dict(row)

    finally:
        connection.close()


def update_user(
    user_id,
    name=None,
    email=None
):
    """
    Update generic user information.

    Only supplied values are changed.
    """

    connection = get_connection()

    try:
        cursor = connection.cursor()

        fields = []
        values = []

        if name is not None:

            if not isinstance(name, str):
                raise TypeError(
                    "name must be a string."
                )

            name = name.strip()

            if not name:
                raise ValueError(
                    "name cannot be empty."
                )

            fields.append(
                "name = ?"
            )

            values.append(name)

        if email is not None:

            fields.append(
                "email = ?"
            )

            values.append(email)

        if not fields:
            return False

        fields.append(
            "updated_at = ?"
        )

        values.append(
            datetime.utcnow().isoformat()
        )

        values.append(user_id)

        cursor.execute(
            f"""
            UPDATE users
            SET {", ".join(fields)}
            WHERE id = ?
            """,
            values
        )

        updated = cursor.rowcount > 0

        connection.commit()

        return updated

    finally:
        connection.close()


# ============================================================
# SEARCH FUNCTIONS
# ============================================================

def save_search(
    user_id,
    user_description,
    ai_description=None,
    search_components=None,
    tags=None,
    images=None
):
    """
    Save one completed DesignForge search.

    The user_id MUST be the local user ID from database.db.
    Use sync_authenticated_user() when the request comes from
    the authentication system.
    """

    if not isinstance(user_description, str):
        raise TypeError(
            "user_description must be a string."
        )

    user_description = user_description.strip()

    if not user_description:
        raise ValueError(
            "user_description cannot be empty."
        )

    if search_components is None:
        search_components = {}

    if tags is None:
        tags = []

    if images is None:
        images = []

    if not isinstance(
        search_components,
        (dict, list)
    ):
        raise TypeError(
            "search_components must be a dictionary or list."
        )

    if not isinstance(tags, list):
        raise TypeError(
            "tags must be a list."
        )

    if not isinstance(images, list):
        raise TypeError(
            "images must be a list."
        )

    # Database.py never generates tags.
    tags = [
        str(tag).strip()
        for tag in tags
        if str(tag).strip()
    ]

    tags = tags[:8]

    # Normalize image references.
    normalized_images = []

    for image in images:

        if isinstance(image, str):

            image_url = image.strip()

            if image_url:
                normalized_images.append(
                    {
                        "image_url": image_url,
                        "source": None
                    }
                )

            continue

        if isinstance(image, dict):

            image_url = (
                image.get("image_url")
                or image.get("url")
            )

            if not image_url:
                continue

            image_url = str(
                image_url
            ).strip()

            if not image_url:
                continue

            normalized_images.append(
                {
                    "image_url": image_url,
                    "source": (
                        image.get("source")
                        or "Pexels"
                    )
                }
            )

    connection = get_connection()

    try:
        cursor = connection.cursor()
        now = datetime.utcnow().isoformat()

        # Give a clear error before SQLite reports a raw
        # FOREIGN KEY constraint failure.
        user_exists = cursor.execute(
            """
            SELECT id
            FROM users
            WHERE id = ?
            """,
            (user_id,)
        ).fetchone()

        if user_exists is None:
            raise ValueError(
                "Local DesignForge database user does not exist."
            )

        cursor.execute(
            """
            INSERT INTO searches (
                user_id,
                user_description,
                ai_description,
                search_components,
                tags,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                user_description,
                ai_description,
                json.dumps(
                    search_components,
                    ensure_ascii=False
                ),
                json.dumps(
                    tags,
                    ensure_ascii=False
                ),
                now
            )
        )

        search_id = cursor.lastrowid

        for position, image in enumerate(
            normalized_images,
            start=1
        ):

            cursor.execute(
                """
                INSERT INTO search_images (
                    search_id,
                    image_url,
                    source,
                    position,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    search_id,
                    image["image_url"],
                    image["source"],
                    position,
                    now
                )
            )

        connection.commit()

        return search_id

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


# ============================================================
# SEARCH RETRIEVAL
# ============================================================

def get_search(search_id):
    """
    Retrieve a complete DesignForge search including its
    filtered image references.
    """

    connection = get_connection()

    try:
        row = connection.execute(
            """
            SELECT
                id,
                user_id,
                user_description,
                ai_description,
                search_components,
                tags,
                created_at
            FROM searches
            WHERE id = ?
            """,
            (search_id,)
        ).fetchone()

        if row is None:
            return None

        search = dict(row)

        try:
            search["search_components"] = json.loads(
                search["search_components"]
            )
        except (
            TypeError,
            json.JSONDecodeError
        ):
            search["search_components"] = {}

        try:
            search["tags"] = json.loads(
                search["tags"]
            )
        except (
            TypeError,
            json.JSONDecodeError
        ):
            search["tags"] = []

        image_rows = connection.execute(
            """
            SELECT
                id,
                image_url,
                source,
                position,
                created_at
            FROM search_images
            WHERE search_id = ?
            ORDER BY position ASC
            """,
            (search_id,)
        ).fetchall()

        search["images"] = [
            dict(image)
            for image in image_rows
        ]

        return search

    finally:
        connection.close()


def get_user_searches(
    user_id,
    limit=50
):
    """
    Retrieve a user's search history.

    Newest searches are returned first.
    """

    try:
        limit = int(limit)
    except (
        TypeError,
        ValueError
    ):
        limit = 50

    limit = max(
        1,
        min(limit, 200)
    )

    connection = get_connection()

    try:
        rows = connection.execute(
            """
            SELECT
                id,
                user_id,
                user_description,
                ai_description,
                search_components,
                tags,
                created_at
            FROM searches
            WHERE user_id = ?
            ORDER BY created_at DESC, id DESC
            LIMIT ?
            """,
            (
                user_id,
                limit
            )
        ).fetchall()

        searches = []

        for row in rows:

            search = dict(row)

            try:
                search["search_components"] = json.loads(
                    search["search_components"]
                )
            except (
                TypeError,
                json.JSONDecodeError
            ):
                search["search_components"] = {}

            try:
                search["tags"] = json.loads(
                    search["tags"]
                )
            except (
                TypeError,
                json.JSONDecodeError
            ):
                search["tags"] = []

            searches.append(search)

        return searches

    finally:
        connection.close()


# ============================================================
# DATABASE STATUS
# ============================================================

def database_exists():
    """
    Return True if the SQLite database file exists.
    """

    return DATABASE_PATH.exists()


# ============================================================
# INITIALIZE DATABASE ON IMPORT
# ============================================================

initialize_database()
