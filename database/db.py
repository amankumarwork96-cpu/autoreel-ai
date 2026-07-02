import mysql.connector
from config import Config


def get_connection() -> mysql.connector.MySQLConnection:
    """
    Opens and returns a MySQL connection using credentials from config.
    autocommit=True ensures every INSERT/UPDATE is saved immediately —
    without this, changes can be lost if conn.commit() doesn't behave
    as expected across separate connection objects.
    """
    conn = mysql.connector.connect(
        host       = Config.DB_HOST,
        port       = Config.DB_PORT,
        user       = Config.DB_USER,
        password   = Config.DB_PASSWORD,
        database   = Config.DB_NAME,
        autocommit = True,
    )
    return conn


def get_cursor(conn):
    """
    Returns a dictionary cursor — rows come back as dicts.
    row["email"] instead of row[0]
    Always use this instead of conn.cursor() directly.
    """
    return conn.cursor(dictionary=True)


def init_db():
    """
    Creates the database (schema) and all tables if they don't exist.
    Safe to call every time the app starts.
    """
    # Connect WITHOUT specifying DB_NAME first
    conn = mysql.connector.connect(
        host     = Config.DB_HOST,
        port     = Config.DB_PORT,
        user     = Config.DB_USER,
        password = Config.DB_PASSWORD,
    )
    cursor = conn.cursor()

    # Create database if it doesn't exist
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{Config.DB_NAME}`")
    cursor.execute(f"USE `{Config.DB_NAME}`")

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id            INT AUTO_INCREMENT PRIMARY KEY,
            email         VARCHAR(255) UNIQUE NOT NULL,
            username      VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Projects table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id          VARCHAR(36)  PRIMARY KEY,
            user_id     INT          NOT NULL,
            topic       TEXT         NOT NULL,
            status      VARCHAR(50)  DEFAULT 'queued',
            error_msg   TEXT,
            script_json LONGTEXT,
            video_path  VARCHAR(500),
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP
                         ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print(f"[db] Database '{Config.DB_NAME}' and tables ready.")


def update_project_status(project_id: str, status: str, error_msg: str = None):
    """
    Updates a project's status as the pipeline progresses.
    """
    conn = get_connection()
    cursor = get_cursor(conn)
    cursor.execute(
        """
        UPDATE projects
        SET status    = %s,
            error_msg = %s
        WHERE id = %s
        """,
        (status, error_msg, project_id)
    )
    conn.commit()
    cursor.close()
    conn.close()


if __name__ == "__main__":
    init_db()