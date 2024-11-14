import os
import tempfile
from openai import OpenAI
from dotenv import load_dotenv

from pitch_desk.prompt import system_prompt
from pitch_desk.tts import XILabsTTS
from pitch_desk.tools import TOOLS

load_dotenv()


class LLMService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.tts = XILabsTTS()

    async def process_user_input(self, user_input, pitch_content):
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt.format(
                        pitch_content=pitch_content,
                        question=user_input,
                    ),
                },
                {
                    "role": "user",
                    "content": user_input,
                },
            ],
            tools=TOOLS,
        )

        return self.tts.generate(response)
