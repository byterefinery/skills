# ImageMagick 7.1.2-26 — Security Policies and Configuration

## Table of Contents

- [Security Policy (policy.xml)](#security-policy-policyxml)
- [Policy Domains](#policy-domains)
- [Built-in Policy Presets](#built-in-policy-presets)
- [Resource Limits](#resource-limits)
- [Delegates](#delegates)
- [Configuration Files](#configuration-files)
- [Security Best Practices](#security-best-practices)

---

## Security Policy (policy.xml)

Located at `/etc/ImageMagick-7/policy.xml` or `/usr/local/etc/ImageMagick-7/policy.xml`. Controls which operations, formats, and paths are allowed.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE policymap [
<!ELEMENT policymap (policy)*>
<!ELEMENT policy EMPTY>
<!ATTLIST policy domain NMTOKEN #REQUIRED>
<!ATTLIST policy name NMTOKEN #IMPLIED>
<!ATTLIST policy pattern CDATA #IMPLIED>
<!ATTLIST policy rights NMTOKEN #IMPLIED>
<!ATTLIST policy stealth NMTOKEN #IMPLIED>
<!ATTLIST policy value CDATA #IMPLIED>
]>
<policymap>
  <!-- Restrict PDF coder -->
  <policy domain="coder" rights="none" pattern="PDF" />

  <!-- Allow only read for MSL, SVG, URL -->
  <policy domain="module" rights="read" pattern="{MSL,MVG,PS,SVG,TXT,URL,XPS}" />

  <!-- Block all delegates -->
  <policy domain="delegate" rights="none" pattern="*" />

  <!-- Resource limits -->
  <policy domain="resource" name="memory" value="256MiB" />
  <policy domain="resource" name="disk" value="1GiB" />
</policymap>
```

Rules are processed in order. First match wins.

---

## Policy Domains

| Domain | Purpose |
|---|---|
| `system` | System-wide settings (font, shred, max-memory-request, symlink, svg) |
| `delegate` | External delegate programs (Ghostscript, etc.) |
| `coder` | Image format coders (JPEG, PNG, PDF, etc.) |
| `filter` | Loadable image filters |
| `module` | Image modules (MSL, SVG, URL, etc.) |
| `path` | File system path access |
| `resource` | Resource limits (memory, disk, time, etc.) |
| `cache` | Pixel cache settings |

### Rights

| Right | Description |
|---|---|
| `none` | No access |
| `read` | Read only |
| `write` | Write only |
| `execute` | Execute (for delegates) |
| `read \| write` | Read and write |

---

## Built-in Policy Presets

ImageMagick 7.1.2-26 ships with four presets in `config/`:

### Open (`policy-open.xml`)

Default. Broad access. Suitable for trusted environments (Docker, firewalled systems).

### Limited (`policy-limited.xml`)

Moderate restrictions. Limits resource usage and restricts some coders.

### Secure (`policy-secure.xml`)

Strict. Blocks risky coders (MSL, SVG, URL), restricts delegates, sets resource limits.

### Websafe (`policy-websafe.xml`)

Maximum security for public-facing web applications.

Key restrictions:
- Only web-safe formats: BMP, GIF, JPEG, PNG, TIFF, WEBP
- No delegates (Ghostscript blocked)
- No filters
- No stdin/stdout
- No indirect reads (`@*` paths blocked)
- No sensitive paths (`/etc/*`)
- No relative paths with `..`
- Resource limits: 768MiB memory, 2GiB disk, 4KP max dimensions, 60s time limit
- Memory anonymization enabled
- Buffer shredding on free

---

## Resource Limits

Set via policy or command-line `-limit`.

| Resource | Description | Default (websafe) |
|---|---|---|
| `memory` | Max heap for pixel cache | 768MiB |
| `map` | Max memory-mapped cache | 2GiB |
| `disk` | Max disk for pixel cache | 2GiB |
| `file` | Max open cache files | 768 |
| `thread` | Max parallel threads | 2 |
| `time` | Max processing time | 60s |
| `area` | Max width×height in memory | 8KP |
| `width` | Max image width | 4KP |
| `height` | Max image height | 4KP |
| `list-length` | Max image sequence length | 16 |
| `throttle` | CPU yield interval (ms) | — |
| `dynamic-throttle` | Dynamic CPU yielding | true |
| `temporary-path` | Temp file directory | — |

Use SI prefixes: `KB`, `MB`, `MiB`, `GB`, `GiB`, `KP` (kilo-pixels), `MP` (mega-pixels), `GP` (giga-pixels), `TP` (tera-pixels).

### Command-Line Override

```bash
magick convert -limit memory 2GiB -limit disk 10GiB input.jpg output.png
```

Note: Policy limits are hard maximums. `-limit` cannot exceed policy values.

---

## Delegates

External programs/libraries used for format support. Check with:

```bash
magick identify -list delegate
```

Common delegates and security concerns:

| Delegate | Risk | Notes |
|---|---|---|
| Ghostscript | High | PDF/EPS processing; can execute arbitrary code via crafted PDFs |
| RSVG | Medium | SVG rendering; SVG can contain external references |
| FFmpeg | Medium | Video processing |
| dcraw | Low | Camera RAW processing |
| curl | Medium | URL fetching |

Block all delegates:
```xml
<policy domain="delegate" rights="none" pattern="*" />
```

---

## Configuration Files

| File | Purpose |
|---|---|
| `policy.xml` | Security policy |
| `delegates.xml` | Delegate command definitions |
| `type.xml` | Font definitions |
| `coders.xml` | Coder configuration |
| `colors.xml` | Named color definitions |
| `locale.xml` | Translation strings |
| `log.xml` | Logging configuration |
| `thresholds.xml` | Auto-threshold settings |

Typical locations:
- System: `/etc/ImageMagick-7/`
- Local: `/usr/local/etc/ImageMagick-7/`
- Build: `config/` in source tree

---

## Security Best Practices

### For Web Applications

1. Use `websafe` or `secure` policy preset
2. Block PDF, MSL, SVG, URL coders
3. Block all delegates (especially Ghostscript)
4. Set resource limits (memory, disk, time, dimensions)
5. Block stdin/stdout and indirect reads
6. Block sensitive paths
7. Enable memory anonymization
8. Enable buffer shredding

### For Processing Untrusted Images

```xml
<policymap>
  <!-- Block dangerous coders -->
  <policy domain="coder" rights="none" pattern="PDF" />
  <policy domain="coder" rights="none" pattern="EPDF" />
  <policy domain="coder" rights="none" pattern="PS" />
  <policy domain="coder" rights="none" pattern="EPS" />
  <policy domain="coder" rights="none" pattern="MSL" />
  <policy domain="coder" rights="none" pattern="MVG" />
  <policy domain="coder" rights="none" pattern="SVG" />
  <policy domain="coder" rights="none" pattern="URL" />
  <policy domain="coder" rights="none" pattern="TEXT" />
  <policy domain="coder" rights="none" pattern="XMPS" />

  <!-- Block delegates -->
  <policy domain="delegate" rights="none" pattern="*" />

  <!-- Block filters -->
  <policy domain="filter" rights="none" pattern="*" />

  <!-- Block indirect reads -->
  <policy domain="path" rights="none" pattern="@*" />
  <policy domain="path" rights="none" pattern="|*" />
  <policy domain="path" rights="none" pattern="-" />

  <!-- Resource limits -->
  <policy domain="resource" name="memory" value="512MiB" />
  <policy domain="resource" name="disk" value="1GiB" />
  <policy domain="resource" name="time" value="30" />
  <policy domain="resource" name="width" value="4KP" />
  <policy domain="resource" name="height" value="4KP" />
</policymap>
```

### Checking Current Policy

```bash
magick identify -list policy
magick identify -list delegate
magick identify -list resource
```

### Validating Policy

Use the [ImageMagick Security Evaluator](https://imagemagick-secevaluator.doyensec.com/) to validate your policy configuration.

### Common Vulnerabilities

- **Ghostscript RCE**: Crafted PDFs can execute arbitrary commands. Block PDF coder or restrict Ghostscript delegate.
- **SVG entity injection**: SVG files can reference external entities. Block SVG coder or restrict.
- **MSL script execution**: MSL files can execute arbitrary ImageMagick operations. Block MSL coder.
- **URL fetch**: URL coder can fetch arbitrary URLs. Block URL coder.
- **Resource exhaustion**: Large images or sequences can exhaust memory/disk. Set resource limits.
- **Path traversal**: Indirect reads (`@`, `|`, `%`) can access arbitrary files. Block with path policies.
