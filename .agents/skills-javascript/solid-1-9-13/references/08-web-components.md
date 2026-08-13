# Web Components

Solid supports Web Components through `solid-element`, which provides `withSolid()` and `@customElement` for creating custom elements from Solid components.

## solid-element

The `solid-element` package bridges Solid's reactive system with the Web Components API.

### Installation

```bash
npm install solid-element solid-js
```

### withSolid

```ts
import { withSolid } from "solid-element";
import { createSignal } from "solid-js";
import { render } from "solid-js/web";

const MyCounter = withSolid(() => {
  const [count, setCount] = createSignal(0);

  return () => (
    <button onClick={() => setCount(c => c + 1)}>
      Count: {count()}
    </button>
  );
});

customElements.define("my-counter", MyCounter);
```

`withSolid()` wraps a Solid function component and returns a class extending `HTMLElement`. The Solid root is created and disposed automatically with the element's lifecycle.

### @customElement Decorator

```ts
import { customElement, withSolid } from "solid-element";
import { createSignal } from "solid-js";

@customElement("my-button")
class MyButton extends withSolid((props: { label: string }) => {
  return () => <button>{props.label}</button>;
}) {}
```

The `@customElement(tagName)` decorator defines the custom element automatically.

### Props

```ts
@customElement("my-card")
class MyCard extends withSolid((props: { title: string; count: number }) => {
  return () => (
    <div>
      <h2>{props.title}</h2>
      <span>{props.count}</span>
    </div>
  );
}) {
  static get observedAttributes() {
    return ["title", "count"];
  }
}
```

- Props are reactive — attribute changes update the Solid component
- `observedAttributes` declares which attributes trigger updates
- Props are converted to signals internally

### Slots

```ts
@customElement("my-layout")
class MyLayout extends withSolid(() => {
  return () => (
    <div class="layout">
      <header><slot name="header" /></header>
      <main><slot /></main>
      <footer><slot name="footer" /></footer>
    </div>
  );
}) {}
```

Standard HTML `<slot>` elements work inside Solid web components.

### Shadow DOM

```ts
import { noShadowDOM } from "solid-element";

// Without shadow DOM (light DOM rendering)
@customElement("my-component")
class MyComponent extends withSolid(() => {
  return () => <div>Light DOM</div>;
}, { useShadowDOM: false }) {}

// Or use noShadowDOM helper
noShadowDOM();
```

By default, `solid-element` uses Shadow DOM. Disable with `useShadowDOM: false` or `noShadowDOM()`.

### Context

```ts
import { createContext, useContext } from "solid-js";
import { customElement, withSolid } from "solid-element";

const ThemeContext = createContext("light");

@customElement("themed-component")
class ThemedComponent extends withSolid(() => {
  const theme = useContext(ThemeContext);
  return () => <div class={theme()}>Themed</div>;
}) {}
```

Solid's context system works inside web components. Parent elements can provide context values.

### Lifecycle

```ts
import { onMount, onCleanup } from "solid-js";

@customElement("my-timer")
class MyTimer extends withSolid(() => {
  const [seconds, setSeconds] = createSignal(0);

  onMount(() => {
    const id = setInterval(() => setSeconds(s => s + 1), 1000);
    onCleanup(() => clearInterval(id));
  });

  return () => <span>{seconds()}s</span>;
}) {}
```

Solid's lifecycle hooks (`onMount`, `onCleanup`) align with the element's connected/disconnected callbacks.

### getCurrentElement

```ts
import { getCurrentElement } from "solid-element";

function MyComponent() {
  const el = getCurrentElement();
  // el is the custom element instance
  createEffect(() => {
    console.log("Element tag:", el.tagName);
  });
  return <div>Content</div>;
}
```

Access the host custom element from within a Solid component.

### hot — HMR Support

```ts
import { hot } from "solid-element";

// Enable hot module replacement during development
hot(module);
```

## Pattern: Solid Component as Web Component

```ts
import { customElement, withSolid } from "solid-element";
import { createSignal, createMemo, For } from "solid-js";

interface TodoProps {
  initialTodos: string[];
}

@customElement("todo-list")
class TodoList extends withSolid((props: TodoProps) => {
  const [todos, setTodos] = createSignal(props.initialTodos || []);
  const [input, setInput] = createSignal("");

  const count = createMemo(() => todos().length);

  const addTodo = () => {
    const value = input().trim();
    if (value) {
      setTodos(t => [...t, value]);
      setInput("");
    }
  };

  return () => (
    <div class="todo-list">
      <h3>Todos ({count()})</h3>
      <form onSubmit={e => { e.preventDefault(); addTodo(); }}>
        <input
          value={input()}
          onInput={e => setInput(e.currentTarget.value)}
          placeholder="Add todo..."
        />
        <button type="submit">Add</button>
      </form>
      <For each={todos()}>
        {(todo) => <li>{todo}</li>}
      </For>
    </div>
  );
}) {}
```

Usage in HTML:

```html
<todo-list initial-todos='["Learn Solid", "Build app"]'></todo-list>
```

## Pattern: Communication Between Components

```ts
// Parent
@customElement("app-shell")
class AppShell extends withSolid(() => {
  const [data, setData] = createSignal("hello");

  return () => (
    <div>
      <child-component data={data()} />
      <button onClick={() => setData(d => d + "!")}>Update</button>
    </div>
  );
}) {}

// Child
@customElement("child-component")
class ChildComponent extends withSolid((props: { data: string }) => {
  return () => <span>{props.data}</span>;
}) {}
```

## Gotchas

- **`solid-element` is separate from `solid-js`** — install both packages
- **Props are read from attributes** — use kebab-case in HTML (`my-prop`), camelCase in TypeScript (`myProp`)
- **Shadow DOM encapsulates styles** — CSS inside the component doesn't leak out; external CSS doesn't penetrate (use `::part` for styling hooks)
- **Custom elements must be defined before use** — import the module before the element appears in HTML
- **`observedAttributes` is required for reactivity** — without it, attribute changes don't trigger Solid re-renders
- **Light DOM mode** — `noShadowDOM()` or `useShadowDOM: false` renders into the element's direct children. Useful for CSS framework integration.
