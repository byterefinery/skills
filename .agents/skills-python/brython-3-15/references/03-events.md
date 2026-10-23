# Events

## Binding

Every element has three methods:

```python
elt.bind("click", handler)        # handler called on the event
elt.unbind("click", handler)      # omit handler to remove all handlers for the event
elt.events("click")               # list of handlers for the event
```

The handler takes one argument: a `DOMEvent` instance. The `browser` module also provides a decorator:

```python
from browser import document, bind

@bind(document["zone"], "mouseover")     # a DOMNode target
def mouseover(ev): ...

@bind("div.foo", "click")                # a CSS selector string — binds to ALL matching elements
def enter(ev): ...
```

## DOMEvent

Common attributes (per the MDN Event reference):

- `bubbles`, `cancelable` — booleans
- `target` — element the event was dispatched on
- `currentTarget` — element the handler is attached to (differs from `target` during bubbling/capturing)
- `defaultPrevented` — whether `preventDefault()` was called
- `eventPhase` — integer phase of the event flow
- `timeStamp` — ms since the document's lifetime began
- `type` — event name string

Mouse events additionally expose `x`, `y` (mouse position relative to the window's upper-left corner).

Methods: `ev.preventDefault()` (suppress the default action) and `ev.stopPropagation()` (stop bubbling to parents).

Creating and firing events:

```python
from browser import window
event = window.MouseEvent.new("click")   # MouseEvent is a JS constructor → .new
element.dispatchEvent(event)
```

## Event types

**Mouse** — `mouseenter` / `mouseleave` (enter/leave the element itself), `mouseover` / `mouseout` (element or its children), `mousemove`, `mousedown`, `mouseup`, `click`, `dblclick`.

**Keyboard** — `keydown` (any key pressed), `keypress` (only keys that produce a character, e.g. of Ctrl+C only C), `keyup` (released). `DOMEvent` attributes documented for keyboard events: `altKey`, `ctrlKey`, `shiftKey`, `key`, `code` (see MDN KeyboardEvent for the full set).

**Focus** — `focus`, `blur` (element gains/loses focus).

**Drag and drop** — `drag` (being dragged), `dragend` (drag ended), `dragenter` / `dragleave` (enters/leaves a valid drop target), `dragover` (dragged over the target), `dragstart` (drag begins), `drop` (dropped on the target). Drag events expose `ev.dataTransfer`, a data store with:

- `dropEffect` — `"copy"`, `"move"`, `"link"`, `"none"`; settable in `dragenter`/`dragover`
- `effectAllowed` — `"copy"`, `"move"`, `"link"`, `"copyLink"`, `"copyMove"`, `"linkMove"`, `"all"`, `"none"`, `"uninitialized"`; typically set in `dragstart`
- `files` — list of local files being dragged (empty list otherwise; invalid index → `None`)
- `getData(type)` / `setData(type, value)` — typed data exchange

The draggable element must have its `draggable` property set to `True`. A typical pattern (per the cookbook drag & drop recipe): `source.draggable = True`, call `ev.dataTransfer.setData("text", ...)` in `dragstart`, `ev.preventDefault()` in `dragover` to allow the drop, and read with `getData` in `drop`.
