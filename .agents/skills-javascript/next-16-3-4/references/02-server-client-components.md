# Server and Client Components

## Table of contents

1. [Choosing the environment](#choosing-the-environment)
2. [The `use client` boundary](#the-use-client-boundary)
3. [Passing data across the boundary](#passing-data-across-the-boundary)
4. [Interleaving server and client components](#interleaving-server-and-client-components)
5. [Context providers](#context-providers)
6. [Third-party components](#third-party-components)
7. [Environment poisoning](#environment-poisoning)
8. [Layouts, templates, and rendering](#layouts-templates-and-rendering)

## Choosing the environment

Layouts and pages are **Server Components by default**. Add `"use client"` to opt a file (and its imports) into the client.

Use **Client Components** when you need:

- State and event handlers (`useState`, `onClick`, `onChange`)
- Lifecycle logic (`useEffect`, `useLayoutEffect`)
- Browser-only APIs (`window`, `localStorage`, `navigator`, `document`)
- Custom hooks

Use **Server Components** when you need to:

- Fetch data from databases or APIs close to the source (queries never ship to the client)
- Use secrets — API keys, tokens stay server-side
- Reduce JavaScript sent to the browser and improve FCP
- Stream content progressively

```tsx
// app/[id]/page.tsx — Server Component
import LikeButton from '@/app/ui/like-button'

export default async function Page({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  const post = await getPost(id)
  return (
    <main>
      <h1>{post.title}</h1>
      <LikeButton likes={post.likes} />
    </main>
  )
}
```

```tsx
// app/ui/like-button.tsx — Client Component
'use client'

export default function LikeButton({ likes }: { likes: number }) { /* ... */ }
```

## The `use client` boundary

`"use client"` declares the **boundary between server and client module graphs**:

- The file, **everything it imports, and the components it directly renders** are bundled for the client. You do *not* need the directive on every interactive file — it propagates down the module graph.
- **Server Components passed as `children` or other props are not** part of the client module graph; they render on the server and arrive as rendered RSC payload.
- Put the directive on the **smallest component** that needs interactivity. Marking a large layout as client drags all of it into the client bundle.
- Server Components can `await` data directly; Client Components can never `await` at top level — pass promises and read them with `use()`.

## Passing data across the boundary

Server → Client is via **props**, and props must be **serializable** (plain data, or functions that are Server Functions). You cannot pass:

- Functions (except `'use server'` functions)
- Class instances, DOM nodes, Maps/Sets, symbols
- Module singletons with side effects

```tsx
// Server: pass serializable data
<Chart data={points} />
```

Stream a promise instead of awaiting it, then resolve client-side with React's `use`:

```tsx
// Server — do NOT await
<Suspense fallback={<Skeleton />}>
  <Posts posts={getPosts()} />
</Suspense>

// Client
'use client'
import { use } from 'react'
export default function Posts({ posts }: { posts: Promise<Post[]> }) {
  const allPosts = use(posts)
  return <ul>{allPosts.map(...)</ul>
}
```

## Interleaving server and client components

Pass a Server Component as a prop (commonly `children`) to embed server UI inside a client component:

```tsx
// app/ui/modal.tsx — client
'use client'
export default function Modal({ children }: { children: React.ReactNode }) {
  return <div>{children}</div>
}

// app/page.tsx — server
<Modal>
  <Cart /> {/* Cart is a Server Component fetching its own data */}
</Modal>
```

## Context providers

React context does not work across the boundary — a context provider created in a Server Component cannot be consumed by Client Components. Wrap `children` in a client provider:

```tsx
// app/theme-provider.tsx
'use client'
import { createContext } from 'react'
export const ThemeContext = createContext({})
export default function ThemeProvider({ children }: { children: React.ReactNode }) {
  return <ThemeContext.Provider value="dark">{children}</ThemeContext.Provider>
}
```

```tsx
// app/layout.tsx
import ThemeProvider from './theme-provider'
export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body><ThemeProvider>{children}</ThemeProvider></body>
    </html>
  )
}
```

Render providers as **deep** as possible (wrap `{children}`, not `<html>`) so Next.js can keep the surrounding markup static.

## Third-party components

If a library component uses client-only features (hooks, context, DOM APIs) but has no `"use client"` directive, it will break when rendered from a Server Component. Wrap it:

```tsx
// app/carousel.tsx
'use client'
import { Carousel } from 'acme-carousel'
export default Carousel
```

Rule of thumb: **any component that throws "X is not a function" or references `window`/`document` at render time needs a client wrapper.**

## Environment poisoning

Modules are shared between both environments, so server-only code can silently be imported into client bundles. Only `NEXT_PUBLIC_*` env vars are inlined on the client; everything else becomes an empty string — a `getData()` that "works" but returns empty keys is the classic symptom.

Prevent it with the marker packages (build-time errors, no runtime code):

```js
import 'server-only'   // in lib/data.js — importing it from a Client Component fails the build
import 'client-only'   // the inverse
```

For sensitive server values, additionally use the `taint` config option / `taint` functions to mark data as tainted and catch it leaving the server.

## Layouts, templates, and rendering

- **Layouts are cached on the client** during navigation and do **not re-render** on client transitions (that is why they cannot read `pathname` or `searchParams` — those would go stale). `template.tsx` remounts when its own segment changes, which is how you get "re-rendering layout" behavior for scroll reset, per-page transitions, etc.
- **Root layout** (`app/layout.tsx`) must contain `<html>` and `<body>`; metadata (`metadata`, `viewport`) is exported from it.
- On the server, rendering is split per route segment: Server Components → RSC payload; Client Components + payload → prerendered HTML. Browsers get HTML instantly, then the RSC payload reconciles and JS hydrates client components. Subsequent navigations transfer only the RSC payload + new JS.
- **Bots and crawlers** are served differently — Next.js waits for all async work and sends one complete HTML document (no streaming shell), so data that exists only at build time can break bot rendering.
