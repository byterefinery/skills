# PDF Engines Reference

Pandoc produces PDFs by converting to an intermediate format, then running an external engine. The engine is chosen automatically based on the intermediate format, or specified explicitly with `--pdf-engine`.

## Engine Selection Matrix

| Intermediate format (`-t`) | Default engine | Alternatives |
|---|---|---|
| `latex` (default) | `pdflatex` | `xelatex`, `lualatex`, `latexmk`, `tectonic` |
| `context` | `context` | — |
| `html` | `weasyprint` | `prince`, `wkhtmltopdf`, `pagedjs-cli` |
| `ms` | `groff` | `pdfroff` |
| `typst` | `typst` | — |

## LaTeX-Based PDF Engines

### pdflatex

Default engine. Fast, wide compatibility. Limited to 8-bit fonts unless packages like `inputenc` are used.

```bash
pandoc -o report.pdf report.md --pdf-engine=pdflatex
```

**Pros**: Available in all TeX Live distributions, fast compilation
**Cons**: Limited Unicode support, requires `fontenc`/`inputenc` for non-ASCII

### xelatex

Full Unicode and system font support via `fontspec`. Recommended for documents with non-Latin scripts or custom fonts.

```bash
pandoc -o report.pdf report.md --pdf-engine=xelatex
pandoc -o report.pdf report.md --pdf-engine=xelatex -V mainfont="Noto Serif"
```

**Pros**: Native Unicode, system fonts, excellent CJK support with `xeCJK`
**Cons**: Slower than pdflatex

### lualatex

Lua-based engine with full Unicode. Supports node-level font features and advanced typography.

```bash
pandoc -o report.pdf report.md --pdf-engine=lualatex
pandoc -o report.pdf report.md --pdf-engine=lualatex -V mainfont="Noto Serif"
```

**Pros**: Lua scripting, `lua-ul` for underlining, `selnolig` for ligature control
**Cons**: Slower compilation

### latexmk

Wrapper around pdflatex/xelatex/lualatex that handles multiple passes automatically (for cross-references, bibliographies, tables of contents).

```bash
pandoc -o report.pdf report.md --pdf-engine=latexmk
pandoc -o report.pdf report.md --pdf-engine=latexmk --pdf-engine-opt=-pdflatex
```

**Pros**: Automatic multi-pass, handles aux files
**Cons**: Requires latexmk installed

### tectonic

Modern LaTeX engine with built-in font management and Unicode support. Self-contained (no TeX Live needed).

```bash
pandoc -o report.pdf report.md --pdf-engine=tectonic
```

**Pros**: No TeX Live dependency, modern toolchain
**Cons**: Separate installation required

## HTML-Based PDF Engines

### weasyprint

Open-source CSS paged-media renderer. Converts HTML+CSS to PDF.

```bash
pandoc -t html -o report.pdf report.md --pdf-engine=weasyprint
pandoc -t html -o report.pdf report.md --pdf-engine=weasyprint --css=styles.css
```

**Pros**: No LaTeX needed, CSS styling control
**Cons**: Requires weasyprint (Python), limited print-CSS support

### prince

Commercial HTML-to-PDF engine with excellent CSS paged-media support.

```bash
pandoc -t html -o report.pdf report.md --pdf-engine=prince
```

**Pros**: Best-in-class CSS print support, PDF/A output
**Cons**: Commercial license required

### wkhtmltopdf

Qt WebKit-based converter. Older but still functional.

```bash
pandoc -t html -o report.pdf report.md --pdf-engine=wkhtmltopdf
```

**Pros**: Available in many package managers
**Cons**: Outdated rendering engine, being deprecated

### pagedjs-cli

JavaScript-based paged media renderer using Paged.js library.

```bash
pandoc -t html -o report.pdf report.md --pdf-engine=pagedjs-cli
```

**Pros**: Modern CSS support, JavaScript ecosystem
**Cons**: Requires Node.js and pagedjs-cli

## Other PDF Engines

### context (ConTeXt)

Alternative typesetting system to LaTeX.

```bash
pandoc -t context -o report.pdf report.md --pdf-engine=context
```

### groff / pdfroff

UNIX roff formatting system. Minimal but functional.

```bash
pandoc -t ms -o manual.pdf manual.md --pdf-engine=groff
pandoc -t ms -o manual.pdf manual.md --pdf-engine=pdfroff
```

### typst

Modern typesetting language, fast compilation, built-in Unicode.

```bash
pandoc -t typst -o report.pdf report.md --pdf-engine=typst
```

**Pros**: Very fast, modern design, no TeX Live needed
**Cons**: Separate installation, newer ecosystem

## Passing Options to Engines

Use `--pdf-engine-opt` to pass arguments through:

```bash
# Shell escape for write18 (required by some packages)
pandoc -o report.pdf report.md --pdf-engine=xelatex --pdf-engine-opt=-shell-escape

# Specify output directory for aux files
pandoc -o report.pdf report.md --pdf-engine=latexmk --pdf-engine-opt=-outdir=build

# Multiple engine options
pandoc -o report.pdf report.md --pdf-engine=lualatex \
  --pdf-engine-opt=-shell-escape \
  --pdf-engine-opt=-interaction=nonstopmode
```

## LaTeX Package Requirements (PDF via pdflatex)

These packages must be available in TeX Live:

**Required**: `amsfonts`, `amsmath`, `lm`, `unicode-math`, `iftex`, `fancyvrb`, `longtable`, `booktabs`, `xcolor`, `soul`, `bookmark`

**Conditional**:
- `graphicx` — if document contains images
- `geometry` — if `geometry` variable set
- `setspace` — if `linestretch` variable set
- `babel` — if `lang` variable set
- `fontspec` — required for xelatex/lualatex
- `listings` — if `--listings` used
- `multirow` — if tables have multi-row cells
- `csquotes` — if `csquotes` variable set
- `biblatex`/`biber` — if citations used
- `cancel` — if `\cancel` math commands used

**Optional quality improvements**: `upquote`, `microtype`, `parskip`, `xurl`, `footnotehyper`

## Debugging PDF Output

```bash
# Inspect the intermediate LaTeX
pandoc -s -o report.tex report.md

# Compile manually to see errors
pdflatex report.tex
xelatex report.tex

# Verbose engine output
pandoc -v -o report.pdf report.md
```

## PDF Variables (LaTeX)

Control PDF appearance via `-V` variables:

```bash
# Document class and options
pandoc -o report.pdf report.md -V documentclass=report

# Fonts
pandoc -o report.pdf report.md -V mainfont="Noto Serif" -V sansfont="Noto Sans"

# Page geometry
pandoc -o report.pdf report.md -V geometry:margin=1in

# Line spacing
pandoc -o report.pdf report.md -V linestretch=1.5

# PDF metadata
pandoc -o report.pdf report.md -V title="My Report" -V author="Jane Doe"
```
