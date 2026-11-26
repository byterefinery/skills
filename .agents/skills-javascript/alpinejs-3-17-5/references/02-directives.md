# Directives (Alpine.js 3.17.5)

All core directives, with modifiers and examples. Most directives require an `x-data` ancestor (the component root).

## x-data

Defines a chunk of HTML as an Alpine component and provides its reactive data.

```html
<div x-data="{ open: false, toggle() { this.open = ! this.open }, get isOpen() { return this.open } }">
    <button @click="toggle">Toggle</button>   <!-- parens optional: @click="toggle" -->
    <div x-show="isOpen">Content...</div>
</div>
```

- **Scope** — properties are available to all descendants, including nested `x-data` components; a child property shadows a same-named parent property.
- **Methods & getters** — the value is a normal JS object: methods (called with or without parens) and getters work; use `this.` to reference sibling properties inside the object.
- **Data-less** — bare `x-data` (no value) makes an element a component root without data.
- **Single-element** — `x-data` may sit directly on the only element of the component.
- **Re-usable** — extract the object with `Alpine.data('name', ...)`, then `x-data="name"` (or `x-data="name(param)"`).

## x-on (event listeners)

```html
<button x-on:click="alert('Hello')">Say Hi</button>
<button @click="alert('Hello')">Say Hi</button>   <!-- shorthand: @ -->
```

- Listen for **any** DOM event by name (`@keyup`, `@mouseenter`, custom events, ...). Event names are lowercase because HTML attributes are case-insensitive.
- **`$event`** — the native event object is injected: `@click="$event.target.remove()"`. Methods referenced without parens also receive the event as their first argument.
- **Keyboard modifiers** — any `KeyboardEvent.key` value in kebab-case: `@keyup.enter`, `@keyup.shift.enter`, `@keyup.page-down`. Common: `.shift .enter .space .ctrl .cmd .meta .alt .up .down .left .right .escape .tab .caps-lock .equal .period .comma .slash`.
- **Mouse modifiers** — `.shift .ctrl .cmd .meta .alt` work on `click`, `auxclick`, `context`, `dblclick`, and `mouseover/mousemove/mouseenter/mouseleave/mouseout/mouseup/mousedown`.
- **Custom events** — `@foo="..."` listens to `CustomEvent('foo')`; use `$dispatch('foo')` to fire (see magics).
- **Modifiers**:
  - `.prevent` — `event.preventDefault()` (e.g. `@submit.prevent`)
  - `.stop` — `event.stopPropagation()`
  - `.outside` — fire only for clicks **outside** the element (evaluates only while the element is visible)
  - `.window` / `.document` — register the listener on `window` / `document` instead of the element
  - `.once` — handler runs at most once
  - `.debounce[.Nms]` — fire after N ms of inactivity (default 250ms)
  - `.throttle[.Nms]` — fire at most every N ms (default 250ms)
  - `.self` — only when the event originated on the element itself, not a child
  - `.camel` — camelCase the event name (`@custom-event.camel` listens for `customEvent`)
  - `.dot` — dotted event names (`@custom-event.dot` listens for `custom.event`)
  - `.passive` — passive listener (touch/wheel performance); `.passive.false` to make them cancelable again
  - `.capture` — run during the capturing phase

## x-bind (attribute binding)

```html
<input x-bind:placeholder="placeholderText">
<input :placeholder="placeholderText">   <!-- shorthand: : -->
```

