"""
DesignForge - User Database

SOLE RESPONSIBILITY:
    Store and retrieve DesignForge user account information.

This module does NOT:
    - Validate passwords
    - Handle login
    - Handle signup rules
    - Run AI
    - Handle Flask
    - Handle searches
    - Handle images
    - Call external APIs
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timezone


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "user_database.db"


# ============================================================
# CONNECTION
# ============================================================

def get_connection():
    """Return a connection to the user database."""

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    return connection


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def initialize_database():
    """Create the users table if it does not exist."""

    connection = get_connection()

    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                name TEXT NOT NULL,

                username TEXT NOT NULL UNIQUE,

                password_hash TEXT NOT NULL,

                created_at TEXT NOT NULL,

                updated_at TEXT NOT NULL
            )
            """
        )

        connection.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS
            idx_users_username
            ON users(username)
            """
        )

        connection.commit()

    finally:
        connection.close()


# ============================================================
# CREATE USER
# ============================================================

def create_user(name, username, password_hash):
    """
    Store a new user.

    Password must already be securely hashed before
    this function is called.

    Returns:
        User ID if successful.
        None if username already exists.
    """

    now = datetime.now(timezone.utc).isoformat()

    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO users (
                name,
                username,
                password_hash,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                name,
                username,
                password_hash,
                now,
                now
            )
        )

        connection.commit()

        return cursor.lastrowid

    except sqlite3.IntegrityError:
        return None

    finally:
        connection.close()


# ============================================================
# FIND USER BY USERNAME
# ============================================================

def get_user_by_username(username):
    """
    Find a user using their username.

    Returns:
        Dictionary containing user data.
        None if the user does not exist.
    """

    connection = get_connection()

    try:
        row = connection.execute(
            """
            SELECT
                id,
                name,
                username,
                password_hash,
                created_at,
                updated_at
            FROM users
            WHERE username = ?
            """,
            (username,)
        ).fetchone()

        if row is None:
            return None

        return dict(row)

    finally:
        connection.close()


# ============================================================
# CHECK USERNAME
# ============================================================

def username_exists(username):
    """
    Check whether a username is already registered.

    Returns:
        True  -> username exists
        False -> username available
    """

    connection = get_connection()

    try:
        row = connection.execute(
            """
            SELECT id
            FROM users
            WHERE username = ?
            """,
            (username,)
        ).fetchone()

        return row is not None

    finally:
        connection.close()


# ============================================================
# GET USER
# ============================================================

def get_user(user_id):
    """Retrieve a user by their database ID."""

    connection = get_connection()

    try:
        row = connection.execute(
            """
            SELECT
                id,
                name,
                username,
                password_hash,
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


# ============================================================
# UPDATE USER
# ============================================================

def update_user(user_id, name=None, username=None, password_hash=None):
    """
    Update user account information.

    Only supplied values are changed.
    """

    current_user = get_user(user_id)

    if current_user is None:
        return False

    new_name = (
        current_user["name"]
        if name is None
        else name
    )

    new_username = (
        current_user["username"]
        if username is None
        else username
    )

    new_password_hash = (
        current_user["password_hash"]
        if password_hash is None
        else password_hash
    )

    now = datetime.now(timezone.utc).isoformat()

    connection = get_connection()

    try:
        connection.execute(
            """
            UPDATE users
            SET
                name = ?,
                username = ?,
                password_hash = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (
                new_name,
                new_username,
                new_password_hash,
                now,
                user_id
            )
        )

        connection.commit()

        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        connection.close()


# ============================================================
# DELETE USER
# ============================================================

def delete_user(user_id):
    """Delete a user from the database."""

    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            DELETE FROM users
            WHERE id = ?
            """,
            (user_id,)
        )

        connection.commit()

        return cursor.rowcount > 0

    finally:
        connection.close()


# ============================================================
# DATABASE STATUS
# ============================================================

def database_exists():
    """Return True if the user database exists."""

    return DATABASE_PATH.exists()


# ============================================================
# INITIALIZE ON IMPORT
# ============================================================

initialize_database()