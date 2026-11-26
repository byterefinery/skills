# Exceptions and Errors

Source: `aiohttp/client_exceptions.py`, `docs/web_quickstart.rst` (Exceptions), `docs/client_advanced.rst` (SSL errors).

## TOC

- Client exception hierarchy
- Common client errors
- Web HTTPException hierarchy
- Raising vs returning

## Client exception hierarchy

Verified from `aiohttp/client_exceptions.py`:

```
Exception
└─ ClientError
   ├─ ClientResponseError           # status-based errors (raise_for_status)
   │  ├─ ContentTypeError           # wrong content type (e.g. resp.json())
   │  ├─ WSServerHandshakeError
   │  ├─ ClientHttpProxyError
   │  └─ TooManyRedirects
   ├─ ClientConnectionError
   │  ├─ ClientConnectionResetError
   │  ├─ ClientOSError
   │  │  └─ ClientConnectorError
   │  │     ├─ ClientConnectorDNSError
   │  │     ├─ ClientProxyConnectionError
   │  │     ├─ UnixClientConnectorError
   │  │     └─ ClientSSLError     # catch both SSL failure types
   │  │        ├─ ClientConnectorSSLError         # wraps ssl.SSLError
   │  │        └─ ClientConnectorCertificateError # wraps ssl.CertificateError
   │  └─ ServerConnectionError
   │     ├─ ServerDisconnectedError
   │     ├─ ServerTimeoutError      # also asyncio.TimeoutError
   │     │  ├─ ConnectionTimeoutError
   │     │  └─ SocketTimeoutError
   │     └─ ServerFingerprintMismatch
   ├─ ClientPayloadError            # e.g. non-rewindable body on redirect
   ├─ UploadAbortedError
   ├─ InvalidURL                    # also ValueError
   │  ├─ InvalidUrlClientError
   │  └─ RedirectClientError
   │     ├─ InvalidUrlRedirectClientError
   │     └─ NonHttpUrlRedirectClientError
   ├─ NonHttpUrlClientError
   └─ (WSMessageTypeError — not a ClientError; TypeError for wrong ws message types)
```

Typical handling:

```python
try:
    async with session.get("https://expired.badssl.com/") as resp:
        ...
except aiohttp.ClientSSLError as e:      # catch SSL verify + certificate failures
    ...
except aiohttp.ClientConnectorError as e:  # DNS, refused, proxy connect failures
    ...
except aiohttp.ServerDisconnectedError:    # peer dropped mid-response
    ...
```

## Common client errors

- `ContentTypeError` — `resp.json()` on a non-JSON Content-Type (see [01-http-client](01-http-client.md) for overrides).
- `ClientPayloadError` — e.g. attempting to replay a consumed async-generator body on a 307/308 redirect; invalid multipart/payload headers (3.14 tightened validation).
- `ServerDisconnectedError` / `ServerTimeoutError` — transport problems after the handshake.
- `InvalidURL` / `RedirectClientError` — malformed or non-HTTP URLs (including redirect targets).
- `TooManyRedirects` — redirect chain limit exceeded.

## Web HTTPException hierarchy

Every HTTP status code has a class (full list in `docs/web_quickstart.rst`). Top levels:

```
Exception
└─ HTTPException
   ├─ HTTPSuccessful
   │   200 HTTPOk · 201 HTTPCreated · 202 HTTPAccepted · 203 HTTPNonAuthoritativeInformation
   │   204 HTTPNoContent · 205 HTTPResetContent · 206 HTTPPartialContent
   ├─ HTTPRedirection
   │   300 HTTPMultipleChoices · 301 HTTPMovedPermanently · 302 HTTPFound · 303 HTTPSeeOther
   │   304 HTTPNotModified · 305 HTTPUseProxy · 307 HTTPTemporaryRedirect · 308 HTTPPermanentRedirect
   └─ HTTPError
      ├─ HTTPClientError
      │   400 HTTPBadRequest · 401 HTTPUnauthorized · 402 HTTPPaymentRequired · 403 HTTPForbidden
      │   404 HTTPNotFound · 405 HTTPMethodNotAllowed · 406 HTTPNotAcceptable · 407 HTTPProxyAuthenticationRequired
      │   408 HTTPRequestTimeout · 409 HTTPConflict · 410 HTTPGone · 411 HTTPLengthRequired
      │   412 HTTPPreconditionFailed · 413 HTTPRequestEntityTooLarge · 414 HTTPRequestURITooLong
      │   415 HTTPUnsupportedMediaType · 416 HTTPRequestRangeNotSatisfiable · 417 HTTPExpectationFailed
      │   421 HTTPMisdirectedRequest · 422 HTTPUnprocessableEntity · 424 HTTPFailedDependency
      │   426 HTTPUpgradeRequired · 428 HTTPPreconditionRequired · 429 HTTPTooManyRequests
      │   431 HTTPRequestHeaderFieldsTooLarge · 451 HTTPUnavailableForLegalReasons
      └─ HTTPServerError
          500 HTTPInternalServerError · 501 HTTPNotImplemented · 502 HTTPBadGateway · 503 HTTPServiceUnavailable
          504 HTTPGatewayTimeout · 505 HTTPVersionNotSupported · 506 HTTPVariantAlsoNegotiates
          507 HTTPInsufficientStorage · 510 HTTPNotExtended · 511 HTTPNetworkAuthenticationRequired
```

Constructor signature (all HTTP exceptions):

```python
HTTPNotFound(*, headers=None, reason=None, body=None, text=None, content_type=None)
HTTPFound(location, *, headers=None, reason=None, body=None, text=None, content_type=None)
HTTPMethodNotAllowed(method, allowed_methods, *, headers=None, ...)
HTTPUnavailableForLegalReasons(link, *, ..., text=...)   # link = self-reference URL
```

Auto-raised by the framework:

- `HTTPRequestEntityTooLarge` (413) — body > `client_max_size` or form fields > `client_max_fields` (3.14.4).
- `HTTPMethodNotAllowed` (405) — method not registered for the resource.
- `HTTPNotFound` (404) — no matching route.
- `HTTPExpectationFailed` (417) — unknown `Expect` value.

## Raising vs returning

Handlers must **raise** `HTTPException` instances. Returning them is deprecated and slated for removal — convert any `return web.HTTPNotFound()` to `raise web.HTTPNotFound()`.
