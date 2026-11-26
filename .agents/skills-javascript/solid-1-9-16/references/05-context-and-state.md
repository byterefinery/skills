# Context and State Management

Solid's context system provides dependency injection through the component tree. Combined with signals, it forms the basis for state management without external libraries.

## createContext

```ts
const Context: Context<T> = createContext<T>(
  defaultValue?: T,
  options?: { name?: string }
);
```

Returns a context object with:
- `id: symbol` — unique identifier
- `Provider: ContextProviderComponent<T>` — provider component
- `defaultValue: T` — fallback when no provider is found

```tsx
const ThemeContext = createContext<{
  theme: Accessor<string>;
  setTheme: Setter<string>;
}>();

// With default value
const CountContext = createContext(0);
```

## useContext

```ts
const value: T = useContext<T>(context: Context<T>): T
```

- Reads the current context value from the nearest provider
- Returns `defaultValue` if no provider is found
- Reactive: re-runs when the provider's value changes (if the value is a signal accessor)

```tsx
const ctx = useContext(ThemeContext);
// ctx.theme() — read the signal
// ctx.setTheme("dark") — update
```

## Provider

```tsx
<Context.Provider value={contextValue}>
  {children}
</Context.Provider>
```

- Wraps children with context value
- `value` can be any type — signals, objects, functions
- Multiple providers of the same context: innermost wins

## Pattern: Store Context

```tsx
interface CounterStore {
  count: Accessor<number>;
  increment: () => void;
  decrement: () => void;
  reset: () => void;
}

const CounterContext = createContext<CounterStore>();

function createCounter(initial = 0): CounterStore {
  const [count, setCount] = createSignal(initial);
  return {
    count,
    increment: () => setCount(c => c + 1),
    decrement: () => setCount(c => c - 1),
    reset: () => setCount(initial),
  };
}

// Provider component
const CounterProvider: ParentComponent<{ initial?: number }> = (props) => {
  const store = createCounter(props.initial);
  return (
    <CounterContext.Provider value={store}>
      {props.children}
    </CounterContext.Provider>
  );
};

// Usage in app
<CounterProvider initial={42}>
  <CounterDisplay />
  <CounterControls />
</CounterProvider>

// Consumer
function CounterDisplay() {
  const store = useContext(CounterContext)!;
  return <div>Count: {store.count()}</div>;
}

function CounterControls() {
  const store = useContext(CounterContext)!;
  return (
    <>
      <button onClick={store.increment}>+1</button>
      <button onClick={store.decrement}>-1</button>
      <button onClick={store.reset}>Reset</button>
    </>
  );
}
```

## Pattern: Multi-Context App State

```tsx
// auth.ts
const AuthContext = createContext<AuthState>();

// theme.ts
const ThemeContext = createContext<ThemeState>();

// preferences.ts
const PreferencesContext = createContext<PreferencesState>();

// app.tsx
<AuthProvider>
  <ThemeProvider>
    <PreferencesProvider>
      <App />
    </PreferencesProvider>
  </ThemeProvider>
</AuthProvider>
```

## children() — Resolving Children

```ts
const resolved: ChildrenReturn = children(fn: Accessor<JSX.Element>)
```

- Resolves child elements to a stable accessor
- Returns an accessor with `.toArray()` method
- Use when you need to inspect or transform children

```tsx
const Wrapper: ParentComponent<{}> = (props) => {
  const resolved = children(() => props.children);

  createEffect(() => {
    const arr = resolved.toArray();
    console.log(`Rendering ${arr.length} children`);
  });

  return <div>{resolved()}</div>;
};
```

## observable — Signal to Observable

```ts
const observable: Observable<T> = observable(signal: Accessor<T>)
```

- Converts a Solid signal to a TC39 Observable
- Compatible with RxJS `from()`, `merge()`, etc.

```ts
import { from } from "rxjs";
const [count, setCount] = createSignal(0);
const count$ = from(observable(count));
count$.subscribe(v => console.log(v));
```

## from — Observable to Signal

```ts
const accessor: Accessor<T> = from<T>(
  producer: Producer<T>,
  initialValue?: T
)
```

- Wraps external producers (RxJS, custom subscribe patterns) as Solid accessors
- Auto-cleanup on component dispose

```ts
// From RxJS
const time$ = interval(1000);
const ticks = from(time$, 0);

// From custom producer
const clock = from(
  (set) => {
    const id = setInterval(() => set(new Date().toLocaleTimeString()), 1000);
    return () => clearInterval(id);
  },
  ""
);
```

## Pattern: Simple State Management (no library)

```tsx
// store.ts
import { createSignal, createContext, Accessor, Setter } from "solid-js";

interface AppState {
  user: Accessor<User | null>;
  setUser: (user: User | null) => void;
  theme: Accessor<string>;
  setTheme: Setter<string>;
  notifications: Accessor<Notification[]>;
  addNotification: (n: Notification) => void;
  clearNotifications: () => void;
}

let appState: AppState;

export function createAppState(): AppState {
  const [user, setUser] = createSignal<User | null>(null);
  const [theme, setTheme] = createSignal("light");
  const [notifications, setNotifications] = createSignal<Notification[]>([]);

  return {
    user,
    setUser,
    theme,
    setTheme,
    notifications,
    addNotification: (n) => setNotifications(ns => [...ns, n]),
    clearNotifications: () => setNotifications([]),
  };
}

export const AppStateContext = createContext<AppState>();

export function useAppState() {
  return useContext(AppStateContext)!;
}

// main.tsx
appState = createAppState();
render(() => (
  <AppStateContext.Provider value={appState}>
    <App />
  </AppStateContext.Provider>
), document.getElementById("root")!);

// components
function UserProfile() {
  const store = useAppState();
  return <Show when={store.user()} keyed>{user => <div>{user.name}</div>}</Show>;
}
```

## Pattern: Signal Store (Proxy-Based)

```tsx
import { createSignal, createContext, useContext } from "solid-js";

function createSignalStore<T extends Record<string, any>>(initial: T) {
  const [state, setState] = createSignal(initial, { equals: false });

  const store = new Proxy({}, {
    get(_, prop) {
      return state()[prop];
    },
    set(_, prop, value) {
      setState(s => ({ ...s, [prop]: value }));
      return true;
    },
  }) as T & { setState: typeof setState };

  (store as any).setState = setState;
  return store;
}

// Usage
const store = createSignalStore({ count: 0, name: "Solid" });
console.log(store.count);  // 0
store.count = 1;           // reactive update
```

## Gotchas

- **Context values should be stable** — pass signal tuples (accessor + setter), not raw values. If you pass a new object on every render, consumers will re-run unnecessarily.
- **`useContext` is reactive** — reading a signal inside a context value creates tracking. The consumer's effects re-run when the signal changes.
- **No `useContext` dependency array** — unlike React, Solid's `useContext` always tracks the context value. Use `untrack` if you need a one-time read.
- **Default values are fallbacks** — `createContext(defaultValue)` means components without a provider get `defaultValue`. This is useful for optional features but can mask missing providers.
