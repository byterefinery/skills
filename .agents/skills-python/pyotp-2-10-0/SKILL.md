---
name: pyotp-2-10-0
description: >
  Python library for generating and verifying TOTP (time-based) and HOTP
  (counter-based) one-time passwords per RFC 6238 / RFC 4226. Use when
  implementing two-factor (2FA) or multi-factor (MFA) authentication,
  provisioning Google Authenticator-compatible QR codes, parsing otpauth://
  URIs, generating random base32 or hex secrets, verifying user-supplied OTP
  codes, or working with Steam's custom TOTP variant.
metadata:
  tags:
    - python
    - authentication
    - security
---

# pyotp 2.10.0

## Overview

`pyotp` 2.10.0 implements server-side support for the OATH one-time password standards — HOTP (RFC 4226) and TOTP (RFC 6238). It generates short numeric codes from a shared base32 secret and verifies codes submitted by clients. It also produces `otpauth://` provisioning URIs for QR-code setup in authenticator apps (Google Authenticator, Authy, 1Password, etc.).

Core classes:

- **`OTP`** — base class implementing HMAC-based OTP generation (`generate_otp()`, `byte_secret()`, `int_to_bytestring()`)
- **`TOTP`** — time-based OTP; codes rotate every N seconds (default 30). Methods: `now()`, `at()`, `verify()`, `provisioning_uri()`, `timecode()`
- **`HOTP`** — counter-based OTP; codes advance with each increment. Methods: `at()`, `verify()`, `provisioning_uri()`
- **`contrib.Steam`** — Steam's proprietary TOTP variant (5-character codes from custom alphabet). Subclass of `TOTP`

Module-level helpers:

- **`random_base32(length=32)`** — generate a random base32 secret (min 32 chars / 160 bits)
- **`random_hex(length=40)`** — generate a random hex secret (min 40 chars / 160 bits)
- **`parse_uri(uri)`** — parse an `otpauth://` URI back into a `TOTP`, `HOTP`, or `Steam` object

All classes accept `digits` (6, 7, or 8; default 6), `digest` (hashlib function, default `sha1`; also supports `sha256`, `sha512`), `name` (account label), and `issuer` (organization name).

No third-party dependencies — pure standard library.

## Usage

### Generating a secret

```python
import pyotp

secret = pyotp.random_base32()   # 32-char base32 string, e.g. "JBSWY3DPEHPK3PXP..."
```

Secrets must be at least 32 characters (160 bits). Shorter lengths raise `ValueError`.

### TOTP — time-based OTP

```python
import pyotp

totp = pyotp.TOTP("JBSWY3DPEHPK3PXP")

# Current code
code = totp.now()          # '492039'

# Code at a specific time
code = totp.at(1609459200)  # Unix timestamp

# Verify a code (exact match)
totp.verify("492039")       # True or False

# Verify with a window (allows ±N intervals for clock drift)
totp.verify("492039", valid_window=1)  # checks current ± 1 interval

# Seconds remaining in current interval
import datetime
remaining = totp.interval - datetime.datetime.now().timestamp() % totp.interval
```

Custom interval and digest:

```python
totp = pyotp.TOTP(
    secret,
    digits=8,
    digest=hashlib.sha256,
    interval=60,
    name="alice@example.com",
    issuer="MyApp",
)
```

### HOTP — counter-based OTP

```python
import pyotp

hotp = pyotp.HOTP("JBSWY3DPEHPK3PXP")

# Generate code at counter N
code = hotp.at(0)          # '260182'
code = hotp.at(1)          # '055283'
code = hotp.at(1401)       # '316439'

# Verify against a specific counter
hotp.verify("316439", 1401)  # True
hotp.verify("316439", 1402)  # False

# With a starting count offset
hotp = pyotp.HOTP("JBSWY3DPEHPK3PXP", initial_count=100)
```

### Provisioning URIs and QR codes

Generate an `otpauth://` URI for scanning into an authenticator app:

```python
totp = pyotp.TOTP("JBSWY3DPEHPK3PXP")
uri = totp.provisioning_uri(name="alice@example.com", issuer_name="MyApp")
# 'otpauth://totp/MyApp:alice%40example.com?secret=JBSWY3DPEHPK3PXP&issuer=MyApp'

# HOTP
hotp = pyotp.HOTP("JBSWY3DPEHPK3PXP")
uri = hotp.provisioning_uri(
    name="alice@example.com",
    issuer_name="MyApp",
    initial_count=0,
)
# 'otpauth://hotp/MyApp:alice%40example.com?secret=...&issuer=MyApp&counter=0'
```

Render the URI as a QR code with any QR library (e.g., `qrcode`, `qrcodegen`, or a QR API).

### Parsing provisioning URIs

```python
otp_obj = pyotp.parse_uri("otpauth://totp/MyApp:alice%40example.com?secret=JBSWY3DPEHPK3PXP&issuer=MyApp")
# Returns a TOTP object

otp_obj = pyotp.parse_uri("otpauth://hotp/MyApp:alice%40example.com?secret=...&issuer=MyApp&counter=0")
# Returns an HOTP object
```

Supported URI parameters: `secret`, `issuer`, `algorithm` (SHA1/SHA256/SHA512), `digits`, `period` (TOTP interval), `counter` (HOTP initial count).

