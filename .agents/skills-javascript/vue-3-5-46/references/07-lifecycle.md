# Lifecycle hooks

Source: `packages/runtime-core/src/apiLifecycle.ts` (v3.5.46). Every hook below is exported there.

## Component hooks

| Hook | When it runs |
|---|---|
| `onBeforeMount` | before the mounted DOM is patched |
| `onMounted` | after the component is mounted |
| `onBeforeUpdate` | before the re-render caused by state changes |
| `onUpdated` | after the re-render / DOM patch |
| `onBeforeUnmount` | before unmount |
| `onUnmounted` | after unmount (cleanup listeners, intervals, etc.) |
| `onServerPrefetch` | SSR only — prefetch data on the server before rendering |
| `onActivated` / `onDeactivated` | KeepAlive activation/deactivation (exported from `components/KeepAlive.ts`) |

## Error capture

- `onErrorCaptured(hook, target?)` — hook receives `(err, instance, info)`; return `false` to stop propagation (per the `ErrorCapturedHook` type in apiLifecycle.ts).

## Debug hooks

- `onRenderTriggered` / `onRenderTracked` — `DebuggerHook` callbacks receiving `DebuggerEvent` (used by devtools/profiling; types `DebuggerOptions`, `DebuggerEventExtraInfo` come from the reactivity effect API).

## Notes from the implementation

- Hooks are created by a `createHook(lifecycle)` factory that injects into `currentInstance` — call them **synchronously** in `setup()` / `<script setup>` top level. The dev warning for async setup says hooks before the first `await` are fine ("hooks before the first await statement"), so top-level-of-setup registration is the requirement, not "no awaits at all".
- Post-create hooks are no-ops during SSR except `onServerPrefetch` (`isInSSRComponentSetup` check in apiLifecycle.ts).
- `injectHook(lifecycle, hook, target?)` is exported for custom renderers to add their own lifecycle points.
