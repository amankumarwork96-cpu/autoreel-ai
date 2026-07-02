import os
from dotenv import load_dotenv

# override=True forces dotenv to reload even if values are already in os.environ
load_dotenv(override=True)


class Config:

    # ── Flask ──────────────────────────────────────────────────────
    SECRET_KEY = os.getenv("SECRET_KEY", "change-this-in-production")
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"

    # ── MySQL Database ─────────────────────────────────────────────
    DB_HOST     = os.getenv("DB_HOST", "localhost")
    DB_PORT     = int(os.getenv("DB_PORT", "3306"))
    DB_USER     = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME     = os.getenv("DB_NAME", "autoreel")

    # ── File Storage ───────────────────────────────────────────────
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
    REELS_FOLDER  = os.getenv("REELS_FOLDER",  "static/reels")

    # ── API Keys ───────────────────────────────────────────────────
    GROQ_API_KEY  = os.getenv("GROQ_API_KEY")
    GROQ_MODEL    = "llama-3.1-8b-instant"

    ELEVENLABS_API_KEY  = os.getenv("ELEVENLABS_API_KEY")
    ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "pNInz6obpgDQGcFmaJgB")

    # ── Pollinations ───────────────────────────────────────────────
    POLLINATIONS_BASE_URL = "https://image.pollinations.ai/prompt"
    IMAGE_WIDTH           = 1080
    IMAGE_HEIGHT          = 1920

    # ── Reel settings ──────────────────────────────────────────────
    SCENE_DURATION_SECONDS = 3
    VIDEO_FPS              = 30


def validate_config():
    required = {
        "GROQ_API_KEY":       Config.GROQ_API_KEY,
        "ELEVENLABS_API_KEY": Config.ELEVENLABS_API_KEY,
    }
    missing = [k for k, v in required.items() if not v]
    if missing:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing)}\n"
            "Add them to your .env file."
        )