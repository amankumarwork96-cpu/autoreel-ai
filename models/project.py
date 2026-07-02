import uuid 
import json
from database.db import get_connection, get_cursor


# ─────────────────────────────────────────────
#  WHY UUID FOR PROJECT ID?
#  ─────────────────────────────────────────────
#  Users table uses AUTO_INCREMENT integers: 1, 2, 3...
#  Projects table uses UUIDs: "a1b2c3d4-..."
#
#  Why the difference?
#  Project IDs appear in URLs: /status/a1b2c3d4-...
#  If we used integers, users could guess other users' project URLs:
#    /status/1  /status/2  /status/3  ← easy to enumerate
#  UUIDs are random and impossible to guess.
# ─────────────────────────────────────────────


def create_project(user_id: int, topic: str) -> str:
    """
    Creates a new rel geenration job.
    Returns the project ID (UUID string).

    Called the moment a user submits a topic.
    Status starts as 'queued' - the worker picks it up from there.
    """
    project_id = str(uuid.uuid4()) # e.g. "a1b2c3d4-e5f6-..."

    conn = get_connection()
    cursor =  get_cursor(conn)

    try:
        cursor.execute(
            """
            INSERT INTO projects (id, user_id, topic, status)
            VALUES (%s, %s, %s, 'queued')
            """,
            (project_id, user_id, topic)
        )
        conn.commit()
        print(f"[project] Created project {project_id} for user {user_id}")
        return project_id
    
    except Exception as e:
        print(f"[project] create_project failed: {e}")
        return None
    
    finally:
        cursor.close()
        conn.close()


def get_project(project_id: str) -> dict:
    """
    Fetches a single project by ID.
    Returns a dict with all columns, or None if not found.
 
    Used by:
    - Status page: polls this every few seconds to show progress
    - Gallery: checks if video_path is set before showing the reel
    """
    conn = get_connection()
    cursor = get_cursor(conn)

    cursor.execute(
        "SELECT * FROM projects WHERE id = %s",
        (project_id,)
    )
    project = cursor.fetchone()

    cursor.close()
    conn.close()
    return project


def get_user_projects(user_id: int) -> list:
    """
    Fetches all projects belonging to a user.
    Returns a list of dicts, newest first.
 
    Used by the dashboard to show the user's reel history.
    """
    conn = get_connection()
    cursor = get_cursor(conn)

    cursor.execute(
        "SELECT * FROM projects WHERE user_id = %s ORDER BY created_at DESC",
        (user_id,)
    )
    projects = cursor.fetchall() # fetchall() returns a list of dicts


    cursor.close()
    conn.close()
    return projects


def set_project_script(project_id: str, scenes: list):
    """
    Saves Groq's generated script into the project row.
    scenes is a Python list of dicts — we store it as a JSON string.
 
    Called by the worker after script generation succeeds.
    """
    # Convert Python list → JSON string for storage
    # e.g. [{"narration": "...", "image_prompt": "..."}]
    script_json = json.dumps(scenes)

    conn = get_connection()
    cursor = get_cursor(conn)

    cursor.execute(
        """
        UPDATE projects
        SET script_json = %s,
            status      = 'generating_images'
        WHERE id = %s
        """,
        (script_json, project_id)
    )
    conn.commit()
    cursor.close()
    conn.close()


def set_project_video(project_id: str, video_path: str):
    """
    Saves the final video path and marks the project as done.
    Called by the worker after FFmpeg finishes rendering.
    """
    conn = get_connection()
    cursor = get_cursor(conn)

    cursor.execute(
        """
        UPDATE projects
        SET video_path = %s,
            status     = 'done'
        WHERE id = %s
        """,
        (video_path, project_id)
    )
    conn.commit()
    cursor.close()
    conn.close()
    print(f"[project] Project {project_id} marked as done.")


# ─────────────────────────────────────────────
#  TEST — python models/project.py
# ─────────────────────────────────────────────
if __name__ == "__main__":
        # We need a real user_id — use the one created in user.py test
        TEST_USER_ID = 1

        # Test 1: Create a project
        print("── Test 1: Create project ──")
        project_id = create_project(TEST_USER_ID, "5 habits of successful people")

        # Test 2: Fetch it back
        print("\n── Test 2: Get project ──")
        project = get_project(project_id)
        print(f"Topic: {project['topic']}")
        print(f"Status: {project['status']}")

        # Test 3: Save a script
        print("\n── Test 3: Set script ──")
        fake_scenes = [
        {"narration": "Most people wait for the right moment.", "image_prompt": "person standing at crossroads at dawn"},
        {"narration": "Successful people create it.", "image_prompt": "confident entrepreneur on city rooftop"},
        ]
        set_project_script(project_id, fake_scenes)
        project = get_project(project_id)
        print(f"Status after script: {project['status']}")
        print(f"Script saved: {project['script_json'][:60]}...")


        # Test 4: Get all user projects
        print("\n── Test 4: Get user projects ──")
        projects = get_user_projects(TEST_USER_ID)
        print(f"Total projects for user {TEST_USER_ID}: {len(projects)}")