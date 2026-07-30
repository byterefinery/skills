# Encryption

## Decrypting PDFs

```python
from pypdf import PdfReader, PasswordType

# Open encrypted PDF
reader = PdfReader("encrypted.pdf")

# Check encryption
if reader.is_encrypted:
    # Decrypt with password
    result = reader.decrypt("password")

    # Check which password worked
    if result == PasswordType.NONE:
        print("No password was needed")
    elif result == PasswordType.USER:
        print("User password accepted")
    elif result == PasswordType.OWNER:
        print("Owner password accepted")

# Or decrypt at open
reader = PdfReader("encrypted.pdf", password="secret")
```

### PasswordType

```python
from pypdf import PasswordType

PasswordType.NONE   # 0 — no password needed
PasswordType.USER   # 1 — user password accepted
PasswordType.OWNER  # 2 — owner password accepted
```

## Encrypting PDFs

```python
from pypdf import PdfWriter

writer = PdfWriter(clone_from="input.pdf")

# Basic encryption (RC4-128)
writer.encrypt("user_password", "owner_password")

# Same password for both
writer.encrypt("password")  # owner_password defaults to user_password

# AES-256
writer.encrypt("user_pw", "owner_pw", algorithm="AES-256")

# With permissions
from pypdf.constants import UserAccessPermissions as UAP
writer.encrypt(
    "user_pw",
    "owner_pw",
    algorithm="AES-256",
    permissions_flag=~(UAP.MODIFY_DOCUMENT | UAP.EXTRACT_TEXT_GRAPHICS),
)

writer.write("encrypted.pdf")
```

### Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `user_password` | `str` | — | Password for opening/reading |
| `owner_password` | `str \| None` | `user_password` | Password for full access |
| `use_128bit` | `bool` | `True` | 128-bit (True) or 40-bit (False) |
| `permissions_flag` | `int` | `ALL_DOCUMENT_PERMISSIONS` | Bitmask of allowed operations |
| `algorithm` | `str \| None` | `None` | Encryption algorithm (overrides use_128bit) |

### Algorithms

| Algorithm | Key size | Revision | Dependency |
|---|---|---|---|
| `RC4-40` | 40-bit | 2 | None |
| `RC4-128` | 128-bit | 3 | None |
| `AES-128` | 128-bit | 4 | `cryptography` |
| `AES-256` | 256-bit | 4 | `cryptography` |
| `AES-256-R5` | 256-bit | 5 | `cryptography` |

Install AES support: `pip install pypdf[crypto]` (includes `cryptography`).

## Permission Flags

```python
from pypdf.constants import UserAccessPermissions as UAP

# Individual permissions
UAP.PRINT                  # Bit 3 — Print document
UAP.MODIFY_DOCUMENT        # Bit 4 — Modify content
UAP.MODIFY_ANNOTATIONS     # Bit 5 — Modify annotations
UAP.FILL_INTERACTIVE_FORMS # Bit 9 — Fill form fields
UAP.EXTRACT_TEXT_GRAPHICS  # Bit 10 — Extract text/graphics (copy)
UAP.MODIFY_ASSEMBY         # Bit 11 — Assemble document
UAP.PRINT_HIGH_QUALITY     # Bit 12 — Print high quality

# Combine permissions (bitwise OR)
allowed = UAP.PRINT | UAP.FILL_INTERACTIVE_FORMS

# Deny specific permissions (bitwise NOT)
denied = ~(UAP.MODIFY_DOCUMENT | UAP.EXTRACT_TEXT_GRAPHICS)

# Allow everything
all_permissions = -1  # all bits set

# Deny everything
no_permissions = 0
```

### Permission bit positions

| Bit | Permission |
|---|---|
| 3 | Print |
| 4 | Modify document |
| 5 | Modify annotations |
| 6 | — |
| 7 | — |
| 8 | — |
| 9 | Fill interactive forms |
| 10 | Extract text and graphics |
| 11 | Assemble document |
| 12 | Print high quality |

## Encryption Limitations

- **Incremental updates cannot be encrypted** — `writer.encrypt()` raises `NotImplementedError` if `writer.incremental` is True
- **40-bit RC4 is weak** — easily broken; use AES for real security
- **Permissions can be bypassed** — PDF encryption permissions are advisory; determined users can remove them
- **Owner vs user password** — owner password grants full access; user password respects permissions

## Checking Encryption

```python
reader = PdfReader("document.pdf")

# Check if encrypted
if reader.is_encrypted:
    print("Document is encrypted")

# After decryption
reader.decrypt("password")
print(reader.is_encrypted)  # Still True (encryption info remains)
# But content is now accessible
```

`is_encrypted` returns `True` even after successful decryption (the encryption dictionary remains in the PDF).

## Crypt Providers

```python
from pypdf._crypt_providers import crypt_provider

# Check which crypto provider is active
print(crypt_provider)
# e.g., "cryptography" or "default" (pure Python)
```

pypdf auto-detects available crypto providers. With `cryptography` installed, AES encryption is available.
