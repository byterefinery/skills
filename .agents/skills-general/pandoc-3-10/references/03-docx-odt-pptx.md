# Microsoft Office and OpenDocument Reference

Detailed reference for converting to and from Microsoft Word (docx), LibreOffice/OpenDocument (odt), and PowerPoint (pptx).

## Microsoft Word (docx)

### Basic Conversions

```bash
# Markdown → docx
pandoc -f markdown -t docx document.md -o document.docx

# docx → Markdown (bi-directional, preserves structure)
pandoc -f docx -t markdown document.docx -o document.md

# docx → HTML (standalone with CSS)
pandoc -s -f docx -t html document.docx -o document.html

# docx → plain text
pandoc -f docx -t plain document.docx

# docx → GFM (GitHub-Flavored Markdown)
pandoc -f docx -t gfm document.docx -o document.md

# docx → LaTeX
pandoc -f docx -t latex document.docx -o document.tex

# Multiple Markdown files → single docx
pandoc -f markdown -t docx intro.md body.md conclusion.md -o report.docx
```

### Round-Trip Quality: Markdown → docx → Markdown

**Preserved**:
- Bold (`**text**`), italic (`*text*`), inline code (`` `code` ``)
- Ordered and unordered lists (including nested)
- Tables (pipe tables → grid tables, structurally equivalent)
- Code blocks (fenced → indented, both valid markdown)
- Block quotes
- Links (`[text](url)`)
- Math: inline `$...$` and display `$$...$$`
- Grid tables (from complex docx with merged cells)

**Lost/Changed**:
- YAML front matter → becomes heading + paragraph text
- Image files → placeholder with alt text (missing images produce `[WARNING] Could not fetch resource`)
- Custom styles → mapped to standard markdown formatting
- Page layout, margins, headers/footers → not preserved in markdown

### Custom Styling with Reference Documents

Pandoc uses a `reference.docx` to determine styles, margins, page size, headers, and footers.

```bash
# Extract default reference docx
pandoc -o custom-reference.docx --print-default-data-file reference.docx

# Use custom reference for styling
pandoc -o styled.docx document.md --reference-doc=custom-reference.docx

# Reference from user data directory (auto-detected)
mkdir -p ~/.local/share/pandoc
cp custom-reference.docx ~/.local/share/pandoc/reference.docx
pandoc -o styled.docx document.md  # auto-uses reference.docx
```

### Paragraph Styles Recognized by Pandoc

When modifying `reference.docx`, these paragraph styles are used:

| Style name | Purpose |
|---|---|
| Normal / Body Text | Default body text |
| First Paragraph | First paragraph of a section |
| Compact | Compact body text |
| Title | Document title |
| Subtitle | Document subtitle |
| Author | Author name |
| Date | Document date |
| Abstract / AbstractTitle | Abstract section |
| Heading 1–9 | Section headings (levels 1–9) |
| Block Text | Block quotes |
| Footnote Block Text | Block quotes in footnotes |
| Source Code | Code blocks |
| Footnote Text | Footnote content |
| Definition Term / Definition | Definition lists |
| Caption / Table Caption / Image Caption | Captions |
| Figure / Captioned Figure | Figures |
| Bibliography | Bibliography section |
| TOC Heading | Table of contents heading |

### Character Styles Recognized

| Style name | Purpose |
|---|---|
| Default Paragraph Font | Default inline style |
| Verbatim Char | Inline code |
| Footnote Reference | Footnote markers |
| Hyperlink | Links |
| Section Number | Section numbering |

### Table Style

- `Table` — applied to all tables

### docx-Specific Options

```bash
# Specify reference docx
pandoc --reference-doc=template.docx -o out.docx input.md

# Extract images as links (not embedded)
pandoc -f docx -t markdown --extract-media=./images document.docx

# Preserve docx lists style
pandoc -f docx -t markdown --wrap=none document.docx
```

### docx Citations Extension

When the `citations` extension is enabled for docx input, pandoc can parse citation markup embedded in Word documents:

```bash
pandoc -f docx+citations -t latex --citeproc document.docx
```

## OpenDocument Text (odt)

### Basic Conversions

```bash
# Markdown → ODT
pandoc -f markdown -t odt document.md -o document.odt

# ODT → Markdown (bi-directional)
pandoc -f odt -t markdown document.odt -o document.md

# ODT → HTML
pandoc -f odt -t html document.odt -o document.html

# ODT → PDF (via LaTeX)
pandoc -f odt -t pdf document.odt -o document.pdf

# ODT → docx
pandoc -f odt -t docx document.odt -o document.docx
```

### Custom Styling with Reference Documents

