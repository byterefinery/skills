---
name: solid-meta-0-29-8
description: SolidJS document head management (@solidjs/meta v0.29.8) providing SSR-ready Title, Meta, Link, Style, Base, and Stylesheet components managed through a MetaProvider context. Use when setting or reactively changing document head tags (title, meta, link, style, base href) in SolidJS, SolidStart, or custom SSR Solid apps, including route-based head updates.
license: MIT
compatibility: Requires the @solidjs/meta npm package and solid-js peer dependency ^1.8.4; Solid 2 support lives on the @solidjs/meta@next tag
metadata:
  tags:
    - javascript
    - frontend
    - seo
    - solidjs
---

# solid-meta 0.29.8

## Overview

@solidjs/meta (v0.29.8, MIT) is asynchronous, SSR-ready document head management for SolidJS, based on React Head. It lets you define `document.head` tags anywhere in your component hierarchy — useful when tag information lives deep in the tree. No dependencies, works with asynchronous rendering, and supports SolidJS 1.x (the 0.29.x peer range is capped at `solid-js ^1.8.4`; Solid 2 support ships on the `@solidjs/meta@next` tag).

Head components: `MetaProvider` (required wrapper), `Title`, `Meta`, `Link`, `Style`, `Base`, `Stylesheet`, plus the low-level `useHead` hook.

## Usage

### Install

```sh
npm i @solidjs/meta
```

### Client setup

Wrap your app with `<MetaProvider />`, then render head tag components anywhere — there is nothing special required on the client:

```jsx
import { MetaProvider, Title, Link, Meta } from "@solidjs/meta";

const App = () => (
  <MetaProvider>
    <div class="Home">
      <Title>Title of page</Title>
      <Link rel="canonical" href="http://solidjs.com/" />
      <Meta name="example" content="whatever" />
    </div>
  </MetaProvider>
);
```

### Components

| Component    | Renders  | Notes                                                        |
| ------------ | -------- | ------------------------------------------------------------ |
| `Title`      | `<title>`| Children are HTML-escaped                                    |
| `Meta`       | `<meta>` | `name` or `property` (treated as `name` for tag identity)    |
| `Link`       | `<link>` |                                                              |
| `Style`      | `<style>`| Children are the CSS text                                     |
| `Base`       | `<base>` |                                                              |
| `Stylesheet` | `<link>` | `Link` shortcut with `rel="stylesheet"` preset (`rel` omitted from its props) |

All accept the standard HTML attributes for their element. Attribute notes:

- **`Meta`** — supports `name`, `property`, `http-equiv`, `charset`, `media`, `content`. Meta tags with the same `name`/`property` deduplicate (deepest/last wins); the same name with different `media` or other key attributes is kept separate.
- **`Link`** — useful for canonical URLs, favicons, preloads, and stylesheets.
- **`Style`** — content is raw CSS and is **not** escaped (unlike `Title`, which HTML-escapes children).
- **`Base`** — sets the `<base>` tag for relative URL resolution.

### Reactive head tags

Head tags respond to signals and component lifecycle — when a component unmounts, its tags are automatically removed and another provider of the same tag takes over:

```jsx
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

### SolidStart setup

1. Wrap your app with `<MetaProvider />` inside the `root` of the `<Router />` component.
2. Optionally provide a `<Title />` fallback inside `<MetaProvider />`.

```jsx
export default function App() {
  return (
    <Router
      root={props => (
        <MetaProvider>
          <Title>SolidStart - Basic</Title>
          <a href="/">Index</a>
          <a href="/about">About</a>
          <Suspense>{props.children}</Suspense>
        </MetaProvider>
      )}
    >
      <FileRoutes />
    </Router>
  );
}
```

Each route can then define its own head tags without affecting other routes — the root `<Title>` acts as a fallback when a route provides none:

```jsx
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

### Custom SSR setup

Wrap your app with `<MetaProvider />` on the server, then insert the collected tags with `getAssets` from `solid-js/web`:

```jsx
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

On the server, tags are collected and rendered with a `data-sm` marker attribute. On the client, those server-generated tags are removed in favor of client-rendered tags so SPAs can change head tags on subsequent page loads.

## Gotchas

- **Never add a normal `<title />` tag in server files.** In SolidStart projects that means `entry-server.jsx|tsx` (or any server template file) — a static title there overrides @solidjs/meta's functionality entirely.
- **`MetaProvider` must be in the tree.** Rendering a head tag component without it throws `"<MetaProvider /> should be in the tree"` — this includes using the `useHead` hook directly.
- **Titles and metas are "cascading" — the last rendered one wins.** Multiple `<Title>` components (or `<Meta>` with the same name/property) collapse to a single element in `<head>`; unmounting the last one restores the previous instance. `<link>`, `<style>`, and `<base>` are not cascading — every instance renders.
- **Meta identity includes all key attributes.** Two metas with the same `name` but different `content` (or `charset`/`media`/`http-equiv`) coexist; same name and same key attributes collapse to the last.
- **The SSR head must actually be emitted.** Server-rendered tags are collected into `getAssets()` — if your server template renders `<head>` statically without it (and without `getAssets()`), the head tags never reach the page.
- **Solid 2 users need the `next` tag.** The 0.29.x line pins `solid-js` peer to `^1.8.4` on purpose so it does not install against Solid 2.0; Solid 2 support is published as `@solidjs/meta@next`. For older bases: Solid 1.0 needs 0.27.x+, Solid 0.x needs 0.26.x.
- **Don't rely on `data-sm` in selectors.** Server-rendered head tags carry a `data-sm` marker attribute so the client provider can strip them during hydration — it's an implementation detail.
- **`MetaContext` is exported but internal.** `MetaContext` and `useHead` are available for advanced use (e.g. conditional meta injection from custom hooks); the standard approach is using the JSX components directly.
- **`<Style>` content is not escaped.** Unlike `<Title>` (which HTML-escapes), `<Style>` passes children through as raw CSS — intentional for CSS injection.
