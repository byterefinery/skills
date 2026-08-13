# Command-Line Reference

## Switch Types

Ghostscript switches use a prefix letter to indicate the argument type:

| Prefix | Type | Example |
|--------|------|---------|
| `-d` | Boolean or integer | `-dNOPAUSE`, `-dFirstPage=1` |
| `-d` (float) | Floating point | `-r300`, `-dCompatibilityLevel=1.5` |
| `-s` | String | `-sDEVICE=png16m`, `-sOutputFile=out.pdf` |
| `-I` | Path (search directory) | `-I/usr/share/fonts` |
| `-P` | Library path prefix | `-P-` (disable library search) |
| `-c` | Inline PostScript code | `-c "save"` |
| `-f` | Read and execute file | `-f input.ps` |
| `-q` | Quiet mode (no banner) | `-q` |
| `--` | End of options, treat rest as filenames | `-- file-with-dashes.ps` |

## Boolean Flags

Boolean flags are set with `-d<NAME>` (true) or `-d<NAME>=false` (explicit false).

### Execution Control

- `NOPAUSE` — Don't pause between pages. Essential for batch processing.
- `BATCH` — Exit after processing all files (don't enter interactive mode).
- `NODISPLAY` — Suppress X11 display even if available.
- `NORASH` — Disable the built-in rash (resource archive) filesystem.
- `NOGPDLSAVE` — Prevent GhostPDL from saving state between jobs.
- `QUIET` — Suppress non-error messages (same as `-q`).
- `NODISCCOMMENT` — Disable DSC comment parsing.
- `NOPLATFONTS` — Don't search platform-specific font directories.
- `NOCACHE` — Disable font caching.
- `NOCOMPAT` — Disable compatibility mode for old PostScript.
- `NOINTERPOLATE` — Disable image interpolation (faster, lower quality).
- `NOPAUSE` + `BATCH` — Standard combination for scripting.

### PDF Output Control

- `PDFSETTINGS=/ebook` — Preset for PDF optimization (not a boolean, uses `-d`).
- `CompatibilityLevel=1.5` — Target PDF version (1.0 through 2.0).
- `Optimize=true` — Enable PDF optimization.
- `CompressPages=true` — Flate-compress page streams.
- `UseFlateCompression=true` — Use Flate for general compression.
- `EmbedAllFonts=true` — Embed all fonts in output.
- `SubsetFonts=true` — Only embed used glyphs.
- `MaxSubsetPct=100` — Maximum percentage of font to subset before embedding all.
- `DetectBlends=true` — Detect and optimize blend modes.
- `PreserveCopyPage=true` — Preserve copy page operators.
- `PassThroughJPEGImages=true` — Pass through existing JPEGs without re-encoding.
- `PassThroughJPXImages=true` — Pass through existing JPEG 2000 images.

### Security

- `SAFER` — Restrict file access to input files and OutputFile.
- `PARANOIDSAFER` — Even stricter: no `run`, no `file`, no `system`.
- `UNSAFER` — Explicitly disable safer mode (counter `-dSAFER`).
- `NOOUTDEV` — Disable output device access.

### Rendering

- `INTERPOLATE=true` — Enable image interpolation (default: true).
- `USEKERNDICTIONARY=true` — Use Adobe Kern pairs.
- `USEKTOTAL=true` — Use Total kerning.
- `DITHERPPI=300` — Dithering resolution.
- `USECOLORKEY=true` — Use color key transparency.
- `USEFASTCOLORIMAGEREDUCTION=true` — Faster color image reduction.
- `GRAYSCALEREDUCTION=true` — Enable grayscale reduction.
- `ANTIALIAS=true` — Enable anti-aliasing.
- `USEANTIALIASEDTEXT=true` — Anti-alias text rendering.
- `TEXTHOLD=true` — Hold text for optimization.
- `USECIDFONTS=true` — Use CID fonts.

### Page Control

- `FirstPage=N` — Start processing from page N (1-indexed).
- `LastPage=N` — Stop processing at page N.
- `PDFFitPage=true` — Scale content to fit the page.
- `AutoRotatePages=/PageByPage` — Auto-rotate pages based on content.
- `AutoRotatePages=/None` — Disable auto-rotation.
- `AutoRotatePages=/All` — Rotate all pages uniformly.

### Memory

- `MaxBitmap=N` — Maximum bitmap size in bytes (default: system-dependent).
- `MaxRestartBacktrack=N` — Maximum backtrack depth for restartable operations.
- `VirtualMemory=N` — Virtual memory allocation size.

## String Parameters

### `-sDEVICE=name`

Select the output device. Must appear before the first input file. See [02-output-devices](references/02-output-devices.md) for the full list.

### `-sOutputFile=path`

Output file path. Special values:

- `-` or `%stdout%` — Write to stdout
- `%pipe%command` — Pipe to external command
- `page_%d.png` — Numbered output (one per page)
- `page_%03d.png` — Zero-padded numbering

### `-sPAPERSIZE=name`

Standard paper sizes: `letter`, `legal`, `ledger`, `a0` through `a10`, `b0` through `b10`, `executive`, `folio`, `government-letter`, `government-legal`, `tabloid`, `statement`, `10x14`, `11x17`, `a3`, `a4`, `a5`, etc.

### `-sOutputProfile=path`

ICC profile path for color management (relative to GS search path or absolute).

### `-sColorConversionStrategy=name`

- `LeaveColorUnchanged` — Keep source color spaces
- `CMYK` — Convert to CMYK
- `Gray` — Convert to grayscale
- `RGB` — Convert to RGB

### `-sPDFPassword=string`

Password for encrypted PDF input.

### `-sOCRLanguage=lang`

Tesseract language(s) for OCR devices. Multiple: `eng+deu`.

## Path Parameters

### `-Ipath`

Add a directory to the search path. Can be used multiple times. Directories are searched in order given, then the default paths.

```bash
gs -I/usr/share/fonts -I./myfonts -sDEVICE=pdfwrite -sOutputFile=out.pdf input.ps
```

### `-sFONTPATH=path`

Set font search path (colon-separated on Unix, semicolon on Windows).

```bash
gs -sFONTPATH=/usr/share/fonts:/opt/fonts -sDEVICE=pdfwrite -sOutputFile=out.pdf input.ps
```

## Resolution

### `-rvalue` or `-rxry`

Set output resolution in DPI.

```bash
gs -r300              # 300 DPI both axes
gs -r300x150           # 300 horizontal, 150 vertical
gs -dNOPAUSE -dBATCH -sDEVICE=png16m -r600 -sOutputFile=out.png input.pdf
```

## PostScript Execution

### `-c "code"`

Execute PostScript code inline. Can be used multiple times.

```bash
gs -c "save" -f setup.ps -c "restore" -f main.ps
```

### `-f file`

Read and execute a file. Unlike positional arguments, `-f` explicitly marks a file.

```bash
gs -c "(Hello) print" -f input.ps
```

### Combining `-c` and `-f`

```bash
# Pre-configure pdfwrite, then process file
gs -dBATCH -dNOPAUSE -sDEVICE=pdfwrite \
   -c "<< /EmbedAllFonts true /SubsetFonts true >> setdistillerparams" \
   -f input.ps -sOutputFile=out.pdf
```

## N-Up Parameters

Set via pdfmark or PostScript:

```bash
# Via pdfmark
gs -dBATCH -dNOPAUSE -sDEVICE=pdfwrite \
   -c "[/PerPage << /NumPagesAcross 2 /NumParamsDown 2 >> /setpagedevice pdfmark]" \
   -f input.pdf -sOutputFile=imposed.pdf
```

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `GS_DEVICE` | Default output device |
| `GS_FONTPATH` | Font search path |
| `GS_LIB` | Additional library search path |
| `GS_LIB64` | 64-bit library search path |
| `GSCOLORDEVICE` | Default color device |
| `GS_DLL` | Path to Ghostscript DLL (Windows) |
| `GS_USE_SYSTEM_FONTS` | Use system fonts (1/0) |
| `HOME` | User home directory (for ~/.ghostscript) |
