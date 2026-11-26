# React Server Components

Contents

- [Model](#model)
- [The directives](#the-directives)
- [What server components can and cannot do](#what-server-components-can-and-cannot-do)
- [The client boundary](#the-client-boundary)
- [Serializability](#serializability)
- [Server Actions](#server-actions)
- [cache and cacheSignal](#cache-and-cachesignal)
- [Taint APIs](#taint-apis)
- [Renderers and wire format](#renderers-and-wire-format)
- [Using RSC in practice](#using-rsc-in-practice)

## Model

React Server Components (RSC, stable in 19) are components that run **only on the server**, at request time. They render into a serialized React tree (the "RSC payload") that the client renderer reads and hydrates — no component code ships to the browser. This lets you:

- use `async/await` directly in components,
- access the database, file system, and secret environment variables,
- keep server-only dependencies out of the client bundle.

Server components render client components, and client components can render server components as children or props.

## The directives

```jsx
// server component (default — no directive needed)
async function Page() {
  const posts = await db.posts.findMany();
  return <PostList posts={posts} />; // PostList may be a client component
}
```

- **`"use client"`** — marks a file's components as **client components**; everything the client graph imports stays client unless it itself has `"use server"`.
- **`"use server"`** — marks an async function as a **Server Action**: a serializable reference the client can call (over HTTP) without bundling its code.

The directive must be the first statement of the module or function.

## What server components can and cannot do

Server components **cannot** use:

- event handlers (`onClick`), `useState`, `useEffect`, `useRef`, or any hook that needs a client runtime (including `useFormStatus`),
- browser-only globals or packages.

They **can** be `async`, `await` anything, read env vars and files, and render client components (passing serializable props).

## The client boundary

A `"use client"` file is the boundary between server and client code:

- Server components **above** the boundary render on the server and pass serialized values down.
- Everything **below** the boundary (imports without directives) runs on the client.
- A client component can receive a server component as a prop (e.g., a `<Layout>` that is a client component wrapping a server-rendered `<Page>`).

Keep boundaries high and few — every client file pulls its whole import graph to the browser.

## Serializability

Props flowing server → client must be serializable: plain objects, arrays, strings, numbers, booleans, `Date`, `Map`, `Set`, `BigInt`, `undefined`, and Server Action references. Functions (except Server Actions), class instances, and React components (as values) do not cross — pass data, and let the client component own its logic. Server → client element references (server components passed as props) cross as serialized references, not code.

## Server Actions

```jsx
// actions.js
export async function saveComment(formData) {
  'use server';
  const text = formData.get('comment');
  await db.comments.create({ text });
}
```

- Use in `<form action={saveComment}>` — with `useActionState(saveComment, initial, 'http://server/save')` you get pending state, error handling, and progressive enhancement in one hook.
- `useOptimistic` gives instant UI while the Action round-trips.
- Actions are serializable references — the client calls them via a fetch round-trip, so their inputs must be serializable (FormData, plain objects, primitives).
- The 19.1–19.3 line added repeated hardening of Server Actions (loop protections, cycle protection, DoS mitigations) — stay on current patch versions.

## `cache` and `cacheSignal`

```jsx
import { cache, cacheSignal } from 'react';

const getUser = cache(async (id) => db.users.find(id)); // memoized per request

async function Profile() {
  const user = await getUser(1);
  const signal = cacheSignal; // becomes aborted when this render's cache lifetime ends
  subscribeToStream(user, signal);
  return <UserView user={user} />;
}
```

`cache()` memoizes a function's results for the lifetime of the current render — call `getUser(1)` twice in the tree, hit the DB once. `cacheSignal` (19.2) is an `AbortSignal` that aborts when that lifetime ends, for cancelling long-running work tied to a request.

## Taint APIs

React 19 ships server-side XSS mitigations: `taintStringToHTML`, `taintStringToJS`, `taintStringUnique`, `taintObject`, and `taintSymbols` (from `react`) mark strings from untrusted sources; rendering or evaluating a tainted string throws a descriptive error instead of leaking it. Apply at the boundary where untrusted input (form fields, query params) enters server code.

## Renderers and wire format

The RSC payload is produced/consumed by renderer pairs, one per bundler:

- `react-server-dom-webpack` — `renderToReadableStream` / `createFromReadableStream`
- `react-server-dom-turbopack`, `react-server-dom-parcel`, `react-server-dom-esm`, `react-server-dom-unbundled`

Plus the HTML layer — `react-dom/server` `renderToPipeableStream`/`renderToReadableStream` for streaming HTML, and `prerender`/`prerenderToNodeStream` for static generation. Since 19.2, `prerender` returns a `postponed` state resumable via `resume`, `resumeAndPrerender`, `resumeToPipeableStream`, `resumeAndPrerenderToNodeStream` (partial pre-rendering), and the SSR APIs also support Node Web Streams. These APIs do **not** follow semver within 19.x — frameworks abstract them; don't build directly on them.

## Using RSC in practice

Use a framework that implements RSC (Next.js App Router, React Router framework mode, TanStack Start) — writing a custom RSC bundler integration is unsupported. Migration checklist from client-only React 18:

1. Move data fetching into server components (`async` components).
2. Mark interactive files `"use client"`; push the boundary as high as possible.
3. Audit props crossing the boundary for serializability.
4. Move `useActionState`/Server Actions to `"use server"` functions for mutations.
5. Add error boundaries server-side (recoverable errors) — unhandled server errors surface differently than client ones.
