import asyncio
from pydantic import BaseModel
from typing import AsyncGenerator, List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from sqlalchemy.future import select

from pitch_desk.database import Pitch, SessionLocal, init_db
from pitch_desk.transcriber import Transcriber

app = FastAPI()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


class PitchRequest(BaseModel):
    slide_no: int
    audio_seq_no: int
    audio_url: str


@app.websocket("/ws/pitch")
async def websocket_endpoint(websocket: WebSocket, db: AsyncSession = Depends(get_db)):
    await websocket.accept()
    audio_marks_sent: List[int] = []
    current_audio_index = 0

    transcription_service = Transcriber()

    async def stream_audio():
        nonlocal current_audio_index
        stmt = select(Pitch).order_by(Pitch.slide_no, Pitch.audio_seq_no)
        result = await db.execute(stmt)
        pitches = result.scalars().all()

        while current_audio_index < len(pitches):
            pitch = pitches[current_audio_index]
            audio_mark = pitch.audio_seq_no
            audio_marks_sent.append(audio_mark)

            await websocket.send_json(
                {
                    "event": "media",
                    "media": {"payload": pitch.audio_url, "mark": audio_mark},
                }
            )

            current_audio_index += 1
            await asyncio.sleep(2)

            if interrupted_event.is_set():
                break

    interrupted_event = asyncio.Event()

    try:
        while True:
            data = await websocket.receive_json()
            event = data.get("event")

            if event == "start":
                current_audio_index = 0
                await stream_audio()

            elif event == "user_audio":
                audio_data = data.get("audio")
                if audio_data:
                    interrupted_event.set()  # Mark that the streaming was interrupted
                    # Take note of the audio sequence that got interrupted
                    interrupted_audio_seq = (
                        audio_marks_sent[-1] if audio_marks_sent else None
                    )
                    print(f"Interrupted audio seq: {interrupted_audio_seq}")
                    current_audio_index -= 1

                    await websocket.send_json({"event": "clear"})

                    transcription_service.set_pitch_content(
                        "Pitch content goes here"
                    )  # Set the pitch content
                    response_audio = await transcription_service.send(audio_data)

                    await websocket.send_json(
                        {
                            "event": "media",
                            "media": {
                                "payload": response_audio,
                                "mark": "user_response",
                            },
                        }
                    )

                    # Continue streaming from where it left off
                    interrupted_event.clear()
                    await stream_audio()

    except WebSocketDisconnect:
        print("WebSocket connection closed")


@app.post("/save_pitch")
async def save_pitch(pitch: PitchRequest, db: AsyncSession = Depends(get_db)):
    try:
        pitch_data = {
            "slide_no": pitch.slide_no,
            "audio_seq_no": pitch.audio_seq_no,
            "audio_url": pitch.audio_url,
        }
        saved_pitch = await Pitch.save_pitch(db, pitch_data)
        return {"message": "Pitch saved successfully", "pitch_id": saved_pitch.id}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error while saving pitch: {str(e)}"
        )


# MySQL Table Structure
# CREATE TABLE pitches (
#    id INT PRIMARY KEY AUTO_INCREMENT,
#    slide_no INT,
#    audio_seq_no INT,
#    audio_url VARCHAR(255)
# );


if __name__ == "__main__":
    import uvicorn
    import asyncio

    async def main():
        await init_db()
        uvicorn.run(app, host="0.0.0.0", port=8000)

    asyncio.run(main())
