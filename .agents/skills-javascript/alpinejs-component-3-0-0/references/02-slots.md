# Slot System

Slots are resolved by manual projection, not the native `<slot>` mechanism. At render time the plugin collects every `<slot>` in the component fragment — including inside nested `<template>` content, which `querySelectorAll` skips — and replaces each with the matching host-side content.

## Declaring slot content

Slot content is authored on the host element as `<template x-slot>` elements. Only **direct children** of the host are captured (`:scope > template[x-slot]`), and the templates are removed from the host before rendering:

```html
<div x-component="'card'">
  <template x-slot>
    <p>Default slot content</p>
  </template>

  <template x-slot="actions">
    <button>Save</button>
  </template>
</div>
```

- `x-slot` (no value) fills `<slot>` elements with no `name`
- `x-slot="name"` fills `<slot name="name">`
- Multiple `x-slot` templates with the same name are merged (appended in order), not replaced
- Non-slot host children are not projected; they are discarded when the component mounts

## Fallback content

A `<slot>` with no matching host content keeps its own children as fallback:

```html
<template id="card">
  <article>
    <slot></slot>
    <footer>
      <slot name="actions">No actions</slot>
    </footer>
  </article>
</template>
```

If the host provides no `x-slot="actions"`, the literal `No actions` renders.

## Scope

Slot content is authored on the host, so it evaluates against the **host's** Alpine scope even after projection — the plugin rebinds each projected element to the host's scope.

Exception — a `<slot>` nested inside `x-for` or `x-if`:

```html
<div x-data="{ label: 'host' }">
  <div x-component="'row-list'">
    <template x-slot="cell">
      <span x-text="label"></span>  <!-- Renders the component's label, not 'host' -->
    </template>
  </div>
</div>

<template id="row-list">
  <ul x-data="{ label: 'component', rows: [1, 2] }">
    <template x-for="row in rows">
      <li><slot name="cell"></slot></li>
    </template>
  </ul>
</template>
```

The slot is still filled and repeated for every iteration, but the content sees the surrounding **component** scope. Alpine clones `x-for`/`x-if` templates with `cloneNode`, which drops the host-scope binding stored as an expando. This is a documented known bug: keep slots out of `x-for` and `x-if` if they need host data.
