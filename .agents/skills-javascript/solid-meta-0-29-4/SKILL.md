---
name: solid-meta-0-29-4
description: solid-meta 0.29.4 — async SSR-ready document head management for Solid.js. Provides MetaProvider, Title, Meta, Link, Style, Base, and Stylesheet components for injecting head tags anywhere in the component tree. Covers cascading title/meta deduplication, SSR hydration, SolidStart integration, and server-side getAssets rendering. Use when managing dynamic title, meta, link, style, or base tags in Solid.js apps, handling SEO meta tags per-route, or integrating head management with SolidStart or custom SSR setups.
license: MIT
compatibility: "Requires solid-js >=1.8.4 as a peer dependency. Works with SolidStart (file-based routing) and custom SSR via solid-js/web renderToString + getAssets. Node.js 18+ for build tooling."
allowed-tools: Bash(npm) Bash(npx) Bash(pnpm) Bash(yarn) Bash(bun) Read
metadata:
  tags:
    - javascript
    - frontend
    - solidjs
    - ssr
    - seo
    - meta-tags
    - document-head
---

# solid-meta 0.29.4

## Overview

`@solidjs/meta` is a lightweight library for managing `<head>` tags in Solid.js applications. It allows components anywhere in the tree to inject `<title>`, `<meta>`, `<link>`, `<style>`, and `<base>` elements into `document.head`, with full SSR support and proper hydration.

The library works by wrapping the app in `<MetaProvider>`, which collects head tags from child components. On the server, tags are gathered and rendered via `getAssets()` from `solid-js/web`. On the client, SSR-generated tags (marked with `data-sm`) are cleaned up and replaced with client-rendered equivalents.

Key behaviors:
- **Cascading deduplication** — `<title>` and `<meta>` tags with the same key (name/property + attributes) are deduplicated; the deepest/last instance wins
- **SSR-ready** — tags collected during server render are available via `getAssets()` for injection into the HTML `<head>`
- **SPA-friendly** — server tags are stripped on client hydration so subsequent navigation updates work correctly
- **Reactive** — head tags respond to signal changes and component mounting/unmounting

## Usage

### Installation

```bash
npm i @solidjs/meta
```

Peer dependency: `solid-js >=1.8.4`.

### SolidStart setup

Wrap the app with `<MetaProvider>` inside the `root` prop of `<Router>`. Optionally provide a `<Title>` fallback inside `<MetaProvider>`.

```tsx
// app.tsx
import { MetaProvider, Title } from "@solidjs/meta";
import { Router } from "@solidjs/router";
import { FileRoutes } from "@solidjs/start";
import { Suspense } from "solid-js";

export default function App() {
  return (
    <Router
      root={props => (
        <MetaProvider>
          <Title>SolidStart - My App</Title>
          <a href="/">Home</a>
          <Suspense>{props.children}</Suspense>
        </MetaProvider>
      )}
    >
      <FileRoutes />
    </Router>
  );
}
```

Then use head tag components in any route or component:

```tsx
// routes/index.tsx
import { Title, Meta, Link } from "@solidjs/meta";

export default function Home() {
  return (
    <main>
      <Title>Home - My App</Title>
      <Meta name="description" content="The home page" />
      <Link rel="canonical" href="https://example.com/" />
      <h1>Welcome</h1>
    </main>
  );
}
```

### Custom SSR setup

On the server, wrap the app with `<MetaProvider>` and use `getAssets()` to inject collected tags:

```tsx
// server.ts
import { renderToString, getAssets } from "solid-js/web";
import { MetaProvider } from "@solidjs/meta";
import App from "./App";

const app = renderToString(() => (
  <MetaProvider>
    <App />
  </MetaProvider>
));

res.send(`
  <!doctype html>
  <html>
    <head>
      ${getAssets()}
    </head>
    <body>
      <div id="root">${app}</div>
    </body>
  </html>
`);
```

On the client, no special setup is needed — just render head tag components inside `<MetaProvider>`:

```tsx
import { MetaProvider, Title, Meta, Link } from "@solidjs/meta";

const App = () => (
  <MetaProvider>
    <Title>Page Title</Title>
    <Meta name="description" content="A description" />
    <Link rel="icon" href="/favicon.ico" />
  </MetaProvider>
);
```

### Available components

#### `<Title>`

Sets the document title. Content is auto-escaped. Only the last `<Title>` in the tree wins (cascading).

```tsx
<Title>My Page Title</Title>
```

#### `<Meta>`

Injects `<meta>` tags. Supports `name`, `property`, `http-equiv`, `content`, `charset`, and `media` attributes.

