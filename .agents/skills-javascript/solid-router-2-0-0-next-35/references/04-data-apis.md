# Data APIs

The data APIs are optional, but they build on the preload mechanism. Data helpers come from the router; response helpers (`redirect`, `reload`, `respond`) come from `@solidjs/web` — they're protocol-level and work without the router.

## query

Wrap a fetching function to dedupe calls and participate in revalidation:

```tsx
const getUser = query(async id => {
  return (await fetch(`/api/users/${id}`)).json();
}, "users"); // query key; arguments are serialized alongside it
```

A query:

1. Dedupes on the server for the lifetime of the request.
2. Fills a preload cache in the browser lasting 5 seconds, so hover preloads and route entry share one fetch.
3. Refetches reactively by key on action revalidation.
4. Serves as a back/forward cache for browser navigation up to 5 minutes; user-initiated navigation bypasses it.

Consume results directly with Solid primitives — there is no router-specific async wrapper:

```tsx
const user = createMemo(() => getUser(params.id));
return <h1>{user().name}</h1>;

// deeply reactive object data
const todos = createProjection(() => getTodos(), []);
```

Keys support targeted invalidation:

```ts
getUser.key; // "users"
getUser.keyFor(5); // "users[5]"
```

Revalidate with the `revalidate` export or by setting `revalidate` keys on action responses — the whole key invalidates every entry for the query, `keyFor` invalidates one:

```ts
import { revalidate } from "@solidjs/router";
revalidate("users"); // every entry
revalidate(getUser.keyFor(5)); // one entry
```

A query may also redirect — a guard read that throws or returns `redirect()` (from `@solidjs/web`) navigates instead of resolving: same-origin targets navigate softly with `replace`, other origins leave the document, any `revalidate` keys on the response invalidate first, and the read itself stays pending so nothing renders the redirect as data. This holds for `"use server"` queries too, where the transport carries the redirect to the client rather than letting `fetch` follow it.

## liveQuery (experimental)

`query`'s live sibling: a keyed query over a value-shaped stream. The function is an async iterable (typically an async generator server function) whose yields are successive **values of one logical query** — each yield is the current state, not an event — with the contract that it re-yields current state on every invocation:

```tsx
const roomMessages = liveQuery(async function* (room: string) {
  "use server";
  yield await db.messages.list(room); // current state, immediately
  for await (const change of db.messages.watch(room)) {
    yield await db.messages.list(room); // current state again, on change
  }
}, "messages");
```

Declaring it is what makes it live — no separate wrapper, and server functions are declared GET at creation just like `query`. Consumption is the same story as `query`: Solid primitives, no router-specific async wrapper. The value updates in place as yields arrive:

```tsx
const messages = createMemo(() => roomMessages(params.room));
return <For each={messages()}>{msg => <Message {...msg} />}</For>;
```

One connection per key (name + arguments) is shared by every consumer: late subscribers get the latest value immediately, delivery is latest-wins, and the connection closes when the last consumer leaves. A connected stream that dies transiently (network, 5xx) reconnects with exponential backoff while the latest value keeps serving; a definite rejection (4xx) or a first-connect failure surfaces to the consumer like any thrown error.

Live queries ride the router's existing machinery rather than adding their own:

- **Preload** — calling one in a preload function warms the connection, so navigation renders against an already-delivered value instead of holding the transition on connect.
- **SSR** — the document face renders the first value; hydration adopts it and reconnects. Server-side, consumers of a key within one request observe the same value.
- **Revalidation** — explicit `revalidate(key)` reconnects (the producer re-yields current state by contract). The post-mutation sweep leaves healthy connections alone: the stream is its own freshness mechanism.
- **Single-flight** — live keys are neither collected nor swept: a mutation reaches a live query through its producer (the `watch` yielding the changed state), not through the mutation response.

The callable carries the `query` conventions (`key`, `keyFor`) plus a reactive `status(...args)` read (`"idle" | "connecting" | "connected" | "reconnecting" | "closed"`) for surfacing connection state in UI.

## action

A router action is _an action with a URL_ — Solid's mutation primitive plus URL addressability, submission tracking, and response handling:

