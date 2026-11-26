# Components and JSX

Contents

- [Function components](#function-components)
- [JSX rules](#jsx-rules)
- [Props](#props)
- [Conditional rendering and lists](#conditional-rendering-and-lists)
- [Composition](#composition)
- [Refs as props](#refs-as-props)
- [Context](#context)
- [memo and createElement](#memo-and-createelement)

## Function components

A component is a plain function that receives a `props` object and returns React elements — JSX, arrays, strings, numbers, booleans (ignored), or `null`. Components must start with a capital letter; lowercase JSX tags are intrinsic DOM elements.

```jsx
function Welcome({ name }) {
  return <h1>Hello, {name}</h1>;
}

root.render(<Welcome name="Taylor" />);
```

Render must be pure — no mutation, no logging, no DOM access, nothing with side effects. Side effects belong in effects or event handlers. React may call render multiple times, discard the result, or (in dev, under `<StrictMode>`) call it twice.

## JSX rules

- JSX is sugar for `createElement`, compiled by the **automatic JSX runtime**. The classic runtime requiring `import React` was removed in 19.
- Curly braces hold expressions — `{value}`, `{cond ? a : b}`, `{arr.map(...)}`, `{str && <X/>}`. To print literal text that looks like markup, use a string: `{'<not-a-tag>'}`.
- `className`, not `class`; `htmlFor`, not `for`; camelCase DOM props (`tabIndex`, `autoFocus`, `onChange`).
- Boolean attributes are real booleans — `disabled`, `disabled={true}`, or `disabled={false}`.
- `null`/`undefined` attributes are omitted from the DOM.
- Unknown attributes on custom elements pass through as-is (React 19 passes Custom Elements tests on Custom Elements Everywhere).
- Fragments `<>...</>` group siblings without a wrapper element; keyed fragments via `<Fragment key="...">`.
- `{...props}` spread works on DOM elements and components.
- `dangerouslySetInnerHTML={{ __html: raw }}` injects raw HTML (sanitize first).

## Props

Props are read-only — treat them as immutable. Destructure at the top of the component; use ES6 default parameters, since `defaultProps` was removed for function components in 19:

```jsx
function Button({ variant = 'primary', children }) {
  return <button className={'btn btn-' + variant}>{children}</button>;
}
```

`children` is just a prop — `<Card><Text /></Card>` arrives as `props.children`.

## Conditional rendering and lists

```jsx
{user ? <Profile user={user} /> : <Login />}
{items.map(item => <Item key={item.id} item={item} />)}
```

Keys must be stable across renders — use database IDs, never array indices for lists that reorder or mutate; React matches children by key during reconciliation. Lists without keys produce dev warnings and wrong component reuse.

## Composition

Components take `children` and named "slot" props; override defaults by rendering children:

```jsx
function Button({ label, children = label }) {
  return <button>{children}</button>;
}

<Button label="Save" />
<Button>Custom <Icon /></Button>
```

Prefer composition over single-axis prop flags (replace `hideSidebar` with `sidebar={null}` or a named slot).

## Refs as props

In React 19, `ref` is a regular prop on function components — no `forwardRef` needed (it still works for compatibility):

```jsx
function Input(props) {
  return <input {...props} className="input" />;
}

// <Input ref={myRef} /> — myRef.current is the <input> DOM node
```

Ref callbacks may return a cleanup function (new in 19), called on unmount:

```jsx
function Item({ ref }) {
  return (
    <div
      ref={node => {
        if (node) tracked.add(node);
        return () => tracked.delete(node);
      }}
    />
  );
}
```

Reading `element.ref` is deprecated — use `element.props.ref`.

## Context

```jsx
const ThemeContext = createContext('light');

function ThemeProvider({ children }) {
  return <ThemeContext value="dark">{children}</ThemeContext>;
}

// 19: <Context> can be rendered directly as a provider; <Context.Provider> still works

function Logo() {
  const theme = useContext(ThemeContext); // or use(ThemeContext)
  return <img src={'/logo-' + theme + '.png'} />;
}
```

Consumers re-render when the nearest provider's value changes (by reference). Split hot contexts into separate objects so unrelated consumers don't re-render.

## memo and createElement

`memo(Component, compare?)` wraps a component so React skips re-rendering when props are shallow-equal (custom `compare(prev, next)` for custom logic). `createElement(type, props, ...children)` is the imperative JSX equivalent — needed when the tag is dynamic or comes from data.
