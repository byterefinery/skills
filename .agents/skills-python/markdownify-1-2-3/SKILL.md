---
name: markdownify-1-2-3
description: Convert HTML to Markdown using python-markdownify 1.2.3. Use when converting HTML strings, files, or BeautifulSoup soup objects to Markdown. Supports heading styles, custom converters, tag stripping/conversion, code language detection, table handling, and CLI usage.
license: MIT
compatibility: Requires Python 3.6+ and beautifulsoup4
metadata:
  tags:
    - html
    - markdown
    - conversion
    - text-processing
---

# markdownify 1.2.3

## Overview

python-markdownify converts HTML to Markdown. It uses BeautifulSoup for parsing and supports extensive customization of heading styles, list bullets, emphasis symbols, code blocks, tables, and more. Works as a library (`markdownify(html)`) or CLI (`markdownify input.html > output.md`).

Install with `pip install markdownify` or `pip install markdownify==1.2.3`.

## Usage

### Basic conversion

```python
from markdownify import markdownify as md

md('<b>Bold</b> <i>Italic</i>')
# > '**Bold** *Italic*'

md('<a href="https://example.com">Link</a>')
# > '[Link](https://example.com)'

md('<h1>Title</h1><p>Paragraph</p>')
# > '\n\nTitle\n=======\n\n\n\nParagraph\n\n'
```

### Stripping or converting specific tags

```python
# Strip anchor tags (keep text, drop links)
md('<b>Yay</b> <a href="http://github.com">GitHub</a>', strip=['a'])
# > '**Yay** GitHub'

# Convert only bold tags
md('<b>Yay</b> <a href="http://github.com">GitHub</a>', convert=['b'])
# > '**Yay** GitHub'
```

`strip` and `convert` are mutually exclusive.

### Heading styles

```python
from markdownify import ATX, ATX_CLOSED, UNDERLINED

md('<h1>Title</h1>', heading_style=ATX)
# > '\n\n# Title\n\n'

md('<h1>Title</h1>', heading_style=ATX_CLOSED)
# > '\n\n# Title #\n\n'

md('<h1>Title</h1>', heading_style=UNDERLINED)  # default
# > '\n\nTitle\n=======\n\n'
```

`UNDERLINED` (alias `SETEXT`) uses underlines for h1/h2 and ATX-style `#` for h3-h6.

### Code blocks with language

```python
md('<pre><code>print("hi")</code></pre>', code_language='python')
# > '\n\n```python\nprint("hi")\n```\n\n'
```

Use `code_language_callback` for dynamic detection:

```python
def lang_callback(el):
    return el.get('class', [None])[0]

md('<pre class="javascript"><code>console.log(1)</code></pre>',
   code_language_callback=lang_callback)
```

### Converting BeautifulSoup objects directly

```python
from markdownify import MarkdownConverter
from bs4 import BeautifulSoup

def md_soup(soup, **options):
    return MarkdownConverter(**options).convert_soup(soup)

soup = BeautifulSoup('<b>Bold</b>', 'html.parser')
md_soup(soup)
# > '**Bold**'
```

### CLI usage

```bash
markdownify input.html > output.md
cat input.html | markdownify > output.md
markdownify -h
```

CLI options mirror the API: `--heading-style`, `--strip`, `--convert`, `--bullets`, `--code-language`, `--wrap`, `--wrap-width`, `--bs4-options`, etc.

### Other useful options

