# Retry and Backoff

Source: docs/retry.rst, `valkey/retry.py`, `valkey/backoff.py`.

## `Retry`

`Retry(backoff, retries, supported_errors=(ConnectionError, TimeoutError, socket.timeout))` — retries a `do` callable up to `retries` times after failures of supported error types; `retries` can be **negative to retry forever**. `backoff.compute(failures)` returns seconds to sleep; `backoff.reset()` is called once at the start of every `call_with_retry`.

## Standalone Client Retry

Three constructor parameters (sync `Valkey` and connection level):

- `retry` — a `Retry` instance
- `retry_on_error` — list of exception types to retry on
- `retry_on_timeout` — `True` to retry on `TimeoutError` only

```python
from valkey.backoff import ExponentialBackoff
from valkey.retry import Retry
from valkey.exceptions import BusyLoadingError, ConnectionError, TimeoutError

retry = Retry(ExponentialBackoff(), 3)
r = valkey.Valkey(host='localhost', port=6379,
                  retry=retry,
                  retry_on_error=[BusyLoadingError, ConnectionError, TimeoutError])
r_only_timeout = valkey.Valkey(host='localhost', port=6379,
                               retry=retry, retry_on_timeout=True)
```

If `retry_on_error` or `retry_on_timeout` is set without an explicit `retry`, the client defaults to `Retry(NoBackoff(), 1)` — one retry immediately after the first failure.

## Backoff Strategies (`valkey.backoff`)

| Class | Behavior | Defaults |
|---|---|---|
| `NoBackoff()` | sleep 0 | — |
| `ConstantBackoff(backoff)` | fixed seconds | — |
| `ExponentialBackoff(cap, base)` | `min(cap, base * 2**failures)` | `cap=0.512`, `base=0.008` |
| `FullJitterBackoff(cap, base)` | `random.uniform(0, min(cap, base*2**failures))` | same |
| `EqualJitterBackoff(cap, base)` | half deterministic + half jitter | same |
| `DecorrelatedJitterBackoff(cap, base)` | decorrelated jitter, stateful (uses `reset()`) | same |

`default_backoff()` returns `EqualJitterBackoff()`.

## Cluster Retry

Cluster has a different, two-tier model (docs/retry.rst):

- `retry` — reconnect retries to a failing node, **default `Retry(NoBackoff(), 0)`**
- `cluster_error_retry_attempts` — number of full cluster re-initialization cycles (removes the failed node from startup nodes) when `TimeoutError`/`ConnectionError`/`ClusterDownError` is hit, **default 3**

```python
rc = ValkeyCluster(host='localhost', port=6379,
                   retry=Retry(ExponentialBackoff(), 6),
                   cluster_error_retry_attempts=1)
```

Documented flow: compute slot for the key → pick node → connect → on `ConnectionError` retry to that node up to `retry` (with backoff) → if still failing, run one `cluster_error_retry_attempts` cycle (cluster update, drop failed node, re-init) → new retry cycle → finally raise to the caller.
