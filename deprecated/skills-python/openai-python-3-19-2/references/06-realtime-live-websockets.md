# Realtime, Live, and WebSocket APIs

All three use WebSockets and require the `openai[realtime]` extra (`websockets >= 13, < 16`).

## Realtime API

Low-latency multimodal (text + audio in/out) conversation over a WebSocket, with function calling. The SDK drives the `websockets` library internally.

```python
import asyncio
from openai import AsyncOpenAI

async def main():
    client = AsyncOpenAI()
    async with client.realtime.connect(model="gpt-realtime-2") as connection:
        await connection.session.update(session={"type": "realtime", "output_modalities": ["text"]})
        await connection.conversation.item.create(
            item={"type": "message", "role": "user",
                  "content": [{"type": "input_text", "text": "Say hello!"}]}
        )
        await connection.response.create()

        async for event in connection:
            if event.type == "response.output_text.delta":
                print(event.delta, flush=True, end="")
            elif event.type == "response.output_text.done":
                print()
            elif event.type == "response.done":
                break

asyncio.run(main())
```

Client-sent events (session config, item create, response create, input audio buffer append/commit) and server-sent events (deltas, done, response lifecycle) — the full event reference is on the OpenAI docs site. Audio input/output is the main use case; `examples/realtime/push_to_talk_app.py` is a complete TUI app (needs `portaudio`/`ffmpeg` on macOS).

**Error handling is on you**: on errors the API sends an `error` event and the connection stays open; the SDK raises nothing.

```python
async for event in connection:
    if event.type == "error":
        print(event.error.type, event.error.code, event.error.message, event.error.event_id)
```

The sync client (`OpenAI`) exposes the same `client.realtime.connect(...)` interface. `websocket_base_url` on the client controls the WebSocket origin (otherwise derived from the HTTP base).

## Live API

`client.live.connect()` opens a Live session (e.g., streaming audio transcripts):

```python
from openai import AsyncOpenAI, OpenAIError
from openai.lib.live import AsyncTranscriptGrouper

async with AsyncOpenAI() as client, AsyncTranscriptGrouper() as transcript:
    transcript.on("segment.updated", render_segment)
    async with client.live.connect(max_retries=0) as connection:
        await connection.session.start(session={
            "model": model,
            "audio": {"format": {"type": "audio/pcm", "rate": 24000}},
            "instructions": "Respond briefly and naturally.",
        })
        async for event in connection:          # or await connection.recv()
            await transcript.push(event)
            if event.type == "error":
                raise OpenAIError(...)         # surface errors yourself
            if event.type == "session.closed":
                break
```

`TranscriptGrouper` / `AsyncTranscriptGrouper` (from `openai.lib.live`) group raw transcript events into per-speaker `TranscriptSegment` objects (`speaker`, `text`, `id`) with `on("segment.updated", cb)`. Audio for Live is 16-bit mono PCM WAV at 24 kHz.

## Responses over WebSocket

`client.responses.connect()` streams Responses API events over a WebSocket instead of SSE:

```python
from openai import OpenAI
from openai.lib.responses_websocket import ResponsesWebSocketLimits, ResponsesWebSocketSession

with OpenAI() as client, \
     client.responses.connect(websocket_connection_options={"max_size": None}) as connection, \
     ResponsesWebSocketSession(connection, limits=limits) as session:
    lane = session.lane("example")
    lane.send({"type": "response.create", "model": "gpt-4o-mini", "input": "Say hello."})
    response = lane.get_final_response(timeout=60)
    lane.send({"type": "response.create", "previous_response_id": response.id, "input": "Now say goodbye."})
    response = lane.get_final_response(timeout=60)
    lane.close()
```

`ResponsesWebSocketLimits` are application budgets (lanes, events per lane, bytes per lane), not service limits — raise them for large images or tool results. `max_response_bytes=None` (default) removes the cumulative response accumulation cap.

## Audio helpers

From `openai.helpers` (require `openai[voice_helpers]` → `sounddevice`, `numpy`):

```python
from openai.helpers import Microphone, LocalAudioPlayer

recording = await Microphone(timeout=10).record()
transcription = await client.audio.transcriptions.create(model="whisper-1", file=recording)

async with client.audio.speech.with_streaming_response.create(
    model="tts-1", voice="alloy", response_format="pcm", input="..."
) as response:
    await LocalAudioPlayer().play(response)
```

`LocalAudioPlayer` plays a streaming speech response (with optional `sample_rate`/`channels` args); `Microphone` records from the default input device and returns `bytes` (16-bit PCM).

## Reconnection

WebSocket connections surface `ReconnectingEvent` types (see `openai.types.websocket_reconnection.ReconnectingEvent`, `ReconnectingOverrides`) when the transport reconnects; configure connection behavior through `websocket_connection_options` on `connect()`.

## Caveats

- Realtime/Live/WebSocket mTLS is not included in the mTLS program (HTTP APIs only, as of this version).
- X.509 workload identity does not cover Realtime/WebSockets.
- Keep audio formats exact (Live expects 24 kHz mono 16-bit PCM); the examples raise on mismatch rather than transcoding.
