# HTML Formats Reference

Detailed reference for HTML output variants, slide frameworks, and self-contained files.

## HTML Output Variants

### Basic HTML

```bash
# HTML5 (default, XHTML polyglot)
pandoc -t html notes.md -o notes.html
pandoc -t html5 notes.md -o notes.html  # same as html

# XHTML 1.0 Transitional
pandoc -t html4 notes.md -o notes.html

# Standalone (full document with <html>, <head>, <body>)
pandoc -s -t html notes.md -o notes.html

# Fragment (no wrapper, just body content)
pandoc -t html notes.md
```

### HTML Variables

| Variable | Description | Example |
|---|---|---|
| `title` | Page title | Document title |
| `author` | Author name | Jane Doe |
| `date` | Document date | 2024-01-15 |
| `lang` | HTML lang attribute | en, de, fr |
| `document-css` | Default CSS (disable with empty) | — |
| `highlight-style` | Syntax highlighting theme | tango, kate, pygments |
| `toc` | Table of contents | true/false |
| `toc-depth` | TOC depth | 3 |
| `number-sections` | Numbered sections | true/false |
| `section-divs` | Wrap in `<section>` tags | true/false |

```bash
# Full standalone HTML with TOC
pandoc -s -t html notes.md \
  --toc \
  --number-sections \
  -V lang=en \
  -o notes.html
```

## Self-Contained HTML

Produce a single HTML file with all resources embedded as `data:` URIs:

```bash
# Embed CSS, images, scripts
pandoc -s -t html notes.md --embed-resources -o notes.html

# Deprecated synonym
pandoc -s -t html notes.md --self-contained -o notes.html
```

**Limitations**:
- Dynamically loaded JavaScript resources cannot be embedded
- MathJax fonts may be missing (use `--katex` instead)
- Some advanced slide features (zoom, speaker notes) may not work offline

### SVG Handling

- Default: SVG images use `<img>` tags with `data:` URIs
- Add class `inline-svg` to the image for inline `<svg>` element insertion
- Inline SVG enables `<use>` elements for deduplication of repeated SVGs

```html
<!-- For inline SVG rendering, add class in markdown -->
![diagram](chart.svg){.inline-svg}
```

### External Resources

Mark resources that should NOT be embedded:

```html
<!-- Leave this link as-is (not downloaded/embedded) -->
<img src="external.png" data-external="1">
```

## Slide Show Formats

Pandoc supports multiple HTML-based slide frameworks. Structure slides with headings or horizontal rules.

### reveal.js

Modern, feature-rich HTML5 slide framework.

```bash
pandoc -t revealjs slides.md -o slides.html
pandoc -t revealjs slides.md --embed-resources -o slides.html
```

**Variables**:
| Variable | Description |
|---|---|
| `revealjs-url` | Base URL for reveal.js | `https://cdn.jsdelivr.net/npm/reveal.js@5` |
| `revealjs-theme` | Slide theme | `white`, `black`, `blood`, `moon` |
| `revealjs-transition` | Transition effect | `default`, `slide`, `convex`, `concave`, `zoom` |
| `revealjs-hash` | Enable URL hash navigation | true/false |
| `revealjs-slideNumber` | Show slide numbers | true/false |
| `revealjs-controlsTutorial` | Controls tutorial | true/false |
| `revealjs-smoothScroll` | Smooth scrolling | true/false |
| `revealjs-smallFontStep` | Font size step | `10` |

### slidy

W3C's simple HTML slide framework.

```bash
pandoc -t slidy slides.md -o slides.html
```

### DZSlides (Dabblet)

HTML5 + JavaScript slides by Richard Rutter.

```bash
pandoc -t dzslides slides.md -o slides.html
```

### S5

Classic slide framework by Rob Crowther.

```bash
pandoc -t s5 slides.md -o slides.html
```

### Slide Structure

