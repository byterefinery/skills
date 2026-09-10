# Server and client components, data, mutations

How to split UI across the server/client boundary, fetch data, and handle mutations in Next.js 16.

## Contents

- [Server Components](#server-components)
- [Client Components](#client-components)
- [Passing data across the boundary](#passing-data-across-the-boundary)
- [Fetching data](#fetching-data)
- [Server Actions and mutations](#server-actions-and-mutations)
- [Draft Mode](#draft-mode)

## Server Components

The default. They run only on the server:

- Can be `async` and `await` directly — data fetching, database queries, `fs` reads.
- No hooks (`useState`, `useEffect`), no event handlers, no browser APIs.
- Their code is never shipped to the client — only the rendered output (RSC payload) is.
- Can import Client Components and pass serializable props down.
- Can read request-time APIs (`cookies()`, `headers()`, `params`, `searchParams`) — all **asynchronously** in 16.

Prefer Server Components for anything that renders data; keep Client Components small and at the leaves.

## Client Components

Opt in with the `'use client'` directive at the top of the file. The file and everything it imports become client code:

- Hooks, event handlers, browser APIs (`window`, `localStorage`), client-side state.
- Server Components render *instances* of Client Components and pass props into them.
- A Client Component can render Server Components and can render other Client Components.
- The boundary is directional: server → client passes serializable props; client → server only via form actions / Server Actions / `next/link` navigation.

Rules of thumb: the component that owns state or handlers is the client boundary; its children can stay server-side if you pass data down as props.

## Passing data across the boundary

Props from Server to Client Components are serialized (RSC serialization). Supported: primitives, plain objects, arrays, `Date`, `Map`, `Set`, `TypedArray`, `ArrayBuffer`, and JSX elements (pass-through). Not supported: class instances, functions (except Server Actions passed as `action` props), symbols, `URL` instances.

Consequences:

- Extract what the client needs; do not pass database handles, Promises, or objects with methods.
- `params`/`searchParams` Promises can be passed through to a `<Suspense>` boundary and awaited there — that is the standard pattern for keeping a static shell (see [04-caching](04-caching.md)).
- Under Cache Components, values captured in a `'use cache'` closure become part of the cache key — pass request data as explicit arguments instead.

## Fetching data

- **Fetch in Server Components or Server Functions**, not in Client Components, for data the server can access. `fetch` is deduplicated per render pass; use `React.cache` to reuse the result of an async function across components in one render.
- With Cache Components, data fetching is **dynamic by default**. Wrap a fetch in a function with `'use cache'` + `cacheLife(...)` to include it in the static shell; leave it uncached and wrap the component in `<Suspense>` to stream it at request time. See [04-caching](04-caching.md).
- Without Cache Components, use the previous model: `fetch` with `cache: 'force-cache'`/`'no-store'` and `next: { revalidate, tags }` options — covered by the [caching-without-cache-components guide](https://nextjs.org/docs/app/guides/caching-without-cache-components).
- **Client-side data fetching** (user-tied, high-frequency updates) is legitimate: use SWR or TanStack Query in Client Components. Do not fetch server-accessible data on the client "just because it is dynamic."
- Never expose secrets to the client: read server env vars only in server code, and use `taint` to guard against passing server values into Client Components.

## Server Actions and mutations

Server Actions are server functions invoked from the client, marked with `'use server'` (in a separate file or in a function inside a Server Component):

```tsx
// app/actions.ts
'use server'
import { updateTag } from 'next/cache'

export async function createPost(formData: FormData) {
  await db.post.create({ title: formData.get('title') })
  updateTag('posts')   // read-your-writes; Server Actions only
}
```

- Pass a Server Action to a Client Component via the form `action` prop or as a callback prop; do not call it inside a `'use cache'` scope (pass through instead).
- **Forms**: `action={createPost}` on `<form>`. In 16 use `useActionState` (state + pending + error after submit) and `useFormStatus` (pending indicator from a child of the form) — the older `useTransition` for forms is superseded by `useActionState`.
- `revalidatePath` / `revalidateTag(tag, profile)` / `updateTag` / `refresh` from `next/cache` after mutations. `refresh()` updates the client router so a count in the header updates without a full navigation.
- Validate and authorize **inside** the Server Action — the client can call any exported Server Action, and a proxy matcher that excludes a path also skips Server Functions on that path.
- Under Cache Components, `updateTag` gives read-your-writes; `revalidateTag(tag, 'max')` gives stale-while-revalidate.

## Draft Mode

`draftMode()` (async in 16) toggles draft content (e.g., CMS preview via `?secret=...`). Typical flow: a Route Handler or Server Action calls `enable()`; pages check `isEnabled` to fetch draft data. Under Cache Components, cached functions re-execute and are not saved while draft mode is active, so previews stay fresh without code changes. `enable()`/`disable()` can only be called from Route Handlers or Server Actions.
