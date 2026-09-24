# SSR and the HTTP exchange, server functions

`@solidjs/web` owns both halves of server rendering: the render entry points and the HTTP exchange they run inside. Anything that can run under Node/Deno/Workers can server-render from core alone — no metaframework required.

Table of contents: [render entry points](#render-entry-points) · [request event](#the-request-event) · [response head from the render tree](#response-head-from-the-render-tree) · [cookies](#cookies) · [response-head lifecycle](#response-head-lifecycle) · [server functions](#server-functions) · [server components](#server-components-experimental)

## Render entry points

Client (browser):

- `render(() => <App />, element)` — fresh mount; returns a dispose function.
- `hydrate(() => <App />, element)` — claim server-rendered DOM. Hydration happens **once, at t = 0**, and never again (see server components).

Server (node/deno/worker conditions):

- `renderToString(() => <App />)` — synchronous; async boundaries render their fallbacks.
- `renderToStream(() => <App />, options?)` — streaming renderer: the shell flushes first, then each async boundary streams its resolved fragment plus the activation script that swaps it in. A primitive marked `deferStream: true` holds the shell flush until its first value resolves. The result is **thenable** — `await renderToStream(...)` resolves to the fully settled HTML string.

The document needs the hydration script ahead of the app markup: `generateHydrationScript({ nonce?, eventNames? })` returns it as a string for hand-built documents; `<HydrationScript />` renders it in JSX documents.

### Consuming the stream

`renderToStream` returns exactly one consumption surface per render (a second consumer throws):

```ts
import { renderToStream } from "@solidjs/web";

export function handler(request: Request): Response {
  const stream = renderToStream(() => <App />);
  return new Response(stream.readable, { headers: { "content-type": "text/html" } });
}

// pipe(writable)    — Node-style writable streams
// pipeTo(writable)  — web WritableStream; promise settles when fully written
// .readable         — Response-body-ready ReadableStream (Uint8Array chunks)
```

## The request event

The per-request context: the incoming `Request` plus a `locals` bag.

```ts
import { getRequestEvent } from "@solidjs/web";
import { provideRequestEvent } from "@solidjs/web/storage";

async function handleRequest(request: Request) {
  return provideRequestEvent({ request, locals: {} }, () =>
    renderToStream(() => <App />)
  );
}

// Anywhere under a request scope (component bodies during SSR, server functions, middleware):
const event = getRequestEvent(); // undefined outside a request scope
```

`locals` is typed via **module augmentation** (no ambient `App.*` namespace):

```ts
declare module "@solidjs/web" {
  interface RequestEventLocals {
    user: User;
  }
}
```

Sharp edges: the augmenting file must be a **module** (a standalone `.d.ts` needs `export {}`; in a global script file `declare module` *replaces* the package types instead of augmenting them), and don't give the declaration file a sibling `.ts` basename (it's treated as compiled output and silently dropped).

## Response head from the render tree

```ts
import { httpStatus, httpHeader } from "@solidjs/web";

function NotFound() {
  httpStatus(404);
  httpHeader("cache-control", "no-store");
  return <h1>Not found</h1>;
}
```

`httpStatus(code, text?)` / `httpHeader(name, value, { append? })` are **scope-tied declarations**: "while this reactive scope is live, the response has this status/header." Call them bare in component/reactive-scope bodies (including behind `if`); they un-declare on scope disposal (each write snapshots the prior value and restores it — a recovering error boundary retracts rather than stomps). Client-side they are no-ops.

They are a **shell-time API**: under streaming, anything resolving after the shell flush is past `committed` and can't speak. If a header depends on late data, put `deferStream: true` on the source that decides it. `httpStatus`/`httpHeader` replace Start's `<HttpStatusCode>`/`<HttpHeader />` components — core ships functions only.

## Cookies

Core ships the **codec + native `Headers`**, nothing ambient:

