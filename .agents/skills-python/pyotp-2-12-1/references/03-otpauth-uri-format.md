# pyotp 2.12.1 — otpauth:// URI Format

## Table of Contents

- [URI Structure](#uri-structure)
- [TOTP URIs](#totp-uris)
- [HOTP URIs](#hotp-uris)
- [Query Parameters](#query-parameters)
- [Encoding Rules](#encoding-rules)
- [Parsing with pyotp](#parsing-with-pyotp)
- [Edge Cases](#edge-cases)

---

## URI Structure

The `otpauth://` scheme follows the format defined by the [Google Authenticator Key Uri Format](https://github.com/google/google-authenticator/wiki/Key-Uri-Format):

```
otpauth://<type>/<label>?<parameters>
```

| Component | Description |
|---|---|
| `otpauth://` | Fixed scheme |
| `<type>` | `totp` or `hotp` |
| `<label>` | `[issuer:][account]` — colon-separated, URL-encoded |
| `<parameters>` | URL-encoded query string |

### Label format

The label uses a literal `:` to separate issuer from account name:

```
otpauth://totp/MyApp:alice%40example.com?secret=...
#              ^^^^^ ^^^^^^^^^^^^^^^^^^
#              issuer account (URL-encoded)

otpauth://totp/alice%40example.com?secret=...
#              ^^^^^^^^^^^^^^^^^^
#              account only (no issuer)
```

pyotp splits the label on the first **unencoded** `:` while the path is still percent-encoded, then unquotes each component — so a percent-encoded `%3A` inside the issuer or account name is a literal colon, not a separator (fixed for encoded-colon mis-parsing in 2.10.0).

---

## TOTP URIs

```
otpauth://totp/<label>?secret=<BASE32_SECRET>&<params>
```

### Example (from the project README)

```
otpauth://totp/Secure%20App:alice%40google.com?secret=JBSWY3DPEHPK3PXPJBSWY3DP&issuer=Secure%20App
```

### Generating with pyotp

```python
pyotp.totp.TOTP('JBSWY3DPEHPK3PXPJBSWY3DP').provisioning_uri(name='alice@google.com', issuer_name='Secure App')
```

The URI type is `totp` when no `initial_count` is passed.

---

## HOTP URIs

```
otpauth://hotp/<label>?secret=<BASE32_SECRET>&counter=<N>&<params>
```

The `counter` parameter is present whenever `initial_count` is provided — **including `initial_count=0`** (fixed in 2.11.0; previously 0 was indistinguishable from "not set").

### Example (from the project README)

```
otpauth://hotp/Secure%20App:alice%40google.com?secret=JBSWY3DPEHPK3PXPJBSWY3DP&issuer=Secure%20App&counter=0
```

### Generating with pyotp

```python
pyotp.hotp.HOTP('JBSWY3DPEHPK3PXPJBSWY3DP').provisioning_uri(name="alice@google.com", issuer_name="Secure App", initial_count=0)
```

---

## Query Parameters

### Required

| Parameter | Type | Description |
|---|---|---|
| `secret` | string | Base32-encoded shared secret (must decode to ≥ 112 bits by default). |

### TOTP parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `issuer` | string | — | Issuer name (organization). |
| `algorithm` | string | `SHA1` | Hash algorithm: `SHA1`, `SHA256`, `SHA512`. |
| `digits` | integer | `6` | Number of digits: `6`, `7`, or `8` when parsing (construction accepts 6–10). |
| `period` | integer | `30` | Time interval in seconds (must be ≤ 120). |

### HOTP parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `issuer` | string | — | Issuer name (organization). |
| `algorithm` | string | `SHA1` | Hash algorithm: `SHA1`, `SHA256`, `SHA512`. |
| `digits` | integer | `6` | Number of digits: `6`, `7`, or `8` when parsing. |
| `counter` | integer | `0` | Current counter value. `counter=0` is honored. |

### Optional (both types)

| Parameter | Type | Description |
|---|---|---|
| `image` | URL | HTTPS URL for an icon displayed in the authenticator app. Must have a host and a path. |
| `encoder` | string | `steam` selects the `contrib.Steam` class in `parse_uri()`. |

### Validation (parse_uri)

- Duplicate security parameters (`secret`, `issuer`, `algorithm`, `encoder`, `digits`, `period`, `counter`) raise `ValueError` ("Duplicate <key> parameter"). Duplicate unknown parameters are ignored.
- Blank parameter values are skipped.
- Unknown parameters are ignored.

---

## Encoding Rules

- **Label encoding** — the issuer and account name are URL-encoded. Spaces become `%20`, `@` becomes `%40`, etc.
- **Secret encoding** — the secret is URL-encoded, but base32 characters (A–Z, 2–7) are all safe ASCII, so no encoding is needed for standard secrets.
- **Default values omitted** — pyotp omits parameters that match defaults: `algorithm=SHA1` (case-insensitive on the wire, uppercased in output), `digits=6`, `period=30`.
- **`+` replaced with `%20`** — pyotp's `build_uri()` replaces `+` with `%20` in the query string to avoid ambiguity with spaces.
- **Extra `**kwargs` values must be strings** — non-string values raise `TypeError` in `provisioning_uri()`.

---

## Parsing with pyotp

```python
import pyotp

# Parse TOTP URI
otp = pyotp.parse_uri("otpauth://totp/Secure%20App:alice%40google.com?secret=JBSWY3DPEHPK3PXPJBSWY3DP&issuer=Secure%20App")
print(type(otp))   # <class 'pyotp.totp.TOTP'>
print(otp.secret)  # 'JBSWY3DPEHPK3PXPJBSWY3DP'
print(otp.name)    # 'alice@google.com'
print(otp.issuer)  # 'Secure App'

# Parse HOTP URI
otp = pyotp.parse_uri("otpauth://hotp/Secure%20App:alice%40google.com?secret=JBSWY3DPEHPK3PXPJBSWY3DP&counter=0")
print(type(otp))            # <class 'pyotp.hotp.HOTP'>
print(otp.initial_count)    # 0

# Parse with custom parameters
otp = pyotp.parse_uri("otpauth://totp/App:user?secret=JBSWY3DPEHPK3PXPJBSWY3DP&algorithm=SHA256&digits=8&period=60")
print(otp.digits)   # 8
print(otp.interval) # 60
```

### Parsing behavior

- **Issuer in label vs parameter** — if the issuer appears in both the label and as a query parameter, they must match exactly. Otherwise `ValueError` is raised.
- **No issuer in label** — if the label has no `:`, the entire label is treated as the account name, and `issuer` comes only from the query parameter (if present).
- **Steam detection** — if `encoder=steam` is in the URI, `parse_uri()` returns a `contrib.Steam` object (the `digits` parameter, if present, is ignored by Steam).
- **Constructed objects are validated** — the parsed secret must still decode to ≥ 112 bits, `digits` 6–10, and `period` (interval) 1–120; violations raise `ValueError`.

---

## Edge Cases

### Colon in issuer or account name

A literal colon in the issuer or account name must be percent-encoded as `%3A`:

```
# Issuer with a colon
otpauth://totp/My%3AApp:user?secret=JBSWY3DPEHPK3PXPJBSWY3DP&issuer=My:App
```

pyotp splits the label on the first unencoded `:` while still percent-encoded, then unquotes each side — encoded colons stay part of the name.

### Missing issuer parameter

If the label contains an issuer but no `issuer` query parameter, the issuer is taken from the label. The reverse is also true — if only the query parameter has an issuer, it's used without a label issuer.

### Invalid digits

Only `6`, `7`, or `8` are accepted when parsing (except for Steam which allows its fixed 5-character encoding). Other values raise `ValueError` during parsing. Note that construction itself accepts 6–10.

### Invalid algorithm

Only `SHA1`, `SHA256`, and `SHA512` (case-sensitive in the parser) are accepted. Other values raise `ValueError`.

### Missing secret

URIs without a `secret` parameter raise `ValueError` ("No secret found in URI"). A secret that decodes to fewer than 112 bits also raises `ValueError` when the object is constructed.

### Non-otpauth scheme

URIs with schemes other than `otpauth` raise `ValueError` ("Not an otpauth URI").

### Unsupported type

Only `totp` and `hotp` are recognized as OTP types. Other values (e.g., `otpauth://email/...`) raise `ValueError` ("Not a supported OTP type").

### Image parameter validation

The `image` parameter must be a valid HTTPS URL with a host and a path. HTTP URLs, or URLs missing host/path, raise `ValueError` in `provisioning_uri()`.

```python
# Valid
uri = totp.provisioning_uri(name="user", issuer_name="App", image="https://example.com/icon.png")

# Invalid — HTTP
uri = totp.provisioning_uri(name="user", issuer_name="App", image="http://example.com/icon.png")
# ValueError
```

### Short secrets

The classic documentation secret `JBSWY3DPEHPK3PXP` (16 chars = 80 bits) no longer passes construction in 2.12.x. Use `JBSWY3DPEHPK3PXPJBSWY3DP` (24 chars = 120 bits) or `random_base32()` output.
