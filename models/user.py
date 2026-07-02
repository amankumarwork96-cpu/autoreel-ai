import bcrypt
from database.db import get_connection, get_cursor


def create_user(email: str, username: str, password: str) -> int:
    """
    Creates a new user. Returns new user ID, or None if email/username exists.
    """
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    password_hash_str = password_hash.decode("utf-8")

    conn = get_connection()
    cursor = get_cursor(conn)

    try:
        cursor.execute(
            """
            INSERT INTO users (email, username, password_hash)
            VALUES (%s, %s, %s)
            """,
            (email, username, password_hash_str)
        )
        conn.commit()
        new_id = cursor.lastrowid
        print(f"[user] Created user: {username} (id={new_id})")
        return new_id

    except Exception as e:
        print(f"[user] create_user failed: {e}")
        return None

    finally:
        cursor.close()
        conn.close()


def get_user_by_email(email: str) -> dict:
    """
    Looks up a user by email. Returns dict or None.
    Used during login to fetch the user row.
    """
    conn = get_connection()
    cursor = get_cursor(conn)

    cursor.execute(
        "SELECT * FROM users WHERE email = %s",
        (email,)
    )
    user = cursor.fetchone()

    cursor.close()
    conn.close()
    return user


def get_user_by_id(user_id: int) -> dict:
    """
    Looks up a user by ID. Returns dict or None.
    Used to load logged-in user from session.
    """
    conn = get_connection()
    cursor = get_cursor(conn)

    cursor.execute(
        "SELECT * FROM users WHERE id = %s",
        (user_id,)
    )
    user = cursor.fetchone()

    cursor.close()
    conn.close()
    return user


def verify_password(plain_password: str, stored_hash: str) -> bool:
    """
    Checks plain text password against stored bcrypt hash.
    Returns True if match, False if not.
    """
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        stored_hash.encode("utf-8")
    )


# ─────────────────────────────────────────────
#  TEST — python models/user.py
# ─────────────────────────────────────────────
if __name__ == "__main__":
    # Test 1: Create a user
    print("── Test 1: Create user ──")
    new_id = create_user("aman@test.com", "aman", "mypassword123")
    print(f"New user ID: {new_id}")

    # Test 2: Fetch that user
    print("\n── Test 2: Get user by email ──")
    user = get_user_by_email("aman@test.com")
    print(f"Found: {user['username']} | {user['email']}")

    # Test 3: Verify password
    print("\n── Test 3: Verify password ──")
    print(f"Correct password: {verify_password('mypassword123', user['password_hash'])}")
    print(f"Wrong password:   {verify_password('wrongpassword', user['password_hash'])}")