```ts
import { parseCookieHeader, serializeCookie } from "@solidjs/web";

const event = getRequestEvent()!;
const cookies = parseCookieHeader(event.request.headers.get("cookie"));
const theme = cookies.theme;

event.response.headers.append(
  "set-cookie",
  serializeCookie("session", token, { httpOnly: true, secure: true, sameSite: "lax", maxAge: 60 * 60 * 24 * 7 })
);
// deleting = expiring: empty value + Max-Age=0
```

- Dependency-free, one thing: percent-encoded names/values, `path` defaults to `/`, everything else emitted exactly when given. No signing — integrity layers belong to the caller.
- Reads are a request-only view: a `Set-Cookie` appended in the same request does **not** read back.
- Writes are event-time `Headers.append` mutations.
- **Multi-`Set-Cookie` guarantee:** every core head materialization carries `Set-Cookie` entry-by-entry (`getSetCookie()` + append) — never fold with `get`/`set`.
- Post-commit writes fail loudly (throw in dev, `console.error` + no-op in prod).
- Sessions are **app-layer** by ruling: the blessed composition is `@remix-run/cookie` (signed, secret-rotating, WebCrypto) + the request event — see the recipe in the Solid 2.0 RFC 12 (documentation/solid-2.0/12-ssr-http.md in the solid repo).

## Response-head lifecycle

A handler's response leaves through exactly two exits:

```ts
import { createRequestEvent, createSSRResponse, commitEventResponse, composeMiddleware } from "@solidjs/web";

export function handleRequest(request: Request): Promise<Response> {
  const event = createRequestEvent(request);
  return provideRequestEvent(event, () =>
    createSSRResponse(renderToStream(() => <App />), event)
  );
}
```

- **Page results** → `createSSRResponse(result, event, options?)` — accepts a string or a `renderToStream` result. At shell flush the stub commits; a `Location` present before flush becomes a real redirect (bodyless, carrying cookies); a post-flush `Location` appends a client-side `window.location` script. Stream results resolve at shell flush, so the head goes out at the right moment by construction.
- **Any other `Response`** (middleware early return, API result) → `commitEventResponse(response, event?)` at the handler edge. Idempotent for already-committed stubs, so a handler applies it unconditionally.
- `composeMiddleware([ (request, next) => ... ])` — web-standard `(request, next) => Response` chains running inside the request scope (`getRequestEvent()` works in middleware); nothing reaches the wire until the outermost middleware returns.

## Server functions

`"use server"` moved from SolidStart into core: a directive compiled by the build plugin, backed by a framework-agnostic runtime at `@solidjs/web/server-functions`.

```ts
export async function addTodo(title: string) {
  "use server";
  await db.insert(title);
  return reload({ revalidate: "todos" });
}
```

- **Function-level** directive extracts that function; **module-level** does the same for every export.
- Anything referenced only inside the body never reaches the client (orphan-scoped dead-code elimination) — **the directive boundary is the privacy mechanism**. Validation, auth guards, and logging are lines of code *inside the body*; there is no third place. Treat arguments as untrusted input.
- Client compiled output POSTs to the endpoint (default `/_server`) with the function id in the `X-Server-Function-Id` header. Server: `handleServerFunctionRequest(request)` (plus `import "virtual:solid-server-function-manifest"`) resolves, decodes, runs under a request-event scope, and encodes the result.

### Response helpers (both sides)

```ts
import { redirect, reload, respond } from "@solidjs/web";

return redirect("/dashboard", { revalidate: "session" }); // integration follows; 302 default
return reload({ revalidate: "todos" });                   // "refetch your data"
return respond(item, { status: 201, revalidate: "items" });// value + HTTP metadata
```

`respond()` produces a `ResponseEnvelope` — real JSON body for no-JS consumers, in-memory value for scripted calls. Check with `isResponseEnvelope()`.

### Thrown errors — sanitized by default

A thrown `Response`/envelope is control flow and travels untouched. A **plain** thrown value (bare `Error`, string, object) is sanitized outside dev builds (generic `"Internal Server Error"` — no leaked queries/connection strings); dev keeps full fidelity. Two ways to send intentional error content in production: `respond(error, { status })`/thrown envelopes, or `markSafeError(error)` (brand it; check with `isSafeError`).

