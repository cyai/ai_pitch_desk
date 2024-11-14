import os
import json
import time
import base64
import requests
from dotenv import load_dotenv

load_dotenv()


class XILabsTTS:
    def __init__(self):
        self.voice_id = os.getenv("VOICE_ID")
        self.next_expected_index = 0
        self.speech_buffer = {}
        self.callbacks = {}

    def on(self, event_name, callback):
        self.callbacks[event_name] = callback
        print(f"Registered callback for {event_name}")

    def emit(self, event_name, data=None):
        if event_name in self.callbacks:
            self.callbacks[event_name](data)

    async def generate(self, text):
        start_time = time.time()

        try:

            output_format = "ulaw_8000"
            response = requests.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}/stream?output_format={output_format}&optimize_streaming_latency=4",
                headers={
                    "xi-api-key": os.getenv("XI_API_KEY"),
                    "Content-Type": "application/json",
                    "accept": "audio/wav",
                },
                data=json.dumps(
                    {
                        "model_id": os.getenv("XI_MODEL_ID"),
                        "text": text,
                        "voice_settings": {
                            "stability": 0.4,
                            "style": 0.2,
                            "similarity_boost": 0,
                            "use_speaker_boost": False,
                        },
                    }
                ),
            )
            audioArrayBuffer = response.content
            end_time = time.time()
            print(f"--->> Time taken for TTS: {end_time - start_time}")

            return base64.b64encode(audioArrayBuffer).decode("utf-8")

        except Exception as err:
            print("Error occurred in TextToSpeech service")
            print(err)
