# Encryption

pypdf supports the PDF standard encryption handler: RC4 and AES algorithms
with various key lengths, up to PDF 2.0.

## Encrypt (writer)

```python
from pypdf import PdfReader, PdfWriter

writer = PdfWriter(clone_from=reader)  # or clone_from="file.pdf"
writer.encrypt("my-secret-password", algorithm="AES-256")
writer.write("out-encrypted.pdf")
```

Signature: `encrypt(user_password, owner_password=None, use_128bit=True,
permissions_flag=ALL_DOCUMENT_PERMISSIONS, *, algorithm=None)`.

- `algorithm` is **keyword-only**; valid values: `"RC4-40"`, `"RC4-128"`,
  `"AES-128"`, `"AES-256-R5"`, `"AES-256"`. Docs recommend `AES-256-R5`.
- Without `algorithm`, the default is **RC4-128** (RC4-40 when
  `use_128bit=False`). RC4 is insecure — prefer AES.
- `owner_password` defaults to the user password.
- `permissions_flag` is a bitfield per PDF 1.7 Table 3.20 (-1 grants
  everything; bit 3 printing, 4 modifying content, 5/6 annotations, 9 form
  fields, 10 text/graphics extraction).
- Not supported on incremental writers (`NotImplementedError`).

## Decrypt (reader)

```python
reader = PdfReader("encrypted-file.pdf")

if reader.is_encrypted:
    result = reader.decrypt("test")   # PasswordType.NONE | .USER | .OWNER

writer = PdfWriter(clone_from=reader)
writer.write("out-decrypted.pdf")
```

`decrypt(password)` returns a `PasswordType` indicating which password
succeeded. Alternatively pass `password=` to the `PdfReader` constructor.
Passing a password to a non-encrypted file raises `PdfReadError`.

## Dependencies

- RC4 works with the base install (pure Python).
- AES needs an extra: `pip install pypdf[crypto]` (cryptography >= 43;
  7.0 dropped cryptography < 43) **or** `pip install pypdf[cryptodome]`
  (pycryptodome).
- `pip install pypdf[full]` installs everything (crypto, image, fonts,
  brotli, RTL text).
- The active crypto provider is available via `pypdf.crypt_provider`.
