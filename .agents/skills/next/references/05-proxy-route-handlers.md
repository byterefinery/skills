# Proxy and Route Handlers

Request interception (`proxy.ts`, the v16 rename of middleware) and API endpoints (`route.ts`).

## Contents

- [Proxy (proxy.ts)](#proxy-proxyts)
- [Matcher](#matcher)
- [Proxy constraints](#proxy-constraints)
- [Execution order](#execution-order)
- [Route handlers](#route-handlers)
- [Choosing between them](#choosing-between-them)
- [Redirects and rewrites in config](#redirects-and-rewrites-in-config)

## Proxy (proxy.ts)

Proxy runs code on the server **before** a request completes: rewrite, redirect, modify request/response headers, or respond directly. Typical uses: auth redirects, A/B rewrites, header injection, CORS.

Location: `proxy.ts` (or `.js`) in the project root, or in `src/` — same level as `app`/`pages`. If `pageExtensions` is customized, the file is `proxy.page.ts` etc. One proxy file per project; split logic into imported modules.

```ts
// proxy.ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function proxy(request: NextRequest) {
  if (request.nextUrl.pathname.startsWith('/about')) {
    return NextResponse.rewrite(new URL('/about-2', request.url))
  }
}

export const config = {
  matcher: '/about/:path*',
}
```

- Named export `proxy` or default export. The function can be `async`.
- Signature: `proxy(request: NextRequest, event: NextFetchEvent)` — `event.waitUntil(promise)` extends the proxy's lifetime for background work (logging, analytics). The `NextProxy` type infers both.
- Respond with `NextResponse.next()` (continue), `NextResponse.redirect(url)`, `NextResponse.rewrite(url)`, `NextResponse.json(...)`, or a plain `Response`.
- Setting **request** headers upstream: `NextResponse.next({ request: { headers } })` — note `NextResponse.next({ headers })` sets *response* headers instead.
- Cookies: `request.cookies.get/set/delete/has/clear`, `response.cookies.set/get/delete`.
- Do **not** rely on shared modules or globals — proxy is invoked separately from render code and may run on a CDN. Pass data via headers, cookies, URL, or rewrites.
- `fetch` with `options.cache`, `options.next.revalidate`, or `options.next.tags` has **no effect** in proxy.
- The `middleware.ts` file still works but is deprecated (and is the only way to get the `edge` runtime). Proxy is **Node.js runtime only**; setting `runtime` in a proxy file throws. Config flag renamed: `skipProxyUrlNormalize` (was `skipMiddlewareUrlNormalize`); `skipTrailingSlashRedirect` also exists.
- Codemod: `npx @next/codemod@latest middleware-to-proxy .`
- Unit testing (experimental): `unstable_doesProxyMatch`, `isRewrite`, `getRewrittenUrl` from `next/experimental/testing/server`.

## Matcher

`config.matcher` targets where proxy runs. **Without a matcher, proxy runs on every request** — including `_next/static`, `_next/image`, and `public/` assets — so auth/redirect logic can silently block your own CSS and JS. Always scope it.

```js
export const config = {
  // The classic negative-lookahead to skip static files and metadata:
  matcher: '/((?!api|_next/static|_next/image|favicon.ico|sitemap.xml|robots.txt).*)',
}
```

Patterns (path-to-regexp v1 semantics):

- Must start with `/`; anchored to the start (`/about` matches `/about/team` but not `/blog/about`).
- `:path` one segment; `:path*` zero or more; `:path?` zero or one; `:path+` one or more.
- Arrays of strings/objects; regexes in parentheses.
- Object form: `{ source, locale, has, missing }` with conditions on headers, query params, and cookies.
- Matchers must be **constants** — dynamic values are ignored at build time.
- Even excluded `_next/data` routes still invoke proxy (intentional, to prevent protecting a page while leaking its data route).

## Proxy constraints

- **Not for slow data fetching** — it sits in front of every request; keep it fast. Optimistic checks (permission-based redirects) are fine; full session management/authorization is not.
- **Server Functions are not separate routes** — they are POST requests to the route that uses them, so a matcher excluding a path also skips Server Function calls on it. Moving a Server Function can silently remove proxy coverage. Always verify authorization inside each Server Function too.
- RSC requests have internal Flight headers stripped from `request.headers`; `NextResponse.rewrite()` propagates the required RSC headers automatically, but custom `fetch`-based rewrites must forward them manually (or enable `skipProxyUrlNormalize`).
- Avoid large custom headers (431 risk).

## Execution order

1. `headers` from next.config
2. `redirects` from next.config
3. **Proxy** (rewrites, redirects, responses)
4. `beforeFiles` rewrites
5. Filesystem routes (`public/`, `_next/static`, `app/`, `pages/`)
6. `afterFiles` rewrites
7. Dynamic routes (`/blog/[slug]`)
8. `fallback` rewrites

## Route handlers

API endpoints in the App Router — `route.ts`/`route.js` (`.ts` only in practice) anywhere in `app/`, e.g., `app/api/items/route.ts`. Cannot coexist with `page.tsx` in the same segment.

```ts
export async function GET(request: Request) {
  return Response.json({ ok: true })
}
export async function POST(request: Request) {
  const body = await request.json()
  return Response.json(body, { status: 201 })
}
```

- Supported methods: `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `HEAD`, `OPTIONS` — anything else returns 405.
- Native `Request`/`Response` plus the extended `NextRequest`/`NextResponse` (cookies, headers, `redirect`, `rewrite`, `next`).
- Caching without Cache Components: not cached by default; `export const dynamic = 'force-static'` opts a `GET` in (other methods never cached). With Cache Components, `GET` handlers follow the page model — prerendered unless they touch uncached/runtime data; the `'use cache'` directive cannot be applied to the `GET` export itself, so call a cached helper function instead.
- `GET` handlers that bail out of prerendering by throwing will be caught by an existing `try/catch` — set `experimental.hideLogsAfterAbort: true` to quiet the noise.
- CORS: set headers per handler, or globally in proxy.

## Choosing between them

| Need | Tool |
| --- | --- |
| Static redirects (`/old` → `/new`) | `redirects` in next.config |
| Conditional redirects/rewrites on request data | `proxy.ts` |
| Custom API endpoint, webhooks | `route.ts` |
| Auth enforcement | Verify in the Server Function/page itself; proxy only for redirects |
| Anything slow | Not proxy — move it into the route handler or component |

## Redirects and rewrites in config

`redirects()`, `rewrites()`, and `headers()` in `next.config.ts` return arrays of `{ source, destination, permanent }` / `{ source, destination }` / `{ source, set }` rules. Use them for anything that does not need request inspection — they run outside the app runtime and are cheaper than proxy. Order among the three: `headers` → `redirects` → proxy (see execution order).
