# requests 2.34.2 — Response Object

## Attributes Summary

| Attribute | Type | Notes |
|---|---|---|
| `status_code` | `int` | HTTP status (200, 404, etc.) |
| `headers` | `CaseInsensitiveDict` | Case-insensitive header access |
| `content` | `bytes` | Raw body bytes; triggers full download if not already consumed |
| `text` | `str` | Body decoded via `encoding` or `apparent_encoding` |
| `encoding` | `str \| None` | Explicit encoding (set before accessing `.text`) |
| `apparent_encoding` | `str \| None` | charset-normalizer/chardet guess from content bytes |
| `cookies` | `RequestsCookieJar` | Server-set cookies; dict-like with cookie policies |
| `elapsed` | `timedelta` | Time from request sent to response headers received |
| `history` | `list[Response]` | Redirect chain, oldest first |
| `request` | `PreparedRequest` | The request that produced this response |
| `reason` | `str \| None` | HTTP reason phrase ("OK", "Not Found") |
| `url` | `str` | Final URL after redirects |
| `raw` | `urllib3.HTTPResponse` | Raw urllib3 response (requires `stream=True`) |
| `ok` | `bool` | True if status < 400 |
| `is_redirect` | `bool` | Has Location header + redirect status code |
| `is_permanent_redirect` | `bool` | 301 or 308 with Location header |
| `links` | `dict` | Parsed Link header values |
| `next` | `PreparedRequest \| None` | Next redirect request (when `allow_redirects=False`) |

## Encoding Detection

`requests` determines text encoding in this order:

1. **Explicit `r.encoding`** — if set by user, used directly
2. **Content-Type charset** — extracted from `charset=...` in the Content-Type header
3. **`apparent_encoding`** — charset-normalizer (or chardet fallback) guesses from content bytes
4. **UTF-8 fallback** — if all else fails

```python
r = requests.get(url)

# If server doesn't report charset, set it manually
if r.encoding is None:
    r.encoding = "utf-8"

# Now .text uses the correct encoding
print(r.text)

# Or use apparent_encoding as fallback
r.encoding = r.apparent_encoding or "utf-8"
```

## JSON Parsing

```python
data = r.json()  # returns dict, list, str, int, float, bool, or None
data = r.json(object_hook=...)  # passes kwargs to json.loads()
```

Raises `requests.exceptions.JSONDecodeError` if the body is not valid JSON (including empty body). The library attempts UTF-8, UTF-16, and UTF-32 decoding per RFC 4627 before falling back to `r.text`.

## Streaming

### `iter_content(chunk_size, decode_unicode=False)`

Iterates over response body in chunks of `chunk_size` bytes. With `stream=True`, data is read as it arrives from the network.

```python
r = requests.get(url, stream=True)
for chunk in r.iter_content(chunk_size=8192):
    # chunk is bytes
    write_to_file(chunk)
r.close()  # release connection
```

- `chunk_size=None` — returns data as it arrives (single chunks from urllib3)
- `chunk_size=1` — byte-by-byte iteration (slow but fine-grained)
- `decode_unicode=True` — yields decoded strings using response encoding

### `iter_lines(chunk_size, decode_unicode=False, delimiter=None)`

Iterates over response body line by line. Useful for server-sent events (SSE), NDJSON streams, or any line-delimited protocol.

```python
r = requests.get(url, stream=True)
for line in r.iter_lines():
    # line is bytes
    if line:
        process(line.decode("utf-8"))
```

- `delimiter` — custom byte delimiter (default splits on `\n` and `\r\n`)
- Not reentrant-safe — do not call concurrently on the same response
- Empty lines at the end of chunks are buffered until a complete line is available

### Context Manager

```python
with requests.get(url, stream=True) as r:
    for chunk in r.iter_content(4096):
        process(chunk)
# Connection automatically released
```

## raise_for_status()

Raises `HTTPError` for 4xx and 5xx status codes:

```python
r = requests.get(url)
try:
    r.raise_for_status()
except requests.exceptions.HTTPError as e:
    print(e)  # "404 Client Error: Not Found for url: https://..."
    # e.response is the Response object
    # e.request is the PreparedRequest
```

Message format:
- 4xx: `{status_code} Client Error: {reason} for url: {url}`
- 5xx: `{status_code} Server Error: {reason} for url: {url}`

## Hooks

The only hook event is `response`, fired after a response is received (before redirect resolution):

```python
def on_response(response, **kwargs):
    print(f"{response.status_code} {response.url}")
    # Return response to pass through, or modified response
    return response

requests.get(url, hooks={"response": on_response})
requests.get(url, hooks={"response": [hook1, hook2]})  # multiple hooks

# Session-level
s = requests.Session()
s.hooks["response"].append(on_response)
```

Each hook receives the `Response` and arbitrary `**kwargs`. If a hook returns `None`, the next hook receives the original response. If it returns a new value, that becomes the response for subsequent hooks.

## RequestsCookieJar

`Response.cookies` is a `RequestsCookieJar` — a `http.cookiejar.CookieJar` with dict-like convenience:

```python
r = requests.get(url)
r.cookies["session_id"]           # get by name
r.cookies.set("name", "value", path="/", domain="example.com")
dict(r.cookies)                   # convert to plain dict
requests.get(url, cookies=r.cookies)  # pass to subsequent requests
```

In a `Session`, cookies are automatically extracted from responses and sent with subsequent requests to matching domains.

## Redirect History

When `allow_redirects=True` (default), the final `Response.history` contains all intermediate responses:

```python
r = requests.get("http://example.com/redirect-me")
print(r.url)           # Final URL
print(len(r.history))  # Number of redirects
for resp in r.history:
    print(resp.status_code, resp.headers.get("Location"))
```

With `allow_redirects=False`, `r.next` holds a `PreparedRequest` for the next redirect hop (if any), allowing manual redirect handling.
