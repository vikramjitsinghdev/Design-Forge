"""
DesignForge - User Credential Manager

SOLE RESPONSIBILITY:
    Validate signup and login credentials.

This module:
    - Validates names
    - Validates usernames
    - Validates passwords
    - Hashes passwords
    - Verifies passwords
    - Handles signup validation
    - Handles login validation

This module does NOT:
    - Handle Flask routes
    - Render HTML
    - Run AI
    - Search Pexels
    - Store design searches
    - Directly manage SQL tables
"""

import hashlib
import hmac
import secrets
import re

import user_database


# ============================================================
# PASSWORD CONFIGURATION
# ============================================================

PASSWORD_MIN_LENGTH = 8

PBKDF2_ITERATIONS = 600_000


# ============================================================
# NAME VALIDATION
# ============================================================

def validate_name(name):
    """
    Validate user's real/display name.

    Returns:
        (True, None)
        or
        (False, error_message)
    """

    if not name or not str(name).strip():
        return False, "Name cannot be empty."

    name = str(name).strip()

    if len(name) < 2:
        return False, "Name must contain at least 2 characters."

    if len(name) > 100:
        return False, "Name is too long."

    return True, None


# ============================================================
# USERNAME VALIDATION
# ============================================================

def validate_username(username):
    """
    Validate username format.

    Allowed:
        Letters
        Numbers
        Underscores

    Username length:
        3-30 characters
    """

    if not username or not str(username).strip():
        return False, "Username cannot be empty."

    username = str(username).strip()

    if len(username) < 3:
        return False, "Username must contain at least 3 characters."

    if len(username) > 30:
        return False, "Username must be 30 characters or fewer."

    if not re.fullmatch(r"[A-Za-z0-9_]+", username):
        return (
            False,
            "Username can only contain letters, numbers, and underscores."
        )

    return True, None


# ============================================================
# PASSWORD VALIDATION
# ============================================================

def validate_password(password):
    """
    Validate password strength.

    Requirements:
        - At least 8 characters
        - At least one letter
        - At least one number
    """

    if not password:
        return False, "Password cannot be empty."

    if len(password) < PASSWORD_MIN_LENGTH:
        return (
            False,
            f"Password must contain at least {PASSWORD_MIN_LENGTH} characters."
        )

    if len(password) > 128:
        return False, "Password is too long."

    if not re.search(r"[A-Za-z]", password):
        return False, "Password must contain at least one letter."

    if not re.search(r"\d", password):
        return False, "Password must contain at least one number."

    return True, None


# ============================================================
# PASSWORD HASHING
# ============================================================

def hash_password(password):
    """
    Securely hash a password using PBKDF2-HMAC-SHA256.

    A unique random salt is generated for every password.

    Returns:
        String containing:
            algorithm
            iterations
            salt
            hash
    """

    salt = secrets.token_bytes(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS
    )

    return (
        f"pbkdf2_sha256$"
        f"{PBKDF2_ITERATIONS}$"
        f"{salt.hex()}$"
        f"{password_hash.hex()}"
    )


# ============================================================
# PASSWORD VERIFICATION
# ============================================================

def verify_password(password, stored_hash):
    """
    Verify a password against a stored PBKDF2 hash.

    Returns:
        True if password is correct.
        False otherwise.
    """

    try:
        algorithm, iterations, salt_hex, hash_hex = stored_hash.split("$")

        if algorithm != "pbkdf2_sha256":
            return False

        iterations = int(iterations)

        salt = bytes.fromhex(salt_hex)

        expected_hash = bytes.fromhex(hash_hex)

        actual_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            iterations
        )

        return hmac.compare_digest(
            actual_hash,
            expected_hash
        )

    except (ValueError, TypeError):
        return False


# ============================================================
# SIGNUP
# ============================================================

def signup(name, username, password):
    """
    Validate and create a new DesignForge account.

    Returns a structured result:

        {
            "success": True,
            "user_id": 1,
            "message": "Account created successfully."
        }

    or:

        {
            "success": False,
            "user_id": None,
            "message": "Username already exists."
        }
    """

    # --------------------------------------------------------
    # Validate name
    # --------------------------------------------------------

    valid, error = validate_name(name)

    if not valid:
        return {
            "success": False,
            "user_id": None,
            "message": error
        }

    # --------------------------------------------------------
    # Validate username
    # --------------------------------------------------------

    username = str(username).strip()

    valid, error = validate_username(username)

    if not valid:
        return {
            "success": False,
            "user_id": None,
            "message": error
        }

    # Usernames are case-insensitive.
    username = username.lower()

    # --------------------------------------------------------
    # Check username uniqueness
    # --------------------------------------------------------

    if user_database.username_exists(username):
        return {
            "success": False,
            "user_id": None,
            "message": "That username is already taken."
        }

    # --------------------------------------------------------
    # Validate password
    # --------------------------------------------------------

    valid, error = validate_password(password)

    if not valid:
        return {
            "success": False,
            "user_id": None,
            "message": error
        }

    # --------------------------------------------------------
    # Hash password
    # --------------------------------------------------------

    password_hash = hash_password(password)

    # --------------------------------------------------------
    # Store user
    # --------------------------------------------------------

    user_id = user_database.create_user(
        name=str(name).strip(),
        username=username,
        password_hash=password_hash
    )

    # Handles the rare case where another request creates
    # the same username between our uniqueness check and
    # database insertion.
    if user_id is None:
        return {
            "success": False,
            "user_id": None,
            "message": "That username is already taken."
        }

    return {
        "success": True,
        "user_id": user_id,
        "message": "Account created successfully."
    }


# ============================================================
# LOGIN
# ============================================================

def login(username, password):
    """
    Validate a user's login credentials.

    Returns:

        {
            "success": True,
            "user_id": 1,
            "message": "Login successful."
        }

    or:

        {
            "success": False,
            "user_id": None,
            "message": "Invalid username or password."
        }
    """

    if not username or not password:
        return {
            "success": False,
            "user_id": None,
            "message": "Username and password are required."
        }

    username = str(username).strip().lower()

    user = user_database.get_user_by_username(username)

    # Do not reveal whether the username exists.
    if user is None:
        return {
            "success": False,
            "user_id": None,
            "message": "Invalid username or password."
        }

    if not verify_password(
        password,
        user["password_hash"]
    ):
        return {
            "success": False,
            "user_id": None,
            "message": "Invalid username or password."
        }

    return {
        "success": True,
        "user_id": user["id"],
        "message": "Login successful."
    }