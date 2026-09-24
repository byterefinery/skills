# openai-python 3.6.0 — Errors, Retries, Pagination, File Uploads

## Error hierarchy

All errors inherit from `openai.APIError`.

- `openai.APIConnectionError` — the server could not be reached (network failure, no response). The underlying transport exception is on `e.__cause__`.
- `openai.APITimeoutError` — subclass of `APIConnectionError`; the request timed out.
- `openai.APIStatusError` — a non-2xx status code was returned. Exposes `e.status_code` and `e.response` (the parsed response body). Subclasses:

| Status code | Error type |
|---|---|
| 400 | `openai.BadRequestError` |
| 401 | `openai.AuthenticationError` |
| 403 | `openai.PermissionDeniedError` |
| 404 | `openai.NotFoundError` |
| 422 | `openai.UnprocessableEntityError` |
| 429 | `openai.RateLimitError` |
| >=500 | `openai.InternalServerError` |

Catch specific subclasses first, `APIStatusError` last:

```python
import openai

try:
    client.fine_tuning.jobs.create(model="gpt-4o", training_file="file-abc123")
except openai.APIConnectionError:
    print("The server could not be reached")
except openai.RateLimitError:
    print("429; back off")
except openai.APIStatusError as e:
    print(e.status_code, e.response, e.request_id)
```

## Retries

Connection errors, 408 Request Timeout, 409 Conflict, 429 Rate Limit, and >=500 are retried **2 times by default** with exponential backoff. Configure globally or per request:

```python
client = OpenAI(max_retries=0)  # disable
client.with_options(max_retries=5).chat.completions.create(...)
```

## Timeouts

Requests time out after **10 minutes (600 s) by default**. A timed-out request still counts against the retry budget.

```python
import httpx2
from openai import OpenAI

client = OpenAI(timeout=20.0)  # seconds
client = OpenAI(timeout=httpx2.Timeout(60.0, read=5.0, write=10.0, connect=2.0))
client.with_options(timeout=5.0).chat.completions.create(...)
```

On timeout, `openai.APITimeoutError` is raised (after retries are exhausted).

## Request IDs

Every object response carries a public `_request_id` property from the `x-request-id` response header — log it when reporting failures to OpenAI. All other `_`-prefixed members are private. For failed requests the ID is only available on the exception:

```python
try:
    completion = client.chat.completions.create(...)
except openai.APIStatusError as exc:
    print(exc.request_id)  # req_123
    raise
```

## Pagination

List endpoints return auto-paginating iterators — iterating fetches further pages as needed:

```python
all_jobs = []
for job in client.fine_tuning.jobs.list(limit=20):  # sync
    all_jobs.append(job)

# async: async for job in client.fine_tuning.jobs.list(limit=20):
```

Page-level control on the returned page object:

- `page.data` — items on this page
- `page.has_next_page()` — bool
- `page.next_page_info()` — dict of params to fetch the next page
- `await page.get_next_page()` / `page.get_next_page()` — the next page object
- Cursor attributes such as `page.after` are exposed when the API returns them

## `None` means `null` or missing

A response field that is JSON `null` or absent both surface as Python `None`. Tell them apart with `.model_fields_set`:

```python
if response.my_field is None:
    if "my_field" not in response.model_fields_set:
        ...  # key absent from the JSON
    else:
        ...  # explicit null
```

## File uploads

Request params that accept a file take `bytes`, an `os.PathLike` (e.g. `pathlib.Path`), or a tuple of `(filename, contents, media_type)`:

```python
from pathlib import Path
from openai import OpenAI

client = OpenAI()
client.files.create(file=Path("input.jsonl"), purpose="fine-tune")
```

In the async client, `PathLike` contents are read asynchronously automatically.

For very large files, `client.uploads.upload_file_chunked(...)` splits the file into 64 MB parts and uploads them sequentially (works for files far larger than the single-request multipart limit):

```python
# from disk
upload = client.uploads.upload_file_chunked(
    file=Path("big_test_file.txt"),
    mime_type="txt",
    purpose="batch",
)

# from memory
upload = client.uploads.upload_file_chunked(
    file=data,            # bytes
    filename="my_file.txt",
    bytes=len(data),
    mime_type="txt",
    purpose="batch",
)
```

Options: `part_size` (override the 64 MB part size), `md5` (expected file checksum). `client.uploads.parts` handles individual parts if you want to manage chunking manually.
