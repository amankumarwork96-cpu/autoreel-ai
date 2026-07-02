import os
import threading
from config import Config
from database.db import update_project_status
from models.project import set_project_script, set_project_video, get_project
from services.script_service import generate_script
from services.image_service import generate_all_images
from services.audio_service import generate_voiceover
from services.video_service import render_video

# ─────────────────────────────────────────────
#  WHY A BACKGROUND WORKER?
#  ─────────────────────────────────────────────
#  The full pipeline takes 1-2 minutes (script + 6 images + audio + render).
#  If we ran this directly inside a Flask route, the user's browser
#  would hang for 2 minutes waiting for a response — bad experience,
#  and the request would likely time out.
#
#  Instead:
#  1. The route creates a project (status='queued') and returns INSTANTLY
#  2. This worker runs in a background thread, doing the slow work
#  3. The status page polls the database every few seconds to show progress
#
#  This is the same pattern as the original project's generate_process.py,
#  but instead of polling a folder every 4 seconds, we trigger it directly
#  per-project using threading.
# ─────────────────────────────────────────────


def run_pipeline(project_id: str, topic: str):
    """
    Runs the full reel generation pipeline for one project.
    Updates the database status at every stage so the status
    page can show real-time progress.

    This function is designed to run in a background thread —
    see start_generation() below.
    """

    project_folder = os.path.join(Config.UPLOAD_FOLDER, project_id)
    os.makedirs(project_folder, exist_ok=True)

    try:
        # ── Stage 1: Generate script ─────────────────────────────
        update_project_status(project_id, "generating_script")
        scenes = generate_script(topic)
        set_project_script(project_id, scenes)  # also sets status → generating_images

        # ── Stage 2: Generate images ─────────────────────────────
        # set_project_script already moved status to 'generating_images'
        image_paths = generate_all_images(scenes, project_folder)

        # ── Stage 3: Generate voiceover ───────────────────────────
        update_project_status(project_id, "generating_audio")
        audio_path = os.path.join(project_folder, "audio.mp3")
        generate_voiceover(scenes, audio_path)

        # ── Stage 4: Render final video ───────────────────────────
        update_project_status(project_id, "rendering_video")
        output_path = os.path.join(Config.REELS_FOLDER, f"{project_id}.mp4")
        render_video(image_paths, audio_path, output_path, project_folder)

        # ── Done ───────────────────────────────────────────────────
        # set_project_video saves the path AND sets status → 'done'
        set_project_video(project_id, output_path)

        print(f"[worker] Pipeline complete for project {project_id}")

    except Exception as e:
        # Any failure at any stage lands here.
        # We save the error message so the status page can show it.
        error_message = str(e)
        print(f"[worker] Pipeline FAILED for project {project_id}: {error_message}")
        update_project_status(project_id, "failed", error_msg=error_message)


def start_generation(project_id: str, topic: str):
    """
    Starts the pipeline in a background thread.
    Returns immediately — the route can respond to the user instantly
    while this keeps running in the background.

    daemon=True means this thread won't block the app from shutting down.
    """
    thread = threading.Thread(
        target=run_pipeline,
        args=(project_id, topic),
        daemon=True
    )
    thread.start()
    print(f"[worker] Started background generation for project {project_id}")


# ─────────────────────────────────────────────
#  TEST — python workers/generate_worker.py
#  ─────────────────────────────────────────────
#  This test runs the pipeline SYNCHRONOUSLY (not in a thread)
#  so we can see all the print statements in order and watch
#  the full pipeline run start to finish.
# ─────────────────────────────────────────────
if __name__ == "__main__":
    from models.project import create_project

    TEST_USER_ID = 1
    TEST_TOPIC = "3 tips to stay focused while studying"

    print(f"Creating project for topic: '{TEST_TOPIC}'\n")
    project_id = create_project(TEST_USER_ID, TEST_TOPIC)
    print(f"Project ID: {project_id}\n")

    print("Running pipeline (this will take 1-2 minutes)...\n")
    run_pipeline(project_id, TEST_TOPIC)   # synchronous call for testing

    print("\n── Final project state ──")
    project = get_project(project_id)
    print(f"Status:     {project['status']}")
    print(f"Video path: {project['video_path']}")