---
name: pyotp-2-12-1
description: >
  Python library for generating and verifying TOTP (time-based) and HOTP
  (counter-based) one-time passwords per RFC 6238 / RFC 4226. Use when
  implementing two-factor (2FA) or multi-factor (MFA) authentication,
  provisioning Google Authenticator-compatible QR codes, parsing otpauth
  URIs, generating random base32 or hex secrets, verifying user-supplied OTP
  codes, preventing OTP replay via timecode tracking, or working with
  Steam's custom TOTP variant.
license: MIT
compatibility: Requires Python 3.10+
metadata:
  tags:
    - python
    - authentication
    - security
---

# pyotp 2.12.1

## Overview

`pyotp` 2.12.1 implements server-side support for the OATH one-time password standards — HOTP (RFC 4226) and TOTP (RFC 6238). It generates short numeric codes from a shared base32 secret and verifies codes submitted by clients. It also produces `otpauth://` provisioning URIs for QR-code setup in authenticator apps (Google Authenticator, Authy, 1Password, etc.).

New in 2.11.0–2.12.1 (breaking changes vs. 2.10.0):

- **Secrets must decode to at least 112 bits** (NIST SP 800-63B-4). Enforced at construction and every time the secret is decoded (generation/verification). Override per class with the `min_secret_length_bits` class variable.
- **`TOTP.verify_and_get_timecode()`** — verifies and returns the matching timecode for replay prevention; raises `pyotp.OTPVerificationError` on mismatch (`verify()` returns `False`).
- **TOTP `interval` is capped at 120 seconds** and must be positive; `digits` must be 6–10 (5 no longer accepted at construction).
- **`parse_uri()` rejects duplicate security parameters**; `HOTP.provisioning_uri()` now honors `initial_count=0`.
- **Timestamp inputs normalized** — `int`, `float`, or `datetime` accepted; naive datetimes use local time with `fold` (DST fix); out-of-range values (before Unix epoch, year ≥ 10000 UTC) raise `ValueError`.
- **Python 3.10+ required.**

Core classes:

- **`OTP`** — base class; `min_secret_length_bits` class variable (default 112), `generate_otp()`, `byte_secret()`, `int_to_bytestring()`
- **`TOTP`** — time-based; codes rotate every N seconds (default 30, max 120). Methods: `now()`, `at()`, `verify()`, `verify_and_get_timecode()`, `provisioning_uri()`, `timecode()`
- **`HOTP`** — counter-based. Methods: `at()`, `verify()`, `provisioning_uri()`
- **`contrib.Steam`** — Steam's proprietary TOTP variant (5-character codes from custom alphabet). Subclass of `TOTP`

Exceptions: **`pyotp.PyOTPError`** (base) → **`pyotp.OTPVerificationError`** (raised by `verify_and_get_timecode()` on mismatch).

Module-level helpers:

- **`random_base32(length=32)`** — random base32 secret (min 32 chars / 160 bits)
- **`random_hex(length=40)`** — random hex secret (min 40 chars / 160 bits)
- **`parse_uri(uri)`** — parse an `otpauth://` URI into a `TOTP`, `HOTP`, or `Steam` object

All constructors take keyword-only parameters after the secret: `digits` (6–10, default 6), `digest` (default `hashlib.sha1`; also `sha256`, `sha512`), `name` (account label, default `"Secret"`), `issuer` (organization name). No third-party dependencies — pure standard library.

## Usage

### TOTP — time-based OTP

```python
import pyotp

totp = pyotp.TOTP('base32secret32323232323232')
totp.now()  # current OTP; changes with the clock

# A fixed Unix timestamp makes these outputs reproducible
totp.at(1234567890)  # => '763850'
totp.verify('763850', for_time=1234567890)  # => True
totp.verify('763850', for_time=1234567920)  # => False

# Verify with a window (±N intervals for clock drift)
totp.verify('763850', for_time=1234567890, valid_window=1)

# Seconds remaining in the current interval
import time
remaining = totp.interval - time.time() % totp.interval
```

Custom configuration:

```python
totp = pyotp.TOTP(
    'base32secret32323232323232',
    digits=8,
    digest=hashlib.sha256,
    interval=60,
    name='alice@example.com',
    issuer='MyApp',
)
```

### HOTP — counter-based OTP

```python
import pyotp

hotp = pyotp.HOTP('base32secret32323232323232')

hotp.at(0)  # => '995369'
hotp.at(1)  # => '511453'
hotp.at(1401)  # => '666948'

# Counter passed to verify() is an offset from initial_count
hotp.verify('666948', 1401)  # => True
hotp.verify('666948', 1402)  # => False

# Starting counter offset
hotp = pyotp.HOTP('base32secret32323232323232', initial_count=100)
```

