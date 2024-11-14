import os
import json
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
from pitch_desk.database import Pitch, SessionLocal, init_db

load_dotenv()
ELEVENLABS_API_KEY = os.getenv("XI_API_KEY")
VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel voice ID
FIXED_SLIDE_NO = 1  # Set a fixed slide number for all entries

headers = {"Content-Type": "application/json", "xi-api-key": ELEVENLABS_API_KEY}

pitch_indices_file = "docs/pitch_indices.json"


async def update_database(
    audio_seq_no, text_content, audio_url, start_time, end_time, session: AsyncSession
):
    pitch_data = {
        "slide_no": FIXED_SLIDE_NO,
        "audio_seq_no": audio_seq_no,
        "audio_url": audio_url,  # Assuming audio_url is the base64 encoded audio
        "text_content": text_content,
        "start_time": start_time,
        "end_time": end_time,
    }

    new_pitch = Pitch(**pitch_data)
    session.add(new_pitch)
    await session.commit()
    print(f"Saved audio for audio sequence {audio_seq_no}")


async def populate_database():
    await init_db()
    async with SessionLocal() as session:
        with open(pitch_indices_file, "r") as f:
            pitch_indices = json.load(f)

        for audio_seq_no, pitch_data in pitch_indices.items():
            text_content = pitch_data["content"]
            audio_url = pitch_data["url"]
            start_time = pitch_data["time_start"]
            end_time = pitch_data["time_end"]
            await update_database(
                int(audio_seq_no),
                text_content,
                audio_url,
                start_time,
                end_time,
                session,
            )


if __name__ == "__main__":
    import asyncio

    asyncio.run(populate_database())
