# openai-python 3.6.0 — Realtime API

The Realtime API enables low-latency, multi-modal conversational experiences over a WebSocket connection. It supports text and audio as both input and output, plus function calling. The SDK uses the `websockets` library under the hood — install it with the `realtime` extra:

```sh
pip install 'openai[realtime]'
```

## Basic text conversation

The connection is a context manager. Send client events (session config, conversation items, response creation) and iterate server events:

```python
import asyncio
from openai import AsyncOpenAI

async def main():
    client = AsyncOpenAI()

    async with client.realtime.connect(model="gpt-realtime-2") as connection:
        await connection.session.update(
            session={"type": "realtime", "output_modalities": ["text"]}
        )
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
                break

asyncio.run(main())
```

Typical client events sent on the connection:

- `connection.session.update(session={...})` — configure modalities, voice, tools, etc.
- `connection.conversation.item.create(item={...})` — add messages (text, audio, function call outputs)
- `connection.response.create()` — request a model response
- `connection.input_audio_buffer.append(audio=base64_chunk)` — stream raw microphone audio
- `connection.input_audio_buffer.commit()` / `.clear()` — finalize or discard the audio buffer

Server events include `conversation.item.*`, `input_audio_buffer.*` (speech started/stopped, committed, timeout), `response.output_text.delta`/`done`, `response.audio.delta`/`done`, `response.done`, `error`, and `rate_limits.updated`.

## Error handling

When an error occurs, the Realtime API sends an `error` event and the connection **stays open and remains usable**. No exceptions are raised by the SDK for `error` events — handle them in the event loop:

```python
async for event in connection:
    if event.type == "error":
        print(event.error.type)
        print(event.error.code)
        print(event.error.event_id)
        print(event.error.message)
```

## Audio

For push-to-talk style apps, capture microphone audio, base64-encode it, and `append` chunks to the input audio buffer; the server emits speech detection and transcription events, then a response with audio deltas. The SDK repo ships a full example: `examples/realtime/push_to_talk_app.py`. Local playback helpers (`openai.helpers.local_audio_player`, `openai.helpers.microphone`) support the example; the `openai[voice_helpers]` extra pulls in `sounddevice` and numpy.

## Supporting resources

- `client.realtime.calls` — manage Realtime call objects (create/retrieve/list)
- `client.realtime.client_secrets` — create client secrets for connecting end users

## Notes and limitations

- Realtime/WebSockets are **not** covered by X.509 workload identity or mTLS (HTTP APIs only).
- Azure Realtime usage: see `examples/realtime/azure_realtime.py` in the SDK repo.
- For the Responses API WebSocket (persistent socket for sequential responses, distinct from the Realtime API), see [02-responses-api.md](02-responses-api.md) — `client.responses.connect()`.
