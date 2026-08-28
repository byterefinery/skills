# Alpine.js 3.16.3 — Core Directives

- [x-data](#x-data)
- [x-on / @](#x-on--at)
- [x-bind / :](#x-bind--colon)
- [x-model](#x-model)
- [x-modelable](#x-modelable)
- [x-for](#x-for)
- [x-if](#x-if)
- [x-show](#x-show)
- [x-text / x-html](#x-text--x-html)
- [x-transition](#x-transition)
- [x-teleport](#x-teleport)
- [x-effect](#x-effect)
- [x-init](#x-init)
- [x-id](#x-id)
- [x-ref](#x-ref)
- [x-ignore](#x-ignore)
- [x-cloak](#x-cloak)

All directives below (except `x-init` and `x-cloak`, which also work standalone) require an `x-data` ancestor. Expressions are plain JavaScript evaluated against the nearest data scope.

## x-data

Defines a component: reactive state, methods, and getters in one attribute.

```html
<div x-data="{ open: false, toggle() { this.open = ! this.open }, get isOpen() { return this.open } }">
    <button @click="toggle">Toggle</button>
    <div x-show="isOpen">Content...</div>
</div>
```

- Bare `x-data` (no value) or `x-data="{}"` creates a data-less component — still required for child directives.
- Scope nesting: children inherit parent properties; a same-named child property shadows the parent's.
- `this.` is required inside the `x-data` object itself; bare names work in directive expressions.
- Getters (`get foo()`) behave like computed properties (not cached).
- An `init()` method in the object is auto-called on component initialization.

## x-on / @

Listens for any DOM event. Shorthand: `@` replaces `x-on:`.

```html
<button @click="count++">Increment</button>
```

The event object is `$event`; a bare method reference without parens also receives it: `@click="handleClick"` with `handleClick(e) {...}`.

### Modifiers

| Modifier | Behavior |
|---|---|
| `.prevent` | `event.preventDefault()` |
| `.stop` | `event.stopPropagation()` |
| `.self` | Only if `event.target === el` |
| `.once` | Listener removes itself after first call |
| `.window` / `.document` | Register on `window` / `document` instead of the element |
| `.outside` | Fires when click happens outside the element (only evaluated while the element is visible) |
| `.debounce` / `.debounce.500ms` | Call after inactivity (default 250 ms) |
| `.throttle` / `.throttle.500ms` | Call at most every interval (default 250 ms) |
| `.passive` / `.passive.false` | Force passive (or cancelable) for touch/wheel listeners |
| `.capture` | Run in the capturing phase |
| `.camel` | CamelCase the event name (`@my-event.camel` → `myEvent`) |
| `.dot` | Literal dot in the event name (`@custom-event.dot` → `custom.event`) |

Key modifiers on `keydown`/`keyup` (chained, e.g. `@keyup.shift.enter`): `.shift .enter .space .ctrl .cmd .meta .alt .up .down .left .right .escape .tab .caps-lock .equal .period .comma .slash` — any `KeyboardEvent.key` works kebab-cased (`.page-down`).

The same key modifiers (`.shift .ctrl .cmd .meta .alt`) work on `click`, `auxclick`, `dblclick`, `contextmenu`, and mouse move/enter/leave/out/up/down events.

Custom events are plain DOM events: `@foo="..."` listens for `foo`; `$dispatch('foo', detail)` fires them (see magics).

## x-bind / :

Binds attributes to expressions. Shorthand: `:` replaces `x-bind:`.

```html
<input :placeholder="placeholderText" :disabled="busy" :aria-expanded="open">
```

`x-bind` also accepts an object (direct or named via `Alpine.bind`): each key is an attribute or directive, each value an expression/function.

```html
<button x-bind="SomeButton"></button>
<script>
Alpine.bind('SomeButton', () => ({
    type: 'button',
    '@click'() { this.doSomething() },
    ':disabled'() { return this.shouldDisable },
}))
</script>
```

### Class binding

```html
<span :class="open ? 'block' : 'hidden'">...</span>
<span :class="{ 'hidden': ! open }">...</span>
```

- Object syntax keeps **only** the classes in the object (original `class` attribute is dropped) — useful for pre-Alpine classes.
- String/short-circuit syntax **preserves** existing classes (unlike other attributes, `:class` never fully overwrites).
- Short-circuit works in both directions: `:class="open && 'block'"` ≡ `open ? 'block' : ''`.

## x-model

Two-way binding for form controls.

```html
<input type="text" x-model="message">
<textarea x-model="message"></textarea>
<input type="checkbox" x-model="show">            <!-- boolean -->
<input type="checkbox" value="red" x-model="colors">  <!-- array membership -->
<input type="radio" value="yes" x-model="answer">
<select x-model="color">
    <option>Red</option>
</select>
<select x-model="colors" multiple>...</select>
```

- The bound property **overrides** the input's `value` attribute; `x-model.fill="msg"` seeds an empty property from the attribute.
- Checkbox bound to an array toggles membership by the input's `value` attribute.
- Works on `<input type="file">` and selects with dynamic `x-for` options.

### Modifiers

| Modifier | Behavior |
|---|---|
| `.lazy` / `.change` | Sync only on native `change` (blur + value changed); equivalent |
| `.blur` | Sync on blur regardless of change |
| `.enter` | Sync on Enter (does not prevent form submit) |
| `.lazy.change` etc. | Event modifiers can be combined (`x-model.blur.enter`) |
| `.number` | Coerce to `Number` |
| `.boolean` | Coerce to `Boolean` (accepts 1/0, 'true'/'false') |
| `.debounce` / `.debounce.500ms` | Defer updates (default 250 ms) |
| `.throttle` / `.throttle.500ms` | Cap update rate (default 250 ms) |
| `.fill` | Populate empty property from `value` attribute at init |
| `.unintrusive` | Don't overwrite the DOM value if the user is editing |

## x-modelable

Makes a custom element two-way bindable so parents can use `x-model` on it:

```html
<custom-input x-modelable="value" @change="$dispatch('input', value)"></custom-input>
```

The parent writes `<custom-input x-model="answer"></custom-input>`; Alpine wires the child's `value` prop back through the dispatched `input` event. Values cross the boundary via JSON clone, so only JSON-safe data (strings, numbers, booleans, `null`, arrays, plain objects) is supported. For `File`/`FileList`/`Date`/class instances, skip `x-modelable` and let the parent listen: `@change="$dispatch('input', Array.from($event.target.files))"`.

## x-for

Loops over arrays, ranges, or object entries. **Must be on a `<template>`**, which must contain exactly one root element.

```html
<ul x-data="{ colors: ['Red', 'Orange'] }">
    <template x-for="(color, index) in colors" :key="color">
        <li x-text="index + ': ' + color"></li>
    </template>
</ul>

<template x-for="i in 5"><button x-text="i"></button></template>
```

- `(item, index) in list` gives the index; `i in 5` loops a range.
- `:key` is required for safe reorder/insert/remove — without it, DOM nodes and their state (inputs, focus) mismatch.
- The loop variable is scoped to the template contents.

## x-if

Adds/removes elements from the DOM. Must be on a `<template>`:

```html
<template x-if="open">
    <div>Content... <input x-model="inner"></div>
</template>
```

- True → content appended; false → removed (state inside is destroyed).
- No transitions (pair with `x-show` + `x-transition` if you need animated toggling).
- Common trick: `<template x-if="true">` defers rendering until Alpine boots (a cloak alternative).

## x-show

Toggles `display: none` without removing the element.

```html
<div x-show="open">Content...</div>
<div x-show.important="open">Content...</div>  <!-- forces display: none !important -->
```

- The element stays in the DOM (unmounted state, tab order, ARIA remain) — use `x-if` when content must not exist.
- Combine with `x-transition` for animation.

## x-text / x-html

```html
<span x-text="count"></span>          <!-- textContent, safe -->
<div x-html="trustedHtml"></div>      <!-- innerHTML — XSS risk, trusted content only -->
```

`x-text` handles numbers/booleans/`null` gracefully; `x-html` does not.

## x-transition

Only works with `x-show` (not `x-if`).

**Helper form** (sensible defaults, fade + scale from 95%):

```html
<div x-show="open" x-transition>Content</div>
<div x-show="open" x-transition.duration.500ms>Content</div>
<div x-show="open" x-transition.opacity>Content</div>
<div x-show="open" x-transition.scale.80.origin.top>Content</div>
<div x-show="open" x-transition:enter.duration.500ms x-transition:leave.duration.1000ms>Content</div>
<div x-show="open" x-transition.delay.50ms.duration.300ms>Content</div>
```

Modifiers: `.opacity` (fade only), `.scale` / `.scale.80` (scale only/from %), `.origin.center|top|bottom|...`, `.duration.Nms` (default in 150 ms / out 75 ms), `.delay.Nms`.

**Class form** (full CSS control):

```html
<div
    x-show="open"
    x-transition:enter="transition ease-out duration-300"
    x-transition:enter-start="opacity-0 transform scale-90"
    x-transition:enter-end="opacity-100 transform scale-100"
    x-transition:leave="transition ease-in duration-300"
    x-transition:leave-start="opacity-100 transform scale-100"
    x-transition:leave-end="opacity-0 transform scale-90"
>Content</div>
```

The element receives `start` classes immediately, transitions to `end` classes, and is cleaned up after the transition.

## x-teleport

Moves a `<template>`'s rendered content to a CSS-selector target (any `querySelector` string), while keeping it in the original Alpine scope.

```html
<button @click="open = ! open">Toggle Modal</button>

<template x-teleport="body" @click.outside="open = false">
    <div x-show="open" role="dialog">
        Modal contents...
    </div>
</template>
```

- The selector is resolved on init; `x-teleport="body"` is the common modal case.
- **Event forwarding**: events registered *on the `<template>` itself* (e.g. `@click.outside`) are re-dispatched from the template, so they behave as if the content were still in place.
- **Nesting**: a teleported modal can contain its own `<template x-teleport>`; rendered as siblings on the page, not nested.

## x-effect

Re-runs an expression whenever any reactive data it reads changes (dependency tracking, like `$watch` without a key):

```html
<div x-data="{ label: 'Hello' }" x-effect="console.log(label)">
    <button @click="label += ' World'">Change</button>
</div>
```

Runs immediately on init and after each change; the callback receives no old value.

## x-init

Runs code when the element initializes — before Alpine's first DOM updates for that element. Works on any element, inside or **outside** `x-data` (standalone).

```html
<div x-data="{ posts: [] }" x-init="posts = await (await fetch('/posts')).json()">...</div>
<span x-init="console.log('standalone init')">
```

- Supports `await` directly.
- `init()` methods on data objects are the object-level equivalent (called for every component using that data).
- Wait for full render with `$nextTick(() => ...)` inside `x-init`.

## x-id

Declares a namespace for `$id()` to avoid ID collisions across repeated components:

```html
<div x-data x-id="['text-input']">
    <label :for="$id('text-input')">Name</label>
    <input :id="$id('text-input')" x-model="name">
</div>
```

Without `x-id`, `$id('text-input')` already yields page-unique IDs (`text-input-1`, `-2`, ...); `x-id` groups related IDs under one shared namespace.

## x-ref

Names a DOM element for later access via `$refs`:

```html
<button @click="$refs.text.remove()">Remove</button>
<span x-ref="text">Hello</span>
```

v3 limitation: refs are resolved statically — `x-ref="item.name"` inside `x-for` stores the literal string `'item.name'`, not the item's name.

## x-ignore

Alpine skips the element and its entire subtree during init — no directives inside it are processed. Use to hand off a section to another library or to raw HTML.

```html
<div x-data="{ label: 'From Alpine' }">
    <div x-ignore>
        <span x-text="label">  <!-- untouched -->
    </div>
</div>
```

## x-cloak

Hides the element until Alpine finishes initializing, preventing a flash of uninitialized markup. Requires this CSS in your page:

```css
[x-cloak] { display: none !important; }
```

```html
<span x-cloak x-text="message"></span>
```

Alpine strips the attribute on boot. Alternative without global CSS: wrap the content in `<template x-if="true">`.
