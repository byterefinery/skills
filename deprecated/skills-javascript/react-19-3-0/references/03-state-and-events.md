# State and Events

Contents

- [Where state lives](#where-state-lives)
- [Designing state](#designing-state)
- [Adjusting state during render](#adjusting-state-during-render)
- [Refs for changing values](#refs-for-changing-values)
- [Batched updates](#batched-updates)
- [Events](#events)
- [Forms](#forms)
- [Actions](#actions)

## Where state lives

Put state in the closest component that needs it; when two components need the same state, lift it to their nearest common ancestor and pass props down:

```jsx
function FruitPicker() {
  const [fruit, setFruit] = useState('Mango');
  return (
    <>
      <Inventory fruit={fruit} />
      <Navigator selectedFruit={fruit} onSelectFruit={setFruit} />
    </>
  );
}
```

## Designing state

- Model the UI from the minimum source of truth — if it can be derived from props or existing state, don't store it.
- Don't duplicate state that can be computed (e.g., store the items and `filter`, not a second filtered array).
- For complex objects, consider one `useState` for the object plus a reducer (`useReducer`) when updates are interdependent.
- If the UI "explodes" (multiple state fields going out of sync), that's a signal to consolidate.

## Adjusting state during render

React lets a component adjust its state during render, without effects, by returning `null` to skip committing:

```jsx
function Greeting({ name }) {
  const [firstName, setFirstName] = useState(name);
  if (name !== firstName) {
    setFirstName(name); // adjust, re-render immediately, no commit yet
  }
  return <h1>Hello, {firstName}</h1>;
}
```

Use this for derived-from-props state (e.g., last-seen name when a prop goes empty). It must converge (React errors on a loop).

## Refs for changing values

When a value changes over time and an effect needs the latest without re-subscribing, store it in a ref assigned during render:

```jsx
function Chat({ roomId }) {
  const [messages, setMessages] = useState([]);
  const latestRoomId = useRef(roomId);
  latestRoomId.current = roomId;
  useEffect(() => {
    const id = connect(roomId);
    function onMessage(msg) { setMessages(prev => [...prev, msg]); }
    addEventListener(id, 'message', onMessage);
    return () => removeEventListener(id, 'message', onMessage);
  }, [roomId]);
  return <h1>{messages.length} messages in room {latestRoomId.current}</h1>;
}
```

Or use `useEffectEvent` (19.2+) to capture latest values directly.

## Batched updates

React 18+ automatically batches multiple `setState` calls inside the same event, timeout, or Promise callback into a single re-render. `flushSync(() => {...})` (from `react-dom`) forces an immediate synchronous flush — for imperative DOM integration (e.g., scrolling to the bottom of a list right after appending to it).

## Events

React attaches listeners at the root and simulates DOM-level events — the same `on*` props work across browsers.

- Handlers receive a **synthetic event** with the same interface as native events; properties are read-only, and there is no event pooling (pooled events were removed in 17) — closing over `event.target` is fine.
- Common props — `onClick`, `onChange` (like `input`), `onSubmit`, `onInput`, `onFocus`, `onBlur`, `onWheel`, `onScroll`.
- For controlled inputs, `onChange` is React's normalized "value changed" event (fires like `input`), not the HTML `change`.
- Event delegation: React can add/remove listeners dynamically, so handlers fire even for DOM inserted outside React.
- To read fresh DOM values in a handler, use a ref or read from `e.target`.

## Forms

Controlled vs uncontrolled:

```jsx
// controlled — React state is the source of truth
function Form() {
  const [email, setEmail] = useState('');
  return (
    <form onSubmit={save}>
      <input value={email} onChange={e => setEmail(e.target.value)} />
    </form>
  );
}

// uncontrolled — the DOM holds the value, read via ref/FormData
<input ref={inputRef} defaultValue="..." />
```

In 19, forms integrate with Actions:

- `<form action={action}>` — an Action function (sync or async); React manages pending state, automatically resets the form for uncontrolled components after success, and routes errors to `useActionState`.
- `<button formAction={...}>` / `<input type="submit" formAction={...}>` — per-button submission Actions.
- `useFormStatus()` (from `react-dom`) — `{ pending, data, method, action }` of the nearest form, like a context provider:

```jsx
function SubmitButton() {
  const { pending } = useFormStatus();
  return <button>{pending ? 'Saving…' : 'Save'}</button>;
}
```

- `requestFormReset(formRef)` — manually reset a form after its Action completes.
- `useActionState(action, initial, 'http://server/action')` — the third argument enables progressive enhancement: with JS the client Action runs; without it, the form posts to the URL.

## Actions

An **Action** is a (usually async) function that mutates state — passed to `startTransition`, a form's `action`/`formAction`, or `useActionState`. Actions may perform side effects (`fetch`), and a Transition waits for them to finish before updating the UI, which is how pending/error state and optimistic updates work.

```jsx
function ChangeTheme({ theme, setTheme }) {
  const [state, formAction, isPending] = useActionState(
    async (state, formData) => {
      const newTheme = formData.get('theme');
      await fetch('/api/theme', { method: 'POST', body: ... });
      setTheme(newTheme);
      return { ok: true };
    },
    { ok: false }
  );
  return <form action={formAction}>{/* ... */}</form>;
}
```

Guidelines: keep Actions small and serializable; return plain data; handle errors inside the Action (try/catch and return an error state) or via an error boundary; use `useOptimistic` for instant UI feedback on long round-trips.
