import os
import subprocess
from config import Config

# ─────────────────────────────────────────────
#  HOW FFMPEG WORKS HERE
#  ─────────────────────────────────────────────
#  FFmpeg is a command line tool. We call it from Python
#  using subprocess.run() — same as typing in the terminal.
#
#  What we're doing:
#  1. Create an input.txt file listing all images with durations
#  2. Run FFmpeg to stitch images + audio into a 1080x1920 MP4
#
#  The input.txt format (FFmpeg concat format):
#    file 'scene_1.jpg'
#    duration 3
#    file 'scene_2.jpg'
#    duration 3
#    ...
# ─────────────────────────────────────────────


def create_input_file(image_paths: list, project_folder: str) -> str:
    """
    Creates the FFmpeg concat input file.
    Lists each image with its display duration.
    Returns the path to the input.txt file.
    """
    input_file_path = os.path.join(project_folder, "input.txt")

    with open(input_file_path, "w") as f:
        for image_path in image_paths:
            # FFmpeg needs forward slashes even on Windows
            clean_path = image_path.replace("\\", "/")
            # Use absolute path to avoid any path resolution issues
            abs_path = os.path.abspath(clean_path).replace("\\", "/")
            f.write(f"file '{abs_path}'\n")
            f.write(f"duration {Config.SCENE_DURATION_SECONDS}\n")

        # FFmpeg concat requires the last file to be listed twice
        # This is a known FFmpeg quirk — without it the last frame is skipped
        last_path = os.path.abspath(image_paths[-1]).replace("\\", "/")
        f.write(f"file '{last_path}'\n")

    print(f"[video] Input file craeted: {input_file_path}")
    return input_file_path


def render_video(image_paths: list, audio_path: str,
                output_path: str, project_folder: str) -> str:
    """
    Stitches images + audio into a final MP4 reel using FFmpeg.
    Returns the output_path if successful.
 
    image_paths    : list of image file paths in scene order
    audio_path     : path to the MP3 voiceover
    output_path    : where to save the final MP4
    project_folder : working folder for temp files
    """

    # Step 1: Create the input file FFmpeg needs
    input_file = create_input_file(image_paths, project_folder)

    # Step 2: Make sure output folder exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Step 3: Build the FFmpeg command
    # Breaking it down piece by piece:
    #
    # -f concat -safe 0 -i input.txt
    #   → read images from our concat list
    #
    # -i audio.mp3
    #   → use this as the audio track
    #
    # -vf "scale=1080:1920:force_original_aspect_ratio=decrease,
    #      pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black"
    #   → scale each image to fit 1080x1920
    #   → pad with black bars if aspect ratio doesn't match perfectly
    #
    # -c:v libx264   → encode video with H.264 (most compatible)
    # -c:a aac       → encode audio with AAC
    # -shortest      → stop when the shorter stream ends (audio or video)
    # -r 30          → 30 frames per second
    # -pix_fmt yuv420p → pixel format required for compatibility
    #                    (especially for phones and social media)

    abs_audio = os.path.abspath(audio_path).replace("\\", "/")
    abs_output = os.path.abspath(output_path).replace("\\", "/")
    abs_input = os.path.abspath(input_file).replace("\\", "/")

    command = [
        "ffmpeg",
        "-y",
         "-f", "concat",
        "-safe", "0",
        "-i", abs_input,         # image list
        "-i", abs_audio,         # audio file
        "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,"
               "pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-shortest",
        "-r", str(Config.VIDEO_FPS),
        "-pix_fmt", "yuv420p",
        abs_output
    ]

    print(f"[video] Rendering reel → {output_path}")
    print(f"[video] This may take 30-60 seconds...")

    # Run FFmpeg — capture output so errors are readable
    result =subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode !=0:
        # FFmpeg writes errors to stderr
        raise Exception(f"Ffmpeg failed:\n{result.stderr[-1000:]}")
    
    print(f"[video] Reel rendered successfully: {output_path}")
    return output_path


# ─────────────────────────────────────────────
#  TEST — python services/video_service.py
# ─────────────────────────────────────────────
if __name__ == "__main__":
    import os
 
    # Use images and audio from previous tests
    test_folder = "uploads/test_project"
    image_paths = [
        f"{test_folder}/scene_1.jpg",
        f"{test_folder}/scene_2.jpg",
    ]
    audio_path  = f"{test_folder}/audio.mp3"
    output_path = "static/reels/test_reel.mp4"
 
    # Make sure static/reels folder exists
    os.makedirs("static/reels", exist_ok=True)
 
    render_video(image_paths, audio_path, output_path, test_folder)
    print(f"\nOpen {output_path} to watch the reel.")