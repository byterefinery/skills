# Multipart

Source: `docs/multipart.rst`, `docs/client_quickstart.rst` (Multipart uploads), `docs/web_quickstart.rst` (File Uploads), `aiohttp/formdata.py`.

## TOC

- Reading multipart responses
- Sending multipart requests
- FormData
- Server-side multipart

## Reading multipart responses

Wrap a response with `MultipartReader.from_response(resp)`, then loop `part = await reader.next()` until it returns `None`. Each part is a `BodyPartReader` (or a nested `MultipartReader` for multipart-within-multipart).

```python
async with aiohttp.request(url) as resp:
    reader = aiohttp.MultipartReader.from_response(resp)
    while True:
        part = await reader.next()
        if part is None:
            break
        # filter by headers, e.g.:
        if part.headers[aiohttp.hdrs.CONTENT_TYPE] == "application/json":
            metadata = await part.json()
            continue
        if part.filename == "secret.txt":
            filedata = await part.read(decode=False)
            break
```

`BodyPartReader` helpers (auto-detect gzip/deflate content encoding, base64/quoted-printable transfer encoding):

- `await part.text()`, `await part.json()`, `await part.form()`
- `await part.read(decode=True/False)` — whole part (raw bytes with `decode=False`)
- `await part.read_chunk()` — chunked raw reads
- `part.headers`, `part.filename` (parsed from `Content-Disposition`)
- `part.decode(data)` — decode previously read raw bytes on demand

Skipping a part: just `continue` the loop — `reader.next()` drains the unread part automatically.

## Sending multipart requests

`MultipartWriter(subtype)` builds a multipart payload as a chunked stream (recursively nestable):

```python
writer = aiohttp.MultipartWriter("mixed")   # or 'related', 'alternative', 'parallel'
writer.append_json({"a": 1})
writer.append_payload(aiohttp.get_payload(open("report.xls", "rb")))  # any payload-like object
await session.post(url, data=writer)
```

Methods (verified from source): `append(obj, headers=None)`, `append_payload(payload)`, `append_json(...)`, `append_form(...)`, plus `async write(writer)` for streaming to a stream writer. Common subtypes: `mixed`, `related`, `alternative`, `parallel`; `form-data` for HTML-form-compatible uploads (via `FormData`).

## FormData

Simpler API for form-style multipart uploads:

```python
data = aiohttp.FormData()
data.add_field("file", open("report.xls", "rb"),
               filename="report.xls",
               content_type="application/vnd.ms-excel")
await session.post(url, data=data)
```

Or pass a dict with file objects directly to `data=` — aiohttp streams file objects to the server automatically:

```python
await session.post(url, data={"file": open("report.xls", "rb")})
```

Since 3.14, `FormData.add_field` rejects invalid bytes in `name`/`filename`.

## Server-side multipart

- `await request.post()` — parses `multipart/form-data` (and urlencoded); files arrive as `FileField` (`.filename`, `.file`). **Reads the whole payload into memory.**
- `await request.multipart()` — streaming `MultipartReader` (same API as client-side):

```python
reader = await request.multipart()
field = await reader.next()
filename = field.filename
with open(f"/spool/{filename}", "wb") as f:
    while True:
        chunk = await field.read_chunk()   # 8192 bytes default
        if not chunk:
            break
        f.write(chunk)
```

Body size is capped by `Application(client_max_size=...)` (1 MiB default) and field count by `client_max_fields` (1000 default, 3.14.4) — exceeded forms get 413 `HTTPRequestEntityTooLarge`.
