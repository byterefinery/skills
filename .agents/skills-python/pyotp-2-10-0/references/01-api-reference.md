# pyotp 2.10.0 — API Reference

## Table of Contents

- [Module-Level Functions](#module-level-functions)
- [OTP (Base Class)](#otp-base-class)
- [TOTP](#totp)
- [HOTP](#hotp)
- [contrib.Steam](#contribsteam)

---

## Module-Level Functions

### `pyotp.random_base32(length: int = 32, chars: Sequence[str] = ...) -> str`

Generate a random base32-encoded secret string.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `length` | `int` | `32` | Length of the generated secret. Minimum 32 (160 bits). |
| `chars` | `Sequence[str]` | `"ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"` | Character set for the secret. |

**Returns:** `str` — random base32 string of the given length.  
**Raises:** `ValueError` if `length < 32`.

### `pyotp.random_hex(length: int = 40, chars: Sequence[str] = ...) -> str`

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

**Returns:** `TOTP`, `HOTP`, or `contrib.Steam` object.  
**Raises:**
- `ValueError` — if scheme is not `otpauth`, no secret found, unsupported OTP type, mismatched issuer, invalid algorithm, or invalid digits value.

---

## OTP (Base Class)

`pyotp.otp.OTP` — base class for all OTP handlers. Not intended for direct instantiation.

### Constructor

```python
OTP(s: str, digits: int = 6, digest: Any = hashlib.sha1, name: Optional[str] = None, issuer: Optional[str] = None)
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `s` | `str` | — | Secret in base32 format. |
| `digits` | `int` | `6` | Number of digits in the OTP (max 10). |
| `digest` | `Any` | `hashlib.sha1` | HMAC digest function. Must produce ≥ 18 bytes. |
| `name` | `str` | `"Secret"` | Account name label. |
| `issuer` | `str` | `None` | Issuer (organization) name. |

**Raises:**
- `ValueError` — if `digits > 10`, digest is `md5`/`shake_128`, or digest size < 18 bytes.

### Methods

#### `generate_otp(input: int) -> str`

Generate an OTP code for the given input (counter or timecode).

| Parameter | Type | Description |
|---|---|---|
| `input` | `int` | The HMAC counter value. Must be ≥ 0. |

**Returns:** `str` — zero-padded OTP string of `digits` length.  
**Raises:** `ValueError` if `input < 0` or digest size < 18 bytes.

#### `byte_secret() -> bytes`

Decode the base32 secret to raw bytes.

**Returns:** `bytes` — the decoded secret with padding added as needed.

#### `int_to_bytestring(i: int, padding: int = 8) -> bytes`

Convert an integer to an 8-byte big-endian bytestring (OATH format).

**Returns:** `bytes` — zero-padded 8-byte representation.

### Attributes

| Attribute | Type | Description |
|---|---|---|
| `secret` | `str` | The base32 secret string. |
| `digits` | `int` | Number of digits in generated OTPs. |
| `digest` | `Any` | The digest function. |
| `name` | `str` | Account name label. |
| `issuer` | `str` | Issuer name. |

---

## TOTP

`pyotp.totp.TOTP` — time-based one-time password handler.

### Constructor

```python
TOTP(s: str, digits: int = 6, digest: Any = None, name: Optional[str] = None, issuer: Optional[str] = None, interval: int = 30)
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `s` | `str` | — | Secret in base32 format. |
| `digits` | `int` | `6` | Number of digits in the OTP. |
| `digest` | `Any` | `hashlib.sha1` | HMAC digest function. |
| `name` | `str` | `None` | Account name. |
| `issuer` | `str` | `None` | Issuer name. |
| `interval` | `int` | `30` | Time interval in seconds for each OTP. |

### Methods

#### `now() -> str`

Generate the current OTP based on the current time.

**Returns:** `str` — current OTP code.

#### `at(for_time: Union[int, datetime.datetime], counter_offset: int = 0) -> str`

Generate an OTP for a specific time.

| Parameter | Type | Description |
|---|---|---|
| `for_time` | `int` or `datetime` | Unix timestamp or datetime object. |
| `counter_offset` | `int` | Number of intervals to add to the timecode (default 0). |

**Returns:** `str` — OTP code for the specified time.

#### `verify(otp: str, for_time: Optional[datetime.datetime] = None, valid_window: int = 0) -> bool`

Verify an OTP code against the current or specified time.

| Parameter | Type | Description |
|---|---|---|
| `otp` | `str` | The OTP code to verify. |
| `for_time` | `datetime` | Time to check against (default: now). |
| `valid_window` | `int` | Number of intervals before/after to accept (default 0). |

**Returns:** `bool` — `True` if the OTP is valid within the window.

Uses timing-attack-resistant comparison via `hmac.compare_digest`.

#### `provisioning_uri(name: Optional[str] = None, issuer_name: Optional[str] = None, **kwargs) -> str`

Generate an `otpauth://totp/` provisioning URI.

| Parameter | Type | Description |
|---|---|---|
| `name` | `str` | Account name (overrides instance `name`). |
| `issuer_name` | `str` | Issuer name (overrides instance `issuer`). |
| `**kwargs` | — | Extra query parameters (e.g., `image="https://..."`). |

**Returns:** `str` — the provisioning URI string.

#### `timecode(for_time: datetime.datetime) -> int`

Compute the timecode (counter value) for a given datetime.

| Parameter | Type | Description |
|---|---|---|
| `for_time` | `datetime` | A datetime object (naive = local time, aware = UTC). |

**Returns:** `int` — the counter value (floor of unix_timestamp / interval).

### Attributes

| Attribute | Type | Description |
|---|---|---|
| `interval` | `int` | Time interval in seconds (default 30). |

---

## HOTP

`pyotp.hotp.HOTP` — HMAC-based counter one-time password handler.

### Constructor

```python
HOTP(s: str, digits: int = 6, digest: Any = None, name: Optional[str] = None, issuer: Optional[str] = None, initial_count: int = 0)
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `s` | `str` | — | Secret in base32 format. |
| `digits` | `int` | `6` | Number of digits in the OTP. |
| `digest` | `Any` | `hashlib.sha1` | HMAC digest function. |
| `name` | `str` | `None` | Account name. |
| `issuer` | `str` | `None` | Issuer name. |
| `initial_count` | `int` | `0` | Starting counter value. |

### Methods

#### `at(count: int) -> str`

Generate an OTP for the given counter value.

| Parameter | Type | Description |
|---|---|---|
| `count` | `int` | The counter offset from `initial_count`. |

**Returns:** `str` — zero-padded OTP string.

#### `verify(otp: str, counter: int) -> bool`

Verify an OTP against a specific counter value.

| Parameter | Type | Description |
|---|---|---|
| `otp` | `str` | The OTP code to verify. |
| `counter` | `int` | The expected counter value. |

**Returns:** `bool` — `True` if the OTP matches.

#### `provisioning_uri(name: Optional[str] = None, initial_count: Optional[int] = None, issuer_name: Optional[str] = None, **kwargs) -> str`

Generate an `otpauth://hotp/` provisioning URI.

| Parameter | Type | Description |
|---|---|---|
| `name` | `str` | Account name (overrides instance `name`). |
| `initial_count` | `int` | Starting counter (overrides instance `initial_count`). |
| `issuer_name` | `str` | Issuer name (overrides instance `issuer`). |
| `**kwargs` | — | Extra query parameters. |

**Returns:** `str` — the provisioning URI string.

### Attributes

| Attribute | Type | Description |
|---|---|---|
| `initial_count` | `int` | Starting counter value. |

---

## contrib.Steam

`pyotp.contrib.Steam` — Steam's custom TOTP implementation. Subclass of `TOTP`.

### Constructor

```python
Steam(s: str, name: Optional[str] = None, issuer: Optional[str] = None, interval: int = 30, digits: int = 5)
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `s` | `str` | — | Secret in base32 format. |
| `name` | `str` | `None` | Account name. |
| `issuer` | `str` | `None` | Issuer name. |
| `interval` | `int` | `30` | Time interval in seconds. |
| `digits` | `int` | `5` | Ignored — always produces 5-character codes. |

### Methods

Inherits all `TOTP` methods (`now()`, `at()`, `verify()`, `provisioning_uri()`, `timecode()`).

#### `generate_otp(input: int) -> str`

Override: generates a 5-character Steam-style code using the alphabet `23456789BCDFGHJKMNPQRTVWXY`.

**Returns:** `str` — 5-character Steam code.

### Constants

| Constant | Value | Description |
|---|---|---|
| `STEAM_CHARS` | `"23456789BCDFGHJKMNPQRTVWXY"` | Steam's custom character alphabet (28 chars, no ambiguous characters). |
| `STEAM_DEFAULT_DIGITS` | `5` | Fixed code length for Steam TOTP. |
