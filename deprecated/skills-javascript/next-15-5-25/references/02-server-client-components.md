# Server and Client Components

Next.js 15 App Router components are **Server Components by default**. Adding `'use client'` to a file makes it a Client Component and the root of a client subtree — all of its descendants stay client components unless they import back into server-only modules.

## Choosing

Use **Server Components** when the component:
- fetches or renders data (they can be `async`)
- uses Node.js APIs, databases, env secrets
- is UI that doesn't need interactivity or browser APIs

Use **Client Components** when the component:
- needs state (`useState`, `useEffect`) or event handlers
- uses browser APIs or effects
- wraps a third-party library that requires the DOM

Rule of thumb: push `'use client'` as deep in the tree as possible. Server Components ship no JavaScript, so each client boundary is a bundle-size decision.

## Data fetching

### Server Components

Components can be async functions — fetch directly with `fetch`, an ORM, or a database client:

```tsx
export default async function Page() {
  const res = await fetch('https://api.example.com/posts')
  const posts = await res.json()
  return <PostList posts={posts} />
}
```

- `fetch` responses are **not cached by default** in 15 (see 04-caching for opt-in).
- Memoization: identical `GET` fetches in the same render pass deduplicate automatically (request memoization), so the same data can be fetched independently in a layout, page, and child components without extra cost.

### Client Components

Two idioms:
1. **React `use` hook** — pass a *promise* (not its awaited value) from a Server Component, then `const posts = use(postsPromise)` inside the client component. Combined with `<Suspense>` this streams data.
2. **Client-side libraries** — SWR or React Query; fetch in the browser, not the server.

## Passing data between components

- Server → Client: props must be **serializable** (primitives, JSON-able objects). Functions and class instances are not allowed — but *promises* are allowed and resolved with `use()`.
- The `children` prop of a layout/page is a special RSC reference, not serializable data — never pass it to a Client Component except as `children`.
- Context providers must be Client Components; render them in a server layout with a client provider as the child.

## Third-party components

Components from a library are treated as Server Components, which breaks libraries that touch the DOM. Two fixes:
1. Mark the wrapper file `'use client'` and import the library there.
2. For SSR-incompatible libraries, isolate them behind a Client Component boundary near the leaf.

## Preventing environment poisoning

`process.env.X` in a Server Component is **inlined at build time** into the serialized RSC payload if that value reaches a client boundary (e.g. as a prop). Never pass secrets from the server tree to the client. Client-only variables must start with `NEXT_PUBLIC_` (see 10-cli-config for the env rules). Experimental `taint` (15.5, enable `experimental.taint: true`) exposes React's `taintObjectReference`/`taintUniqueValue` to mark values as unserializable so an accidental client boundary fails loudly instead of leaking.

## Streaming and Suspense

- Wrap async data in `<Suspense fallback={...}>` to stream: the rest of the page ships immediately, the fallback renders until data resolves.
- A `loading.tsx` file provides the default fallback per segment; explicit `<Suspense>` boundaries inside a page give finer control.
- Dynamic content (anything using Dynamic APIs or uncached fetches) can only stream when wrapped in Suspense — otherwise it makes the whole route dynamic (see 04-caching).

## Common patterns

- Keep layouts as Server Components; add a client provider only where context is needed.
- A page can be a Server Component that fetches data and renders a Client Component editor/form with the data as serializable props.
- For optimistic UI, use `useOptimistic` in the client tree (see 03-server-actions).
- Check bundle impact with the `next build` route table — each client boundary's JS shows up in `First Load JS`.
