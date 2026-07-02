import os
import time
import requests
from urllib.parse import quote
from config import Config

# ─────────────────────────────────────────────
#  HOW POLLINATIONS WORKS
#  ─────────────────────────────────────────────
#  No API key needed. Just build a URL with the prompt
#  and make a GET request. Pollinations generates the image
#  and returns it as raw image bytes.
#
#  URL format:
#  https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1920&nologo=true
#
#  We save each image as a JPG file in the project's folder.
# ─────────────────────────────────────────────


def generate_image(prompt: str, save_path: str) -> str:
    """
    Generates one image from a prompt and saves it to disk.
    Returns the save_path if successful.
 
    prompt    : the image description from the script
    save_path : full path where the JPG should be saved
                e.g. "uploads/abc123/scene_1.jpg"
    """

    # URL-encode the prompt so spaces and special chars work in a URL
    # "morning garden sunrise" → "morning%20garden%20sunrise"
    encoded_prompt = quote(prompt)

    url = (
        f"{Config.POLLINATIONS_BASE_URL}/{encoded_prompt}"
        f"?width={Config.IMAGE_WIDTH}"
        f"&height={Config.IMAGE_HEIGHT}"
        f"&nologo=true"
        f"&model=flux"
    )

    # Pollinations can be slow — set a generous timeout
    # timeout=(10, 60) means:
    #   10 seconds to establish connection
    #   60 seconds to finish downloading the image
    response = requests.get(url, timeout=(10, 60))

    if response.status_code != 200:
        raise Exception(
            f"Pollination error {response.status_code} for prompt: '{prompt}"
        )
    
    # Make sure the folder exists before saving
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    # Write raw image bytes to file
    with open(save_path, "wb") as f:
        f.write(response.content)

        print(f"[image] Saved: {save_path}")
        return save_path
    

def generate_all_images(scenes: list, project_folder: str) -> list:
    """
    Generates one image per scene and saves them all to disk.
    Returns a list of file paths in scene order.
 
    scenes         : list of scene dicts from script_service
    project_folder : folder to save images in e.g. "uploads/abc123"
 
    Why we sleep 1 second between requests:
    Pollinations is free — being polite prevents rate limiting.
    """
    image_paths = []

    for i, scene in enumerate(scenes):
        prompt = scene["image_prompt"]
        save_path = os.path.join(project_folder, f"scene_{i+1}.jpg")

        print(f"[image] Generating scene {i+1}/{len(scenes)}: '{prompt}'")

        try:
            path = generate_image(prompt, save_path)
            image_paths.append(path)
        except Exception as e:
            print(f"[image] Failed scene {i+1}: {e}")
            raise

        # Be polite to the free API — 1 second between requests
        if 1 < len(scene) - 1:
            time.sleep(1)

    print(f"[image] All {len(image_paths)} images generated.")
    return image_paths


# ─────────────────────────────────────────────
#  TEST — python services/image_service.py
# ─────────────────────────────────────────────
if __name__ == "__main__":
    import os
 
    # Use the scenes from our script test
    test_scenes = [
        {"narration": "Wake up 1 hour earlier and watch your productivity soar.",
         "image_prompt": "early riser sitting in quiet morning garden surrounded by nature"},
        {"narration": "Start with a 10-minute meditation to clear your mind.",
         "image_prompt": "calm woman in lotus position on serene mountain peak at sunrise"},
    ]
 
    # Save to a test folder
    test_folder = "uploads/test_project"
    os.makedirs(test_folder, exist_ok=True)
 
    print("Generating test images (this may take 20-30 seconds)...\n")
    paths = generate_all_images(test_scenes, test_folder)
 
    print(f"\nImages saved:")
    for p in paths:
        print(f"  {p}")
    print("\nOpen the uploads/test_project folder to view the images.")