# Security — -dSAFER, -dPARANOIDSAFER, Sandboxing

## Overview

Ghostscript executes PostScript code, which can read/write files, execute system commands, and access network resources. Security modes restrict these capabilities.

## Security Levels

### No Security (Default)

By default, Ghostscript runs with full system access. PostScript code can:

- Read and write any file
- Execute system commands via `(cmd) system`
- Access network resources
- Load and execute arbitrary code
- Modify system dictionaries

### -dSAFER

Restricts file and system access:

- **File read:** Only input files and files in `-I` directories
- **File write:** Only the file specified by `-sOutputFile`
- **System commands:** Disabled
- **`run` operator:** Disabled
- **`file` operator:** Restricted
- **`rmfile` operator:** Disabled
- **`renfile` operator:** Disabled
- **`mkdir` operator:** Disabled

```bash
gs -dSAFER -dBATCH -dNOPAUSE -sDEVICE=pdfwrite \
   -sOutputFile=out.pdf input.ps
```

### -dPARANOIDSAFER

The strictest security mode. Everything in `-dSAFER` plus:

- **No `run` operator** at all
- **No `file` operator** at all
- **No `system` operator** at all
- **No `.runlibfile`** — can't load library files
- **No disk-based resources** — only compiled-in resources
- **No user-defined procedures** that access files

```bash
gs -dPARANOIDSAFER -dBATCH -dNOPAUSE -sDEVICE=pdfwrite \
   -sOutputFile=out.pdf input.ps
```

### -dUNSAFER

Explicitly disables safer mode (counters `-dSAFER`):

```bash
gs -dSAFER -dUNSAFER -dBATCH -dNOPAUSE -sDEVICE=pdfwrite \
   -sOutputFile=out.pdf input.ps
# Equivalent to running without -dSAFER
```

## File Access Control

### Allowed Read Paths

```bash
# Specify allowed directories
gs -dSAFER -I/usr/share/fonts -I./trusted \
   -dBATCH -dNOPAUSE -sDEVICE=pdfwrite \
   -sOutputFile=out.pdf input.ps

# The -I flag adds directories to the search path
# Files in these directories can be read in SAFER mode
```

### Allowed Write Paths

```bash
# Only OutputFile is writable in SAFER mode
gs -dSAFER -dBATCH -dNOPAUSE -sDEVICE=pdfwrite \
   -sOutputFile=/tmp/output.pdf input.ps

# Multiple output files with %d
gs -dSAFER -dBATCH -dNOPAUSE -sDEVICE=png16m \
   -sOutputFile=/tmp/page_%d.png input.pdf
```

## System Command Restrictions

### Disabled in -dSAFER

```postscript
% These fail in -dSAFER mode:
(ls) system          % Execute shell command
(ls) run             % Run external program
(filename) (r) file  % Open arbitrary file
(filename) rmfile    % Delete file
(old, new) renfile   % Rename file
(dir) mkdir          % Create directory
```

### Workaround for Legitimate Needs

```bash
# If a PostScript file needs to read a font, add its directory:
gs -dSAFER -I/path/to/fonts -dBATCH -dNOPAUSE \
   -sDEVICE=pdfwrite -sOutputFile=out.pdf input.ps

# If you need system commands, don't use -dSAFER:
gs -dBATCH -dNOPAUSE -sDEVICE=pdfwrite \
   -sOutputFile=out.pdf input.ps
```

## PostScript Sandboxing

### Writing Safe PostScript

```postscript
% Safe: uses only built-in operators
/Helvetica findfont 12 scalefont setfont
72 720 moveto (Hello, World!) show showpage

% Unsafe: file operations
(filename) (r) file      % Opens file
(filename) (w) file      % Creates file
(cmd) system             % Executes command
```

### Checking Security Mode