### Steam TOTP

```python
from pyotp.contrib import Steam

steam = Steam("BASE32SECRET")
code = steam.now()       # 5-char code using Steam's custom alphabet
steam.verify(code)        # True
```

Steam uses a 5-character code from the alphabet `23456789BCDFGHJKMNPQRTVWXY` (no ambiguous characters). Internally it generates a 10-digit OTP and maps it to the custom alphabet.

### Typical 2FA enrollment flow

```python
import pyotp

# 1. Generate secret
secret = pyotp.random_base32()

# 2. Create provisioning URI
totp = pyotp.TOTP(secret)
uri = totp.provisioning_uri(name=user.email, issuer_name="MyApp")

# 3. Render uri as QR code for user to scan

# 4. Verify user scanned correctly (they submit the code from their app)
if totp.verify(user_submitted_code, valid_window=1):
    # Store secret (hashed or encrypted) for this user
    save_user_secret(user.id, secret)
```

### Typical 2FA login flow

```python
import pyotp

# 1. Load stored secret
secret = load_user_secret(user.id)
totp = pyotp.TOTP(secret)

# 2. Verify submitted code
if totp.verify(submitted_code, valid_window=1):
    grant_access()
else:
    reject()
```

## Gotchas

- **Secrets must be base32-encoded strings** — pass the raw base32 string (uppercase letters + digits 2-7, no padding `=`). The library handles padding internally via `byte_secret()`. Lowercase works too (casefold is applied).
- **`TOTP.now()` depends on system clock** — if the server clock is wrong, generated and verified codes will be off. Keep NTP synchronized. Use `valid_window` in `verify()` to tolerate small drift.
- **`valid_window` is in intervals, not seconds** — `valid_window=1` checks ±1 interval (default 30 s), not ±1 second. With `interval=60`, `valid_window=1` covers ±60 seconds.
- **`HOTP.verify()` requires the exact counter** — unlike TOTP, HOTP has no automatic counter. The server must track the last used counter per user and reject replayed codes. Store the counter state in your database.
- **No built-in replay protection** — pyotp does not track which codes have been used. For HOTP, maintain a counter. For TOTP, track verified timestamps or code hashes to reject replays within the same interval.
- **`parse_uri()` raises on mismatched issuer** — if the URI label contains an issuer and the `issuer` query param differs, a `ValueError` is raised. Both must match.
- **`parse_uri()` raises on missing secret** — URIs without a `secret` parameter raise `ValueError`.
- **`parse_uri()` raises on unsupported OTP type** — only `otpauth://totp/`, `otpauth://hotp/`, and Steam URIs are recognized.
- **`digits` must be ≤ 10** — the base `OTP` class rejects `digits > 10`. Standard apps support 6, 7, or 8. Steam uses 5 (via its own encoding).
- **`md5` and `shake_128` are rejected as digest** — they produce digests < 18 bytes, which breaks the truncation step. Use `sha1`, `sha256`, `sha512`, or any digest ≥ 18 bytes.
- **`random_base32()` minimum length is 32** — passing `length < 32` raises `ValueError` (160-bit minimum). The default charset is `ABCDEFGHIJKLMNOPQRSTUVWXYZ234567` (no padding).
- **`random_hex()` minimum length is 40** — passing `length < 40` raises `ValueError`.
- **`provisioning_uri()` omits default values** — algorithm SHA1, digits 6, and period 30 are omitted from the URI when they match defaults, keeping the URI shorter.
- **`provisioning_uri()` auto-selects totp vs hotp** — if `initial_count` is passed, the URI type is `hotp`; otherwise it is `totp`.
- **`Steam` is not standardized** — it's a third-party contribution (`pyotp.contrib.Steam`), not defined by any RFC. Its behavior may change or be removed.
- **`TOTP.at()` accepts `datetime` or int** — pass a `datetime.datetime` object or a Unix timestamp integer. Naive datetimes are treated as local time; aware datetimes are converted to UTC.
- **Naive datetime = local time, not UTC** — `TOTP.at(datetime.datetime.now())` uses the server's local timezone. Use `datetime.datetime.utcnow()` or a timezone-aware datetime to ensure UTC.
- **`provisioning_uri()` `image` param must be HTTPS** — the optional `image` parameter (for authenticator app icons) must be a valid HTTPS URL, otherwise `ValueError` is raised.
- **Secrets should be stored securely** — pyotp does not encrypt or hash secrets. Store them in a controlled-access database, ideally hashed (e.g., HMAC of the secret with a server-side key) so the raw secret is never in the DB.
- **Use HTTPS for all OTP endpoints** — sending OTP codes over plaintext HTTP exposes them to interception. The RFCs require transport confidentiality.
- **Rate-limit verification attempts** — brute-force against 6-digit codes is feasible (1 in 1 million). Throttle failed attempts per account.

## References

- [01-api-reference](references/01-api-reference.md) — Full API surface: all class constructors, methods, parameters, and return types
- [02-security-checklist](references/02-security-checklist.md) — Security best practices: secret storage, replay protection, rate limiting, clock sync
- [03-otpauth-uri-format](references/03-otpauth-uri-format.md) — Complete otpauth:// URI specification, all parameters, encoding rules, and edge cases