- **Class binding** — `:class="open ? '' : 'hidden'"` or short-circuit `:class="show || 'hidden'"`; string syntax **preserves** existing classes on the element.
- **Class object syntax** — `:class="{ 'hidden': ! show }"`; does **not** preserve original classes (only the object's keys are kept) — the intended way to toggle a class that existed before Alpine loaded.
- **Style binding** — `:style="{ color: 'red', display: 'flex' }"`; object syntax merges with existing inline styles; short-circuit also works (`:style="true && { color: 'red' }"`).
- **Binding whole directive objects** — `x-bind` with no attribute binds an object of directives/attributes; values are strings or callbacks:

  ```js
  trigger: {
      ['x-ref']: 'trigger',
      ['@click']() { this.open = true }
  }
  ```

  When binding `x-for` this way, the callback returns the expression **string** (`['x-for']() { return 'item in items' }`).

## x-model (two-way input binding)

Works with `<input type="text">`, `<textarea>`, `<input type="checkbox">`, `<input type="radio">`, `<select>`, `<input type="range">`. Two-way: typing updates the property; changing the property updates the input.

- **Checkboxes** — single checkbox binds a boolean; multiple checkboxes with the same `x-model` bind an array of their `value`s.
- **Selects** — single or `multiple`; placeholder via `<option value="" disabled>`.
- **Modifiers**:
  - `.lazy` — sync on focus-out (equivalent to the native `change` event)
  - `.change` — sync only when the input loses focus **and** its value changed
  - `.blur` — sync when the input loses focus, regardless of change
  - `.enter` — sync when Enter is pressed (does **not** prevent form submission)
  - event modifiers combine: `x-model.blur.enter="search"`
  - `.number` — store as JS number
  - `.boolean` — store as JS boolean (1/0 or true/false values)
  - `.debounce[.Nms]` (default 250ms) / `.throttle[.Nms]` (default 250ms)
  - `.fill` — if the bound property is empty, seed it from the input's `value` attribute (otherwise the attribute is ignored)
- **Programmatic** — `el._x_model.get()` / `el._x_model.set(value)` expose the bound property for custom inputs.
- Custom components can feed `x-model` by dispatching an `input` event: `@change="$dispatch('input', value)"`.

## x-for (looping)

```html
<ul x-data="{ colors: ['Red', 'Orange'] }">
    <template x-for="color in colors">
        <li x-text="color"></li>
    </template>
</ul>
```

- **MUST** be on a `<template>` element whose **only** content is a single root element.
- **Objects** — `x-for="(value, index) in car"`.
- **Index** — `x-for="(item, index) in items"`; `index` is also available in `:key`.
- **Range** — `x-for="i in 10"` loops 10 times.
- **Keys** — `:key="item.id"` is important when items are reordered/added/removed; keeps DOM nodes and state matched.

## x-if (conditional DOM)

```html
<template x-if="open">
    <div>Contents...</div>
</template>
```

- Adds/removes the element from the DOM entirely (vs `x-show`'s `display: none`).
- **MUST** be on a `<template>` with a single root element.
- **No `x-transition` support** — unlike `x-show`, toggling cannot be animated with `x-transition`.

## x-show (visibility toggle)

```html
<div x-show="open">Contents...</div>
```

- Hides via inline `display: none`; the element stays in the DOM.
- `.important` — sets `display: none !important` to beat CSS that uses `!important`.
- Combine with `x-transition` for animated toggles.
- If the default on-page state is hidden, consider `x-cloak` to avoid a "flicker" before Alpine boots.

## x-text / x-html

```html
<strong x-text="username"></strong>          <!-- text content, auto-escaped -->
<span x-html="htmlString"></span>           <!-- innerHTML — XSS risk, trusted content only -->
```

## x-transition

Animated show/hide, **only with `x-show`**.

**Transition helper** — bare `x-transition` applies fade+scale defaults (150ms enter / 75ms leave):

```html
<div x-show="open" x-transition.duration.500ms>...</div>

<div x-show="open"
    x-transition:enter.duration.500ms
    x-transition:leave.duration.400ms>...</div>
```

- `.duration.Nms` — duration (shared or per-phase via `:enter` / `:leave`)
- `.delay.Nms` — delay
- `.opacity` — opacity only (no scale); `.scale` — scale only; `.scale.80` — scale percent; `.origin.top` / `.origin.top.right` — transform origin (`top|bottom|left|right`, two combinable)

**Transition classes** — full control with per-phase classes (Tailwind example):

```html
<div
    x-show="open"
    x-transition:enter="transition ease-out duration-300"
    x-transition:enter-start="opacity-0 transform scale-90"
    x-transition:enter-end="opacity-100 transform scale-100"
    x-transition:leave="transition ease-in duration-300"
    x-transition:leave-start="opacity-100 transform scale-100"
    x-transition:leave-end="opacity-0 transform scale-90"
>...</div>
```

Phase semantics:

| Directive | Description |
| --- | --- |
| `:enter` | Applied during the entire entering phase. |
| `:enter-start` | Added before element is inserted, removed one frame after. |
| `:enter-end` | Added one frame after insertion (when `enter-start` is removed), removed when transition/animation finishes. |
| `:leave` | Applied during the entire leaving phase. |
| `:leave-start` | Added immediately when leaving is triggered, removed after one frame. |
| `:leave-end` | Added one frame after leaving is triggered (when `leave-start` is removed), removed when the transition/animation finishes. |

## x-init

Run code when an element initializes (before further DOM updates). Works on any element, inside or outside an `x-data` block.

```html
<div x-data="{ posts: [] }" x-init="posts = await (await fetch('/posts')).json()">
```

- Supports `await`.
- Use `$nextTick(() => ...)` inside to wait for Alpine's DOM updates (React `useEffect(..., [])` / Vue `mount` equivalent).
- If the `x-data` object has an `init()` method it runs **before** the `x-init` directive on the same element.

## x-effect

Re-runs its expression whenever any Alpine data it reads changes. Runs immediately on load (unlike `$watch`, which is lazy) and has no old value.

```html
<div x-data="{ label: 'Hello' }" x-effect="console.log(label)">
```

## x-cloak

Hides an element until Alpine finishes loading, preventing "page flicker" of uninitialized templates.

- Requires this CSS rule on the page: `[x-cloak] { display: none !important; }`
- Alpine removes `x-cloak` from the DOM at boot.
- Alternative without global CSS: `<template x-if="true"><span x-text="message"></span></template>` (templates are hidden by browsers until Alpine renders them).

## x-ref + $refs

```html
<button @click="$refs.text.remove()">Remove Text</button>
<span x-ref="text">Hello 👋</span>
```

Named handles for DOM elements within a component. In v3 refs must be **static** — a dynamic expression like `x-ref="item.name"` stores the literal string, not the evaluated value.

## x-id + $id

Generates page-unique IDs for repeatable components (inputs, modals, listboxes).

```html
<div x-id="['text-input']">
    <label :for="$id('text-input')">Username</label>   <!-- for="text-input-1" -->
    <input type="text" :id="$id('text-input')">         <!-- id="text-input-1" -->
</div>
```

- `x-id` takes an **array** of ID names and declares an "id scope"; nesting creates new groups.
- `$id('name', key)` — optional second parameter appends a suffix (keyed IDs for loops, e.g. `aria-activedescendant`).

## x-teleport

Moves part of a template to another part of the DOM (modals, escaping z-index).

```html
<div x-data="{ open: false }">
    <button @click="open = ! open">Toggle Modal</button>

    <template x-teleport="body">
        <div x-show="open">Modal contents...</div>
    </template>
</div>
```

- The argument is any `querySelector`-style selector (`body`, `.my-class`, `#my-id`).
- Teleported content keeps the component's Alpine scope (`$refs`, `$root`, ...).
- **Event forwarding** — register listeners on the `<template x-teleport>` element itself; Alpine re-dispatches events from the teleported DOM through the template.
- **Nesting** — nested teleports render as siblings on the page, not inside each other.

## x-ignore

Prevents Alpine from initializing a subtree:

```html
<div x-data="{ label: 'From Alpine' }">
    <div x-ignore>
        <span x-text="label"></span>   <!-- stays as literal markup -->
    </div>
</div>
```

## x-modelable

Exposes component state as the target of a parent's `x-model` — useful for abstracting components into backend templates (Laravel Blade etc.).

```html
<div x-data="{ number: 5 }">
    <div x-data="{ count: 0 }" x-modelable="count" x-model="number">
        <button @click="count++">Increment</button>
    </div>
    Number: <span x-text="number"></span>
</div>
```

- Values cross the boundary as **JSON clones** — only JSON-compatible state (strings, numbers, booleans, null, arrays, plain objects) survives. `File`, `FileList`, `Map`, `Set`, `Date`, class instances, DOM nodes do not cross intact.
- For custom inputs producing such values, omit `x-modelable` and dispatch `input` instead: `@change="$dispatch('input', Array.from($event.target.files))"` — `x-model` reads the value directly from the event without cloning.
