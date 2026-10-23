# DOM access, attributes, and element construction

- [Accessing elements](#accessing-elements)
- [Attributes vs properties](#attributes-vs-properties)
- [Brython-specific element properties and methods](#brython-specific-element-properties-and-methods)
- [browser.html element classes](#browserhtml-element-classes)
- [Custom tags and attribute mapping](#custom-tags-and-attribute-mapping)
- [pydom](#pydom)

## Accessing elements

`document` (module `browser`) behaves like a dictionary keyed by element `id`; missing ids raise `KeyError`.

```python
from browser import document
data = document["data"]          # <input id="data">
```

Every element has search methods (CSS selectors per the MDN reference):

- `elt.get(name=N)` — list of descendants whose attribute `name` equals `N`
- `elt.get(selector=S)` — list of descendants matching CSS selector `S`
- `elt.select(S)` — alias of `get(selector=S)`
- `elt.select_one(S)` — first match or `None`

```python
document.select(".foo")          # elements with class "foo"
document.select("form")          # all <form>
document.select("H1.bar")        # <h1> with class "bar"
document.select("#container")    # element with that id, i.e. [document["container"]]
document.select("a[title]")      # <a> elements having a title attribute
document.select("#tid td")       # <td> inside #tid
```

The standard DOM API also works, via `document` and `window` from module `browser`: `document.getElementById(id)`, `document.createElement("A")`, `document.appendChild(elt)`, and so on.

`document.query` parses the URL query string: `query[key]` (list if the key repeats, `KeyError` otherwise), `query.getfirst(key[, default])`, `query.getlist(key)`, `query.getvalue(key[, default])`.

## Attributes vs properties

The DOM distinguishes *attributes* (defined in the tag, always strings, case-insensitive for HTML and case-sensitive for SVG) from *properties* (dotted access, any type, always case-sensitive). Setting an attribute usually also sets the matching property, but not always (e.g. `checked` attribute `"checked"` vs property `true`), and the names can differ (`class` → `className`).

Brython manages attributes through the dict-like `elt.attrs`:

```python
element.attrs["title"] = "hint"
value = element.attrs["title"]            # KeyError if absent
value = element.attrs.get("title", dflt)
if "title" in element.attrs: ...
del element.attrs["title"]
for name, value in element.attrs.items(): ...
```

## Brython-specific element properties and methods

- `text` (R/W) — text inside the element; `html` (R/W) — inner HTML code
- `class_name` (R/W) — the `class` attribute
- `children` (R) — child elements; `child_nodes` (R) — all children
- `parent` (R) — parent element, `None` for the document
- `width`, `height` (R/W) — pixels (same as `style.width`/`style.height` as integers)
- `left`, `top` (R/W) — position relative to the first positioned parent (integer form of `style.left`/`style.top`)
- `abs_left`, `abs_top` (R) — position relative to the document borders
- `scrolled_left`, `scrolled_top` (R) — position relative to the visible part of the document (decremented by scrolling; `abs_*` stay fixed)
- `index([selector])` — index among the parent's children, or among children matching the CSS selector (`-1` if none)
- `inside(other)` — containment test
- `clear()` — remove all descendants
- `closest(tag_name)` — first parent with that tag, `KeyError` if none
- `bind`, `get`, `select`, `select_one` — see above / events reference

Tree operations: add a child with `elt <= child` (the "left arrow" operator; equivalent to `elt.attach(child)`), add siblings with `+`, iterate children with a plain `for`, remove an element with `del document["zone"]`. The `options` collection of a `SELECT` element has a list interface (`options[i]`, `insert`, `append`, `del`).

## browser.html element classes

`browser.html` exposes every HTML tag as a class in uppercase: HTML4 (`A, B, BUTTON, DIV, FORM, H1-H6, IMG, INPUT, OL, P, SCRIPT, SELECT, TABLE, TD, TEXTAREA, UL, ...`), HTML5 (`ARTICLE, ASIDE, AUDIO, CANVAS, DATALIST, FIGURE, FOOTER, HEADER, MAIN, MARK, METER, NAV, OUTPUT, PROGRESS, SECTION, SOURCE, VIDEO, WBR, ...`), and HTML5.1 (`DETAILS, DIALOG, MENUITEM, PICTURE, SUMMARY`).

Creation syntax: `Tag(content, **attributes)` —

- `content` may be a string, a number, another element, or an iterable (each item becomes a child). A string is interpreted as HTML code; for plain text set the `text` property instead.
- attribute names with hyphens become underscores: `http_equiv` not `http-equiv`. Complex names use `**{"v-on:click": "count++"}`.
- `style=` takes a dict with JavaScript (camelCase) keys: `style={"backgroundColor": "#fff"}`.
- `class` is a Python keyword, so write `Class="container"`.

```python
from browser import document
from browser.html import A, B, DIV, P, SELECT, OPTION, TR, TH, TABLE, TD, UL, LI

document <= A("Python", href="http://python.org")
row = TR(TH("Number") + TH("Square"))
table = TABLE()
table <= (TR(TD(i) + TD(i * i)) for i in range(10))
document <= SELECT(OPTION(elt, value=i) for i, elt in enumerate(["one", "two"]))
```

An element can also be built incrementally: `elt = DIV()`, then `elt <= child`, `elt.attrs["id"] = "x"`, `elt.href = ...`.

**One DOM node per instance** — an element instance maps to a single DOM object; reusing it in two places renders it only at the last one. Duplicate with `elt.clone()`.

### Custom tags and attribute mapping

- `html.maketag("P2")` creates a new class usable like the standard ones; `html.tags` maps tag names to classes (updated by `maketag`).
- `html.attribute_mapper(attr)` is called to translate each keyword arg into an attribute name (default: underscores → hyphens). Override it to support framework syntaxes, e.g.

```python
import re
def f(attr):
    return re.sub("^v_(.*)_(.*)$", r"v-\1:\2", attr)
html.attribute_mapper = f
```

## pydom

`browser.pydom` emulates the jQuery API for element selection and manipulation (see the pydom documentation page for details); it is an alternative to `select`/`select_one`/`get`.
