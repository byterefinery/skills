# Runtime (`dom-expressions`)

The runtime package is what the compilers emit calls into and what the tagged-jsx / hyperscript adapters delegate to. Entry points: `dom-expressions/src/client`, `dom-expressions/src/server`, `dom-expressions/src/universal`, `dom-expressions/src/reconcile`.

## rxcore — the reactive core contract

The runtime imports its reactivity from the virtual module `rxcore`, renamed at build time by `babel-plugin-transform-rename-import` to your reactive core file. Required exports:

- `root(dispose => {...}, { id })` — create a root owner; `dispose` is the disposer.
- `effect(fn, cb)` / `createRenderEffect` — reactive effect with an update callback (the compiler's `effectWrapper`, default name `effect`).
- `memo(fn, equal)` — derived value (the compiler's `memoWrapper`, default name `memo`).
- `getOwner`, `untrack`, `runWithOwner`, `mergeProps` (typically `merge`), `flatten`, `sharedConfig` (plain object the runtime mutates), `createComponent(Comp, props)`.

Optional seams (cores that don't provide them degrade gracefully):

- `waitAsset` — CSS-reveal gating: throws a core `NotReadyError` bound to the promise while unsettled so tracked contexts (transitions, boundary reveals) hold and retry on settle; no-op once settled.
- `driveList` — patch-mode lists: drives a keyed store array through the store's row-ops channel instead of `mapArray` + `reconcileArrays`.
- `patchableRaw` / `registerPatch` — patch-mode records: resolve a subject to its patchable raw backing and register a compiled patch body.

Example core (Solid):

```js
import { untrack } from "@solidjs/signals";
export const sharedConfig = {};
export function createComponent(Comp, props) { return untrack(() => Comp(props)); }
export { createRoot as root, createRenderEffect as effect, createMemo as memo,
         getOwner, untrack, merge as mergeProps } from "@solidjs/signals";
```

## Client entry — `dom-expressions/src/client`

### render / hydrate

`render(code, element, init?, options?)` — registers the element as a delegated root, creates a root owner, and inserts `code()` into the element. Returns a disposer that tears down effects, unregisters delegation, and clears `element.textContent`.

`hydrate(code, element, options?)` — installs the hydration runtime and walks server HTML, claiming nodes by the `pl-` placeholder protocol instead of creating them. If the document was already fully hydrated (`_$HY.done`) it falls back to `render`. It wires `sharedConfig` to the `_$HY` globals (`completed`, `events`, `load`, `has`, `gather`, `loadModuleAssets`, `cleanupFragment`, `registry`, `boundaryScopes`). Multiple `hydrate` roots share one `sharedConfig` but each call replaces `registry`/`gather`; boundary scopes are keyed by full boundary id so a boundary that resumes after another root has started claims against the root it registered under.

Support: `getNextElement`, `getNextMatch`, `getNextMarker`, `getFirstChild`, `getNextSibling`, `runHydrationEvents`, `getHydrationKey`, `installHydrationRuntime`.

### template and insert — the two workhorses

`template(html, flag)` returns a thunk. `flag === 1` → `document.importNode` of a cached `<template>` (used for components, `_$template` with import semantics); `flag === 2` returns the first child's first child (nested); otherwise `cloneNode(true)` of a shared cached node. Creating real DOM during hydration throws in dev (`bypassGuard` exists for the hydration path).

`insert(parent, accessor, marker, initial, options)` — the universal binding primitive:

- `accessor` may be a value or a function; non-functions are normalized and inserted once.
- `marker !== undefined` means **multi** (a list hole, e.g. compiled `<For>`/`.map()`): the region is bounded by `parent` + `marker`, empty multi-holes get a `""` placeholder text node.
- Two-level effect: the outer effect reads the accessor; if the value is itself a function it opens an inner effect that unwraps it (`INNER_OWNED` sentinel distinguishes the two), with `{ schedule: true }` on the update so nested updates are batched.
- `accessor.$s` (compiler-stamped scope marker) opts the outer effect into `scope: true`.
- **Patch-mode list seam**: an accessor carrying `$ll` metadata is offered to the core's `driveList` first. Admission is compile-time only — the row function must carry the `rowProof` stamp and the subject must be a patchable store array. A declined offer (unproven rows, non-store subject, marker-bounded hydration region, key/count mismatch) runs the classic `mapArray`/reconcile path; if an engaged list later *leaves* the contract (identity swap to a derived array, shallow↔deep switch) the driver clears the region and re-enters `insert` with a bare accessor under the **original** owner. There is no runtime purity probe.
- Under hydration, initial nodes are claimed via `hydrationRt.claimInitial` and regions reclaimed on each update.

`assign(node, props, skipChildren, prevProps, skipRef)` — updates an element from a new props object; removed props are cleared through the same `assignProp` path with `null`; `children` routes through `insertExpression`.

### Attribute / property / class / style

- `setProperty(node, name, value)` — plain property set (skipped during hydration).
- `setAttribute(node, name, value)` — `null`/`false` removes, `true` → `""`. Frozen contract with compiled output: `href`/`action` can only change through compiler-owned write paths that land here, so this one spot re-runs the element-claim check (see below).
- `setAttributeNS`, `className(node, value, prev)` (handles arrays/objects/strings, prev-diffed), `style(node, value, prev)`, `setStyleProperty(node, name, value)`.
- `spread(node, props, skipChildren)` — the spread binding; order of independent bindings is not guaranteed.
- `dynamicProperty(props, key)` — reads a getter prop from a component props object.

### Events and delegation

CamelCase handlers (`onClick`) compile to delegation: `addEvent(node, name, handler, delegate)` stores handlers in a per-node map, and `delegateEvents(["click"])` attaches one listener per event name per container. `registerDelegatedRoot(root)` / `unregisterDelegatedRoot` manage root containers; `registerDelegatedContainer(container, owner)` / `unregisterDelegatedContainer` let you scope delegation to sub-containers (e.g. shadow roots). Delegates are owned by render roots and removed on disposal. Delegated events work with Web Components and Shadow DOM **only when the event is composed** (most UA UI events + custom composed events). Non-bubbling events fall back to Level-1 `on_____` bound listeners. Bound (non-delegated) value-carrying handlers: pass an array — `onClick={[handler, item.id]}` passes `item.id` first, the event second.

Custom delegated events should be all-lowercase (native convention) for casing to work; use a ref/directive with `addEventListener` when you need `addEventListener` options or custom event casing.

**Behavior claims** (Solid 2 line): frames sweep materialized/adopted subtrees for `_bnd` markers, stamping each marked element with its owning frame, arming document listeners for claimed event types, and firing ref positions once per (element, prop) — with morph-replacement re-fire. Dispatch resolves handlers at event time through the frame's live client props (`FrameOptions.props`), so re-renders are latest-props by construction. Event arming flows through the `delegate` host option on `createFrameHost` rather than a module-scope global (the old top-level publication retained the whole event system in every tree-shaken subset). Ref props fire under the frame creator's owner scope, so effects/context/cleanup work inside them, bound to the frame owner (run at disposal, not element replacement). The dispatch seam key is `Symbol.for("dx.bnd")` mirroring the `_bnd` marker attribute.

### Element claims (navigation contract)

`registerElementClaim(handler)` / `claimElement(node)` / `claimElementTree(root)` — a dormant registry of consumer handlers (e.g. external-link, `download`, `target`, base-path handling). The selector is `a[href], form[action]`. Claims fire indiscriminately — filtering is the consumer's job. `claimElementTree` is the subtree sweep used when serialized server content becomes live DOM without per-element compiled creation code. Without a registered consumer every claim call is one null check.

### Head and assets

`useHead(tags)` — declarative `<head>` management: tags can be a tag object, array, or thunk; winners are resolved per document (see `head.js`: `HEAD_ELIGIBLE_TAGS`, `classifyHeadTag`, `resolveHead`, replaceable/resource identity). A static shell `<title>` is byte-rewritten in place (original stashed on `data-dhf`, shed with `data-dh` on disposal) so the registry winner wins the served page; embedded (`onHead`) hosts get a retitle script under `noScripts` instead.

`acquireAsset(descriptor)` / `warmAsset(descriptor)` — CSS/script asset management with exclusive-asset descriptors; module assets of lazy boundaries are preloaded during server rendering, and the client entry's static JavaScript imports get `modulepreload` links during SSR so the browser fetches them in parallel.

### Other

- `ref(fn, element)` / `applyRef(r, element)` — `ref` prop binding (not reactive).
- `rowProof(fn)` — compiler stamp marking a row function as patch-eligible (used with `driveList`).
- `scope(fn)` — stamps `fn.$s = true` so `insert` opts into scoping.
- `patchDriver(subject, body)` — runs a compiled patch body against a patchable record subject (falls back to the classic dual-phase effect when the core lacks the patch seams).
- `getOwner()`, `sharedConfig`, `RequestContext` (symbol) re-exported for cores/integrations.
- Element sets: `DOMElements`, `SVGElements`, `MathMLElements`, `VoidElements`, `RawTextElements`, `Namespaces`, `DelegatedEvents`, `DOMWithState`, `ChildProperties` — the classification tables the compilers and adapters share.

## SSR entry — `dom-expressions/src/server`

- `renderToString(code, options?)` / `renderToStream(code, options?)` — options include `context` (with `nonce`), `onHead`, `documentMode`, `stream` flags.
- `useHead(tags)` (SSR-side registry), `scriptNonce(nonce)` / `styleNonce(nonce)` — split CSP nonce API: a `{ script, style }` pair requires both keys (`false` leaves a destination un-nonced); `context.nonce` stays user-supplied.
- `HydrationScript(props)` component and `generateHydrationScript({ eventNames, nonce })` — emits the `_$HY` bootstrap (event registry, module loader, hydration driver).
- `createSSRResponse(result, event, options?)`, `getRequestEvent()`, `createRequestEvent(request, init)`, `commitResponseStub(stub, { allowLateLocation })`, `getExpectedRedirectStatus(response)`, `commitEventResponse(response, event)` — request/response plumbing for server handlers.
- `ssr(t)` / `ssrElement` / `ssrAttribute` / `ssrClassName` / `ssrStyle` / `ssrStyleProperty` / `ssrSelectValues` / `ssrHydrationKey` / `ssrClaim(map)` — the string-builders the SSR-compiled code calls.
- `ssrGroup(fn, n)`, `createLiveHoles(sink, scoped)` — async hole / streaming plumbing feeding the frame-stream wire format.
- `escape(s, attr)` — HTML/attribute escaping (the only safe HTML insertion is through these; raw `innerHTML` bypasses escaping).
- `composeMiddleware(middlewares)` — SSR middleware composition.

## Universal entry — `dom-expressions/src/universal`

`createRenderer({ createElement, createTextNode, createSentinel, isTextNode, replaceText, insertNode, removeNode, cleanupNodes, setProperty, getParentNode, getFirstChild, getNextSibling })` — builds the same `insert`/`spread`/`assign` machinery on top of abstract node primitives. This is what `generate: "universal"` and `"dynamic"` (universal fallback + per-tag DOM routing via `renderers: [{ name, moduleName, elements }]`) compile against. In the 0.50 line, compile-time static host props are passed to `createElement(tag, staticProps)` so custom renderers can configure nodes before children are inserted; dynamic props and spreads still use `setProp`/`spread`.

## Reconcile

`dom-expressions/src/reconcile` — `reconcileArrays` used by `For`/`.map()` for keyed list diffing (prefix/suffix common matching, single-anchor end swap). Fixed in this line for reorderings where a detached node could still match as a common suffix — DOM and universal prefix/suffix now require the node to still belong to the same parent.
