# Component Patterns

Solid components are plain functions that receive props and return JSX. They are called once — reactivity flows through signal reads inside the component body.

## Component Typing

```ts
import { Component, ParentComponent, VoidComponent, FlowComponent, ComponentProps, ValidComponent, Ref } from "solid-js";

// Basic — no implicit children
type Component<P = {}> = (props: P) => JSX.Element;

// With optional children
type ParentComponent<P = {}> = Component<P & { children?: JSX.Element }>;

// Without children (forbids children prop)
type VoidComponent<P = {}> = Component<P & { children?: never }>;

// With required children (specific type)
type FlowComponent<P = {}, C = JSX.Element> = Component<P & { children: C }>;
```

### Usage

```tsx
// No children
const Button: VoidComponent<{ onClick: () => void; label: string }> = (props) => (
  <button onClick={props.onClick}>{props.label}</button>
);

// Optional children
const Card: ParentComponent<{ title: string }> = (props) => (
  <div>
    <h2>{props.title}</h2>
    {props.children}
  </div>
);

// Required children as function
const WithChildren: FlowComponent<{}, (value: string) => JSX.Element> = (props) => {
  const [value] = createSignal("hello");
  return <>{props.children(value())}</>;
};
```

## splitProps — Fine-Grained Prop Tracking

```ts
const [local, rest] = splitProps(props, "key1", "key2");
```

- Partitions props into tracked subsets
- Without `splitProps`, reading `props.key` inside an effect tracks the entire props proxy
- Each subset is a proxy that tracks only its keys
- The last element is "remaining props" (everything not listed)

```tsx
const Button: Component<ButtonProps> = (props) => {
  const [local, others] = splitProps(props, "variant", "size", "onClick", "children");

  return (
    <button
      class={`btn btn-${local.variant} btn-${local.size}`}
      onClick={local.onClick}
      {...others}  // spreads remaining props (disabled, title, etc.)
    >
      {local.children}
    </button>
  );
};
```

### Gotchas

- `splitProps` is essential for fine-grained reactivity. Without it, any prop change can trigger re-runs of effects that read other props.
- Keys must be known at compile time (literal strings).

## mergeProps — Default Props

```ts
const merged = mergeProps(defaults, props);
```

- Reactively merges multiple prop sources
- Later sources override earlier ones
- Returns a proxy that resolves properties reactively

```tsx
const defaultProps = { variant: "primary" as const, size: "md" as const };

const Button: Component<ButtonProps> = (props) => {
  const [local, others] = splitProps(
    mergeProps(defaultProps, props),
    "variant", "size", "onClick", "children"
  );
  // local.variant is always defined (defaults to "primary")
};
```

## Refs

```ts
type Ref<T> = T | ((val: T) => void);

// Callback ref
const MyInput: Component<{ ref?: Ref<HTMLInputElement> }> = (props) => {
  return <input ref={props.ref} />;
};

// Usage
const inputRef = createSignal<HTMLInputElement>();
// or
let inputRef: HTMLInputElement;
<MyInput ref={(el) => { inputRef = el; }} />;
```

Solid doesn't have `useRef`. Use `createSignal` for reactive refs or `let` declarations for mutable refs.

## createComponent

```ts
createComponent<T>(Comp: Component<T>, props: T): JSX.Element
```

- Programmatic component instantiation
- Use for rendering components from variables or arrays

```tsx
const components = [Header, Main, Footer];

{components(Comp) => (
  {Comp => createComponent(Comp, {})}
)}
```

## ComponentProps / ValidComponent

```ts
// Extract props type from a component
type BtnProps = ComponentProps<typeof Button>;

// Extract props from intrinsic elements
type DivProps = ComponentProps<'div'>;

// Union of all valid component types
type ValidComponent = keyof JSX.IntrinsicElements | Component<any> | (string & {});
```

## Dynamic Component Rendering