```tsx
import { action } from "@solidjs/router";
import { redirect } from "@solidjs/web";
import { paths } from "./router";

const updateUser = action(async (form: FormData) => {
  await db.users.update(form.get("id"), form);
  throw redirect(paths.users(form.get("id"))); // typed paths work in redirects
}, "update-user");
```

```tsx
<form action={updateUser} method="post">
  <button>Save</button>
</form>

// or
<button type="submit" formaction={updateUser}>Save</button>
```

Actions only work with POST requests, so put `method="post"` on your form. Since form actions serialize to string attributes that must match across SSR, actions that aren't server functions need a stable name: `action(fn, "my-action")`.

Submitting forms get `aria-busy="true"` automatically from submit until the action's result is on screen — the mutation, then its revalidation or redirect, until that update commits — the same CSS story as links:

```css
form[aria-busy] button {
  pointer-events: none;
  opacity: 0.6;
}
```

Busy state belongs to the form's `action` URL, not the element: a form re-rendered or replaced mid-flight (a server-component morph, a keyed re-mount) still shows it. An `aria-busy` you set yourself is left alone.

Forms work without JavaScript: a real POST, a redirect back, and the result seeded into submission state through a one-shot flash cookie. Single-flight mutations are on by default — the mutation response carries the refreshed route data in the same round trip.

Delegation doesn't require the action's module on the client either. A form bound directly to a server action in a server-only module renders a plain `action="/_server?id=...&args=..."` — a self-describing URL. On submit, the router synthesizes the invocation from it: the form data posts to that URL through the server-function transport, `.with()` arguments ride along in the query string, and submissions, `aria-busy`, redirects, revalidation, and single-flight data flow through the normal pipeline. The handler loads lazily on first such submit, so router-only bundles don't carry the data layer. The no-JS POST remains the fallback only for clients that actually have no JavaScript. (Client-only actions — `action(fn, "name")` without `use server` — are their module's JS by definition and still require it on the client.)

### Optimistic UI

Attach owner-scoped hooks to the action and use Solid's optimistic primitives for rendered state:

```tsx
import { createOptimisticStore } from "solid-js";
import { action, query } from "@solidjs/router";

const getTodos = query(async () => fetchTodos(), "todos");
const [todos, setTodos] = createOptimisticStore(() => getTodos(), []);

const addTodo = action(async todo => {
  await saveTodo(todo);
  return { ok: true, todo };
}, "add-todo").onSubmit(todo => {
  setTodos(items => {
    items.push({ ...todo, pending: true });
  });
});
```

`onSubmit(...)` registers a listener in the current reactive owner — multiple components can register against the same action, and hooks are removed when their owner is disposed. `onSettled(...)` works the same way for observing completed submissions. A submission settles when its result is on screen: the hooks run, the record enters `useSubmissions`, and `aria-busy` clears once the action's update commits — after any revalidation or redirect it triggered, which may be later than the promise from `useAction` resolves. The hooks that run are the ones registered when the action finished: a hook whose owner that commit unmounts (the page a redirect leaves) still sees the submission, while a hook registered later, or removed with its owner before then, does not.

The preferred pattern is returning values and letting the client interpret the result; thrown errors are still captured on `Submission.error` as an escape hatch.

### with

Actions have a `with` method (like `bind`) for typed arguments instead of hidden form fields:

```tsx
const deleteTodo = action(api.deleteTodo);

<form action={deleteTodo.with(todo.id)} method="post">
  <button type="submit">Delete</button>
</form>;
```

## useAction

Call an action directly instead of through a form — this is how the router context is captured. Outside a form you can pass typed data instead of `FormData`, but this requires client-side JavaScript and is not progressively enhanceable:

```tsx
const submit = useAction(myAction);
submit(...args);
```

## useSubmissions

Returns settled submission records for an action — the durable history layer, not in-flight state. Useful for reading completed results, clearing old submissions, retrying, or replaying settled errors:

```tsx
const submissions = useSubmissions(action, input => filter(input));
const latest = submissions.at(-1);
// { input, result?, error, url, clear(), retry() }
```

Use Solid's `createOptimistic` / `createOptimisticStore` for in-flight UI. The second argument optionally filters by input. `retry()` re-runs the action with the same input; `clear()` removes the record.
