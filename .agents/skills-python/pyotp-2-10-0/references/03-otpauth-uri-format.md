# pyotp 2.10.0 — otpauth:// URI Format

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

A percent-encoded `%3A` inside the label is a literal colon that is part of the issuer or account name, not a separator.

---

## TOTP URIs

```
otpauth://totp/<label>?secret=<BASE32_SECRET>&<params>
```

### Example

```
otpauth://totp/Secure%20App:alice%40google.com?secret=JBSWY3DPEHPK3PXP&issuer=Secure%20App
```

### Generating with pyotp

```python
totp = pyotp.TOTP("JBSWY3DPEHPK3PXP")
uri = totp.provisioning_uri(name="alice@google.com", issuer_name="Secure App")
```

---

## HOTP URIs

```
otpauth://hotp/<label>?secret=<BASE32_SECRET>&counter=<N>&<params>
```

The `counter` parameter is required to distinguish HOTP from TOTP.

### Example

```
otpauth://hotp/Secure%20App:alice%40google.com?secret=JBSWY3DPEHPK3PXP&issuer=Secure%20App&counter=0
```

### Generating with pyotp

```python
hotp = pyotp.HOTP("JBSWY3DPEHPK3PXP")
uri = hotp.provisioning_uri(
    name="alice@google.com",
    issuer_name="Secure App",
    initial_count=0,
)
```

---

## Query Parameters

### Required

| Parameter | Type | Description |
|---|---|---|
| `secret` | string | Base32-encoded shared secret. |

### TOTP parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `issuer` | string | — | Issuer name (organization). |
| `algorithm` | string | `SHA1` | Hash algorithm: `SHA1`, `SHA256`, `SHA512`. |
| `digits` | integer | `6` | Number of digits: `6`, `7`, or `8`. |
| `period` | integer | `30` | Time interval in seconds. |

### HOTP parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `issuer` | string | — | Issuer name (organization). |
| `algorithm` | string | `SHA1` | Hash algorithm: `SHA1`, `SHA256`, `SHA512`. |
| `digits` | integer | `6` | Number of digits: `6`, `7`, or `8`. |
| `counter` | integer | `0` | Current counter value. |

### Optional (both types)

| Parameter | Type | Description |
|---|---|---|
| `image` | URL | HTTPS URL for an icon displayed in the authenticator app. |

---

## Encoding Rules

- **Label encoding** — the issuer and account name are URL-encoded. Spaces become `%20`, `@` becomes `%40`, etc.
- **Secret encoding** — the secret is URL-encoded but base32 characters (A-Z, 2-7) are all safe ASCII, so no encoding is needed for standard secrets.
- **Default values omitted** — pyotp omits parameters that match defaults:
  - `algorithm=SHA1` is omitted
  - `digits=6` is omitted
  - `period=30` is omitted
- **`+` replaced with `%20`** — pyotp's `build_uri()` replaces `+` with `%20` in the query string to avoid ambiguity with spaces.

---

## Parsing with pyotp

```python
import pyotp

# Parse TOTP URI
otp = pyotp.parse_uri("otpauth://totp/MyApp:user?secret=JBSWY3DPEHPK3PXP&issuer=MyApp")
print(type(otp))  # <class 'pyotp.totp.TOTP'>
print(otp.secret) # 'JBSWY3DPEHPK3PXP'
print(otp.name)   # 'user'
print(otp.issuer) # 'MyApp'

# Parse HOTP URI
otp = pyotp.parse_uri("otpauth://hotp/MyApp:user?secret=JBSWY3DPEHPK3PXP&counter=0")
print(type(otp))  # <class 'pyotp.hotp.HOTP'>
print(otp.initial_count)  # 0

# Parse with custom parameters
otp = pyotp.parse_uri("otpauth://totp/App:user?secret=ABC&algorithm=SHA256&digits=8&period=60")
print(otp.digest)   # <built-in function sha256>
print(otp.digits)   # 8
print(otp.interval) # 60
```

### Parsing behavior

- **Issuer in label vs parameter** — if the issuer appears in both the label and as a query parameter, they must match exactly. Otherwise `ValueError` is raised.
- **No issuer in label** — if the label has no `:`, the entire label is treated as the account name, and `issuer` comes only from the query parameter (if present).
- **Steam detection** — if `encoder=steam` is in the URI, `parse_uri()` returns a `contrib.Steam` object.

---

## Edge Cases

### Colon in issuer or account name

A literal colon in the issuer or account name must be percent-encoded as `%3A`:

```
# Issuer with a colon
otpauth://totp/My%3AApp:user?secret=ABC&issuer=My:App

# Account with a colon
otpauth://totp/MyApp:user:name?secret=ABC&issuer=MyApp
# This parses as issuer="MyApp", account="user:name" (if : is encoded)
```

pyotp splits on the first unencoded `:` to separate issuer from account.

### Missing issuer parameter

If the label contains an issuer but no `issuer` query parameter, the issuer is taken from the label. The reverse is also true — if only the query parameter has an issuer, it's used without a label issuer.

### Invalid digits

Only `6`, `7`, or `8` are accepted (except for Steam which allows `5`). Other values raise `ValueError` during parsing.

### Invalid algorithm

Only `SHA1`, `SHA256`, and `SHA512` are accepted. Other values raise `ValueError`.

### Missing secret

URIs without a `secret` parameter raise `ValueError`.

### Non-otpauth scheme

URIs with schemes other than `otpauth` raise `ValueError`.

### Unsupported type

Only `totp` and `hotp` are recognized as OTP types. Other values (e.g., `otpauth://email/...`) raise `ValueError`.

### Image parameter validation

The `image` parameter must be a valid HTTPS URL. HTTP URLs, malformed URLs, or URLs without a host/path raise `ValueError`.

```python
# Valid
uri = totp.provisioning_uri(name="user", issuer_name="App", image="https://example.com/icon.png")

# Invalid — HTTP
uri = totp.provisioning_uri(name="user", issuer_name="App", image="http://example.com/icon.png")
# ValueError
```
