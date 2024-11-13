import os
import base64
import asyncio
from deepgram.client import (
    DeepgramClient,
    LiveTranscriptionEvents,
    LiveOptions,
    DeepgramClientOptions,
)
from dotenv import load_dotenv

from pitch_desk.llm_service import LLMService

load_dotenv()


class Transcriber:
    def __init__(self) -> None:

        config = DeepgramClientOptions(options={"keepalive": "true"})
        deepgram = DeepgramClient(api_key=os.getenv("DEEPGRAM_API_KEY"), config=config)
        self.deepgram_live = deepgram.listen.live.v("1")

        self.finalResult = ""
        self.speechFinal = False
        self.silenceStart = None
        self.silenceCount = 0
        self.callbacks = {}

        self.deepgram_live.on(LiveTranscriptionEvents.Transcript, self.on_transcript)
        self.deepgram_live.on(LiveTranscriptionEvents.Error, self.on_error)
        self.deepgram_live.on(LiveTranscriptionEvents.Warning, self.on_warning)
        self.deepgram_live.on(LiveTranscriptionEvents.Metadata, self.on_metadata)
        self.deepgram_live.on(LiveTranscriptionEvents.Close, self.on_close)
        self.deepgram_options = LiveOptions(
            # encoding="mulaw",
            # sample_rate="8000",
            model="nova-2-conversationalai",
            punctuate=True,
            interim_results=True,
            endpointing=500,
            utterance_end_ms="1000",
            vad_events=True,
            smart_format=True,
            language="en-US",
            filler_words=True,
        )

        self.deepgram_live.start(self.deepgram_options)

        self.llm_service = LLMService()

    def set_pitch_content(self, pitch_content):
        self.pitch_content = pitch_content

    def on(self, event_name, callback):
        self.callbacks[event_name] = callback

    def emit(self, event_name, data=None):
        if event_name in self.callbacks:
            self.callbacks[event_name](data)

    def on_transcript(self, transcription, *args, **kwargs):
        transcription = kwargs["result"]
        channel = transcription.channel
        alternatives = channel.alternatives
        text = ""

        if alternatives:
            text = alternatives[0].transcript

        if transcription.is_final and len(text.strip()) > 0:
            self.finalResult += text

            if transcription.speech_final:
                self.speechFinal = True
                final_text = self.finalResult
                self.finalResult = ""
                return asyncio.run(
                    self.llm_service.process_user_input(final_text, self.pitch_content)
                )

            else:
                self.speechFinal = False

    def on_error(self, error, *args, **kwargs):
        error = kwargs
        print("STT -> deepgram error")
        print("ARGS: ", args)
        print(error)

    def on_warning(self, warning, *args, **kwargs):
        warning = kwargs
        print("STT -> deepgram warning")
        print(warning)

    def on_metadata(self, metadata, *args, **kwargs):
        metadata = kwargs
        print("STT -> deepgram metadata")
        print(metadata)

    def on_close(self, *args, **kwargs):
        print("STT -> Deepgram connection closed")

    async def send(self, payload):
        """
        Send the payload to Deepgram
        :param payload: A base64 audio stream
        """
        self.deepgram_live.send(base64.b64decode(payload))
