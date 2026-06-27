# LaTeX, ConTeXt, and typst Reference

Detailed reference for LaTeX, ConTeXt, Beamer slides, and typst conversions.

## LaTeX Output

### Basic Conversions

```bash
# Markdown → LaTeX (standalone document)
pandoc -s -t latex notes.md -o notes.tex

# Markdown → LaTeX (fragment, no document wrapper)
pandoc -t latex notes.md -o notes.tex

# LaTeX → HTML (bi-directional)
pandoc -f latex -t html paper.tex -o paper.html

# LaTeX → Markdown (bi-directional)
pandoc -f latex -t markdown paper.tex -o paper.md

# LaTeX → PDF (via pandoc's PDF pipeline)
pandoc -f latex -o paper.pdf paper.tex

# HTML → LaTeX (bi-directional)
pandoc -f html -t latex page.html -o page.tex
```

### Document Classes and Variables

```bash
# Specify document class
pandoc -s -t latex notes.md -V documentclass=report -o notes.tex

# Common classes: article, report, book, memoir, letter
pandoc -s -t latex notes.md -V documentclass=book -o book.tex

# Class options
pandoc -s -t latex notes.md -V documentclass=report -V classoption=draft -o notes.tex

# Multiple class options
pandoc -s -t latex notes.md -V classoption="11pt,a4paper,twoside" -o notes.tex
```

### Layout Variables

| Variable | Description | Example |
|---|---|---|
| `documentclass` | LaTeX document class | `article`, `report`, `book` |
| `classoption` | Class options | `11pt`, `a4paper`, `twoside` |
| `geometry` | Page geometry (geometry package) | `margin=1in`, `letterpaper` |
| `linestretch` | Line spacing (setspace package) | `1.5`, `2.0` |
| `fontsize` | Base font size | `10pt`, `11pt`, `12pt` |
| `lang` | Language (babel package) | `english`, `german`, `norsk` |
| `leqno` | Left-aligned equation numbers | — |
| `urlstyle` | URL formatting | `rm`, `sf`, `tt` |
| `colorlinks` | Colored hyperlinks | true/false |
| `linkcolor` | Color of internal links | `red`, `blue` |
| `citecolor` | Color of citation links | `green` |
| `urlcolor` | Color of URL links | `cyan` |
| `toccolor` | Color of TOC links | `purple` |

### Font Variables (xelatex/lualatex)

```bash
# Main font (serif)
pandoc -s -t latex notes.md -V mainfont="Noto Serif" -o notes.tex

# Sans-serif and monospace fonts
pandoc -s -t latex notes.md \
  -V mainfont="Noto Serif" \
  -V sansfont="Noto Sans" \
  -V monofont="Noto Mono" \
  -o notes.tex

# CJK fonts (with xelatex)
pandoc -s -t latex notes.md -V CJKmainfont="Noto Serif CJK SC" -o notes.tex
```

### Top-Level Division Control

```bash
# Auto-detect (default): heuristics choose section/chapter/part
pandoc -s -t latex notes.md -o notes.tex

# Force top-level headings as sections
pandoc -s -t latex notes.md --top-level-division=section -o notes.tex

# Force as chapters (requires book/report/memoir class)
pandoc -s -t latex notes.md --top-level-division=chapter -o notes.tex

# Force as parts
pandoc -s -t latex notes.md --top-level-division=part -o notes.tex
```

When `documentclass` is `report`, `book`, or `memoir`, `--top-level-division=chapter` is implied.

### Numbered Sections

```bash
# Enable section numbering
pandoc -s -t latex notes.md --number-sections -o notes.tex

# With custom offset
pandoc -s -t latex notes.md --number-sections --number-offset=1,4 -o notes.tex
```

Sections with class `unnumbered` are never numbered, even with `--number-sections`.

### Code Highlighting

```bash
# Pygments-based highlighting (default)
pandoc -s -t latex code.md -o code.tex

# Idiomatic highlighting (listings package)
pandoc -s -t latex code.md --syntax-highlighting=idiomatic -o code.tex

# Default theme
pandoc -s -t latex code.md --syntax-highlighting=default -o code.tex

# No highlighting
pandoc -s -t latex code.md --syntax-highlighting=none -o code.tex
```

### LaTeX-Specific Extensions

```bash
# Enable smart typography in LaTeX input
pandoc -f latex+smart -t html paper.tex

# Auto-identifiers from LaTeX section commands
pandoc -f latex+auto_identifiers -t markdown paper.tex
```

## Beamer Slides

### Creating Beamer Presentations

```bash
# Markdown → Beamer LaTeX
pandoc -t beamer slides.md -o slides.tex

# Compile to PDF
pandoc -t beamer -o slides.pdf slides.md --pdf-engine=xelatex

# With custom theme
pandoc -t beamer slides.md -V theme=Madrid -o slides.tex
```

