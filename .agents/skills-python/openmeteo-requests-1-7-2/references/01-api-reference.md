# API Reference — openmeteo-requests 1.7.2

## Client

Synchronous client for the Open-Meteo API.

### Constructor

```python
Client(session: niquests.Session | None = None)
```

- `session` — optional `niquests.Session`. If `None`, a new session is created and owned by the client (closed on `__del__`). If provided, the client uses it without ownership.

### Methods

#### `weather_api(url, params, method="GET", *, verify=None, **kwargs) -> list[WeatherApiResponse]`

Fetch weather data from the Open-Meteo API.

| Parameter | Type | Description |
|---|---|---|
| `url` | `str` | API endpoint URL (e.g., `https://api.open-meteo.com/v1/forecast`) |
| `params` | `MutableMapping[str, Any]` | Query parameters (latitude, longitude, variables, etc.) |
| `method` | `str` | HTTP method: `"GET"` (default) or `"POST"`. Use POST for large parameter sets |
| `verify` | `bool \| str \| None` | SSL verification: `True` (default, system CA), `False` (disable), or path to CA bundle |
| `**kwargs` | — | Extra keyword arguments passed to `niquests.get()` / `niquests.post()` |

Returns: `list[WeatherApiResponse]` — one entry per location/model combination.

The `format=flatbuffers` parameter is added automatically.

### Attributes

- `_session` — the underlying `niquests.Session`
- `_close_session` — `True` if the client created its own session (will close on `__del__`)

### Lifecycle

The client implements `__del__` which closes the session if it created one. For explicit cleanup, close the session manually or use a context manager pattern on the session.

---

## AsyncClient

Asynchronous client for the Open-Meteo API.

### Constructor

```python
AsyncClient(session: niquests.AsyncSession | None = None)
```

- `session` — optional `niquests.AsyncSession`. If `None`, per-request connections are used (no persistent session).

### Methods

#### `async weather_api(url, params, method="GET", *, verify=None, **kwargs) -> list[WeatherApiResponse]`

Same parameters as `Client.weather_api()`. Uses `niquests.aget()` / `niquests.apost()` for async HTTP calls.

### Notes

- `AsyncClient` does not manage session lifecycle — no `__del__` cleanup
- If no session is provided, each request creates a new connection
- Pass a `niquests.AsyncSession` for connection reuse

---

## OpenMeteoRequestsError

```python
class OpenMeteoRequestsError(Exception):
    """Open-Meteo Error."""
```

Raised for:
- HTTP 400 (bad request) — response body (JSON) is the error message
- HTTP 429 (rate limited) — response body (JSON) is the error message
- HTTP errors from `response.raise_for_status()` — wrapped with context
- FlatBuffers stream errors — decoded from the response bytes

Access the original exception via `error.__cause__`.

---

## WeatherApiResponse

Decoded FlatBuffers response. All attribute access uses method calls (e.g., `.Latitude()`), not properties. This enables zero-copy data access.

### Top-level methods

| Method | Return | Description |
|---|---|---|
| `Latitude()` | `float` | Latitude of the location |
| `Longitude()` | `float` | Longitude of the location |
| `Elevation()` | `float` | Elevation in meters above sea level |
| `UtcOffsetSeconds()` | `int` | Timezone offset from UTC in seconds |
| `Timezone()` | `str` | IANA timezone name (e.g., `"Europe/Berlin"`) |
| `TimezoneAbbreviation()` | `str` | Timezone abbreviation (e.g., `"CEST"`) |
| `Current()` | `Current` | Current conditions block |
| `Hourly()` | `Hourly` | Hourly forecast/historical block |
| `Daily()` | `Daily` | Daily forecast block |
| `Model()` | `str` | Weather model name (when requesting multiple models) |

### Current block

| Method | Return | Description |
|---|---|---|
| `Time()` | `int` | Unix timestamp of current observation |
| `VariablesLength()` | `int` | Number of variables |
| `Variables(index)` | `Variable` | Variable at position `index` (matches request order) |

### Hourly / Daily blocks

| Method | Return | Description |
|---|---|---|
| `Time()` | `int` | Start time (Unix timestamp) |
| `TimeEnd()` | `int` | End time (Unix timestamp) |
| `Interval()` | `int` | Interval between data points in seconds (3600 = hourly, 86400 = daily) |
| `VariablesLength()` | `int` | Number of variables |
| `Variables(index)` | `Variable` | Variable at position `index` |

### Variable block

| Method | Return | Description |
|---|---|---|
| `Variable()` | `Variable` | Variable type enum (from `openmeteo_sdk.Variable`) |
| `Altitude()` | `float` | Altitude in meters (e.g., 2 for 2m temperature, 10 for 10m wind) |
| `ValuesAsNumpy()` | `np.ndarray` | Values as NumPy float32 array |
| `ValuesLength()` | `int` | Number of data points |
| `Values(index)` | `float` | Single value at index |

---

## HTTPVerb

```python
class HTTPVerb(str, Enum):
    GET = "GET"
    POST = "POST"
```

String enum for HTTP methods. Passable as `method` parameter to `weather_api()`.

---

## Imports

```python
from openmeteo_requests import Client, AsyncClient, OpenMeteoRequestsError
from openmeteo_sdk.Variable import Variable  # for filtering variables by type
```
