import os
from elevenlabs import ElevenLabs, VoiceSettings
from config import Config

# ─────────────────────────────────────────────
#  HOW ELEVENLABS WORKS
#  ─────────────────────────────────────────────
#  ElevenLabs converts text to speech using AI voices.
#  We send all scene narrations joined as one block of text.
#  ElevenLabs returns audio bytes which we save as an MP3.
#
#  Free tier: 10,000 characters/month
#  Our scripts are ~150 words = ~900 characters per reel
#  So free tier gives you ~11 reels/month
# ─────────────────────────────────────────────


def generate_voiceover(scenes: list, save_path: str) -> str:
    """
    Takes all scene narrations, joins them, converts to MP3.
    Returns the save_path if successful.
 
    scenes    : list of scene dicts from script_service
    save_path : where to save the MP3 e.g. "uploads/abc123/audio.mp3"
    """

    # Join all narrations into one block of text
    # Add a short pause between scenes using "..." 
    # ElevenLabs reads punctuation naturally — "..." creates a brief pause
    full_text = " ... ".join(scene["narration"] for scene in scenes)

    print(f"[audio] Generating voiceover ({len(full_text)} characters)...")

    # Initialize the ElevenLabs client with your API key
    client = ElevenLabs(api_key=Config.ELEVENLABS_API_KEY)

    # Convert text to speech
    # convert() returns a generator of audio chunks
    audio_chunks = client.text_to_speech.convert(
        voice_id=Config.ELEVENLABS_VOICE_ID,
        text=full_text,
        model_id="eleven_turbo_v2_5",
        output_format="mp3_22050_32",

        voice_settings=VoiceSettings(
            stability=0.5,
            similarity_boost=0.8,
            style=0.0,
            use_speaker_boost=True,
            speed=0.9
        )
    )

    # Make sure the folder exists
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    # Write audio chunks to MP3 file
    # ElevenLabs returns a generator — we loop through chunks and write each
    with open(save_path, "wb") as f:
        for chunk in audio_chunks:
            if chunk:
                f.write(chunk)

    print(f"[audio] Voiceover saved: {save_path}")
    return save_path 


# ─────────────────────────────────────────────
#  TEST — python services/audio_service.py
# ─────────────────────────────────────────────
if __name__ == "__main__":
    test_scenes = [
        {"narration": "Wake up 1 hour earlier and watch your productivity soar."},
        {"narration": "Start with a 10-minute meditation to clear your mind and set intentions."},
        {"narration": "Drink a full glass of water to rehydrate and energize your body."},
    ]
 
    save_path = "uploads/test_project/audio.mp3"
    os.makedirs("uploads/test_project", exist_ok=True)
 
    generate_voiceover(test_scenes, save_path)
    print(f"\nOpen {save_path} to hear the voiceover.")