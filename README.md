### TODO:

-   Set `.env`:

    -   OPENAI_API_KEY
    -   DEEPGRAM_API_KEY
    -   XI_API_KEY
    -   VOICE_ID
    -   XI_MODEL_ID
    -   DATABASE_URL

-   Prompt Better
-   Add `pitch.py` to handle pitch sentence and index

### WebSocket Endpoint

-   **URL**: `/ws/pitch`

### Events and Expected Payloads

#### 1. `start` Event

-   **Description**: Starts the audio streaming from the first pitch. The frontend should send this event to initiate the pitch audio stream.
-   **Payload**: None

**Request example**:

```json
{
    "event": "start"
}
```

#### 2. `user_audio` Event

-   **Description**: Sends user spoken audio to the backend when they ask question or intruputes. This will trigger the backend to process the audio and respond accordingly.
-   **Payload**: Contains the user audio data in a base64-encoded format.

**Request example**:

```json
{
    "event": "user_audio",
    "audio": "<base64-encoded-audio-data>"
}
```

-   **Important**: The `audio` field must contain the raw audio data in base64 format.

#### 3. `media` Event (Response)

-   **Description**: The server sends audio content for the user. This is part of the ongoing pitch audio stream.
-   **Payload**: Contains the pitch audio data in base64 format and the associated audio sequence mark.

**Response example**:

```json
{
    "event": "media",
    "media": {
        "payload": "<base64-encoded-audio-data>",
        "mark": "<audio-sequence-number>"
    }
}
```

#### 4. `clear` Event (Response)

-   **Description**: Indicates that the current pitch has been interrupted and will be cleared.
-   **Payload**: None

**Response example**:

```json
{
    "event": "clear"
}
```

#### 5. `end` Event (Response)

-   **Description**: Indicates that the pitch audio stream has ended.
-   **Payload**: None

**Response example**:

```json
{
    "event": "end"
}
```

### WebSocket Flow

1. **Client sends `start` event** to begin streaming.
2. The server responds with pitch audio in a series of `media` events.
3. If the user wants to interrupt or asks a question, client send a `user_audio` event with the base64-encoded audio data of the user.
4. The server will process the user’s audio and resume streaming the pitch from the point it was interrupted.

### Interrupting the Stream

-   When the frontend sends a `user_audio` event, the backend processes the audio and then clears the previous stream using the `clear` event.
-   After processing, the server continues streaming the remaining pitches from where it left off.
