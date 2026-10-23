# Templates, dialogs, menus, web components, SVG

- [browser.template](#browsertemplate)
- [browser.widgets.dialog](#browserwidgetsdialog)
- [browser.widgets.menu](#browserwidgetsmenu)
- [browser.webcomponent](#browserwebcomponent)
- [browser.svg](#browsersvg)

## browser.template

Renders Python expressions and code blocks inside HTML.

```xml
<span id="team">{name}</span>
```

```python
from browser import document
from browser.template import Template

Template(document["team"]).render(name="Liverpool FC")
Template("team").render(name="Liverpool FC")   # element given by id works too
```

Rules:

- rendering uses f-strings, so literal braces must be doubled: `{{these are literal braces}}`
- tag attributes can be variables: `<a id="link" href="{url}">{name}</a>`
- any valid Python expression works: `{tag.upper()}`
- valueless attributes (`selected`, ...) take a boolean expression: `<option selected="{name==expected}">`

**Includes** — share fragments between pages with `b-include`:

```xml
<div id="menu" b-include="menu.html"></div>
```

The included template is rendered with the parent's arguments: `Template("menu").render(title="Home page")`.

**Code blocks** — `b-code` attributes hold `for`, `if`/`elif`/`else` blocks (nestable):

```xml
<ul id="team-list">
    <li b-code="for team in teams:">{team}
</ul>
```

**Event handlers** — pass handler functions as the second argument of `Template`, and declare them with `b-on` (`event:function`, several separated by `;`):

```xml
<button id="hello" b-on="click:say_hello">Hello !</button>
<button id="counter" b-on="click:incr">+1</button>{counter}
```

```python
def say_hello(event, element):
    alert(element.data.text)      # data comes from render(**kwargs)

def incr(event, element):
    element.data.counter += 1     # changing element.data re-renders the template

Template("hello", [say_hello]).render(text="Hello, world !")
Template("counter", [incr]).render(counter=0)
```

Handler signature: `(event, element)` where `element` is the `Template` instance; `element.data` exposes the `render()` kwargs.

## browser.widgets.dialog

- `InfoDialog(title, message, *, top=None, left=None, default_css=True, remove_after=None, ok=False)` — info popup; `remove_after` seconds auto-closes; `ok` boolean or button label string
- `EntryDialog(title, message=None, *, top=None, left=None, default_css=True, ok=True)` — prompt with entry zone; fires event `"entry"` on Ok/Enter; the entered text is in `dialog.value`

```python
from browser import bind
from browser.widgets.dialog import EntryDialog, InfoDialog

d = EntryDialog("Test", "Name")

@bind(d, "entry")
def entry(ev):
    value = d.value
    d.close()
    InfoDialog("Test", f"Hello, {value} !")
```

- `Dialog(title, *, top=None, left=None, default_css=True, ok_cancel=False)` — generic box; add content to `d.panel`; `d.ok_button` (bind its `"click"`), `d.cancel_button`, `d.close_button`, `d.title_bar`; `ok_cancel=True` or a 2-string list labels the buttons

With `default_css=False`, style via the CSS classes `brython-dialog-main`, `brython-dialog-title`, `brython-dialog-close`, `brython-dialog-panel`, `brython-dialog-message`, `brython-dialog-button` (CSS custom properties `--brython-dialog-*` tune the defaults).

## browser.widgets.menu

`Menu(container=document.body, default_css=True)` builds a horizontal navigation bar with drop-down submenus:

- `menu.add_item(label, callback=None)` — item; callback takes the event
- `menu.add_link(label, href)` — link item
- `menu.add_menu(label)` — submenu (also a `Menu`, so methods nest)

```python
from browser import document
from browser.widgets.menu import Menu

menu = Menu(document["zone"])
file_menu = menu.add_menu("File")
file_menu.add_item("Open")
save_menu = file_menu.add_menu("Save")
save_menu.add_item("choice 1")
```

Customize with `default_css=False` and the `brython-menu-*` CSS classes / `--brython-menu-*` variables.

## browser.webcomponent

Creates custom HTML tags (standard Web Components). The tag name must contain a dash.

```python
from browser import html, webcomponent

class BoldItalic:
    def __init__(self):
        shadow = self.attachShadow({'mode': 'open'})
        shadow <= html.B(html.I(self.attrs['data-val']))

webcomponent.define("bold-italic", BoldItalic)
```

- `define(tag_name, component_class[, options])` — `options` supports `"extends"`; if the class inherits a `browser.html` class, `extends` is added automatically with the base class name
- `get(tag_name)` — return the registered class or `None`
- lifecycle callbacks are ordinary class methods: `connectedCallback()`, etc.
- attribute observation: class attribute `observedAttributes = ["data"]` plus method `attributeChangedCallback(self, name, old, new, ns)`

Shadow DOM subtrees use the same `<=` operator as the main DOM.

## browser.svg

SVG elements as lowercase classes: `a, circle, clipPath, defs, ellipse, g, image, line, linearGradient, mask, path, pattern, polygon, polyline, radialGradient, rect, stop, svg, text, tspan, use`, plus animation elements (`animate`, `animateMotion`, `animateTransform`, ...). Hyphenated SVG attributes become underscores (`text_anchor` for `text-anchor`).

```python
from browser import document, svg

title = svg.text("Title", x=70, y=25, font_size=22, text_anchor="middle")
circle = svg.circle(cx=70, cy=120, r=40, stroke="black", stroke_width="2", fill="red")
panel = document["panel"]          # <g id="panel"> inside an <svg> zone
panel <= title
panel <= circle
```

Note: SVG attribute values are strings; when animating with `timer.set_interval`, convert explicitly (`int(rect.attrs["y"])`).