```markdown
# Title Slide

Subtitle and author

## Section Heading {#section1}

Content on this slide...

- Point 1
- Point 2

### Sub-heading within section

More detailed content...

---

Manual slide break (use with --slide-level=0)
```

### Slide Options

```bash
# Headings at level 2 create slides
pandoc -t revealjs slides.md --slide-level=2 -o slides.html

# Manual breaks only
pandoc -t revealjs slides.md --slide-level=0 -o slides.html

# Incremental list items (one by one)
pandoc -t revealjs slides.md --incremental -o slides.html
```

## Chunked HTML

Split a document into multiple linked HTML files:

```bash
# Produce zip archive of HTML chunks
pandoc -t chunkedhtml notes.md -o notes.zip

# Produce directory of HTML chunks (no extension = directory)
pandoc -t chunkedhtml notes.md -o notes/
```

Each top-level section becomes a separate HTML file, linked together.

## CSS Styling

```bash
# Link external stylesheet
pandoc -s -t html notes.md -c styles.css -o notes.html

# Multiple stylesheets (applied in order)
pandoc -s -t html notes.md -c base.css -c theme.css -o notes.html

# Remote stylesheet URL
pandoc -s -t html notes.md -c https://example.com/styles.css -o notes.html
```

For PDF via HTML engine, CSS controls the output:

```bash
pandoc -t html -o report.pdf report.md --pdf-engine=weasyprint --css=print.css
```

## HTML-Specific Options

### Section Divs

Wrap sections in `<section>` tags with identifiers on the container rather than the heading:

```bash
pandoc -s -t html notes.md --section-divs -o notes.html
```

For `html4`, uses `<div>` instead of `<section>`.

### Email Obfuscation

Protect email addresses from harvesters:

```bash
# No obfuscation (default)
pandoc -s -t html notes.md -o notes.html

# JavaScript obfuscation
pandoc -s -t html notes.md --email-obfuscation=javascript -o notes.html

# Character references
pandoc -s -t html notes.md --email-obfuscation=references -o notes.html
```

### Title Prefix

```bash
pandoc -s -t html notes.md -T "My Site —" -o notes.html
```

Adds prefix to the `<title>` tag only (not the body title).

### ID Prefix

Prevent identifier collisions when including fragments:

```bash
pandoc -t html notes.md --id-prefix=section1- -o notes.html
```

All identifiers and internal links get the prefix prepended.

### Figure/Table Caption Position

```bash
# Captions above figures
pandoc -s -t html notes.md --figure-caption-position=above -o notes.html

# Captions below tables
pandoc -s -t html notes.md --table-caption-position=below -o notes.html
```

## Math Rendering in HTML

| Option | Description |
|---|---|
| `--mathjax` | Render with MathJax (default for HTML) |
| `--mathjax=url` | Custom MathJax URL |
| `--katex` | Render with KaTeX (faster, no fonts issue with --embed-resources) |
| `--katex=url` | Custom KaTeX URL |
| `--webtex` | Render via web service (CodeCogs) as images |
| `--webtex=url` | Custom webtex URL |
| `--gladtex` | Render via gladtex service |
| `--mhchem` | Enable mhchem support with MathJax/KaTeX |

```bash
# KaTeX for self-contained HTML
pandoc -s -t html notes.md --katex --embed-resources -o notes.html

# MathJax with mhchem
pandoc -s -t html notes.md --mathjax --mhchem -o notes.html
```

## HTML Input Parsing

When reading HTML input, pandoc understands:

- Full documents and fragments
- Semantic HTML5 elements (`<article>`, `<section>`, `<nav>`)
- Tables (including `colspan`/`rowspan`)
- MathML
- Raw JavaScript/CSS
- Data attributes as header attributes

```bash
# HTML → Markdown
pandoc -f html -t markdown page.html -o page.md

# HTML → LaTeX
pandoc -f html -t latex page.html -o page.tex

# Fetch and convert web page
pandoc -f html -t markdown https://example.com/article -o article.md
```
