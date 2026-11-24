import io
import os
import re
import json
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from pydub import AudioSegment

load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
SWATHI_VOICE_ID = os.getenv("SWATHI_VOICE_ID")
SAGE_VOICE_ID = os.getenv("SAGE_VOICE_ID")

client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

def clean_dialogue_for_tts(text: str) -> str:
    return re.sub(r'\[.*?\]', '...', text).strip()

def synthesize_episode(script_json_path: str, output_mp3_path: str):
    """Reads a chapter JSON script and stitches clean MP3 segments with natural pauses."""
    with open(script_json_path, "r", encoding="utf-8") as f:
        script_data = json.load(f)

    turns = script_data.get("turns", [])
    if not turns:
        print(f"No dialogue turns found in {script_json_path}")
        return

    os.makedirs(os.path.dirname(output_mp3_path), exist_ok=True)
    print(f"Synthesizing {len(turns)} dialogue turns for {os.path.basename(output_mp3_path)}...")

    combined_audio = AudioSegment.empty()
    pause_between_speakers = AudioSegment.silent(duration=350)  # 350ms natural breath pause

    for idx, turn in enumerate(turns, start=1):
        speaker = turn.get("speaker", "").lower().strip()
        spoken_text = clean_dialogue_for_tts(turn.get("text", ""))
        if not spoken_text:
            continue

        voice_id = SWATHI_VOICE_ID if "swathi" in speaker else SAGE_VOICE_ID
        print(f"  [{idx}/{len(turns)}] {speaker.upper()}: {spoken_text[:45]}...")

        audio_generator = client.text_to_speech.convert(
            voice_id=voice_id,
            text=spoken_text,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128",
            voice_settings={
                "stability": 0.45,
                "similarity_boost": 0.80,
                "style": 0.15,
                "use_speaker_boost": True
            }
        )

        # Load the turn into pydub so headers are stripped cleanly
        turn_bytes = b"".join(chunk for chunk in audio_generator if chunk)
        turn_segment = AudioSegment.from_mp3(io.BytesIO(turn_bytes))
        combined_audio += turn_segment + pause_between_speakers

    combined_audio.export(output_mp3_path, format="mp3", bitrate="192k")
    print(f"\nFinished! Clean episode saved to: {output_mp3_path}")
if __name__ == "__main__":
    sample_script = os.path.join("data", "intermediate", "chapter_1_script.json")
    sample_output = os.path.join("data", "output_audio", "episode_1_chapter_1.mp3")

    if os.path.exists(sample_script):
        synthesize_episode(sample_script, sample_output)
    else:
        print(f"Could not find {sample_script}")