# JSX and Transform

Solid uses JSX syntax but compiles it differently from React. The JSX transform generates efficient DOM operations directly, not a Virtual DOM tree.

## JSX Runtime

Solid uses the standard JSX runtime (`solid-js/jsx-runtime`). Configure your build tool to use Solid's transformer:

### Vite

```js
// vite.config.ts
import { defineConfig } from "vite";
import solid from "vite-plugin-solid";

export default defineConfig({
  plugins: [solid()],
});
```

### Webpack / Babel

```js
// babel.config.js
module.exports = {
  presets: [
    ["solid", {
      generate: "dom",       // "dom" (default) or "universal"
      preserveAttributeCase: false,
    }],
  ],
};
```

### tsconfig.json / jsconfig.json

```json
{
  "compilerOptions": {
    "jsx": "preserve",
    "jsxImportSource": "solid-js",
    "module": "ESNext",
    "moduleResolution": "bundler"
  }
}
```

## How Solid's JSX Differs from React's

| Aspect | React | Solid |
|---|---|---|
| JSX output | `React.createElement()` calls | Direct DOM operations |
| Re-render | Full component re-execution | Signal-driven fine-grained updates |
| `key` prop | Required for list items | No `key` — use `<For>` or `<Index>` |
| `children` | Passed as prop | Passed as prop (same) |
| Event handlers | `onClick={handler}` | `onClick={handler}` (same syntax) |
| Spread attrs | `{...props}` | `{...props}` (same syntax) |
| Fragments | `<>...</>` or `<Fragment>` | `<>...</>` (same) |

## Event Handlers

```tsx
<button
  onClick={(e) => console.log(e.currentTarget)}
  onDoubleClick={handleDblClick}
  onMouseEnter={handleEnter}
  onKeyPress={handleKey}
>
  Click me
</button>
```

- Standard DOM event names, prefixed with `on`
- Event objects are native DOM events (not synthetic)
- Handlers are fine-grained — only re-bound when the specific handler signal changes

### Event Delegation

Solid uses event delegation at the root level. Event handlers are not attached to individual elements — they're handled at the container level. This is transparent to the developer.

## Spread Attributes

```tsx
const props = { class: "btn", disabled: true, "aria-label": "Submit" };

<button {...props}>Click</button>
```

- Spread attributes are applied reactively
- Only changed attributes are updated on the DOM element
- Event handlers in spreads are properly delegated

### Spread Gotchas

```tsx
// This tracks the entire `props` object
<button {...props}>Click</button>

// Use splitProps for fine-grained tracking
const [local, others] = splitProps(props, "onClick", "class");
<button {...others} onClick={local.onClick} class={local.class}>Click</button>
```

## Attribute Handling

### Class and Style

```tsx
<div class="base" classList={{ active: isActive(), disabled: isDisabled() }} />
<div style={{ color: color(), [`--${theme()}-size`]: size() }} />
```

- `classList` — toggles classes based on boolean values (reactive)
- `style` — accepts an object; individual properties update reactively
- `class` — full class string replacement

### Boolean Attributes

```tsx
<input disabled={true} />    // <input disabled>
<input disabled={false} />   // <input> (attribute removed)
<input disabled={cond()} />  // reactive toggle
```

Boolean attributes (`disabled`, `checked`, `selected`, `readOnly`, etc.) are added/removed based on truthiness.

### DOM Properties vs Attributes

```tsx
// Sets the property (reactive)
<input value={signal()} />

// For non-reactive initial value
<input value="static" />
```

Solid distinguishes between attributes and properties. `value`, `checked`, `selected` set DOM properties (not attributes) for form elements.

## JSX Types

```ts
import type { JSX } from "solid-js";

// Element type
type JSXElement = JSX.Element;

// Custom element definitions
declare module "solid-js" {
  namespace JSX {
    interface IntrinsicElements {
      "my-custom": {
        "on:change": (e: CustomEvent) => void;
        "my-prop"?: string;
      };
    }
  }
}
```

## Directive Functions

Solid supports custom JSX directives via the `use:` namespace (through `solid-js/web`):

```tsx
import { use } from "solid-js/web";

// Custom directive
function myDirective(element: Element, value: Accessor<boolean>) {
  createEffect(() => {
    element.style.opacity = value() ? "1" : "0";
  });
}

<div use:myDirective={show()} />
```

## Template Elements

```tsx
// <template> is supported
<template>
  <div>This is a template</div>
</template>

// Access template content
let template: HTMLTemplateElement;
<div ref={el => { template = el; }}>
  {template.content.cloneNode(true)}
</div>
```

## Fragment

```tsx
// Shorthand
<>
  <div>A</div>
  <div>B</div>
</>

// Explicit
<Fragment>
  <div>A</div>
  <div>B</div>
</Fragment>
```

## Gotchas

- **No `key` prop** — Solid doesn't use `key` for list identification. Use `<For>` (keyed) or `<Index>` (non-keyed). Adding `key` to elements has no effect.
- **JSX is compiled, not runtime** — Solid's JSX is transformed at build time into DOM operations. The `solid-js/jsx-runtime` is used during compilation, not at runtime.
- **Event handlers are native** — Solid uses native DOM events, not synthetic events. Event pooling doesn't apply; event properties are always available.
- **`className` vs `class`** — Solid uses `class` (not `className`). The JSX transform handles this.
- **`htmlFor` vs `for`** — Use `for` in Solid JSX (not `htmlFor`).
- **Self-closing tags** — Void elements (`<br/>`, `<img/>`, `<input/>`) must be self-closing. Solid doesn't auto-complete them.
- **JSX expressions are tracked** — `{count()}` inside JSX creates a reactive binding. The text node updates when `count` changes, without re-rendering the parent component.
- **`babel-preset-solid` vs native transform** — Vite's `vite-plugin-solid` uses the native JSX transform. Webpack/Babel setups need `babel-preset-solid`. Both produce the same output.
