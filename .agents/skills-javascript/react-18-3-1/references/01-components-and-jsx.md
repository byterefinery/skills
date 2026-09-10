# Components and JSX

## Function components

A function component is a plain JavaScript function that takes a `props` object and returns UI. It has no `this`, no lifecycle methods, and no constructor — all state and behavior come from hooks.

```jsx
function Greeting({ name, onDone }) {
  const [open, setOpen] = useState(false);
  return (
    <button onClick={() => setOpen(!open)}>
      Hello, {name}
    </button>
  );
}
```

Rules:

- The function must be **pure with respect to its render** — given the same props and state it must produce the same output. No mutations of props, no side effects, no random values.
- It may return any `ReactNode`: JSX, strings, numbers, arrays, fragments, portals, `null`, or `undefined`. Since React 18, returning `undefined` is legal (it used to throw) — a linter should still catch accidental missing `return`s.
- It may be called as `<Greeting name="Ada" />` (props) or `Greeting({ name: 'Ada' })` via `createElement`.
- Arrow functions and function declarations both work; class components still exist for imperative escape hatches (below).
- Components must be referenced as uppercase variables in JSX (`<greeting />` is a DOM tag, `<Greeting />` is a component).

## Class components

`Component` and `PureComponent` from `react` remain fully supported in 18.3.1; most new code uses function components + hooks, but you will meet classes in libraries.

```jsx
import { Component } from 'react';

class Timer extends Component {
  static displayName = 'Timer';        // improves error messages

  constructor(props) {
    super(props);
    this.state = { seconds: 0 };
  }

  // Derived state — the only sanctioned place to sync state from props
  static getDerivedStateFromProps(props, state) {
    return { seconds: props.initialSeconds ?? state.seconds };
  }

  // Return false to skip a re-render (shallow compare)
  shouldComponentUpdate(nextProps, nextState) {
    return nextProps.initialSeconds !== this.props.initialSeconds;
  }

  // Read DOM layout before update; return a value for getSnapshotBeforeUpdate
  getSnapshotBeforeUpdate(prevProps, prevState) {
    return this.node ? this.node.scrollTop : 0;
  }

  componentDidUpdate(prevProps, prevState, snapshot) {}

  render() {
    return <div ref={(n) => (this.node = n)}>{this.state.seconds}</div>;
  }
}
```

Lifecycle order: `constructor` → `render` → `componentDidMount` (mount), `shouldComponentUpdate` → `render` → `getSnapshotBeforeUpdate` → `componentDidUpdate` (update), `componentWillUnmount` (unmount). Static context: `ContextName` via `static contextType = MyContext` (then read `this.context`). `setState` in event handlers is batched; `setState` with a callback receives the updated value. `PureComponent` adds a built-in shallow `shouldComponentUpdate`.

Class components in 18 support the same concurrent rendering and Suspense as function components (a class can `throw` a promise to suspend).

## JSX

JSX is a syntactic extension compiled to `createElement`/`jsx` calls — it is not required, but it is idiomatic.

- **Attributes are camelCase** — `className`, `tabIndex`, `autoFocus`, `readOnly`, `htmlFor`. Inline styles are objects — `style={{ marginTop: 12 }}`.
- **Expressions in braces** — `{value}`, `{cond ? <A/> : <B/>}`, `{arr.map(x => <Item key={x.id} />)}`. Strings without braces are literal text (`<div>Hi</div>`), strings in braces are trimmed/newline-collapsed (`{' '}` is the canonical space).
- **Self-closing tags** need a slash — `<img src="a.png" />`; boolean attributes are `value={true}` or presence, not bare.
- **One root per return** — wrap multiple siblings in a fragment `<>...</>` or `<Fragment key="k">` (a fragment is the only way to key a group of siblings).
- **Spread props** — `<div {...props} className={override} />`; later keys win.
- **`dangerouslySetInnerHTML`** — takes `{ __html: string }` and must not be combined with children; React does not sanitize the string.
- **Events are props** — `onClick`, `onChange`, `onSubmit`, … see 03 for the event system.