```tsx
// Variable component type
const [page, setPage] = createSignal<"home" | "about">("home");
const pages = { home: Home, about: About };

// Direct use
<.pages[page()] />

// Or with Switch
<Switch>
  <Match when={page() === "home"}><Home /></Match>
  <Match when={page() === "about"}><About /></Match>
</Switch>
```

## createMemo for Derived Props

```tsx
const ExpensiveComponent: Component<{ data: Data[]; filter: string }> = (props) => {
  const [local, rest] = splitProps(props, "data", "filter");

  const filtered = createMemo(() =>
    local.data().filter(d => d.name.includes(local.filter()))
  );

  return <For each={filtered()}>{item => <div>{item.name}</div>}</For>;
};
```

Memos inside components derive computed values from props without re-running on every prop change.

## Pattern: Compound Components

```tsx
// Tabs.tsx
const TabsContext = createContext<TabsContextType>();

const Tabs: ParentComponent<{ orientation?: "horizontal" | "vertical" }> = (props) => {
  const [activeIndex, setActiveIndex] = createSignal(0);

  return (
    <TabsContext.Provider value={{ activeIndex, setActiveIndex, orientation: props.orientation }}>
      <div role="tablist">{props.children}</div>
    </TabsContext.Provider>
  );
};

const TabList: ParentComponent<{}> = (props) => {
  const ctx = useContext(TabsContext)!;
  return (
    <div class={`tabs ${ctx.orientation() === "vertical" ? "tabs-vertical" : ""}`}>
      {props.children}
    </div>
  );
};

const Tab: Component<{ index: number; children: JSX.Element }> = (props) => {
  const ctx = useContext(TabsContext)!;
  const [local] = splitProps(props, "index", "children");

  return (
    <button
      role="tab"
      aria-selected={ctx.activeIndex() === local.index}
      onClick={() => ctx.setActiveIndex(local.index)}
    >
      {local.children}
    </button>
  );
};

const TabPanel: Component<{ index: number; children: JSX.Element }> = (props) => {
  const ctx = useContext(TabsContext)!;
  const [local] = splitProps(props, "index", "children");

  return (
    <Show when={ctx.activeIndex() === local.index} keyed>
      <div role="tabpanel">{local.children}</div>
    </Show>
  );
};

Tabs.List = TabList;
Tabs.Tab = Tab;
Tabs.Panel = TabPanel;

export { Tabs };

// Usage
<Tabs>
  <Tabs.List>
    <Tabs.Tab index={0}>Home</Tabs.Tab>
    <Tabs.Tab index={1}>Settings</Tabs.Tab>
  </Tabs.List>
  <Tabs.Panel index={0}>Home content</Tabs.Panel>
  <Tabs.Panel index={1}>Settings content</Tabs.Panel>
</Tabs>
```

## Pattern: Render Props (Function Children)

```tsx
const MouseTracker: FlowComponent<{}, (pos: { x: number; y: number }) => JSX.Element> = (props) => {
  const [pos, setPos] = createSignal({ x: 0, y: 0 });

  createEffect(() => {
    const handler = (e: MouseEvent) => setPos({ x: e.clientX, y: e.clientY });
    window.addEventListener("mousemove", handler);
    onCleanup(() => window.removeEventListener("mousemove", handler));
  });

  return <>{props.children(pos())}</>;
};

// Usage
<MouseTracker>
  {(pos) => (
    <div>Mouse at: {pos.x}, {pos.y}</div>
  )}
</MouseTracker>
```

## Pattern: Controlled vs Uncontrolled

```tsx
// Controlled
const [value, setValue] = createSignal("");
<Input value={value()} onInput={e => setValue(e.currentTarget.value)} />

// Uncontrolled (via ref)
let inputEl: HTMLInputElement;
<Input ref={el => { inputEl = el; }} />
// Read: inputEl.value
```

## createUniqueId

```ts
const id: string = createUniqueId();
```

- Generates a unique ID (stable across SSR hydration)
- Use for `id`/`aria-labelledby`/`htmlFor` attribute pairing

```tsx
const labelId = createUniqueId();

<label htmlFor={labelId}>Name</label>
<input id={labelId} />
```
