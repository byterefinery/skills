# Filters Reference

Pandoc filters transform the intermediate AST between reading and writing. Two types: JSON filters (external programs) and Lua filters (built-in).

## JSON Filters

JSON filters receive the document as JSON on stdin and write modified JSON to stdout. The document is represented as pandoc's native AST in JSON format.

### Pipeline Architecture

```
Input → Reader → AST (JSON) → Filter → Modified AST (JSON) → Writer → Output
```

```bash
# Basic filter usage
pandoc -f markdown -t html input.md | json-filter.py | pandoc -f json -t html -o output.html

# Using --filter flag
pandoc -f markdown -t html input.md --filter ./my-filter.py -o output.html

# Multiple filters (applied in order)
pandoc -f markdown -t html input.md \
  --filter ./caps.py \
  --filter ./add-links.py \
  -o output.html
```

### JSON Filter Example (Python)

A simple filter that capitalizes all text:

```python
#!/usr/bin/env python3
import json
import sys

def capitalize(element):
    """Recursively capitalize all Text elements."""
    if element['t'] == 'Text':
        element['c'][0] = element['c'][0].upper()
    elif 'c' in element and isinstance(element['c'], list):
        for child in element['c']:
            if isinstance(child, dict):
                capitalize(child)
    elif isinstance(element, dict):
        for key, value in element.items():
            if isinstance(value, dict):
                capitalize(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        capitalize(item)
    return element

def main():
    doc = json.load(sys.stdin)
    for elem in doc['blocks']:
        capitalize(elem)
    json.dump(doc, sys.stdout)

if __name__ == '__main__':
    main()
```

Usage: `pandoc -f markdown -t html input.md | ./capitalize.py | pandoc -f json -t html`

### Inspecting the AST

```bash
# JSON AST (pretty-printed)
pandoc -t json input.md | python3 -m json.tool

# Compact JSON
pandoc -t json input.md

# Native Haskell AST
pandoc -t native input.md

# XML AST
pandoc -t xml input.md
```

### AST Structure Overview

The JSON AST is a tree with these key element types:

| Type (`t`) | Description | Content (`c`) |
|---|---|---|
| `Pandoc` | Root document | `[meta, [blocks], [blocks], format_version]` |
| `Para` | Paragraph | `[inlines]` |
| `Plain` | Plain text block | `[inlines]` |
| `LineBreak` | Hard line break | `[]` |
| `Space` | Space | `[]` |
| `Str` | Text string | `["text"]` |
| `Emph` | Emphasis | `[inlines]` |
| `Strong` | Strong emphasis | `[inlines]` |
| `Link` | Hyperlink | `[[inlines], "url", "title"]` |
| `Image` | Image | `[[inlines], "src", "alt"]` |
| `Code` | Inline code | `["attr", "code"]` |
| `CodeBlock` | Code block | `["attr", "code"]` |
| `Header` | Heading | `[level, "attr", [inlines]]` |
| `BlockQuote` | Block quote | `[blocks]` |
| `BulletList` | Unordered list | `[[items]]` |
| `OrderedList` | Ordered list | `[(start, style, delimiter), [items]]` |
| `Table` | Table | `[caption, headers, rows]` |
| `Math` | Math | `["displaymode", "formula"]` |
| `Cite` | Citation | `[[citations], [inlines]]` |
| `Div` | Div container | `["attr", [blocks]]` |
| `Span` | Span container | `["attr", [inlines]]` |

Attribute format: `["id", "classes", [("key", "value")]]`

### Popular JSON Filter Tools

- **pandoc-filter** (Python): Generic filter framework
- **pandoc-xnos** (Python): Cross-references, notes, ordered/unordered labels
- **pandoc-include-code** (Shell): Include code files in code blocks
- **pandoc-figure** (Shell): Manage figures with captions
- **pandoc-listings** (Shell): Code listings with line numbers

## Lua Filters

Lua filters run inside pandoc's Haskell process. Faster than JSON filters (no serialization overhead). Written in Lua using pandoc's Lua API.

### Basic Usage

```bash
# Apply a Lua filter
pandoc -f markdown -t html input.md --lua-filter=./my-filter.lua -o output.html

# Multiple Lua filters
pandoc -f markdown -t html input.md \
  --lua-filter=./caps.lua \
  --lua-filter=./links.lua \
  -o output.html

# Combined JSON and Lua filters
pandoc -f markdown -t html input.md \
  --filter ./json-filter.py \
  --lua-filter=./lua-filter.lua \
  -o output.html
```

### Lua Filter Example

```lua
-- Capitalize all text
function Str(elem)
  return pandoc.Str(elem.text:upper())
end
```

Save as `caps.lua`, run: `pandoc --lua-filter=caps.lua input.md`

### Common Lua Filter Patterns

#### Transform Headings

```lua
-- Add a class to all level-2 headings
function Header(el)
  if el.level == 2 then
    el.classes:insert("section-heading")
  end
  return el
end
```

#### Modify Links

```lua
-- Convert all external links to open in new tab
function Link(el)
  if not el.target:match("^#") and not el.target:match("^[^/]") then
    el.attributes["target"] = "_blank"
  end
  return el
end
```

#### Add Attributes

```lua
-- Add language attribute to code blocks
function CodeBlock(el)
  if el.attr.classes:includes("python") then
    el.attr.attributes["data-lang"] = "python3"
  end
  return el
end
```

#### Traverse and Modify

```lua
-- Replace specific text throughout document
function Str(elem)
  if elem.text == "old term" then
    return pandoc.Str("new term")
  end
  return nil  -- no change
end
```

### Lua Filter Walk Functions

Use `pandoc.walk_block` and `pandoc.walk_inline` for complex traversals:

```lua
function Pandoc(doc)
  local transformer = {
    Link = function(el)
      -- transform links
      return el
    end,
    Image = function(el)
      -- transform images
      return el
    end
  }
  doc.blocks = pandoc.walk_block(pandoc.Div(doc.blocks), transformer)
  return doc
end
```

### Built-in Lua Filters

Pandoc ships with useful filters accessible via `--lua-filter`:

```bash
# Trim whitespace
pandoc --lua-filter=pandoc.trim input.md

# Include code files
pandoc --lua-filter=pandoc.include-code input.md
```

## Filter Comparison

| Feature | JSON Filters | Lua Filters |
|---|---|---|
| Speed | Slower (serialization) | Faster (in-process) |
| Language | Any language | Lua only |
| Complexity | Full AST access | Full AST access |
| Debugging | Easier (inspect JSON) | Requires Lua debugging |
| Portability | Depends on runtime | Bundled with pandoc |
| Use case | Complex logic, existing tools | Simple transforms, performance |

## Best Practices

- **Prefer Lua filters** for simple transformations (faster, no external dependency)
- **Use JSON filters** when you need a specific language or existing library
- **Chain filters carefully**: order matters; each filter sees the output of the previous
- **Test with `--t json`** to inspect AST before/after filtering
- **Return `nil`** in Lua filters to leave an element unchanged
- **Return modified element** to replace it; return empty list `{}` to remove it