```tsx
<Meta name="description" content="Page description" />
<Meta property="og:title" content="Open Graph Title" />
<Meta name="theme-color" media="(prefers-color-scheme: light)" content="#fff" />
<Meta charset="utf-8" />
```

Meta tags with the same `name` or `property` are deduplicated — the deepest instance wins. Tags with the same name but different `media` or other attributes are kept separate.

#### `<Link>`

Injects `<link>` tags. Useful for canonical URLs, favicons, preloads, and stylesheets.

```tsx
<Link rel="canonical" href="https://example.com/page" />
<Link rel="icon" href="/favicon.ico" type="image/x-icon" />
<Link rel="preload" href="/font.woff2" as="font" crossorigin />
```

#### `<Stylesheet>`

Shorthand for `<Link rel="stylesheet">`. Omits the `rel` prop.

```tsx
<Stylesheet href="/styles.css" />
```

#### `<Style>`

Injects `<style>` tags. Content is not auto-escaped (raw CSS).

```tsx
<Style>{`body { margin: 0; }`}</Style>
```

#### `<Base>`

Sets the `<base>` tag for relative URL resolution.

```tsx
<Base href="/app/" />
```

### Reactive head tags

Head tags respond to signals and component lifecycle:

```tsx
import { createSignal } from "solid-js";
import { Title, Meta } from "@solidjs/meta";

function DynamicMeta() {
  const [page, setPage] = createSignal("home");

  return (
    <>
      <Title>{page()} - My App</Title>
      <Meta name="description" content={`The ${page()} page`} />
      <button onClick={() => setPage("about")}>About</button>
      <button onClick={() => setPage("home")}>Home</button>
    </>
  );
}
```

When a component unmounts, its head tags are automatically removed. If another component provides the same tag, it takes over.

### Per-route meta in SolidStart

Each route can define its own head tags without affecting other routes:

```tsx
// routes/about.tsx
import { Title, Meta } from "@solidjs/meta";

export default function About() {
  return (
    <main>
      <Title>About - My App</Title>
      <Meta name="description" content="About our company" />
      <Meta property="og:type" content="website" />
      <h1>About Us</h1>
    </main>
  );
}
```

The `<Title>` from `app.tsx` acts as a fallback when no route provides one.

## Gotchas

- **`<MetaProvider>` must be in the tree** — rendering `<Title>`, `<Meta>`, etc. without `<MetaProvider>` throws `<MetaProvider /> should be in the tree`. Wrap at the root of your app, typically inside `<Router root={...}>`.
- **Only the last `<Title>` wins** — multiple `<Title>` components cascade; the deepest one in the tree determines the actual title. When it unmounts, the next deepest takes over. This is by design for per-route titles with a root fallback.
- **`<Meta>` deduplication uses `name`/`property` as key** — two `<Meta name="description">` tags will deduplicate (last wins). But `<Meta name="theme-color" media="light">` and `<Meta name="theme-color" media="dark">` are kept separate because `media` is part of the key.
- **`property` is treated as `name` for meta tags** — `<Meta property="og:title">` and `<Meta name="og:title">` are considered the same tag. The last one wins.
- **No `<title>` in server templates** — avoid hardcoding `<title>` in your server HTML template (e.g., `entry-server.tsx`). It would override `@solidjs/meta`'s dynamic title. Let the library manage it entirely.
- **SSR tags are marked with `data-sm`** — server-rendered head tags carry a `data-sm` attribute. The client-side provider strips these during hydration. Don't rely on `data-sm` in selectors.
- **`<Style>` content is not escaped** — unlike `<Title>` which auto-escapes, `<Style>` passes content as raw CSS. This is intentional for CSS injection.
- **`<Link>` and `<Base>` are not deduplicated** — unlike `<title>` and `<meta>`, link and base tags are not cascading. Each instance is added independently. Place them where needed.
- **SolidStart: put `<MetaProvider>` inside `root`** — not outside `<Router>`. The provider needs to be in the routing tree so route-level meta components work correctly.
- **Hydration requires `getAssets()`** — in custom SSR (non-SolidStart), you must call `getAssets()` from `solid-js/web` and inject its output into `<head>`. Without it, no server-rendered tags appear.
- **`<Stylesheet>` is just `<Link rel="stylesheet">`** — it's a convenience wrapper. Use `<Link>` directly when you need full control over `rel` or other attributes.
- **`MetaContext` is exported but internal** — `MetaContext` and `useHead` are available for advanced use cases (e.g., conditional meta injection from custom hooks). The standard approach is using the JSX components directly.
