# API Reference — openmeteo-requests 1.7.6

Extracted from the v1.7.6 tag of [open-meteo/python-requests](https://github.com/open-meteo/python-requests) (`openmeteo_requests/Client.py`, `openmeteo_requests/__init__.py`, `pyproject.toml`).

## Package exports

`openmeteo_requests.__init__` exports:

```python
__all__ = ["AsyncClient", "Client", "OpenMeteoRequestsError"]
```

The package includes a `py.typed` marker file, so the library is typed per PEP 561 (type checkers see inline annotations).

## Client

Synchronous Open-Meteo API client.

### Constructor

```python
Client(session: niquests.Session | None = None)
```

- `session` — optional `niquests.Session`. If `None`, a new session is created and owned by the client (closed in `__del__`). If provided, the client uses it without ownership and will not close it.
- Internal state: `_close_session` is `True` only when the client created its own session.

### `weather_api(url, params, method="GET", *, verify=None, **kwargs) -> list[WeatherApiResponse]`

Fetch and decode weather data.

| Parameter | Type | Description |
|---|---|---|
| `url` | `str` | API endpoint URL, e.g. `https://api.open-meteo.com/v1/forecast` |
| `params` | `MutableMapping[str, Any]` | Query parameters (latitude, longitude, variable groups, dates, models, …). Copied via `dict(params)` before use; `format` is added to the copy |
| `method` | `str` | `"GET"` (default) or `"POST"` (compared via the `HTTPVerb` enum, case-insensitive). POST sends params as the request body (`data=`); GET sends them as query parameters |
| `verify` | `bool \| str \| None` | keyword-only. SSL verification flag or path to a CA bundle, passed to niquests |
| `**kwargs` | — | Passed through to `niquests.Session.get()` / `niquests.Session.post()` |

Returns `list[WeatherApiResponse]` — one entry per location/model combination in the response.

Behavior:

1. Sets `params["format"] = "flatbuffers"` (constant `_FLAT_BUFFERS_FORMAT`).
2. Performs GET or POST through `self._session`.
3. On HTTP 400 or 429, raises `OpenMeteoRequestsError` with the JSON response body as the message.
4. Otherwise calls `response.raise_for_status()` (other HTTP errors raise via niquests).
5. Decodes the FlatBuffers payload with `_process_response` and returns the message list.
6. Any exception from the above is caught and re-raised as `OpenMeteoRequestsError(f"failed to request {url!r}: {e}")` with the original as `__cause__`.

### Lifecycle

`Client.__del__` closes the session only when the client created it itself (`_close_session` is `True`).

## AsyncClient

Asynchronous Open-Meteo API client.

### Constructor

```python
AsyncClient(session: niquests.AsyncSession | None = None)
```

- `session` — optional `niquests.AsyncSession`. If `None`, the client does **not** create one; each request goes through module-level `niquests.aget()` / `niquests.apost()` instead.
- No session lifecycle management at all (no `__del__`, no closing). Close an `AsyncSession` yourself (`await session.close()`).

### `async weather_api(url, params, method="GET", *, verify=None, **kwargs) -> list[WeatherApiResponse]`

Same signature and behavior as `Client.weather_api`, awaited. Error handling (400/429 JSON body, `raise_for_status`, wrapping into `OpenMeteoRequestsError` with `failed to request <url>: ...`) is identical.

## Exceptions

### `OpenMeteoRequestsError(Exception)`

Raised in three situations:

- HTTP 400 or 429 — message is the API's JSON error body (a dict)
- Stream error — the decoded body starts with the `Unexpected` marker (see framing below); message is the decoded text (e.g. `Unexpected error while streaming data: timeoutReached`)
- Wrapping — any other failure during the request; message `failed to request <url>: <error>`, original exception available via `__cause__`

## HTTPVerb

```python
class HTTPVerb(str, Enum):
    GET = "GET"
    POST = "POST"
```

Used internally by `_request`/`_request` to dispatch; comparing with `.upper()` means `method="post"` also works.

## Response framing (`_process_response`)

The FlatBuffers payload is a stream of length-prefixed messages:

- Each message starts with a 4-byte little-endian length prefix.
- Loop while position < total bytes: read the length at `data[pos:pos+4]`.
- If the 4 bytes equal `0x78656E55` (the ASCII `Unexpected`), the stream contains an error — raise `OpenMeteoRequestsError` with `data[pos:total]` decoded as UTF-8.
- Otherwise decode a message via `WeatherApiResponse.GetRootAs(data, pos + 4)` and advance by `length + 4`.
- Returns the list of decoded `WeatherApiResponse` objects.

`WeatherApiResponse` comes from the `openmeteo-sdk` package (dependency `openmeteo-sdk>=1.22.0`); the `Variable` enum used for filtering is `openmeteo_sdk.Variable.Variable`.

## Package metadata

From `pyproject.toml` (v1.7.6 tag):

- `requires-python = ">=3.9"`; classifiers list Python 3.9–3.14
- CI matrix (`.github/workflows/ci.yaml`): CPython 3.11, 3.12, 3.13, 3.14, 3.15 and PyPy 3.11
- Runtime dependencies: `niquests>=3.15.2`, `openmeteo-sdk>=1.22.0`
- License: MIT