### Preventing replay attacks

`TOTP.verify()` is stateless — it accepts the same OTP repeatedly while it remains valid. Use `verify_and_get_timecode()` and persist its returned timecode per credential in a database shared by all workers. Reject timecodes ≤ the last accepted one, atomically:

```python
import pyotp

def verify_totp_once(db, credential_id, totp, otp):
    try:
        matched_timecode = totp.verify_and_get_timecode(otp)
    except pyotp.OTPVerificationError:
        return False

    with db:
        updated = db.execute(
            "UPDATE totp_credentials SET last_timecode = ? "
            "WHERE id = ? AND (last_timecode IS NULL OR last_timecode < ?)",
            (matched_timecode, credential_id, matched_timecode),
        )
    return updated.rowcount == 1
```

If you enable `valid_window`, persist the returned matching timecode, which may differ from the server's current timecode. Full patterns (HOTP counter tracking, atomicity) in [02-security-checklist](references/02-security-checklist.md).

### Generating a secret

```python
import pyotp

secret = pyotp.random_base32()  # 32-char base32, 160 bits
secret_hex = pyotp.random_hex()  # 40-char hex, 160 bits
```

Generator minimums: `random_base32(length < 32)` and `random_hex(length < 40)` raise `ValueError`. Construction minimum: the secret must decode to ≥ 112 bits, so `random_base32()` output is always acceptable but older 16-char example secrets (80 bits) are no longer.

### Adjusting the minimum seed length

Default minimum is 112 bits after base32 decoding (NIST SP 800-63B-4). To require more (e.g., 128 bits per RFC 4226), subclass and override the class variable:

```python
import pyotp

class TOTP128(pyotp.TOTP):
    min_secret_length_bits = 128

class HOTP128(pyotp.HOTP):
    min_secret_length_bits = 128
```

The minimum applies at construction and whenever the secret is decoded to generate or verify an OTP.

### Provisioning URIs and QR codes

```python
pyotp.totp.TOTP('JBSWY3DPEHPK3PXPJBSWY3DP').provisioning_uri(name='alice@google.com', issuer_name='Secure App')
# 'otpauth://totp/Secure%20App:alice%40google.com?secret=JBSWY3DPEHPK3PXPJBSWY3DP&issuer=Secure%20App'

pyotp.hotp.HOTP('JBSWY3DPEHPK3PXPJBSWY3DP').provisioning_uri(name="alice@google.com", issuer_name="Secure App", initial_count=0)
# 'otpauth://hotp/Secure%20App:alice%40google.com?secret=JBSWY3DPEHPK3PXPJBSWY3DP&issuer=Secure%20App&counter=0'
```

Render the URI as a QR code with any QR library (e.g., `qrcode`) for the user to scan.

### Parsing provisioning URIs

```python
otp_obj = pyotp.parse_uri('otpauth://totp/Secure%20App:alice%40google.com?secret=JBSWY3DPEHPK3PXPJBSWY3DP&issuer=Secure%20App')
# TOTP object

otp_obj = pyotp.parse_uri('otpauth://hotp/Secure%20App:alice%40google.com?secret=JBSWY3DPEHPK3PXPJBSWY3DP&counter=0')
# HOTP object
```

Supported URI parameters: `secret` (required), `issuer`, `algorithm` (SHA1/SHA256/SHA512), `encoder` (`steam`), `digits`, `period` (TOTP interval), `counter` (HOTP initial count). Duplicate security parameters raise `ValueError`; unknown parameters are ignored.

### Steam TOTP

```python
from pyotp.contrib import Steam

steam = Steam("BASE32_SECRET_AT_LEAST_112_BITS")
steam.now()  # 5-char code from the custom alphabet
steam.verify(steam.now())  # True
```

Steam uses a 5-character code from the alphabet `23456789BCDFGHJKMNPQRTVWXY` (no ambiguous characters). Internally it generates a 10-digit OTP and maps it to the custom alphabet. It is a third-party contribution — not standardized, not officially supported.

## Gotchas

