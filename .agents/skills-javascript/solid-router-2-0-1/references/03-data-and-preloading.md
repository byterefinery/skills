# Data APIs and preloading

## Preload strategies

Preloading **code** loads the matched routes' `lazy()` components (and any lazy subtree on the way); preloading **data** also runs their preload functions with `intent: "preload"`. Nothing is preloaded unless you opt in — earlier versions preloaded on hover/focus/touch by default; that built-in is gone. A boolean `preloadLinks` is a type error and, in development, a warning — it preloads nothing.

```tsx
import { createRouter, intentPreload } from "@solidjs/router";

const Router = createRouter({ routes, preloadLinks: intentPreload() });
```

| strategy | preloads a link when | defaults |
| --- | --- | --- |
| `intentPreload({ delay = 20, data = true })` | the pointer rests on it for `delay` ms, it is focused (`focusin`), or a touch starts (`touchstart`). Re-hovering an already-preloaded link does not re-preload until the pointer leaves | code and data |
| `tapPreload({ data = true })` | a pointer goes down on it (`pointerdown`: mouse, touch, or pen), ahead of the click | code and data |
| `viewportPreload({ all = false, data = false, delay = 100, rootMargin })` | it has stayed in the viewport for `delay` ms and the browser is then idle (`requestIdleCallback`, or `setTimeout` fallback). Once per `href`; leaving before the idle flush cancels it. One shared `IntersectionObserver`; `rootMargin` passes through | code |
| `eagerPreload({ all = false, data = false })` | the page has loaded and the browser is idle, including links mounted later. Once per `href`; a link removed before that flush is dropped | code |

- Pass an array to combine strategies — e.g. viewport for code, intent for data: `preloadLinks: [viewportPreload({ all: true }), intentPreload()]`.
- Strategies are client-only; an app ships only the ones it imports. `intentPreload` and `tapPreload` apply to every router link. `viewportPreload` and `eagerPreload` apply only to links that name them (`<a preload="viewport">` / `preload="eager"`) unless created with `{ all: true }`.
- Viewport/eager preloading skips when the browser reports Save-Data or a 2g connection (`effectiveType` of `"2g"` or `"slow-2g"`).
- The `href` and `preload` attributes are read when the preload runs, so a dynamic `href` is the one the link has then.
- Hover/focus/touch preloads don't check modifier keys or `defaultPrevented`, and neither does `tapPreload`'s `pointerdown`. A click still does: the router ignores it when `preventDefault` was already called, when it isn't the primary button, or when alt/ctrl/meta/shift is held.
- Whether a strategy preloads data is its own `data` option, not a per-link choice: `intentPreload`/`tapPreload` default to data (the user is about to click); `viewportPreload`/`eagerPreload` default to code only (opt in with `{ data: true }`).
- `usePreloadRoute` triggers the same work by hand.

Preloading is purely an optimization — without it every navigation loads the same code and data, just after the click. A link with `preload="false"` is never preloaded by any strategy.

## Preload functions

Preload functions start fetching data in parallel with loading the route — called when a route renders, and eagerly when the router preloads a link with data:

```tsx
import { lazy } from "solid-js";

const User = lazy(() => import("./pages/users/[id].js"));

function preloadUser({ params, location }) {
  void getUser(params.id);
}

const routes = defineRoutes([{ path: "/users/:id", component: User, preload: preloadUser }]);
```

The preload function receives:

| key      | type                                             | description                                                              |
| -------- | ------------------------------------------------ | ------------------------------------------------------------------------ |
| `params` | object                                           | The route parameters (same value as `useParams()` inside the route)      |
| `location` | `{ pathname, search, hash, query, state, key }` | Path information (corresponds to `useLocation()`)                        |
| `intent` | `"initial" \| "navigate" \| "native" \| "preload"` | `initial` — first render; `navigate` — router navigation; `native` — back/forward; `preload` — link preloading, not navigating |

The factory-level `preload` option is the app-wide counterpart: it runs once per mount/request with the merged params of every match, and its result reaches the root render-prop as `props.data`.

## `query`

Wrap a fetching function to dedupe calls and participate in revalidation:

```tsx
const getUser = query(async id => {
  return (await fetch(`/api/users/${id}`)).json();
}, "users"); // query key; arguments are serialized alongside it
```

