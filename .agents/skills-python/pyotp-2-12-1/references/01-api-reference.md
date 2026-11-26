# pyotp 2.12.1 — API Reference

## Table of Contents

- [Module-Level Functions](#module-level-functions)
- [Exceptions](#exceptions)
- [OTP (Base Class)](#otp-base-class)
- [TOTP](#totp)
- [HOTP](#hotp)
- [contrib.Steam](#contribsteam)
- [utils (Internal Helpers)](#utils-internal-helpers)

---

## Module-Level Functions

### `pyotp.random_base32(length: int = 32, chars: Sequence[str] = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567") -> str`

Generate a random base32-encoded secret string (uses `secrets.SystemRandom`).

| Parameter | Type | Default | Description |
|---|---|---|---|
| `length` | `int` | `32` | Length of the generated secret. Minimum 32 (160 bits). |
| `chars` | `Sequence[str]` | `"ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"` | Character set for the secret. |

**Returns:** `str` — random base32 string of the given length (no padding).
**Raises:** `ValueError` ("Secrets should be at least 160 bits") if `length < 32`.

### `pyotp.random_hex(length: int = 40, chars: Sequence[str] = "ABCDEF0123456789") -> str`

Generate a random hex-encoded secret string.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `length` | `int` | `40` | Length of the generated secret. Minimum 40 (160 bits). |
| `chars` | `Sequence[str]` | `"ABCDEF0123456789"` | Character set for the secret. |

**Returns:** `str` — random hex string of the given length.
**Raises:** `ValueError` if `length < 40`.

### `pyotp.parse_uri(uri: str) -> OTP`

Parse an `otpauth://` provisioning URI into an OTP object.

| Parameter | Type | Description |
|---|---|---|
| `uri` | `str` | An `otpauth://totp/...` or `otpauth://hotp/...` URI. |

**Returns:** `TOTP`, `HOTP`, or `contrib.Steam` object (Steam when `encoder=steam`).
**Raises:**
- `ValueError` — scheme is not `otpauth`; duplicate security parameter (`secret`, `issuer`, `algorithm`, `encoder`, `digits`, `period`, `counter`); issuer in label and query parameter differ; `algorithm` not SHA1/SHA256/SHA512; `digits` not 6/7/8 (unless `encoder=steam`); no `secret` parameter; type other than `totp`/`hotp`.
- Blank parameter values are skipped; unknown parameters are ignored.

---

## Exceptions

`pyotp.exceptions`, re-exported at package level.

### `PyOTPError(Exception)`

Base class for PyOTP-specific errors.

### `OTPVerificationError(PyOTPError)`

Raised when an OTP does not match any permitted counter. Raised by `TOTP.verify_and_get_timecode()`; `verify()` returns `False` instead.

---

## OTP (Base Class)

`pyotp.otp.OTP` — base class for all OTP handlers. Not intended for direct instantiation.

### Class Variables

| Variable | Type | Default | Description |
|---|---|---|---|
| `min_secret_length_bits` | `ClassVar[int]` | `112` | Minimum decoded secret length in bits (NIST SP 800-63B-4). Override in a subclass to change the floor. |

### Constructor

```python
OTP(s: str, *, digits: int = 6, digest: Any = hashlib.sha1, name: str | None = None, issuer: str | None = None)
```

All parameters after `s` are keyword-only.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `s` | `str` | — | Secret in base32 format (case-insensitive; missing padding is added automatically). |
| `digits` | `int` | `6` | Number of digits in the OTP. Must be 6–10. |
| `digest` | `Any` | `hashlib.sha1` | HMAC digest function. `md5`/`shake_128` rejected; digest size must be ≥ 18 bytes. |
| `name` | `str` | `"Secret"` (when falsy) | Account name label. |
| `issuer` | `str` | `None` | Issuer (organization) name. |

**Raises:**
- `ValueError` — if `digits` is outside 6–10; digest is `md5`/`shake_128`; or `byte_secret()` validation fails (invalid base32, or decoded length < `min_secret_length_bits`).

The secret is validated (base32-decoded, length checked) at construction.

### Methods

#### `generate_otp(input: int) -> str`

Generate an OTP code for the given input (counter or timecode).

| Parameter | Type | Description |
|---|---|---|
| `input` | `int` | The HMAC counter value. Must be ≥ 0. |

**Returns:** `str` — zero-padded OTP string of `digits` length.
**Raises:** `ValueError` if `input < 0` or digest size < 18 bytes.

#### `byte_secret() -> bytes`

Decode the base32 secret to raw bytes, enforcing `min_secret_length_bits`.

**Returns:** `bytes` — the decoded secret (padding added as needed).
**Raises:** `ValueError` if the secret is not valid base32 or decodes to fewer than `min_secret_length_bits` bits ("Secrets must be at least 112 bits after decoding" by default).

#### `int_to_bytestring(i: int, *, padding: int = 8) -> bytes`

Convert an integer to the OATH big-endian bytestring. `padding` is keyword-only.

**Returns:** `bytes` — zero-padded 8-byte representation (default).

### Attributes

| Attribute | Type | Description |
|---|---|---|
| `secret` | `str` | The base32 secret string. |
| `digits` | `int` | Number of digits in generated OTPs. |
| `digest` | `Any` | The digest function. |
| `name` | `str` | Account name label (default `"Secret"`). |
| `issuer` | `str` | Issuer name (or `None`). |

---

## TOTP

`pyotp.totp.TOTP` — time-based one-time password handler.

### Constructor

```python
TOTP(s: str, *, digits: int = 6, digest: Any = None, name: str | None = None, issuer: str | None = None, interval: int = 30)
```

All parameters after `s` are keyword-only. `digest=None` means `hashlib.sha1`.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `s` | `str` | — | Secret in base32 format (must decode to ≥ 112 bits by default). |
| `digits` | `int` | `6` | Number of digits in the OTP (6–10). |
| `digest` | `Any` | `hashlib.sha1` | HMAC digest function. |
| `name` | `str` | `None` | Account name. |
| `issuer` | `str` | `None` | Issuer name. |
| `interval` | `int` | `30` | Time interval in seconds. Must be > 0 and ≤ 120 (NIST SP 800-63B-4). |

**Raises:** `ValueError` — if `interval` is outside 1–120, or any base-class validation fails.

### Methods

#### `now() -> str`

Generate the current OTP based on the current time (`time.time()`).

**Raises:** `ValueError` if the current time is before the Unix epoch or after year 9999 UTC.

#### `at(for_time: int | float | datetime.datetime, *, counter_offset: int = 0) -> str`

Generate an OTP for a specific time. `counter_offset` is keyword-only.

| Parameter | Type | Description |
|---|---|---|
| `for_time` | `int`, `float`, or `datetime` | Unix timestamp (seconds since 1970 UTC) or datetime. Naive datetimes are interpreted as local time, respecting `fold`. |
| `counter_offset` | `int` | Number of intervals to add to the timecode (default 0). |

**Returns:** `str` — OTP code for the specified time.
**Raises:** `ValueError` if `for_time` is before the Unix epoch or after year 9999 in UTC.

#### `verify(otp: str, *, for_time: int | float | datetime.datetime | None = None, valid_window: int = 0) -> bool`

Verify an OTP code against the current or specified time. Uses timing-attack-resistant, NFKC-normalized comparison.

| Parameter | Type | Description |
|---|---|---|
| `otp` | `str` | The OTP code to verify. |
| `for_time` | `int`, `float`, `datetime`, or `None` | Time to check against (default: now). |
| `valid_window` | `int` | Number of intervals before/after to accept (default 0). |

**Returns:** `bool` — `True` if the OTP is valid within the window.
**Raises:** `ValueError` if `for_time` is out of range.

#### `verify_and_get_timecode(otp: str, *, for_time: int | float | datetime.datetime | None = None, valid_window: int = 0) -> int`

Verify an OTP and return the **matching timecode** (not the server's current timecode). Intended for replay prevention — persist the returned timecode and reject anything ≤ it.

| Parameter | Type | Description |
|---|---|---|
| `otp` | `str` | The OTP code to verify. |
| `for_time` | `int`, `float`, `datetime`, or `None` | Time to check against (default: now). |
| `valid_window` | `int` | Number of intervals before/after to accept (default 0). Must not be negative. |

**Returns:** `int` — the matching timecode (may differ from the current timecode when a window is used).
**Raises:**
- `pyotp.OTPVerificationError` — if the OTP does not match within the window (this method never returns `False`).
- `ValueError` — if `valid_window < 0` or `for_time` is out of range.

#### `provisioning_uri(*, name: str | None = None, issuer_name: str | None = None, **kwargs: Any) -> str`

Generate an `otpauth://totp/` provisioning URI. All parameters are keyword-only.

| Parameter | Type | Description |
|---|---|---|
| `name` | `str` | Account name (overrides instance `name`; falls back to it). |
| `issuer_name` | `str` | Issuer name (overrides instance `issuer`; falls back to it). |
| `**kwargs` | `str` | Extra query parameters, all values must be strings. `image` must be an HTTPS URL with host and path. |

**Returns:** `str` — the provisioning URI string.
**Raises:** `TypeError` for non-string `kwargs` values; `ValueError` for an invalid `image` URL.

#### `timecode(for_time: int | float | datetime.datetime) -> int`

Compute the timecode (counter value) for a given time: `int(timestamp // interval)`.

| Parameter | Type | Description |
|---|---|---|
| `for_time` | `int`, `float`, or `datetime` | Unix timestamp or datetime (naive = local time with `fold`; subsecond precision ignored). |

**Returns:** `int` — the counter value.
**Raises:** `ValueError` — "for_time must be at or after the Unix epoch and before year 10000 UTC".

### Attributes

| Attribute | Type | Description |
|---|---|---|
| `interval` | `int` | Time interval in seconds (default 30, max 120). |

---

## HOTP

`pyotp.hotp.HOTP` — HMAC-based counter one-time password handler.

### Constructor

```python
HOTP(s: str, *, digits: int = 6, digest: Any = None, name: str | None = None, issuer: str | None = None, initial_count: int = 0)
```

All parameters after `s` are keyword-only. `digest=None` means `hashlib.sha1`.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `s` | `str` | — | Secret in base32 format (must decode to ≥ 112 bits by default). |
| `digits` | `int` | `6` | Number of digits in the OTP (6–10). |
| `digest` | `Any` | `hashlib.sha1` | HMAC digest function. |
| `name` | `str` | `None` | Account name. |
| `issuer` | `str` | `None` | Issuer name. |
| `initial_count` | `int` | `0` | Starting counter value. |

### Methods

#### `at(count: int) -> str`

Generate an OTP for the given counter offset: `generate_otp(initial_count + count)`.

| Parameter | Type | Description |
|---|---|---|
| `count` | `int` | Counter offset from `initial_count`. |

**Returns:** `str` — zero-padded OTP string.

#### `verify(otp: str, counter: int) -> bool`

Verify an OTP against a specific counter offset (same offset semantics as `at()`). Uses timing-attack-resistant, NFKC-normalized comparison.

| Parameter | Type | Description |
|---|---|---|
| `otp` | `str` | The OTP code to verify. |
| `counter` | `int` | Counter offset from `initial_count`. |

**Returns:** `bool` — `True` if the OTP matches.

#### `provisioning_uri(*, name: str | None = None, initial_count: int | None = None, issuer_name: str | None = None, **kwargs: Any) -> str`

Generate an `otpauth://hotp/` provisioning URI. All parameters are keyword-only.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `name` | `str` | `None` | Account name (falls back to instance `name`). |
| `initial_count` | `int` | `None` | Starting counter (falls back to instance `initial_count`). `initial_count=0` is honored and emits `counter=0`. |
| `issuer_name` | `str` | `None` | Issuer name (falls back to instance `issuer`). |
| `**kwargs` | `str` | — | Extra query parameters (strings only; `image` must be HTTPS). |

**Returns:** `str` — the provisioning URI string.

### Attributes

| Attribute | Type | Description |
|---|---|---|
| `initial_count` | `int` | Starting counter value (default 0). |

---

## contrib.Steam

`pyotp.contrib.Steam` — Steam's custom TOTP implementation. Subclass of `TOTP`. Not standardized, not officially supported, provided for reference only.

### Constants

| Constant | Value | Description |
|---|---|---|
| `STEAM_CHARS` | `"23456789BCDFGHJKMNPQRTVWXY"` | Steam's custom character alphabet (28 chars, no ambiguous characters). |
| `STEAM_DEFAULT_DIGITS` | `5` | Fixed code length for Steam TOTP. |

### Constructor

```python
Steam(s: str, *, name: str | None = None, issuer: str | None = None, interval: int = 30, digits: int = 5)
```

All parameters after `s` are keyword-only. `digits` is accepted but ignored — Steam always emits 5 characters (the superclass is constructed with `digits=10`, `digest=hashlib.sha1`). Inherits `min_secret_length_bits` (112).

### Methods

Inherits all `TOTP` methods (`now()`, `at()`, `verify()`, `verify_and_get_timecode()`, `provisioning_uri()`, `timecode()`).

#### `generate_otp(input: int) -> str` (override)

Generate a 5-character Steam-style code: internally compute a 10-digit OTP, then map it to `STEAM_CHARS`.

**Returns:** `str` — 5-character Steam code.

---

## utils (Internal Helpers)

`pyotp.utils` — used internally; `build_uri` is marked "For module-internal use."

### `build_uri(secret, name, initial_count=None, issuer=None, algorithm=None, digits=None, period=None, **kwargs: str) -> str`

Assemble the provisioning URI.

- `initial_count` may be 0 (valid); presence switches the URI type to `hotp`, otherwise `totp`.
- Defaults omitted: `algorithm` `sha1`, `digits` 6, `period` 30.
- `algorithm` is uppercased in the output (`SHA1`, `SHA256`, `SHA512`).
- Query string is URL-encoded with `+` replaced by `%20`.
- `**kwargs` values must be strings (`TypeError` otherwise); `image` must be an HTTPS URL with host and path (`ValueError` otherwise).

### `strings_equal(s1: str, s2: str) -> bool`

Timing-attack-resistant comparison (`hmac.compare_digest` over UTF-8) with Unicode NFKC normalization. Returns `False` if either input exceeds 1024 Unicode code points (bounds CPU cost; CVE-2026-3276 mitigation).