### Beamer Structure

```markdown
# Title Slide {#title-slide .title-slide}

Subtitle here
Author Name

## Section Heading

Content on this slide...

- Bullet point
- Another point

### Sub-heading within section

More content...

---

Manual slide break
```

### Beamer Variables

| Variable | Description |
|---|---|
| `theme` | Beamer theme name | `Madrid`, `Berlin`, `default` |
| `colortheme` | Color theme | `dolphin`, `beaver`, `orchid` |
| `fonttheme` | Font theme | `structurebold`, `professionalfonts` |
| `innertheme` | Inner theme | `rounded`, `miniframes`, `trees` |
| `outertheme` | Outer theme | `miniframes`, `smoothbars`, `sidebar` |
| `aspectratio` | Slide aspect ratio | `169`, `1610`, `43` |
| `beameroption` | Extra beamer options | `handout`, `compress` |

```bash
# Full theme customization
pandoc -t beamer slides.md \
  -V theme=Madrid \
  -V colortheme=dolphin \
  -V fonttheme=structurebold \
  -V aspectratio=169 \
  -o slides.tex
```

### Beamer Slide Level

```bash
# Headings at level 2 create slides (default auto-detect)
pandoc -t beamer slides.md --slide-level=2 -o slides.tex

# Top-level headings = parts, second-level = sections
pandoc -t beamer slides.md --top-level-division=part -o slides.tex
```

Incremental lists: `--incremental` makes list items appear one by one.

## ConTeXt Output

### Basic Conversions

```bash
# Markdown → ConTeXt
pandoc -t context notes.md -o notes.tex

# ConTeXt → HTML (bi-directional)
pandoc -f context -t html document.tex -o document.html

# ConTeXt → PDF
pandoc -t context -o notes.pdf notes.md --pdf-engine=context
```

### ConTeXt Variables

| Variable | Description |
|---|---|
| `papersize` | Paper size | `A4`, `letter`, `A5` |
| `layout` | Layout settings | `arranging=on` |
| `textwidth` | Text width | `12cm` |
| `margin` | Margins | `2.5cm` |
| `fontsize` | Font size | `10pt`, `12pt` |
| `mainfont` | Main font | `Noto Serif` |
| `sansfont` | Sans-serif font | `Noto Sans` |
| `monofont` | Monospace font | `Noto Mono` |
| `interlinespace` | Line spacing | `1.4ex` |
| `lang` | Language | `en`, `nl`, `de` |

## typst Output

### Basic Conversions

```bash
# Markdown → typst
pandoc -t typst notes.md -o notes.typ

# typst → PDF
pandoc -t typst -o notes.pdf notes.md --pdf-engine=typst

# typst → HTML
pandoc -f typst -t html document.typ -o document.html
```

### typst Variables

| Variable | Description |
|---|---|
| `papersize` | Paper size | `a4`, `letter` |
| `page-width` | Page width | `170mm` |
| `page-height` | Page height | `230mm` |
| `text-align` | Text alignment | `justify`, `left` |
| `fill-page` | Fill page with content | true/false |
| `first-font` | Serif font | `Noto Serif` |
| `sans-font` | Sans-serif font | `Noto Sans` |
| `mono-font` | Monospace font | `Noto Mono` |
| `emph-font` | Italic font variant | — |
| `strong-font` | Bold font variant | — |
| `font-size` | Base font size | `11pt` |
| `line-height` | Line height | `1.5` |
| `heading-prefix` | Section numbering prefix | `§` |
| `link-color` | Link color | `blue` |
| `note-color` | Footnote marker color | — |
| `cite-color` | Citation color | — |
| `figure-caption-position` | Caption position | `above`, `below` |
| `table-caption-position` | Caption position | `above`, `below` |
| `show-links` | Show URLs inline | true/false |
| `margin` | Page margins | `2.5cm` |

### typst Extensions

```bash
# Enable citations in typst
pandoc -t typst+citations paper.md -o paper.typ
```

## LaTeX Input Parsing

When reading LaTeX input, pandoc understands:

- Sections (`\section`, `\subsection`, etc.)
- Environments (`itemize`, `enumerate`, `table`, `figure`, `verbatim`)
- Inline formatting (`\textbf`, `\textit`, `\texttt`, `\emph`)
- Math (`$...$`, `\[...\]`, `\(...\)`, `begin{equation}`)
- Footnotes (`\footnote`)
- Links (`\href`, `\url`, `\hyperref`)
- Citations (`\cite`, `\citep`, `\citet`, `\citeauthor`)
- Verbatim/raw content

```bash
# Parse LaTeX with smart typography
pandoc -f latex+smart -t markdown paper.tex

# Parse LaTeX with auto-identifiers
pandoc -f latex+auto_identifiers -t html paper.tex
```