### JSX runtime

Two transform modes exist:

- **Classic (default in old configs)** — compiles `<A x={1}/>` to `React.createElement(A, {x: 1})`; `React` must be in scope (hence the old `import React from 'react'`).
- **Automatic (recommended)** — compiles to `import { jsx as _jsx } from 'react/jsx-runtime'` (development: `react/jsx-dev-runtime`, which records source location for better errors). No `React` import needed for JSX.

`react/jsx-runtime` exports `jsx(type, props, key?)`, `jsxs(type, props, key?)` (stable children variant), and `Fragment`. Configure Babel with `@babel/preset-react` options `{ runtime: 'automatic' }`, esbuild with `jsx: 'automatic'`, or TypeScript with `"jsx": "react-jsx"`.

## Props and children

- `props` is a read-only object; React warns in development if you mutate it. The `children` prop is just like any other prop — components receive children via `props.children` or via JSX nesting.
- Every element is an object of the shape `{ type, props, key, ref, ... }` (see `createElement` below); `key` is special and never reaches `props`.
- `key` must be a stable, unique string/number within a list. It tells the reconciler which items moved. Do not use array index as key for lists that are reordered, filtered, or have insertions — React will reuse the wrong component state.
- `ref` on a component type only works on DOM elements and classes (function components need `forwardRef`); `ref` on a class component gives the class instance, on a DOM element the DOM node.

## Lists and keys

```jsx
function TodoList({ todos }) {
  return (
    <ul>
      {todos.map((todo) => (
        <TodoItem key={todo.id} todo={todo} />
      ))}
    </ul>
  );
}
```

- Keys only need to be unique among siblings, not globally.
- `key` changes → the element is unmounted and remounted (state and effects reset, ref callbacks fire cleanup). This is a deliberate "nuke the subtree" mechanism, not a performance trick.
- Conditional lists (`{flag && <List/>}`) render `false` — React skips booleans; `{flag ? <A/> : <B/>}` and arrays all work.

## Composition

React has no inheritance; components compose through props:

```jsx
// children pattern
function Card({ title, children }) {
  return (
    <section>
      <h2>{title}</h2>
      {children}
    </section>
  );
}

<Card title="Notes">
  <p>Any nodes here.</p>
</Card>

// multiple named children slots
function Layout({ header, main, footer }) { ... }

// render props
function UserBox({ renderUser }) {
  const user = fetchUserSync();
  return renderUser(user);
}
```

## Element APIs

From `react`:

```ts
createElement(type: ElementType, config?: Attributes & P, ...children: ReactNode[]): ReactElement
cloneElement(element: ReactElement, props?: object, ...children: ReactNode): ReactElement
isValidElement(object: any): boolean
```

- `createElement` is rarely called directly (JSX does it for you); use it for dynamic component selection `const El = props.as; return <El {...rest} />` or for arrays built imperatively.
- `cloneElement` copies an element with replaced props/children — used for prop injection patterns; it is shallow and cannot replace `type`/`key`.
- `isValidElement` guards against accidentally passing a plain object as an element.
- `createFactory` is deprecated (behind a feature flag) — do not use it.

## Children utilities

`React.Children` normalizes `props.children` (which may be a single node, array, or nested arrays):

```ts
Children.map(children, fn: (child, index) => ReactNode): Array
Children.forEach(children, fn: (child, index) => void): void
Children.count(children): number
Children.toArray(children): ReactNode[]          // flattens, adds keys
Children.only(children): ReactElement             // throws unless exactly one
```

`map` and `toArray` attach `.$`-prefixed keys to flatten nesting; they are the classic "render each child with an index" tool, but prefer restructuring the data so each child already has a stable key.

## Version

`import { version } from 'react'` returns the runtime version string (`"18.3.1"`); `react-dom` and `react-dom/server` export the same. Use it for feature detection or logging, never for flow control in UI code.
