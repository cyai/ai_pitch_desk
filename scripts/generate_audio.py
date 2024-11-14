import os
import base64
import asyncio
import requests
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession

from pitch_desk.database import SessionLocal
from docs.pitch_indices import pitch_indices

load_dotenv()
ELEVENLABS_API_KEY = os.getenv("XI_API_KEY")
VOICE_ID = "bIHbv24MWmeRgasZH58o"  # Will voice ID
FIXED_SLIDE_NO = 1  # Set a fixed slide number for all entries

headers = {"Content-Type": "application/json", "xi-api-key": ELEVENLABS_API_KEY}


async def generate_and_save_audio(audio_seq_no, text_content, session: AsyncSession):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/with-timestamps"

    data = {
        "text": text_content,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
    }

    response = requests.post(url, json=data, headers=headers)

    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return

    response_dict = response.json()
    audio_base64 = response_dict["audio_base64"]
    alignment = response_dict["alignment"]

    audio_data = base64.b64decode(audio_base64)
    audio_filename = f"audio/{audio_seq_no}.mp3"

    with open(audio_filename, "wb") as audio_file:
        audio_file.write(audio_data)
    print(f"    Audio file saved as {audio_filename}")


async def generate_audio():
    async with SessionLocal() as session:
        for audio_seq_no, text_content in pitch_indices.items():
            print(f"Generating audio for audio sequence {audio_seq_no}")
            await generate_and_save_audio(int(audio_seq_no), text_content, session)


if __name__ == "__main__":
    asyncio.run(generate_audio())
