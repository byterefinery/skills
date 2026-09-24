# DOM rendering, refs, attributes, events

## render / hydrate

```ts
import { render, hydrate, Portal } from "@solidjs/web";

const dispose = render(() => <App />, document.getElementById("root")!); // fresh mount
hydrate(() => <App />, document.getElementById("root")!);               // claim server-rendered DOM
```

`render`/`hydrate` also **own event delegation**: delegated listeners are installed on the root container and disposed with the root (the 1.x document-global model with `clearDelegatedEvents()` is gone — dispose the root instead).

`Portal` registers outside-root mount points as listener containers for the owning render root; it **throws on the server**.

## Refs and directives

Refs are callback functions. `use:` directives are removed — directives are **ref directive factories**:

```jsx
// Element access
<button ref={el => (myButton = el)} />

// Directive factory (replaces use:tooltip={...})
<input ref={autofocus} />
<button ref={tooltip({ content: "Save" })} />

// Compose — arrays (nestable)
<button ref={[autofocus, tooltip({ content: "Save" })]} />
```

### Two-phase directive factories (recommended)

Setup phase (owned) creates primitives/subscriptions; apply phase (unowned) does DOM writes. Don't mix the two:

```ts
function titleDirective(source) {
  // Setup (owned): create primitives; avoid imperative DOM mutation at top level
  let el;
  createEffect(source, value => {
    if (el) el.title = value; // effect can run before the element exists
  });
  // Apply (unowned): DOM writes only; create no primitives here
  return nextEl => {
    el = nextEl;
    el.title = source();
  };
}

// <button ref={titleDirective(() => props.title)} />
```

Native event listener options also live in ref callbacks:

```ts
const on = (type, handler, options) => el => el.addEventListener(type, handler, options);

<button ref={on("click", handleClick, { capture: true })} />
```

## Attributes — HTML standards by default

- **Attributes over properties**, generally **lowercase** built-in names (`tabindex`, not `tabIndex`).
- **Boolean attributes are presence/absence** — `muted={true}` adds, `muted={false}` removes (no `="true"` strings). When the platform requires the string: `enabled="true"`.
- `attr:`, `bool:`, `on:`, `oncapture:` namespaces and the tolerated `class:`/`style:` syntax are **removed**.
- Form stateful properties remain props (special-cased to avoid confusion): `input.value`, `input.defaultValue`, `input.checked`, `input.defaultChecked`, `select.value`, `option.value`, `option.selected`, `option.defaultSelected`, `textarea.value`, `textarea.defaultValue`, `video.muted`, `video.defaultMuted`, `audio.muted`, `audio.defaultMuted`.
- SVG/MathML work as expected; Solid adds `xmlns` automatically to recognizable tags.
- `/*@once*/` is out of the public JSX model — keep reactive reads reactive; use DOM default props (`defaultValue`) for initial state; use `untrack` for a deliberate one-time JS read.

## class — object/array forms (classList removed)

```jsx
<div class="card" />                                             // static string
<div class={{ active: isActive(), invalid: !valid() }} />        // object: toggle by truthiness
<div class={["card", props.class, { active: isActive() }]} />    // array: merge entries
```

Don't build class strings manually — string concatenation, template literals, and `.join(" ")` over conditionals are the React/`classnames` reflex. The array+object form composes reactively.

```jsx
<li class={["todo", { completed: props.todo.completed, errored: !!err() }]} /> // ✅
```

## Events

- CamelCase handlers (`onClick`, `onInput`) use Solid's delegated path — unchanged.
- Delegation is root-owned: nested roots don't synthesize events across each other; rendering into a `ShadowRoot` scopes delegation to that shadow root.
- Compiler-emitted `delegateEvents([...])` only declares which event names are needed; physical listener lifetime belongs to render roots.
- `event.stopPropagation()` inside a nested root can prevent outer roots/host page code from seeing the native event.
- For native listener options (capture, once, passive) use ref callbacks instead of `on:`/`oncapture:`.
