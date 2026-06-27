# Templates and Defaults Files Reference

Pandoc templates control document structure and defaults files store reusable option configurations.

## Templates

Templates define the skeleton of standalone output documents. They use a simple templating language with variables, conditionals, loops, and pipes.

### Template Syntax

#### Variables

```
$variable$
```

Variables are substituted with their values. Undefined variables produce empty strings.

```
$title$
$author$
$date$
$body$
```

#### Comments

```
% This is a comment (ignored)
```

Lines starting with `%` are comments.

#### Delimiters

Default delimiters: `$...$`. Can be changed in template files.

#### Conditionals

```
$if(title)$
<h1>$title$</h1>
$endif$
```

Conditional blocks render only if the variable is defined and truthy. Supports `else`:

```
$if(title)$
<h1>$title$</h1>
$else$
<h1>Untitled</h1>
$endif$
```

Nested conditionals:

```
$if(title)$
<h1>$title$</h1>
  $if(subtitle)$
  <h2>$subtitle$</h2>
  $endif$
$endif$
```

#### For Loops

Iterate over list variables:

```
$for(authors)$
<p class="author">$authors$</p>
$endfor$
```

With separators:

```
$for(authors)$Authors: $authors$$sep$, $endfor$
```

#### Partials

Include other template files:

```
$partial(head.html)$
```

Partials are searched in the same directory as the main template.

#### Pipes

Transform variable values with filters:

```
$title|lowercase$
$date|date("%B %e, %Y")$
$body|highlighting-hljs$
```

Built-in pipe filters: `uppercase`, `lowercase`, `title`, `capitalize`, `reverse`, `strip-comments`, `smart`, `trim`, `json`, `reverse`, `pandoc`.

Custom pipes can be defined as external programs.

#### Nesting

All constructs nest arbitrarily:

```
$for(chapters)$
$if(chapters.title)$
<h2>$chapters.title$</h2>
$endif$
$for(chapters.sections)$
<p>$chapters.sections$</p>
$endfor$
$endfor$
```

#### Breakable Spaces

Spaces inside `$...$` delimiters are trimmed. Use `~` for explicit spaces:

```
$if(x)$ $x$ $endif$
```

The spaces around `$x$` are breakable (collapsed to one space or newline).

### Accessing Default Templates

```bash
# List available templates
pandoc --list-templates

# Print a default template
pandoc --print-default-data-file templates/default.html5

# Print all templates
pandoc --print-default-data-file=templates/

# Save a template for customization
pandoc -o my-template.html --print-default-data-file templates/default.html5
```

### Using Custom Templates

```bash
# Apply custom template
pandoc -s -t html input.md --template=my-template.html -o output.html

# Template from user data directory
mkdir -p ~/.local/share/pandoc/templates
cp my-template.html ~/.local/share/pandoc/templates/
pandoc -s -t html input.md --template=my-template -o output.html

# Format-specific default template override
# For docx: customize default.openxml
# For odt: customize default.opendocument
# For pdf (latex): customize default.latex
```

### Template Variables by Format

#### HTML Variables

| Variable | Description |
|---|---|
| `title` | Document title |
| `author` | Author name(s) |
| `date` | Document date |
| `lang` | HTML `lang` attribute |
| `subtitle` | Subtitle |
| `abstract` | Abstract text |
| `body` | Document body content |
| `header-includes` | Extra content in `<head>` |
| `footer-includes` | Extra content before `</body>` |
| `toc` | Table of contents (if enabled) |
| `toc-title` | TOC title text |
| `css` | Linked CSS files |
| `scripts` | Script includes |

#### LaTeX Variables

