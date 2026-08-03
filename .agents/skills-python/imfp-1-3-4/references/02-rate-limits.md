# Rate Limits, Retries, and Caching

## IMF API Rate Limiting

The IMF API imposes restrictive rate limits:

- **Per-application limit**: 50 requests per second per `User-Agent` header
- **Global limit**: undocumented overall cap across all users
- **Peak times**: requests may fail even under the per-app limit

### Default Behavior

By default, all imfp users share the same `User-Agent` (`"imfp Python package ..."`). This means all users share the same 50 req/s bucket. At high-traffic times, this causes failures.

### Setting a Custom App Name

```python
import imfp

# Set unique app name — best practice
imfp.set_imf_app_name("my_research_project")
```

This sets the `IMF_APP_NAME` environment variable. The value is used as the `User-Agent` header in API requests.

### Wait Time Between Requests

imfp enforces a minimum delay between requests using the `_min_wait_time_limited` decorator on `_imf_get()`. Default is 1.5 seconds.

```python
# Increase to 5 seconds for heavy workloads
imfp.set_imf_wait_time(5)

# Disable (risky — may trigger rate limits)
imfp.set_imf_wait_time(0)
```

This sets the `IMF_WAIT_TIME` environment variable.

## Retry Logic

imfp uses exponential backoff for failed requests:

1. Wait for `IMF_WAIT_TIME` (default 1.5s)
2. Attempt the request
3. On HTTP error (≥400), wait `5^attempt` seconds and retry
4. Stop after `times` attempts (default 3)

Retry schedule on failure: wait 5s → retry → wait 25s → retry → wait 125s → retry → give up.

```python
# More retries for unreliable connections
df = imfp.imf_dataset("PPI", frequency=["A"], times=5)
```

## Caching Strategies

imfp has no built-in disk cache. Implement caching manually:

### Parquet Caching (Recommended)

```python
import os
import pandas as pd
import imfp

def cached_imf_call(func, *args, cache_dir="data", **kwargs):
    """Cache imfp function results as parquet files."""
    # Build cache key from function name + args
    key = f"{func.__name__}_{hash(str(args) + str(sorted(kwargs.items())))}"
    cache_path = os.path.join(cache_dir, f"{key}.parquet")

    if os.path.exists(cache_path):
        return pd.read_parquet(cache_path)

    os.makedirs(cache_dir, exist_ok=True)
    result = func(*args, **kwargs)
    result.to_parquet(cache_path, index=False)
    return result

# Usage
databases = cached_imf_call(imfp.imf_databases)
params = cached_imf_call(imfp.imf_parameters, "PPI")
```

### Conditional Caching Pattern

```python
import os
import pandas as pd

cache_path = "data/imf_databases.parquet"
if os.path.exists(cache_path):
    databases = pd.read_parquet(cache_path)
else:
    databases = imfp.imf_databases()
    os.makedirs("data", exist_ok=True)
    databases.to_parquet(cache_path, index=False)
```

Requires `pyarrow`: `pip install pyarrow`.

## Performance Tips

1. **Filter early** — use dimension filters in `imf_dataset()` to limit data at the API level. Fetching entire databases fails for large ones.

2. **Reuse parameters dict** — call `imf_parameters()` once, then reuse the dict across multiple `imf_dataset()` calls to avoid repeated API lookups.

3. **Avoid parallel requests** — do not run imfp calls in parallel (threads, multiprocessing, async). The IMF API may block shared IP ranges.

4. **Cache the databases list** — `imf_databases()` rarely changes. Cache it and reuse.

5. **Use efficient storage** — parquet files are compact and fast to read/write. Prefer over CSV for cached data.

6. **Batch requests with delays** — when making multiple `imf_dataset()` calls, add `time.sleep()` between them beyond the built-in wait time.

7. **Validate before fetching** — check that your parameter codes are valid using `imf_parameters()` before calling `imf_dataset()`. Invalid codes are silently dropped with a warning.

## Error Handling

Common errors and responses:

| Error | Cause | Fix |
|---|---|---|
| `ValueError: No data found` | Filters too restrictive | Relax filters or check valid codes |
| `ValueError: ... not valid parameter(s)` | Wrong parameter name for database | Use `imf_parameters()` to find correct names |
| HTTP 429 / bandwidth error | Rate limited | Increase `set_imf_wait_time()`, set custom app name |
| HTTP 503 / service error | API overwhelmed or dataset too large | Retry with `times=`, reduce filter scope |
| `ValueError: Dataflow not found` | Invalid `database_id` | Use `imf_databases()` to find valid IDs |