### Extension surface (shipped)

- **`GET(fn)`** — declare HTTP GET (args codec-encoded in the query string — cacheable). `export const getUser = GET(async (id) => { "use server"; ... })`.
- **`withMeta(fn, meta)`** — user-declared transport metadata; read in `prepareRequest` as `context.meta` (declare-on-function, react-in-hook).
- **`getServerFunctionMetadata(fn)` / `isServerFunction(fn)`** — typed accessors over the metadata channel.
- **`prepareRequest`** — client transport middleware (single hook, userland composition); the OAuth-bearer home.
- Client config: `configureServerFunctionsClient({ endpoint?, codec?, prepareRequest?, serializeArgs?, responseHandler? })`. Arguments with a natural HTTP encoding (lone string, FormData, File, Blob) go as-is; everything else is **plain JSON by default** — values JSON can't carry (Dates, Maps, Sets, typed arrays, cycles) throw with a directed message unless you opt in via `enableRichArguments()` from `@solidjs/web/server-functions/rich-args`. Results always travel through the codec.
- **Single-flight:** server hook `collectFlightData(event, outcome)` envelopes `{ value, data }` under `X-Single-Flight`; client `subscribeFlightData(consumer)` is the opt-in (the transport then sends the header). A mutation response can carry both the new value and the invalidated route data in one round trip.
- **No-JS:** a reference's `.url` is a self-describing form `action`; unscripted calls (no `X-Server-Function-Instance` header) parse args from the query string/FormData; the `handleNoJS` hook builds the response.
- **Validation** deliberately ships from neither core nor router — it's ordinary code at the top of the body over [Standard Schema](https://standardschema.dev) (zod, valibot, arktype).

## Server components (experimental)

**Status:** experimental preview — excluded from 2.0's stability guarantees; API and wire format may change between prereleases.

A **server component is a function returned from a server function** — no new component API, no `"use client"`. The server function's arguments are the server's inputs; the returned component's props are client positions (**slots**) the server marks but never renders. The client's entire consumption surface is `dynamic`:

```tsx
async function getStory(id: number) {
  "use server";
  const story = await db.stories.get(id);
  return (props) => (
    <article>
      <h1>{story.title}</h1>
      {story.comments.map(c => (
        <props.comment $key={c.id} cid={c.id}>
          <p>{c.text}</p>
        </props.comment>
      ))}
      <footer>{props.children}</footer>
    </article>
  );
}

function StoryPage(props) {
  const Story = dynamic(() => getStory(props.storyId));
  return (
    <Story comment={(p) => <CollapsibleComment cid={p.cid}>{p.children}</CollapsibleComment>}>
      <ShareBar />
    </Story>
  );
}
```

- Boundary identity is **derived, never declared**: the `(function, arguments)` address keys the boundary, so same-args refetches morph content in place (client state inside the boundary survives) and different args swap boundaries instantly from retained state.
- **Single-copy invariant:** server content travels as HTML, data as records — nothing travels as both. View-source test: any piece of content appears exactly once.
- **Hydration happens once at t = 0, never again.** Post-load responses carry server content and slot args only.
- `<props.children>` is a direct-insert slot; `<props.x>` is a render-prop slot (one occurrence per call); `$key` names occurrence identity for reordering live lists.
- Client cost: ~6.5 KB for an app already using server functions; zero bytes if unused.

Enablement: `serverFunctions: { components: true }` on `@solidjs/vite-plugin`, or manually — server: `frameTransformResult`/`frameTransformDirectResult`/`frameTransformFlightResult` from `@solidjs/web/frames/server` into `configureServerFunctionsServer`; client: `installServerComponents()` from `@solidjs/web/frames` before `hydrate`; document SSR: `ServerComponentPlugin` + `SERVER_COMPONENT_BOOTSTRAP` from `@solidjs/web/frames/server` with `renderToStream(..., { plugins: [...] })`. The `examples/hackernews` app in the solid repo is the complete working recipe (no Vite, no metaframework).
