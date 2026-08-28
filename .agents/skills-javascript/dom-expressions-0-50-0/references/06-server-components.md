# Server Components and Frame Streams (Solid 2.x line)

The `next` branch's headline feature. Primary docs in the repo: `docs/server-components.md` (usage/architecture), `docs/server-components-principles.md` (axioms, derivation decisions), `docs/frame-streams-rfc.md` (wire format + runtime mechanics), `docs/frame-seams-decision.md`, `docs/progressive-frame-emission-proposal.md`, `docs/generator-only-model.md` (deliberation, nothing decided).

## The model in three sentences

1. **A server component is a function returned from a `"use server"` server function.** The server function's *arguments* are the server's inputs (ids, filters — they drive fetching). The returned component's *props* are **client positions** — holes the client fills — and never travel to the server.
2. **Props are positions, not data.** When a server component renders `{props.children}`, it emits a marked range in the HTML, nothing more. The client decides what lives there, and whatever it puts there survives every server update.
3. **A boundary is a call.** A server component renders into a frame addressed by the call that produced it — function + arguments, the same per-args rule a query cache keys by. Re-fetching the same call *morphs* the server content in place (client state inside survives); different arguments are a different boundary — the call site rebinds, re-materialized instantly from retained state when that call has shown before.

Writing one:

```tsx
async function getStory(storyId) {
  "use server";
  const story = await db.stories.get(storyId);
  return (props) => (
    <article>
      <h1>{story.title}</h1>
      {story.comments.map((c) => (
        <props.comment cid={c.id}>
          <p>{c.text}</p>
        </props.comment>
      ))}
    </article>
  );
}
```

## The `$key` rule

Defaults need no identity: server content is stateless output (updates converge); a one-of-a-kind position (`props.children`) is identified by its prop name; iterated positions are positional by default. The one case that breaks is a **live reordering list** — positional identity keeps client state at position 0 while the entity that owned it moves. Name the occurrence by entity:

```tsx
<props.comment $key={c.id} cid={c.id}>…</props.comment>
```

