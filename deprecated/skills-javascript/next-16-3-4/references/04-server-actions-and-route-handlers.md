# Server Actions, Route Handlers, and Proxy

## Server Actions (Server Functions)

A **Server Function** is an async function marked with `'use server'` that runs on the server and is callable from the client over a network request. In a mutation/form context it is called a **Server Action**.

```ts
// app/lib/actions.ts — file-level 'use server' makes every export a Server Function
import 'server-only'

export async function createPost(formData: FormData) {
  const session = await auth()
  if (!session?.user) throw new Error('Unauthorized')
  // mutate...
  // revalidate / updateTag...
}
```

Or per-function, even inlined in a Server Component:

```tsx
export default function Page() {
  async function deletePost(formData: FormData) {
    'use server'
    // ...
  }
  return <form action={deletePost}>...</form>
}
```

Key rules:

- Must be **async** — the client calls it via a network request (always `POST`).
- **Invoked automatically** when passed to `<form action={fn}>` or `<button formAction={fn}>`; those submissions run inside `startTransition`. Otherwise call with `await fn(args)` from a client component.
- Params and return values must be **serializable**.
- **Reachable via direct POST** — every Server Action must verify auth and authorization itself; the UI is not a security boundary.
- In a Server Action, call `redirect('/new-url')` after mutation for the post-action navigation.
- Single roundtrip: the response contains both the updated UI and new data.

### Forms

```tsx
// plain HTML form — progressive enhancement, works without JS
<form action={createPost}>
  <input name="title" />
  <button>Submit</button>
</form>
```

- `action` on `<form>`/`<button>`: native submit, no JS required, works with `redirect()`.
- `useActionState` (React 19) for tracking pending/error state of a form across submissions.
- `useFormStatus` in a child component for `pending`/`data` state.
- **`<Form>`** from `next/form` (new in 16): client-side navigation + loading UI prefetching for forms that update search params, e.g. `<Form action="/search"><input name="query" /></Form>` → `/search?query=abc` with no reload.
- `useFormStatus`/`useActionState` require the form to be in the client module graph.

### Optimistic updates and error handling

- Wrap `await action(...)` in `startTransition` for optimistic UI.
- Throw from an action to show the nearest `error.tsx` boundary (client side); `useActionState` captures thrown errors.
- `revalidatePath`/`revalidateTag`/`updateTag`/`refresh` (see data & caching) are the standard way to sync caches after mutation.

---

## Route Handlers

Custom request handlers using the Web `Request`/`Response` APIs, defined in `route.ts` (or `.js`) inside `app/`:

```ts
// app/api/route.ts
export async function GET(request: Request) {
  return Response.json({ ok: true })
}
```

- Supported methods: `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `HEAD`, `OPTIONS` (unsupported → 405).
- **Cannot share a segment with `page.tsx`** — `route` takes over all HTTP verbs for that URL.
- Nest anywhere in `app/`; convention is `app/api/...`.
- Extended APIs: `NextRequest` (parsed cookies, `geo`, `nextUrl`) and `NextResponse` (`revalidate()`, `nextUrl` helpers) from `next/server`.
- With Cache Components, `GET` handlers follow the PPR model (prerender when deterministic; `use cache` in a helper to include data in the static response).

### Caching in the previous model

Route Handlers are **not cached by default**; opt in per `GET` with segment config (`export const dynamic = 'force-static'`, `revalidate`, etc.). Other methods are never cached.

---

## Proxy (formerly Middleware)

In v16 the `middleware.ts` convention was renamed to **`proxy.ts`**. It runs code **before a request completes** — rewrite, redirect, modify request/response headers, or respond directly.

```ts
// proxy.ts — project root (or src/), same level as app/
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function proxy(request: NextRequest) {
  // name it `proxy` (named export recommended; default export also works)
  if (request.nextUrl.pathname === '/about') {
    return NextResponse.redirect(new URL('/home', request.url))
  }
  const requestHeaders = new Headers(request.headers)
  requestHeaders.set('x-foo', 'bar')
  return NextResponse.next({ request: { headers: requestHeaders } })
}

export const config = {
  matcher: '/about/:path*',   // path filter; path-to-regexp syntax
}
```

Rules and limits:

- **`proxy` runs on the `nodejs` runtime only** — the `edge` runtime is *not* supported in `proxy`. If you need edge, keep the old `middleware.ts` filename (deprecated but functional; the v16 codemod migrates the rest).
- **One `proxy.ts` per project** — split logic into imported modules.
- Not for slow data fetching or full authorization — optimistic checks (permission-based redirects) only.
- `fetch` caching options (`cache`, `next.revalidate`, `next.tags`) have **no effect** in proxy.
- Config flag renames: `skipMiddlewareUrlNormalize` → `skipProxyUrlNormalize`, `proxyClientMaxBodySize` (new).
- Prefetching: proxy can mark links prefetchable via `NextResponse` headers (`x-nextjs-prefetch`); see the Link API for details.
- Renaming files/config: `npx @next/codemod@canary upgrade latest` handles `middleware` → `proxy` plus the config flags.