```postscript
% Check if running in SAFER mode
systemdict /saferset known {
  (% Running in SAFER mode\n) print
} if

% Check available permissions
systemdict /runexecknownknown known {
  (% Can execute system commands\n) print
} if
```

## Trust Levels

### Trusted Code

Some PostScript code needs elevated privileges. Ghostscript distinguishes between:

- **System initialization files** (`Resource/Init/`) — run with full privileges
- **Library files** (`lib/`) — run with full privileges
- **User input files** — run with current security restrictions

### `.forcedefaultprinting`

```postscript
% Some operations require .forcedefaultprinting
% This is only available in non-SAFER mode
systemdict /.forcedefaultprinting known
```

## Environment Variables

| Variable | Security Impact |
|----------|----------------|
| `GS_LIB` | Adds to search path (readable in SAFER) |
| `GS_FONTPATH` | Font paths (readable in SAFER) |
| `GS_DEVICE` | Default device (no security impact) |

## Common Security Errors

### File Access Errors

```
Error: /invalidfileaccess in -- run --
Operand stack:
   (filename)
   (r)
```

**Fix:** Add the file's directory to `-I` paths, or don't use `-dSAFER`.

### System Command Errors

```
Error: /invalidaccess in -- system --
Operand stack:
   (ls)
```

**Fix:** Remove `-dSAFER` or `-dPARANOIDSAFER`, or rewrite the PostScript to not use `system`.

### Library Loading Errors

```
Error: /invalidfileaccess in -- .runlibfile --
```

**Fix:** In `-dPARANOIDSAFER`, library files can't be loaded from disk. Use `-dSAFER` instead, or compile the library into the binary.

## Best Practices

### For Server Deployments

```bash
# Always use -dSAFER for untrusted input
gs -dSAFER -dNOPAUSE -dBATCH -sDEVICE=pdfwrite \
   -sOutputFile=/var/output/out.pdf \
   -I/var/trusted/fonts \
   input.ps

# Use -dPARANOIDSAFER for maximum security
gs -dPARANOIDSAFER -dNOPAUSE -dBATCH -sDEVICE=pdfwrite \
   -sOutputFile=/var/output/out.pdf \
   input.ps
```

### For Development

```bash
# Don't use -dSAFER during development
gs -dBATCH -dNOPAUSE -sDEVICE=pdfwrite \
   -sOutputFile=out.pdf input.ps

# Add -dSAFER before deploying
```

### For PDF Processing

```bash
# PDF input is generally safe (no executable code in most PDFs)
# But some PDFs contain JavaScript or PostScript
gs -dSAFER -dBATCH -dNOPAUSE -sDEVICE=pdfwrite \
   -dPDFSETTINGS=/ebook \
   -sOutputFile=out.pdf input.pdf
```

## Gotchas

- **`-dSAFER` breaks some legitimate PostScript** — files that use `(file) (r) file` to load external resources will fail. Add those directories to `-I`.
- **`ps2pdf` uses `-dSAFER` by default** — the `ps2pdf` wrapper enables `-dSAFER`. If your PostScript fails with `ps2pdf` but works with `gs`, try `ps2pdfwr` directly or add `-dUNSAFER`.
- **`-dPARANOIDSAFER` is very restrictive** — it prevents loading any disk-based resources. Use only when processing completely untrusted input.
- **PDF JavaScript isn't executed by default** — Ghostscript doesn't run PDF JavaScript unless explicitly requested. This is a security feature.
- **`-I` directories are trusted** — any PostScript files in `-I` directories can be loaded and executed. Don't point `-I` at untrusted directories.
- **Output file is always writable** — even in `-dSAFER`, the `-sOutputFile` path is writable. Ensure the output directory is controlled.
- **Environment variables can affect security** — `GS_LIB` and `GS_FONTPATH` add to the search path. In containerized deployments, ensure these are set correctly.
- **`-P-` disables library search** — the `-P-` flag (used by `ps2pdfwr`) prevents searching default library paths, adding an extra layer of security.