| Variable | Description |
|---|---|
| `title` | Title text |
| `author` | Author(s) |
| `date` | Date |
| `abstract` | Abstract |
| `thanks` | Acknowledgments |
| `subtitle` | Subtitle |
| `body` | Document body |
| `header-includes` | Extra content in preamble |
| `bibliography` | Bibliography file(s) |
| `biblio-style` | BibTeX style |
| `colorlinks` | Colored hyperlinks |
| `linkcolor`, `urlcolor`, etc. | Link colors |
| `geometry` | Page geometry options |
| `linestretch` | Line spacing |
| `documentclass` | Document class |
| `classoption` | Class options |
| `fontsize` | Base font size |
| `mainfont`, `sansfont`, `monofont` | Font names (xelatex/lualatex) |
| `lang` | Language (babel/polyglossia) |
| `linenumings` | Line numbers |
| `secnumdepth` | Section numbering depth |
| `beamerarticle` | Beamer → article mode |
| `handout` | Beamer handout mode |
| `aspectratio` | Slide aspect ratio |
| `theme`, `colortheme`, etc. | Beamer themes |
| `toc-own-page` | TOC on own page |
| `caption-position` | Caption position |

#### typst Variables

| Variable | Description |
|---|---|
| `title` | Document title |
| `authors` | Author list |
| `date` | Date |
| `abstract` | Abstract |
| `body` | Document body |
| `papersize` | Paper size |
| `page-width`, `page-height` | Page dimensions |
| `margin` | Page margins |
| `text-align` | Text alignment |
| `first-font`, `sans-font`, `mono-font` | Fonts |
| `font-size` | Base font size |
| `line-height` | Line height |
| `link-color` | Link color |
| `show-links` | Show URLs inline |

## Defaults Files

Defaults files (YAML or JSON) store option configurations for reuse.

### Creating Defaults Files

```yaml
# defaults.yaml
from: markdown
to: html5
standalone: true
table-of-contents: true
number-sections: true
columns: 72
output-file: output.html
```

### Using Defaults Files

```bash
# Apply defaults file
pandoc -d defaults.yaml input.md

# Override specific options
pandoc -d defaults.yaml --to=latex input.md

# Multiple defaults files (merged in order)
pandoc -d defaults.yaml -d overrides.yaml input.md

# Defaults from user data directory
pandoc -d mydefaults input.md
# Searches: ./mydefaults.yaml, then ~/.local/share/pandoc/defaults/mydefaults.yaml
```

### Defaults File Format

All command-line options can be expressed in YAML:

```yaml
# defaults.yaml
from: markdown
to: latex
standalone: true
output-file: output.tex
pdf-engine: xelatex
variables:
  documentclass: report
  mainfont: "Noto Serif"
  linestretch: 1.5
metadata:
  title: "My Document"
  author: "Jane Doe"
  date: "2024-01-15"
resource-path:
  - ./images
  - ./assets
filters:
  - ./filter.lua
citeproc: true
bibliography: references.bib
```

### Defaults File Merging

When multiple defaults files are specified, later files override earlier ones. Lists are appended unless the key ends with `+`:

```yaml
# defaults.yaml
variables:
  documentclass: article
filters:
  - ./filter1.lua

# overrides.yaml
variables:
  linestretch: 1.5
filters+:
  - ./filter2.lua
```

Result: `documentclass=article`, `linestretch=1.5`, filters = `[filter1.lua, filter2.lua]`

### Variable Defaults in YAML

```yaml
# Set default variables
variables:
  toc: true
  number-sections: true
  lang: en

# Variables can be overridden on command line
pandoc -d defaults.yaml -V lang=de input.md
```

### Metadata in Defaults

```yaml
metadata:
  title: "Report Title"
  author:
    - "Jane Doe"
    - "John Smith"
  date: "2024-01-15"
  abstract: |
    This is the abstract text.
    It can span multiple lines.
```

Metadata from defaults files merges with metadata from the document itself, with document metadata taking precedence.

### Resource Path

Specify directories for resolving relative paths (images, includes):

```yaml
resource-path:
  - ./images
  - ./assets
  - ../shared
```

Equivalent to `--resource-path=dir1:dir2:dir3`.

## Template and Defaults Workflow

1. **Extract default template**: `pandoc --print-default-data-file templates/default.html5 > my-template.html`
2. **Customize template**: Edit variables, add CSS, modify structure
3. **Create defaults file**: Store common options in YAML
4. **Use together**: `pandoc -d defaults.yaml --template=my-template.html input.md`
