# SSR and Hydration

Solid supports server-side rendering through `solid-js/web` (client) and `solid-js/server` (server). The SSR system supports streaming, Suspense boundaries, and hydration.

## Server-Side Rendering

```ts
import { renderToString, renderToStringAsync } from "solid-js/web";

// Synchronous
const html = renderToString(() => <App />);

// Async (awaits all resources)
const html = await renderToStringAsync(() => <App />);
```

- `renderToString` — renders immediately, unresolved resources render as empty
- `renderToStringAsync` — waits for all resources to resolve before returning HTML

### Server Entry Point

On the server, import from `solid-js/server` (not `solid-js`):

```ts
// server.ts
import { renderToString } from "solid-js/web";
import { App } from "./App";

const html = renderToString(() => <App />);
// html contains the rendered HTML string
```

The `solid-js/server` package provides the server-side implementation of reactive primitives and rendering. It's automatically used when bundling for Node.js.

## Hydration

```ts
// Client entry
import { render } from "solid-js/web";
import { App } from "./App";

render(() => <App />, document.getElementById("root")!);
```

- `render()` automatically detects existing server-rendered HTML and hydrates it
- No separate `hydrate()` call needed
- Components re-run on the client; DOM is patched to match

### enableHydration

```ts
import { enableHydration } from "solid-js";
enableHydration();
```

- Required for SSR + hydration to work
- Enables the hydration context tracking
- Usually called automatically by Solid's adapter/framework

## Streaming with Suspense

```tsx
// App.tsx
<Suspense fallback={<p>Loading user...</p>}>
  <UserProfile />  // uses createResource
</Suspense>
<Header />         // renders immediately
```

- `<Suspense>` boundaries become streaming boundaries in SSR
- Content outside Suspense renders immediately
- Content inside Suspense streams when resources resolve
- `deferStream: true` on a resource prevents it from streaming (waits for resolution)

### Resource SSR Options

```ts
const [data] = createResource(fetcher, {
  ssrLoadFrom: "server",    // Use server-fetched data (default)
  ssrLoadFrom: "initial",   // Use initialValue, ignore server data
  deferStream: true,         // Don't stream — wait for resolution
});
```

- `ssrLoadFrom: "server"` — hydrates with server-fetched data
- `ssrLoadFrom: "initial"` — ignores server data, uses `initialValue`
- `deferStream: true` — resource blocks the entire page (no streaming)

## sharedConfig

```ts
import { sharedConfig } from "solid-js/web";
```

- Internal configuration object for SSR/hydration
- Used by adapters to provide server context (load, gather, done callbacks)
- Generally accessed through framework adapters, not directly

## Pattern: Express SSR

```ts
// server.ts
import express from "express";
import { renderToString } from "solid-js/web";
import { App } from "./App";

const app = express();

app.get("*", (req, res) => {
  const html = renderToString(() => <App />);

  res.send(`
    <!DOCTYPE html>
    <html>
      <head>
        <script type="module" src="/client.js"></script>
      </head>
      <body>
        <div id="root">${html}</div>
      </body>
    </html>
  `);
});

app.listen(3000);
```

## Pattern: Vite SSR (SolidStart-style)

```ts
// entry-server.tsx
import { renderToString } from "solid-js/web";
import { App } from "./App";

export function render(url: string, manifest: any) {
  return renderToString(() => <App />);
}
```

## Pattern: Data Loading on Server

```tsx
// Server component with data
function Page() {
  const [data] = createResource(async () => {
    // Runs on server during SSR
    // Runs on client during hydration (skip with ssrLoadFrom)
    return fetch("/api/data").then(r => r.json());
  });

  return (
    <Suspense fallback={<Loading />}>
      <Show when={data()} keyed>
        {(d) => <div>{d.title}</div>}
      </Show>
    </Suspense>
  );
}
```

## isServer / isBrowser Detection

Solid doesn't provide built-in `isServer`/`isBrowser` flags. Detect environment:

```ts
const isServer = typeof window === "undefined";
const isBrowser = typeof window !== "undefined";
```

Or use the `sharedConfig` context:

```ts
import { sharedConfig } from "solid-js/web";
const isServer = !!sharedConfig?.context;
```

## Hydration Mismatch Handling

```tsx
function Component() {
  const [visible, setVisible] = createSignal(
    typeof window !== "undefined" ? localStorage.getItem("visible") === "true" : true
  );

  return (
    <Show when={visible()} keyed>
      <div>Content</div>
    </Show>
  );
}
```

- SSR and client must produce the same initial HTML
- Use `typeof window !== "undefined"` guards for browser-only data
- Mismatches cause hydration warnings and potential re-renders

## Gotchas

- **`enableHydration()` must be called** — without it, SSR output won't hydrate correctly
- **Server and client must produce matching HTML** — any mismatch causes hydration failures. Use `createEffect` (runs after render) for browser-only logic instead of component body.
- **`createResource` on server** — runs during SSR. Use `ssrLoadFrom: "initial"` if you want to skip server fetching.
- **`lazy()` in SSR** — uses `createResource` internally. The component suspends on both server and client.
- **`onMount` doesn't run on server** — use it for browser-only side effects. The server skips effects.
- **`createUniqueId()` is SSR-safe** — generates IDs that match between server and client during hydration.
- **Streaming requires server support** — the server must support HTTP streaming (e.g., Node.js `res.write()`). Simple `renderToString` sends complete HTML.