```python
# Custom bullet characters per nesting level
md('<ul><li>A<ul><li>B</li></ul></li></ul>', bullets='-')
# Single bullet for all levels. Default is '*+-' (cycles by depth).

# Choose emphasis symbol
from markdownify import UNDERSCORE
md('<b>Bold</b> <i>Italic</i>', strong_em_symbol=UNDERSCORE)
# > '__Bold__ _Italic_'

# Escape miscellaneous Markdown-special characters
md('Text with *asterisks* and _underscores_', escape_misc=True)

# Keep inline images in table cells (default: alt text only)
md(html, keep_inline_images_in=['td', 'th'])

# Infer table header from first row when <thead>/<th> is missing
md(html, table_infer_header=True)

# Strip document-level newlines
from markdownify import LSTRIP, RSTRIP, STRIP
md(html, strip_document=LSTRIP)  # only leading
md(html, strip_document=None)    # keep all

# BeautifulSoup parser selection
md(html, bs4_options='lxml')
md(html, bs4_options='html5lib')
md(html, bs4_options={'features': 'html.parser', 'from_encoding': 'utf-8'})
```

### Custom converters

Subclass `MarkdownConverter` to override or add tag handlers:

```python
from markdownify import MarkdownConverter

class CustomConverter(MarkdownConverter):
    def convert_img(self, el, text, parent_tags):
        # Add extra newlines after images
        return super().convert_img(el, text, parent_tags) + '\n\n'

    def convert_p(self, el, text, parent_tags):
        # Ignore paragraphs entirely
        return ''

    def convert_video(self, el, text, parent_tags):
        # Custom video handling
        src = el.get('src', '')
        return f'[Video]({src})' if src else text

def md(html, **options):
    return CustomConverter(**options).convert(html)
```

Converter methods follow the pattern `convert_<tag>(self, el, text, parent_tags)` and return a string. `el` is the BeautifulSoup element, `text` is the already-converted child content, and `parent_tags` is a set of ancestor tag names.

## Gotchas

- **`strip` and `convert` are mutually exclusive** — specifying both raises `ValueError`. Choose one or neither (convert all tags).
- **`escape_asterisks` and `escape_underscores` default to `True`** — literal `*` and `_` in text content are escaped to `\*` and `\_`. This prevents accidental Markdown formatting in plain text. Set to `False` only if you need raw asterisks/underscores in output.
- **Inline images become alt text inside headings and table cells** — by default, `<img>` inside `<h1>`–`<h6>` or `<td>`/`<th>` converts to just the `alt` attribute. Use `keep_inline_images_in=['td']` to preserve full image syntax in those contexts.
- **Tables without `<thead>` or `<th>` get empty header rows** — unless `table_infer_header=True`, the first row becomes body content and an empty header row is inserted.
- **`heading_style=UNDERLINED` only works for h1/h2** — h3 through h6 always use ATX-style `#` prefixes regardless of heading_style setting, because Markdown has no underline syntax for deeper headings.
- **`<pre>` content preserves newlines** — whitespace inside `<pre>` is not normalized. Use `strip_pre` (`STRIP`, `STRIP_ONE`, or `None`) to control leading/trailing blank lines in code blocks.
- **`code_language_callback` receives a BeautifulSoup element** — the callback gets the `<pre>` element, not the `<code>` child. Access classes via `el.get('class')` or attributes via `el.get('attr')`.
- **`bullets` cycles by nesting depth** — with default `'*+-'`, level 0 uses `*`, level 1 uses `+`, level 2 uses `-`, then cycles back. Use a single-character string like `'-'` for uniform bullets.
- **`wrap` interacts with `<br>` tags** — when `wrap=True`, newlines from `<br>` are preserved while other text is reflowed. Use `newline_style=BACKSLASH` to keep explicit line breaks in wrapped paragraphs.
- **`<script>` and `<style>` tags produce empty output** — their content is silently dropped during conversion.
- **`<video>` conversion is basic** — it extracts `src` or first `<source>` and optionally wraps with a poster image. For complex video embeds, write a custom `convert_video` handler.
- **Dependencies** — markdownify requires `beautifulsoup4` and `six`. Parser options like `lxml` or `html5lib` need their respective packages installed separately.
- **Python 2 compatibility is legacy** — the library supports Python 2.5+, but in practice use Python 3.6+. The `six` dependency is for cross-version string handling.
