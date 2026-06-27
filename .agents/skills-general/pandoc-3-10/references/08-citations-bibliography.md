# Citations and Bibliography Reference

Pandoc's citation system uses the `--citeproc` option with CSL (Citation Style Language) styles to automatically generate citations and bibliographies.

## Citation Syntax

### Basic Citations

```markdown
Cite a single source: @author2024

Multiple sources in one bracket: [@author2024; @other2023]

With locator: @author2024 [p. 42]
@author2024 [see chap. 3]
```

### Citation Modifiers

```markdown
# Suppress author name (e.g., in "as noted by Author [@author2024]")
as noted by Smith [@smith2024]

# Negated citations
This is not the case [@nottrue2023, -].

# Locator prefixes
@smith2024 [p. 42]      # page
@smith2024 [chap. 3]    # chapter
@smith2024 [eq. 5]      # equation
@smith2024 [fig. 2]     # figure
@smith2024 [sec. 1.2]   # section
@smith2024 [n. 5]       # note
```

### Multiple Citations

```markdown
Single bracket, semicolon-separated:
[@smith2024; @jones2023; @brown2022]

With individual locators:
[@smith2024 p. 42; @jones2023 chap. 1]

Mixed suppressed and normal:
As Smith argues [@smith2024], and as Jones confirms [@jones2023].
```

### Citation Keys with Special Characters

Keys starting with a letter, digit, or `_`, containing only alphanumerics and single internal punctuation (`:.#$%&-+?<>~/`) don't need braces:

```markdown
@Foo_bar.baz     # key is Foo_bar.baz (trailing period excluded)
@{Foo_bar.baz.}  # key includes trailing period
@{my-key}        # braces required for keys with special chars
```

## Bibliography Sources

### External Bibliography Files

```bash
# Single bibliography
pandoc --citeproc -o output.html input.md --bibliography=references.bib

# Multiple bibliographies
pandoc --citeproc -o output.html input.md \
  --bibliography=refs1.bib \
  --bibliography=refs2.json
```

### Bibliography in Metadata

YAML metadata block:

```yaml
---
bibliography:
  - references.bib
  - online-sources.json
csl: apa.csl
---
```

Or via command line:

```bash
pandoc --citeproc -o output.html input.md -M bibliography=references.bib
```

### Supported Bibliography Formats

| Format | File extension |
|---|---|
| BibLaTeX | `.bib` |
| BibTeX | `.bibtex` |
| CSL JSON | `.json` |
| CSL YAML | `.yaml` |
| RIS | `.ris` |

Note: `.bib` can be used with both BibTeX and BibLaTeX. Use `.bibtex` to force BibTeX interpretation.

### Bibliography Field Markup

- **BibTeX/BibLaTeX**: LaTeX markup parsed inside fields like `title`
- **CSL YAML**: Markdown parsed in fields
- **CSL JSON**: HTML-like markup (`<i>`, `<b>`, `<sub>`, `<sup>`, `<span style="font-variant:small-caps;">`)

## CSL Styles

### Using CSL Styles

```bash
# Use a specific CSL style
pandoc --citeproc -o output.html input.md --csl=apa.csl

# CSL from URL
pandoc --citeproc -o output.html input.md --csl=https://zotero.org/styles/apa

# CSL from user data directory
cp apa.csl ~/.local/share/pandoc/csl/
pandoc --citeproc -o output.html input.md --csl=apa
```

### Finding CSL Styles

- [Zotero Style Repository](https://www.zotero.org/styles) — thousands of journal/publisher styles
- Common styles: `apa.csl`, `chicago-author-date.csl`, `ieee.csl`, `nature.csl`

### Built-in Styles

Pandoc ships with a default style. Override with `--csl` or `csl` metadata field.

## Citation Rendering Options

```bash
# Generate citations and bibliography
pandoc --citeproc -o output.html input.md --bibliography=refs.bib

# Use biblatex for LaTeX output
pandoc --citeproc --biblatex -o output.tex input.md --bibliography=refs.bib

# Specify bibliography title
pandoc --citeproc -o output.html input.md --biblio-title="References"

# Sort bibliography by citation order (not alphabetical)
pandoc --citeproc -o output.html input.md --biblio-style=plain

# Include only cited entries
pandoc --citeproc -o output.html input.md  # default: only cited

# Include uncited entries too
pandoc --citeproc -o output.html input.md --natbib
```

### Citation Rendering Options Summary

| Option | Description |
|---|---|
| `--citeproc` | Process citations and generate bibliography |
| `--csl=FILE` | CSL style file |
| `--bibliography=FILE` | Bibliography source file |
| `--biblio-title=TEXT` | Title of bibliography section |
| `--biblio-style=STYLE` | List style: `plain`, `authoryear`, `note` |
| `--citation-abbreviations=FILE` | Abbreviations file (JSON) |
| `--natbib` | Use natbib for LaTeX citations |
| `--biblatex` | Use biblatex for LaTeX citations |

## Citation in Different Output Formats

### HTML Output

Citations render as superscript numbers or author-year depending on CSL style. Bibliography appears at the end.

```bash
pandoc --citeproc -s -t html input.md \
  --bibliography=refs.bib \
  --csl=apa.csl \
  -o output.html
```

### LaTeX Output

```bash
# With natbib (default)
pandoc --citeproc -s -t latex input.md \
  --bibliography=refs.bib \
  -o output.tex

# With biblatex
pandoc --citeproc --biblatex -s -t latex input.md \
  --bibliography=refs.bib \
  -V biblatex=true \
  -o output.tex
```

### docx Output

Citations render as footnotes or author-year in Word. Enable with the `citations` extension:

```bash
pandoc --citeproc -t docx+citations input.md \
  --bibliography=refs.bib \
  -o output.docx
```

## Inline Bibliography Data

Embed references directly in the document's YAML metadata:

```yaml
---
references:
  - id: smith2024
    type: article-journal
    author:
      - family: Smith
        given: John
    title: "Title of the Article"
    container-title: "Journal Name"
    year: 2024
    volume: "10"
    page: "100-110"
  - id: jones2023
    type: book
    author:
      - family: Jones
        given: Jane
    title: "Book Title"
    publisher: "Publisher Name"
    year: 2023
---
```

## Complete Example

```markdown
---
title: "My Paper"
author: "Jane Doe"
date: "2024-01-15"
bibliography: references.bib
csl: https://zotero.org/styles/apa
---

# Introduction

Previous work has shown this effect [@smith2024; @jones2023].

As noted by Smith [@smith2024 p. 42], the results are significant.

# Conclusion

Further research is needed [@brown2022].

# References

(: bibliography :)
```

```bash
pandoc --citeproc -s -t html paper.md -o paper.html
```

## Gotchas

- **`--citeproc` is required** — without it, `@key` citations appear as literal text
- **Bibliography IDs must match citation keys** — `@smith2024` must have a corresponding entry with `id: smith2024`
- **CSL styles control everything** — author-year vs. numbered, bibliography format, date style all come from the CSL file
- **`.bib` ambiguity** — use `.bibtex` extension to force BibTeX (not BibLaTeX) parsing
- **Missing references produce warnings** — pandoc warns about cited keys not found in bibliography