```bash
# Extract default reference ODT
pandoc -o custom-reference.odt --print-default-data-file reference.odt

# Use custom reference for styling
pandoc -o styled.odt document.md --reference-doc=custom-reference.odt

# Reference from user data directory
cp custom-reference.odt ~/.local/share/pandoc/reference.odt
pandoc -o styled.odt document.md  # auto-uses reference.odt
```

### ODT-Specific Options

```bash
# Link images instead of embedding
pandoc -t odt --link-images -o document.odt input.md

# Extract media from ODT
pandoc -f odt -t markdown --extract-media=./images document.odt
```

### ODT Math Rendering

Math in ODT output is rendered using MathML when possible. For complex formulas, verify the output in LibreOffice as rendering fidelity varies.

## PowerPoint (pptx)

### Basic Conversions

```bash
# Markdown → PowerPoint
pandoc -f markdown -t pptx slides.md -o presentation.pptx

# PowerPoint → Markdown (bi-directional)
pandoc -f pptx -t markdown presentation.pptx -o slides.md

# PowerPoint → HTML
pandoc -f pptx -t html presentation.pptx -o slides.html

# PowerPoint → LaTeX
pandoc -f pptx -t latex presentation.pptx -o slides.tex

# PowerPoint → plain text
pandoc -f pptx -t plain presentation.pptx

# HTML slides → PowerPoint
pandoc -f html -t pptx slides.html -o presentation.pptx
```

### Round-Trip Quality: Markdown → pptx → Markdown

**Preserved**:
- Headings (become `## <heading> {#slide-N}`)
- Tables (pipe tables → simple tables, structurally equivalent)
- Paragraph text content

**Lost/Changed**:
- YAML front matter (title/author) → becomes first slide heading + paragraph
- List markers (`-`, `*`) → become plain paragraphs without bullets
- Heading levels → all become level-2 (`##`) with `{#slide-N}` identifiers
- Slide transitions, animations, speaker notes → not preserved in markdown

### Slide Structure

PowerPoint presentations are structured from headings:

```markdown
# Title Slide

Subtitle and author info

## Section Title

Content on this slide...

### Sub-slide

More detailed content...

---

Manual slide break (use --slide-level=0)
```

### Custom Templates

```bash
# Use a PowerPoint template
pandoc -f markdown -t pptx slides.md --reference-doc=template.pptx -o presentation.pptx
```

Templates must contain layouts named:
- `Title Slide`
- `Title and Content`

Microsoft PowerPoint 2013+ templates (`.pptx` or `.potx`) are known to work.

### Slide Level Control

```bash
# Headings at level 2 create slides
pandoc -f markdown -t pptx slides.md --slide-level=2 -o presentation.pptx

# Manual slide breaks only (no automatic heading-based splits)
pandoc -f markdown -t pptx slides.md --slide-level=0 -o presentation.pptx
```

## Common Options for Office Formats

### Extracting Media

```bash
# Extract images and embedded files from docx
pandoc -f docx -t markdown --extract-media=./media document.docx

# Extract media from pptx
pandoc -f pptx -t markdown --extract-media=./slides-media presentation.pptx
```

### Top-Level Division

```bash
# Treat top-level headings as chapters (adds section breaks in docx)
pandoc -f markdown -t docx --top-level-division=chapter input.md -o output.docx

# Treat as parts
pandoc -f markdown -t docx --top-level-division=part input.md -o output.docx
```

### Numbered Sections

```bash
# Number section headings in docx
pandoc -f markdown -t docx --number-sections input.md -o output.docx

# With custom offset (first heading = 6)
pandoc -f markdown -t docx --number-sections --number-offset=5 input.md -o output.docx
```

## Conversion Quality Summary

### docx → markdown
- **Headings**: Preserved (levels 1–6)
- **Paragraphs**: Preserved with inline formatting (bold, italic, underline)
- **Lists**: Ordered and unordered preserved
- **Tables**: Simple tables well-preserved; complex merged-cell tables become grid tables
- **Images**: Extracted to `--extract-media` directory; linked in markdown
- **Code blocks**: Preserved as fenced code blocks
- **Block quotes**: Preserved
- **Math**: LaTeX math delimiters preserved
- **Lost**: Custom styles, page layout, headers/footers, comments, track changes

### odt → markdown
- Similar to docx → markdown
- MathML in ODT converts to LaTeX math delimiters
- OpenDocument-specific formatting may not map perfectly

### pptx → markdown
- **Slide titles**: Become `##` headings with `{#slide-N}` IDs
- **Text content**: Preserved as paragraphs
- **Tables**: Preserved as simple tables
- **Lists**: Bullet markers lost (become plain paragraphs)
- **Lost**: Animations, transitions, speaker notes, embedded media, custom layouts

### markdown → docx/odt/pptx
- High fidelity for standard elements (headings, paragraphs, lists, tables)
- Custom styles via reference documents
- YAML front matter mapped to document metadata (title, author, date)
