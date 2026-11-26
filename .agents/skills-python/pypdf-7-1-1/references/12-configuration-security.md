# Configuration and Security

pypdf provides secure defaults plus a global configuration for tuning
security limits. Internally the configuration relies on `contextvars`, so
scoped changes do not leak across threads.

## API

From `pypdf` top level:

```python
from pypdf import (
    Configuration,
    PdfReader,
    apply_configuration,
    get_configuration,
    overwrite_configuration,
)

# Scoped: changed values reset when exiting the context manager
with apply_configuration(maximum_declared_stream_length=10_000):
    reader = PdfReader("example.pdf")
    ...

# Global: persists for the process
overwrite_configuration(maximum_declared_stream_length=5_000)

current = get_configuration()   # current Configuration instance
```

`Configuration` is a class describing the available limits and their
defaults; `apply_configuration(**kwargs)` is a context manager,
`overwrite_configuration(**kwargs)` mutates globally, and
`get_configuration()` returns the current values.

## Reader limits (PdfReader)

Passed as keyword-only constructor arguments:

| Parameter | Default | Meaning |
|---|---|---|
| `root_object_recovery_limit` | `10_000` | Max objects read during root-object recovery in non-strict mode; `None` disables |
| `xref_stream_maximum_entries` | `2_000_000` | Max cross-reference stream entries |

```python
reader = PdfReader("file.pdf", root_object_recovery_limit=42)
```

## Writer limits (PdfWriter)

For incremental cloning (incremental mode or cloning from a reader):

| Parameter | Default | Meaning |
|---|---|---|
| `incremental_clone_object_count_limit` | `500_000` | Max objects read during cloning; `None` disables |
| `incremental_clone_object_id_limit` | `1_000_000` | Max object ID read during cloning; `None` disables |

The currently preferred way to apply reader limits to a writer is to
initialize the writer from the reader:
`PdfWriter(clone_from=PdfReader("file.pdf", root_object_recovery_limit=42))`.

## Other security-relevant behavior

- 7.0 made file identifiers non-deterministic and blocked non-increasing
  offsets in object streams; 7.1.1 added further limits (inline image size,
  page-label size, cross-reference stream work/memory).
- XMP is parsed with `xml.minidom`; modern Expat builds are not vulnerable
  to the usual entity-expansion attacks.
- RC4/AES-in-ECB/MD5 usage in encryption is required by the PDF standard for
  compatibility and is not a pypdf defect.
- Exceptions raised by pypdf are a known, documented set; catching them is
  the library user's responsibility in services.
