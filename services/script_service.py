import json
import requests
from config import Config

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM_PROMPT = """You are a viral short-form video scriptwriter.

When given a topic, write a reel script broken into exactly 6 scenes.
Each scene must have:
- narration: 1-2 punchy sentences for voiceover (max 25 words)
- image_prompt: a vivid visual description for AI image generation (max 15 words)

Rules:
- Keep narration energetic and motivational
- Image prompts must be cinematic and specific
- No hashtags, no emojis, no markdown
- Reply ONLY with a valid JSON array. No explanation, no preamble, no code fences.

Example format:
[
  {
    "narration": "Most people wait for the perfect moment. Successful people create it.",
    "image_prompt": "confident entrepreneur standing at sunrise on city rooftop dramatic lighting"
  }
]"""


def generate_script(topic: str) -> list:
    """
    Calls Groq API and returns a list of scene dicts.
    Each dict: { "narration": "...", "image_prompt": "..." }
    """

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {Config.GROQ_API_KEY}"
    }

    payload = {
        "model": Config.GROQ_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": f"Write a reel script about: {topic}"}
        ],
        "temperature": 0.7,
        "max_tokens": 1000
    }

    response = requests.post(GROQ_API_URL, headers=headers, json=payload)

    # Raise an exception if status code is not 200
    if response.status_code != 200:
        raise Exception(f"Groq API error {response.status_code}: {response.text}")

    result = response.json()
    raw_text = result["choices"][0]["message"]["content"].strip()

    # Strip markdown code fences if model added them
    if raw_text.startswith("```"):
        lines = raw_text.split("\n")
        raw_text = "\n".join(lines[1:-1]).strip()

    # Parse JSON
    try:
        scenes = json.loads(raw_text)
    except json.JSONDecodeError as e:
        raise Exception(f"Groq returned invalid JSON: {e}\nRaw: {raw_text}")

    # Validate structure
    if not isinstance(scenes, list) or len(scenes) == 0:
        raise Exception(f"Expected a non-empty list, got: {type(scenes)}")

    for i, scene in enumerate(scenes):
        if "narration" not in scene or "image_prompt" not in scene:
            raise Exception(f"Scene {i} missing keys: {scene}")

    print(f"[script] Generated {len(scenes)} scenes for: '{topic}'")
    return scenes


# ─────────────────────────────────────────────
#  TEST — python services/script_service.py
# ─────────────────────────────────────────────
if __name__ == "__main__":
    topic = "5 morning habits that will change your life"
    print(f"Generating script for: '{topic}'\n")

    scenes = generate_script(topic)

    for i, scene in enumerate(scenes, 1):
        print(f"Scene {i}:")
        print(f"  Narration    : {scene['narration']}")
        print(f"  Image Prompt : {scene['image_prompt']}")
        print()