Constraints: `$key` means something **only on slot calls** (on a DOM element it's just an attribute — server elements have no identity), and keyed occurrences must be **siblings** for reorders to follow the key (let the *client* wrapper provide the per-item element; a server-wrapped occurrence that reorders keeps correct content but resets client state).

## Client usage — `dynamic` is the whole surface

There is no server-component client API. `dynamic()` from `@solidjs/web` does it:

```tsx
const Story = dynamic(() => getStory(props.storyId));
return <Story comment={(p) => <CollapsibleComment …>{p.children}</CollapsibleComment>}>
  <ShareBar /> {/* client-only; remounts with the boundary when the story changes */}
</Story>;
```

- **Navigation is a prop change** — `storyId` changes → source re-calls → the site shows that story's boundary. Two panes on different stories are independent; two panes on the same story share one logical stream that fans out to both mounts.
- **Refetches don't re-fallback** — same (function, args) resolves to the *identical* component reference, so it passes `dynamic`'s equals-gate; the tree doesn't blink and the stream morphs in place.
- **State ownership follows the boundary** — a signal that lives *outside* the boundary (`collapsedAll`) survives navigation; state *inside* belongs to the call.
- Transport policy (mirror of the server's `frameTransformResult`): when the client's server-function runtime sees a frame-stream response, it streams chunks into the boundary and resolves with a per-boundary stable component (get-or-create). The host **retains an unmounted boundary's state** — stash on last-frame unregister, seed the next mount — so a pure cache hit renders what the call last showed, instantly. `applyFrameResponse(response, host, { as })` is the low-level surface for routers.
- **Data layer is the same data layer**: wrap section functions in `query` (route-level `preload` warms them — chunks buffer until a boundary mounts), `revalidate` streams fresh versions to every boundary on the stream, and single-flight mutations ride the response as regions addressed by (function, args) alongside the `{ value, data }` envelope.

## Initial page load

First load is streamed SSR — client components *inside* positions render on the server too, so the page is complete before JS. The client **adopts** the DOM:

- No hydration data blob for server content (the HTML *is* the data) and no per-element hydration keys: server output renders inside a `NoHydration` zone (adopted markup never hydrates element-by-element); each client position re-enters via `Hydration` under its occurrence namespace — those wrapper keys are the only claim keys the page carries.
- **Occlusion is handled, not leaked**: content a wrapper didn't render at SSR (collapsed comment thread) serializes once as a data record and mounts from the client store when revealed — one copy, always: markup when rendered, data when not, never both.
- **Hydration happens once, at load, and never again.** Post-load responses carry server content and args only; client components render client-side. This is the boundary that makes state preservation sound.
- Boot makes **zero requests**: markers are the record, wrappers claim by hydration key, occurrence args ride tiny records containing only values not recoverable from the page.

## Streaming / async

`<Loading>` (Suspense) works inside server components with no ceremony: the shell streams immediately with the fallback; async content arrives as a later chunk and reveals in place — initial document and every navigation response alike. Client positions inside async content mount when it reveals.

## Wire format — frame streams

Frames are addressed by (function, args); server content travels as HTML chunks, client positions as marked ranges. Client-side mechanics (from the runtime `frame-*` modules: `frame-client`, `frame-sink`, `frame-transport`, `frame-container-plugin`):

- **Live holes** (`createLiveHoles` in the server entry): async regions streamed after the shell; on the wire, container traces cross the slot border as **raw seroval streams** — not async iterables — because seroval decodes an async iterable as a generator wrapper that buffers every value a microtask behind, while hydration's claim walk is synchronous. A raw stream decodes as the stream object whose `.on()` replays the buffer synchronously; older payloads still take the async-iterable path.
- **Shell hold for `deferStream`**: a streaming shell is held for `deferStream` reads whose boundary mounts behind a root-level async hole; when hole resolution grows the blocking set the flush loop re-awaits it, and the boundary's pre-flush `replace()` splices resolved content into the held shell.
- **Streaming retry robustness**: a boundary that re-suspends mid-refetch loses nothing — the DOM is preserved off screen, the frame client morphs the detached range as chunks arrive (no document connectivity required), and resolution restores the already-updated nodes.
- **Chunk coalescing** and **readable-stream getters** (`docs/progressive-frame-emission-proposal.md`, changesets) smooth emission.
- **Preload of client JS during SSR**: the runtime emits `modulepreload` links for the client entry's static imports so the browser fetches them in parallel; the document's module script still loads the entry, dynamic imports stay demand-driven.

## Behavior claims (client half)

Frame content has no compiled creation code, so the frame runtime **sweeps materialized/adopted subtrees** for `_bnd` markers — stamping each marked element with its owning frame, arming document listeners for claimed event types, and firing ref positions once per (element, prop) with morph-replacement re-fire. Dispatch resolves handlers at event time through the frame's live client props, so re-renders are latest-props by construction. Ref props fire under the frame creator's owner scope (effects/context/cleanup work inside, bound to the frame owner). The dispatch seam key is `Symbol.for("dx.bnd")` mirroring the `_bnd` attribute.

**Link state rides the element-claim contract**: compiled client output claims `a[href]`/`form[action]` at creation (`registerElementClaim`); the frame runtime re-claims a claimable element whenever a morph touches any of its attributes — the morph makes attributes match server output exactly, which strips consumer-applied state (`aria-current`, `data-active`), and the re-claim lets the consumer reassert it (`href`/`action` transitions re-claim even on removal). Claims fire under the boundary's reactive owner so `onCleanup`-scoped per-element state disposes with the boundary. One registry, both render paths, dormant without a consumer. A claim-carrying stub landing in a **spread** on a server-rendered element dev-warns — claims ride named `ref`/`on*` positions only, because the compiler can't see through spreads.

## Architecture invariants (for integrators)

1. **Everything ships once** — server content as HTML, client values as data records, never both.
2. **Hydration is t = 0 only** — never design flows where the server renders client components post-load.
3. **The call names the content; the site owns the mount** — content keyed by (function, args) both peers derive independently; same call ⇒ same store ⇒ morph in place; different args ⇒ rebind.
4. **Occurrence identity belongs to keys** — `$key`d positions keep state across refetches; unkeyed are positional.
5. **The server never sees client state; the client never re-renders server content** — server HTML is wrapped, moved, revealed — never rebuilt.

## Cost and identity

~6.5 KB min+gzip for the whole client machinery (store, streaming, slot model, transport, stable-component policy, claim sweeps) for an app already using server functions; the inner DOM reconciler is 0.86 KB. Apps importing none of it pay zero bytes (CI size-guard enforced). It is not RSC (no serialized element trees, no double-shipped content), not islands (one client tree wraps the server content), not hypermedia-with-a-morpher (updates preserve client-owned regions structurally through typed positions).

## SSR utilities reference (from the runtime)

`renderToString` / `renderToStream` · `useHead` (SSR registry; static shell `<title>` byte-rewritten in place so the registry winner wins — see runtime reference) · `HydrationScript` / `generateHydrationScript({ eventNames, nonce })` · `createSSRResponse` / `getRequestEvent` / `createRequestEvent` / `commitResponseStub` / `commitEventResponse` / `getExpectedRedirectStatus` · `ssrGroup` / `createLiveHoles` · `scriptNonce` / `styleNonce` (split CSP nonce API: `{ script, style }` requires both keys, `false` leaves a destination un-nonced) · `escape(s, attr)` · `composeMiddleware`.