A query:

1. Dedupes on the server for the lifetime of the request.
2. Fills a preload cache in the browser lasting 5 seconds, so link preloads and route entry share one fetch.
3. Refetches reactively by key on action revalidation.
4. Serves as a back/forward cache for browser navigation up to 5 minutes; user-initiated navigation bypasses it.

After a query rejects in the browser, a subsequent read can fetch again immediately (an `<Errored>` fallback can call `reset()` to retry). Consume results directly with Solid primitives — there is no router-specific async wrapper:

```tsx
const user = createMemo(() => getUser(params.id));
return <h1>{user().name}</h1>;

// deeply reactive object data
const todos = createProjection(() => getTodos(), []);
```

Keys support targeted invalidation: `getUser.key` is `"users"`, `getUser.keyFor(5)` is `"users[5]"`. Revalidate with the `revalidate` export or `revalidate` keys on action responses — the whole key invalidates every entry for the query, `keyFor` invalidates one.

A query may also redirect: a guard read that throws or returns `redirect()` (from `@solidjs/web`) navigates instead of resolving. A path starting with `/` is a full path — the base is never added. Same-origin targets navigate softly with `replace` only within the router's base when the history integration can represent their URL; otherwise they navigate the document. On the client, a `Location` header only navigates for redirect statuses (301/302/303/307/308) — `respond({ id: 1 }, { status: 201, headers: { Location: "/items/1" } })` delivers `{ id: 1 }` without navigating. Any `revalidate` keys on a redirect response invalidate first, and the client read stays pending so nothing renders the redirect as data. This holds for `"use server"` queries too, where the transport carries the redirect to the client rather than letting `fetch` follow it.

## `liveQuery`

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

Declaring it is what makes it live — server functions are declared GET at creation just like `query`. Consumption is the same story as `query` — Solid primitives, no router-specific wrapper; the value updates in place as yields arrive:

```tsx
const messages = createMemo(() => roomMessages(params.room));
return <For each={messages()}>{msg => <Message {...msg} />}</For>;
```

One connection per key (name + arguments) is shared by every consumer: late subscribers get the latest value immediately, delivery is latest-wins, and the connection closes when the last consumer leaves. A connected stream that dies transiently (network, 5xx) reconnects with exponential backoff while the latest value keeps serving; a definite rejection (4xx) or first-connect failure surfaces to the consumer like any thrown error.

Live queries ride the router's existing machinery:

- **Preload** — calling one in a preload function warms the connection, so navigation renders against an already-delivered value.
- **SSR** — the document face renders the first value; hydration adopts it and reconnects. Within one server request, consumers of a key observe the same value.
- **Revalidation** — explicit `revalidate(key)` reconnects. The post-mutation sweep leaves healthy connections alone — the stream is its own freshness mechanism.
- **Single-flight** — live keys are neither collected nor swept; a mutation reaches a live query through its producer.

The callable carries the `query` conventions (`key`, `keyFor`) plus a reactive `status(...args)` read (`"idle" | "connecting" | "connected" | "reconnecting" | "closed"`).

## `formAction`

A form action is _an action with a URL_ — Solid's `action` primitive plus a form binding: URL addressability, submission tracking, `aria-busy`, and no-JS posts. Data helpers come from the router; response helpers (`redirect`, `reload`) come from `@solidjs/web`:

```tsx
import { formAction } from "@solidjs/router";
import { redirect } from "@solidjs/web";
import { paths } from "./router";

const updateUser = formAction(async (form: FormData) => {
  await db.users.update(form.get("id"), form);
  throw redirect(paths.users(form.get("id"))); // typed paths work in redirects
});
```

```tsx
<form action={updateUser} method="post">
  <button>Save</button>
</form>

// or
<button type="submit" formaction={updateUser}>Save</button>
```