- **Secrets must decode to ≥ 112 bits (14 bytes)** — enforced at construction and on every `generate_otp()`/`verify()` call (secret re-decodes each time). 16-char base32 secrets from pre-2.11 examples raise `ValueError` now. Raise the floor with the `min_secret_length_bits` class variable (e.g., 128).
- **`random_base32()` / `random_hex()` minimums are separate** — 32 and 40 characters (160 bits) respectively; shorter `length` arguments raise `ValueError` even though the construction floor is only 112 bits.
- **`digits` must be 6–10** — the base `OTP` class rejects anything outside 6–10 (`ValueError`). Steam bypasses this by passing `digits=10` internally and emitting 5 characters from its own alphabet.
- **TOTP `interval` must be > 0 and ≤ 120 seconds** — NIST SP 800-63B-4 requires a new nonce at least every two minutes. `TOTP(interval=0)` and `TOTP(interval=300)` raise `ValueError`.
- **Keyword-only parameters** — all constructor parameters after the secret (`digits`, `digest`, `name`, `issuer`, `interval`, `initial_count`), `TOTP.verify()`/`verify_and_get_timecode()` (`for_time`, `valid_window`), and both `provisioning_uri()`s are keyword-only. Positional passing raises `TypeError`.
- **`verify()` returns `False`; `verify_and_get_timecode()` raises** — mismatch in `verify_and_get_timecode()` raises `pyotp.OTPVerificationError` (subclass of `pyotp.PyOTPError`); it never returns `None` or `False`.
- **`verify_and_get_timecode()` rejects negative `valid_window`** — `ValueError: valid_window cannot be negative`.
- **OTP comparison is Unicode-NFKC-normalized** — `verify()` treats `123456` and `１２３４５６` as the same code. Never use the raw submitted OTP or a hash of it as the replay-detection key; persist and compare counters/timecodes instead.
- **Comparison is capped at 1024 code points** — an OTP longer than 1024 Unicode code points always fails (returns `False` / raises `OTPVerificationError`).
- **Timestamp range is enforced** — `at()`, `verify()`, `timecode()` accept Unix timestamps (int/float) or datetimes; values before the Unix epoch or at/after year 10000 UTC (timestamp 253402300800) raise `ValueError`.
- **Naive datetimes are local time with `fold`** — prefer Unix timestamps or timezone-aware UTC datetimes. `TOTP.at(datetime.datetime.now())` uses the server's local timezone, including DST handling via `fold`.
- **`HOTP` counter is an offset from `initial_count`** — `at(count)` computes `generate_otp(initial_count + count)`; `verify(otp, counter)` uses the same offset. With the default `initial_count=0` the two coincide.
- **No built-in replay protection** — `verify()` is stateless. For TOTP, use `verify_and_get_timecode()` plus an atomic persisted timecode; for HOTP, persist the last accepted counter per user and reject lower values.
- **`parse_uri()` validation** — duplicate security parameters (`secret`, `issuer`, `algorithm`, `encoder`, `digits`, `period`, `counter`) raise `ValueError`; blank parameter values are ignored; unknown parameters are ignored; `digits` must be 6, 7, or 8 (except `encoder=steam`); missing `secret`, non-`otpauth` scheme, and types other than `totp`/`hotp` raise `ValueError`. Issuer in label and in query parameter must match.
- **`provisioning_uri()` honors `initial_count=0` for HOTP** — passing `initial_count=0` explicitly emits `counter=0` (fixed in 2.11.0); omitting it produces a TOTP-type URI.
- **`provisioning_uri(**kwargs)` values must be strings** — non-string values raise `TypeError`; the `image` key must be an HTTPS URL with a host and path, otherwise `ValueError`.
- **`provisioning_uri()` omits defaults** — `algorithm=SHA1`, `digits=6`, `period=30` are left out when they match defaults; `+` is encoded as `%20` in the query string.
- **`name` defaults to `"Secret"`** — pass `name=` (constructor) or `name=` (`provisioning_uri()`) for a meaningful account label.
- **`md5` and `shake_128` are rejected as digest** — digests must produce ≥ 18 bytes to survive the truncation step. Use `sha1`, `sha256`, `sha512`.
- **`Steam` is not standardized** — `pyotp.contrib.Steam` is provided for reference only; its behavior may change or be removed.
- **Secrets should be stored securely** — pyotp does not encrypt or hash secrets. Store them in a controlled-access database; never log them. Rate-limit verification and use HTTPS — see [02-security-checklist](references/02-security-checklist.md).

## References

- [01-api-reference](references/01-api-reference.md) — Full API surface for 2.12.1: constructors, keyword-only signatures, exceptions, all methods and parameters
- [02-security-checklist](references/02-security-checklist.md) — Security best practices: 112-bit secret strength, replay prevention via timecode/counter tracking, rate limiting, clock sync
- [03-otpauth-uri-format](references/03-otpauth-uri-format.md) — Complete otpauth:// URI specification, all parameters, validation rules, and edge cases
