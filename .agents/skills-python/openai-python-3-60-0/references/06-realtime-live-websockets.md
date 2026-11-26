# Realtime, Live, and WebSockets (v3.60.0)

Install `openai[realtime]` (websockets) for WebSocket-based APIs.

## Realtime API

Low-latency multi-modal conversations over WebSocket — text and audio in/out, function calling. `client.realtime.connect(model="gpt-realtime-2")` opens a context-managed connection:

```python
import asyncio
from openai import AsyncOpenAI, OpenAIError

async def main():
    client = AsyncOpenAI()

    async with client.realtime.connect(model="gpt-realtime-2") as connection:
        await connection.session.update(session={"type": "realtime", "output_modalities": ["text"]})

        await connection.conversation.item.create(
            item={
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": "Say hello!"}],
            }
        )
        await connection.response.create()

        async for event in connection:
            if event.type == "response.output_text.delta":
                print(event.delta, flush=True, end="")
            elif event.type == "response.output_text.done":
                print()
            elif event.type == "response.done":
                if event.response.status != "completed":
                    raise OpenAIError("The Realtime response did not complete")
                break
            elif event.type == "error":
                raise OpenAIError("Realtime returned an error; inspect the event in your application")
        else:
            raise OpenAIError("Realtime disconnected before response.done")

asyncio.run(main())
```

**Errors are events, not exceptions** — on `error` the connection stays open and usable; the SDK never raises directly, so handle `event.error.type` / `.code` / `.event_id` / `.message` yourself.

Retained `client.beta.realtime` interface (REST `sessions.create`, `transcription_sessions.create`) does **not** exchange workload-identity tokens or sign Bedrock requests — supply `Authorization` via `default_headers` or `connect(extra_headers=...)` or the SDK rejects the connection locally. Connection headers override defaults case-insensitively; `omit` removes a header. Beta WebSockets always reject X.509 clients, even with explicit headers. Full audio TUI example: `examples/realtime/push_to_talk_app.py`.

## Realtime Translation

`client.realtime.translations.connect()` provides the typed connection; `openai.lib.realtime_translation.TranslationSession` (sync) / `AsyncTranslationSession` (async) adds finish and cleanup rules:

```python
from openai import OpenAI
from openai.lib.realtime_translation import TranslationSession

with OpenAI() as client:
    with TranslationSession(client.realtime.translations, model="gpt-realtime-translate") as connection:
        connection.send({"type": "session.input_audio_buffer.append", "audio": base64.b64encode(pcm_audio).decode("ascii")})
        connection.send({"type": "session.close"})
        while True:
            event = connection.recv()
            if event.type == "session.output_transcript.delta":
                print(event.delta, end="", flush=True)
            if event.type == "session.closed":
                break
```

Rules:

- Send `session.close` **once** to stop input; keep receiving until `session.closed` to retain trailing audio/text. Repeated finish commands are no-ops; new input after finish raises `OpenAIError`; a socket closing before `session.closed` is an error, not success.
- The helper does not reconnect or replay commands; it closes the connection when the context exits (including on cancellation or exception). Use one receiver per connection; server error events and unknown future events remain visible.
- `extra_query`, `extra_headers`, `websocket_connection_options` configure the request/connection. The helper rejects unsupported providers and `intent` query parameters before opening.

## Live API

`client.live.sessions` — WebRTC call control for the Live API (models such as `gpt-live-1.1`): `accept`, `reject`, `fork`, `refer`, `hangup`, `download_recording`. WebRTC standby support was added in 3.57. Examples: `examples/live/audio_transcript.py`, `examples/live/transcript_grouper.py`.

## Responses WebSocket

`client.responses.connect()` opens a WebSocket for the Responses API (see `examples/responses_websocket.py`, `examples/responses/websocket.py`).