- Form actions only work with POST — put `method="post"` on the form.
- Submitting forms get `aria-busy="true"` from submit until the action's result is on screen — the mutation, then its revalidation or redirect, until that update commits. Busy state belongs to the form's `action` URL, not the element; a form re-rendered mid-flight (a server-component morph, a keyed re-mount) still shows it.
- Forms work without JavaScript: a real POST, a redirect back, and the result seeded into submission state through a one-shot flash cookie. Single-flight mutations are on by default — the mutation response carries the refreshed route data in the same round trip.
- Single flight is the router's, not the form action's: a mounted router applies any server function's revalidation keys, `redirect()`, `reload()`, and flight data — call the server function (or a core `action`) directly from an event handler, no wrapper needed. `singleFlight={false}` on the router opts out.
- **Every POST server function call is treated as a mutation.** A POST that declares no `revalidate` keys makes the server re-collect the current page's data, and the client revalidates every `query` on screen. Reads are exempt when they go through `query()` (switches a server function to GET automatically) or `GET(fn)`. A POST that isn't a mutation (logging, keystroke search) should return `respond(value, { revalidate: "" })` to touch nothing, or name the keys it did change.
- Delegation doesn't require the action's module on the client: a form bound to a server action in a server-only module renders a plain `action="/_server?id=...&args=..."` — a self-describing URL the router synthesizes the invocation from on submit.
- For optimistic UI, attach owner-scoped hooks and use Solid's optimistic primitives:

```tsx
import { createOptimisticStore } from "solid-js";

const getTodos = query(async () => fetchTodos(), "todos");
const [todos, setTodos] = createOptimisticStore(() => getTodos(), []);

const addTodo = formAction(async todo => {
  await saveTodo(todo);
  return { ok: true, todo };
}, "add-todo").onSubmit(todo => {
  setTodos(items => {
    items.push({ ...todo, pending: true });
  });
});
```

`onSubmit(...)` registers a listener in the current reactive owner (multiple components can register; hooks are removed when their owner is disposed); `onSettled(...)` works the same way for completed submissions. A submission settles when its result is on screen — after any revalidation or redirect it triggered. The preferred pattern is returning values and letting the client interpret the result; thrown errors are captured on `Submission.error` as an escape hatch.

Form actions have a `with` method for typed arguments instead of hidden form fields:

```tsx
const deleteTodo = formAction(api.deleteTodo);

<form action={deleteTodo.with(todo.id)} method="post">
  <button type="submit">Delete</button>
</form>
```

Since form actions serialize to string attributes that must match across SSR, form actions that aren't server functions need a stable name: `formAction(fn, "my-action")`.

### `useAction` (deprecated)

Deprecated, with no replacement: outside a form, call the server function (or a core `action`) directly — the router applies its revalidation and redirect either way. Still works, with a dev warning, until the next major.

## `useSubmissions`

Returns settled submission records for an action — the durable history layer, not in-flight state. Useful for reading completed results, clearing old submissions, retrying, or replaying settled errors:

```tsx
const submissions = useSubmissions(addTodo, input => filter(input));
const latest = submissions.at(-1);
// { input, result?, error, url, clear(), retry() }
```

The list is history: a later submission never removes an earlier record, so every failed row keeps its own `retry()`. Records go away through their own `clear()` / `retry()`, and every client navigation clears the list. A form that shows only its latest outcome clears the old records when a new submission starts:

```tsx
const submissions = useSubmissions(addTodo);
addTodo.onSubmit(() => submissions.forEach(s => s.clear()));
const error = () => submissions.at(-1)?.error;
```

Use Solid's `createOptimistic` / `createOptimisticStore` for in-flight UI.

## Typed search params

Give a route a Standard Schema validator (Valibot, Zod, ArkType, hand-rolled…) and its types flow into `paths` and `useSearchParams`:

```tsx
import * as v from "valibot";

const routes = defineRoutes([
  {
    path: "/search",
    component: Search,
    search: v.object({
      q: v.optional(v.string(), ""),
      page: v.optional(v.pipe(v.unknown(), v.transform(Number)), 1)
    })
  }
]);
```

```tsx
const [search, setSearch] = useSearchParams(paths.search);
search.page; // number (parsed, not "2")
setSearch({ page: search.page + 1 }); // typed setter

<a href={paths.search({ q: "solid", page: 2 })}>Search</a>; // typed builder
```

Without a schema, `useSearchParams()` behaves as before: raw string values, merge-on-set semantics (`''`, `undefined`, and `null` remove keys), navigation-like updates with auto-scrolling disabled.
