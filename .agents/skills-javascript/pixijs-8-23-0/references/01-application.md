# Application setup

## Contents

- [application](#application)
  - [Lifecycle: construct, init, render, destroy](#lifecycle-construct-init-render-destroy)
  - [ResizePlugin](#resizeplugin)
  - [Changing resolution after init](#changing-resolution-after-init)
  - [Render loop](#render-loop)
  - [CullerPlugin (opt-in)](#cullerplugin-opt-in)
  - [Custom Application plugins](#custom-application-plugins)
- [application-options](#application-options)
  - [View / canvas](#view--canvas)
  - [Background](#background)
  - [Renderer preference](#renderer-preference)
  - [Shared rendering](#shared-rendering)
  - [Ticker (TickerPluginOptions)](#ticker-tickerpluginoptions)
  - [Resize (ResizePluginOptions)](#resize-resizepluginoptions)
  - [Culler (CullerPluginOptions)](#culler-cullerpluginoptions)
  - [Events](#events)
  - [Accessibility](#accessibility)
  - [WebGL-only options](#webgl-only-options)
  - [WebGPU-only options](#webgpu-only-options)
  - [Garbage collection](#garbage-collection)
  - [Per-renderer overrides](#per-renderer-overrides)

## application

`new Application()` and async `app.init()`, `app.stage`/`renderer`/`canvas`/`screen`, resizing and resolution, plugins, and `app.destroy()`.

### Lifecycle: construct, init, render, destroy

```ts
import { Application } from "pixi.js";

const app = new Application();

await app.init({
  resizeTo: window,
  background: "#1099bb",
  antialias: true,
  autoDensity: true,
  resolution: window.devicePixelRatio,
});

document.body.appendChild(app.canvas);

app.destroy(
  { removeView: true, releaseGlobalResources: true },
  { children: true, texture: true, textureSource: true },
);
```

- The constructor takes no arguments; v7's `new Application({ ... })` options are ignored with a deprecation warning. All options go to the async `app.init()`, which creates the renderer via `autoDetectRenderer`. Every option with its default: [application-options](01-application.md).
- `app.renderer` is `undefined` until `init()` resolves, and `app.canvas` / `app.screen` read through it, so they throw a `TypeError` until then.
- v7's `app.view` is `app.canvas`; the old getter still works but warns.
- `app.screen` is the visible area in CSS pixels. `app.domContainerRoot` is the `<div>` that hosts `DOMContainer` overlays; the renderer attaches it next to `app.canvas` automatically when a `DOMContainer` renders, so read it only to style or inspect it (see [scene-dom-container](09-dom-gif-html.md)).
- `app.destroy()` throws if `init()` has not resolved yet (the plugins it tears down are not installed). In component cleanup (React StrictMode, fast unmounts) keep the init promise and destroy after it: `initPromise.then(() => app.destroy(true))`.
- `app.destroy(rendererDestroyOptions, stageDestroyOptions)`: the first argument forwards to `renderer.destroy()`. Pass `true` or `{ removeView: true }` to remove the canvas from the DOM. Add `releaseGlobalResources: true` to drain global pools (batches, texture caches) when tearing down and re-creating an app in the same tab; without it the new app reuses the old app's pooled batches and textures, which shows as flickering and corrupted or stale textures.
- Stage textures on teardown: `texture: true, textureSource: true` frees textures your code created (`generateTexture`, canvases). Textures from `Assets.load` stay in the `Assets` cache (`releaseGlobalResources` does not clear it), so destroying them leaves dead entries that the next app's `Assets.load` returns; release those with `Assets.unload(...)` instead, or skip the texture flags if the next app reuses them.
- There is no teardown event to hook: `Application` is not an event emitter, and `app.renderer` emits only `resize`, so `app.renderer.once("destroy", ...)` fails TypeScript (TS2345). Stop and destroy the `Ticker`s, observers and DOM listeners you created in the same cleanup function that calls `app.destroy()`.

### ResizePlugin

Set `resizeTo` at init (or reassign `app.resizeTo` later) to have the plugin call `renderer.resize()` with the target's size (`innerWidth`/`innerHeight` for `window`, `clientWidth`/`clientHeight` for an element). Assigning `resizeTo` resizes immediately.

The plugin listens only to the window `resize` event. An element target that changes size without a window resize (layout change, sidebar toggle, CSS change) leaves the canvas at its old size unless you observe the element:

```ts
import type { Application } from "pixi.js";

declare const app: Application;

const container = document.querySelector("#game-container") as HTMLElement;
app.resizeTo = container;

const observer = new ResizeObserver(() => app.queueResize());
observer.observe(container);
// before app.destroy(): observer.disconnect();

app.resize(); // immediate resize to the target's current size
app.queueResize(); // resize on the next animation frame; repeated calls coalesce
```

A window resize is applied on the next animation frame, so your own `window` `resize` listener still reads the old `app.screen`. Lay out from the renderer's event, which fires after every resize (plugin, `app.resize()` or `renderer.resize()`):

```ts
import type { Application, Container } from "pixi.js";

declare const app: Application;
declare const title: Container;

app.renderer.on("resize", (width, height) => {
  title.position.set(width / 2, height / 2); // logical (CSS) pixels, same as app.screen
});
```

`resizeTo` does not work inside a Web Worker; resize by message there (see [environments](20-environments-builds.md#web-worker-with-offscreencanvas)). `app.cancelResize()` is declared in the typings but does not exist at runtime in 8.22 (calling it throws); `queueResize()` already cancels a pending request.

### Changing resolution after init

```ts
import type { Application } from "pixi.js";

declare const app: Application;

app.renderer.view.autoDensity = true; // the runtime flag lives on the view system
app.renderer.resize(app.screen.width, app.screen.height, window.devicePixelRatio);
// or: app.renderer.resolution = window.devicePixelRatio;
```

`autoDensity` is an init option, but `app.renderer.autoDensity` does not exist (TS2339); read or toggle it at `app.renderer.view.autoDensity`. `renderer.resize(w, h, resolution)` sets the backing store to `w * resolution` while `app.screen` stays in logical pixels, and emits the renderer's `resize` event. The `renderer.resolution` setter does the same without emitting `resize`. The CSS size stays logical only with `autoDensity` on; without it the canvas element displays at backing-store size (2x larger at resolution 2). Later `ResizePlugin` resizes keep the new resolution. Lay out with `app.screen`, not `app.canvas.width` (device pixels).

### Render loop

The `TickerPlugin` creates `app.ticker`, registers `app.render()` on it, and adds `app.start()` / `app.stop()`. Callbacks receive the `Ticker`, not a delta. `autoStart: false` only leaves the ticker stopped, so a manual loop calls either `app.ticker.update(time)` or `app.render()`, never both. All of it: [ticker](17-ticker.md).

### CullerPlugin (opt-in)

`extensions.add(CullerPlugin)` before `app.init()` makes every render cull `app.stage` against the screen; only objects with `cullable = true` are culled, and by default with last frame's transforms. Setup and the one-frame lag: [performance](18-performance.md#culling).

### Custom Application plugins

Register a class with `static extension = ExtensionType.Application` and static `init` / `destroy`. Both run with `this` bound to the Application, so `this.renderer` and `this.stage` are available.

```ts
import {
  Application,
  ExtensionType,
  extensions,
  type ApplicationOptions,
} from "pixi.js";

class FpsOverlay {
  public static extension = ExtensionType.Application;

  public static init(this: Application, options: Partial<ApplicationOptions>) {
    // runs inside app.init() after the renderer exists; attach props/methods to `this`
  }

  public static destroy(this: Application) {
    // runs inside app.destroy(); tear down what init attached
  }
}

extensions.add(FpsOverlay);
```

Plugins initialize in descending `extension.priority` (registration order breaks ties; the built-ins use the default) and destroy in reverse. A plugin that wraps `this.render` must initialize before `TickerPlugin`, which captures `render` when it adds it to the ticker; give it a positive priority (`static extension = { type: ExtensionType.Application, priority: 10 }`), as `CullerPlugin` does. Typed plugin options extend `PixiMixins.ApplicationOptions`:

```ts
import type { Application } from "pixi.js";

declare const app: Application;

declare global {
  namespace PixiMixins {
    interface ApplicationOptions {
      fpsOverlay?: { visible?: boolean };
    }
  }
}

await app.init({ fpsOverlay: { visible: true } });
```

The built-in `ResizePlugin`, `TickerPlugin` and `CullerPlugin` use this same contract. Importing `Application` registers `ResizePlugin` and `TickerPlugin`, so they keep working with `skipExtensionImports: true` (see [environments: custom builds](20-environments-builds.md#custom-builds)).


---

## application-options

Every option `app.init(options)` accepts, with its default and the v8 behaviour behind it. Options with no default are unset unless you pass them. They merge from `AutoDetectOptions` (renderer), `PixiMixins.ApplicationOptions` (plugins) and each renderer system's own options.

### View / canvas

| Option | Type | Default | Notes |
| --- | --- | --- | --- |
| `width` / `height` | `number` | `800` / `600` | CSS pixels. |
| `canvas` | `ICanvas` | — | Existing `HTMLCanvasElement` or `OffscreenCanvas` to render into. `view` is its alias, deprecated since 8.0.0. |
| `resolution` | `number` | `1` | Device pixel ratio. Change later with `app.renderer.resize(w, h, resolution)` or `app.renderer.resolution = n`. |
| `autoDensity` | `boolean` | `false` | Sizes the canvas CSS so `width`/`height` stay in CSS pixels while the backing store matches `resolution`. Ignored on `OffscreenCanvas`. At runtime it is `app.renderer.view.autoDensity`; `app.renderer.autoDensity` does not exist. |
| `antialias` | `boolean` | `false` | MSAA where supported. On WebGL with `useBackBuffer: true` it applies to the back buffer instead of the context. |
| `depth` | `boolean` | — | Depth buffer for the main view. Always on for WebGL. |
| `transient` | `boolean` | `false` | WebGPU only, with `antialias`. Discards the canvas's multisample depth/stencil buffer at the end of each pass, and its colour buffer on GPUs that aren't tile-based (tile-based GPUs already discard colour). Only for apps that never reopen the canvas pass while still needing depth or stencil: no filters or masks popping back onto it, no render with `clear: false`. |
| `format` | `TEXTURE_FORMATS` | — | WebGPU only. Canvas format: `bgra8unorm`, `rgba8unorm` or `rgba16float`. Defaults to the browser's preferred format, as the other 8-bit format can cost an extra full-screen copy every frame. Use `rgba16float` for an HDR canvas. |

### Background

| Option | Type | Default | Notes |
| --- | --- | --- | --- |
| `backgroundColor` | `ColorSource` | `0x000000` | Clear colour; any `ColorSource`. |
| `background` | `ColorSource` | — | Alias for `backgroundColor`; wins if both are set. |
| `backgroundAlpha` | `number` | `1` | **Cannot be changed after init**: the canvas is allocated with or without alpha from this value. Set `< 1` now if you may ever need transparency. |
| `clearBeforeRender` | `boolean` | `true` | Disable only if you draw a full-frame background yourself. |

### Renderer preference

| Option | Type | Default | Notes |
| --- | --- | --- | --- |
| `preference` | `'webgl' \| 'webgpu' \| 'canvas' \| RendererPreference[]` | `'webgl'` | String = try first, then fall back through `webgl` → `webgpu` → `canvas`. Array = try only the listed renderers, in order; anything not listed is excluded. See [renderers](02-renderers.md#preference-forms). |
| `webgl` / `webgpu` / `canvasOptions` | partial renderer options | — | Applied only when that renderer is selected; see [per-renderer overrides](#per-renderer-overrides). |

### Shared rendering

| Option | Type | Default | Notes |
| --- | --- | --- | --- |
| `roundPixels` | `boolean` | `false` | Rounds vertex positions to whole pixels at shader time; slow sub-pixel motion then steps one pixel at a time. |
| `skipExtensionImports` | `boolean` | `false` | Skips the dynamic import of the environment extensions (events, filters, accessibility, `DOMContainer`) and renderer loaders; what then silently stops and the imports that restore it: [environments: custom builds](20-environments-builds.md#custom-builds). |
| `hello` | `boolean` | `false` | Logs the version and renderer banner on init. |
| `failIfMajorPerformanceCaveat` | `boolean` | `false` | Treats WebGL as unsupported on blocklisted or software GPUs, so `autoDetectRenderer` falls through to the next renderer in the preference order instead of failing. |
| `bezierSmoothness` | `number` | `0.5` | Graphics curve tessellation; higher = more triangles. |

### Ticker (TickerPluginOptions)

| Option | Type | Default | Notes |
| --- | --- | --- | --- |
| `autoStart` | `boolean` | `true` | `false` leaves `app.ticker` stopped, but `app.render` stays registered on it, so `app.ticker.update()` or `app.start()` still renders. No effect with `sharedTicker: true` (`Ticker.shared` starts itself); call `app.stop()` after init instead. |
| `sharedTicker` | `boolean` | `false` | Use `Ticker.shared` instead of a per-app ticker; syncs several apps, loses per-app start/stop. |

Manual loops and the ticker API: [ticker](17-ticker.md#app-lifecycle-and-manual-rendering).

### Resize (ResizePluginOptions)

| Option | Type | Default | Notes |
| --- | --- | --- | --- |
| `resizeTo` | `Window \| HTMLElement` | `null` | `window` uses the viewport; an element uses `clientWidth`/`clientHeight`. |

The plugin listens only for `resize` on `window`; resizing to an element that changes size on its own, and laying out on resize: [application](01-application.md#resizeplugin).

### Culler (CullerPluginOptions)

Opt-in: the option does nothing until `extensions.add(CullerPlugin)`.

| Option | Type | Default | Notes |
| --- | --- | --- | --- |
| `culler.updateTransform` | `boolean` | `false` (effectively) | Must be `true` to update transforms before culling; otherwise cull bounds lag one frame for moving objects. |

```ts
import { Application, CullerPlugin, extensions } from "pixi.js";

declare const app: Application;

extensions.add(CullerPlugin);

await app.init({ culler: { updateTransform: true } });
```

### Events

| Option | Type | Default | Notes |
| --- | --- | --- | --- |
| `eventMode` | `'none' \| 'passive' \| 'auto' \| 'static' \| 'dynamic'` | `'passive'` | Default interaction mode for every container. See [events](11-events.md). |
| `eventFeatures.move` | `boolean` | `true` | `pointermove`/`mousemove`/`touchmove` and `pointerover`/`pointerout`. |
| `eventFeatures.globalMove` | `boolean` | `true` | `globalpointermove`/`globalmousemove`/`globaltouchmove` regardless of hit target. Expensive; turn off if unused. |
| `eventFeatures.click` | `boolean` | `true` | `pointerdown`/`pointerup`/`click`/`tap`. |
| `eventFeatures.wheel` | `boolean` | `true` | `wheel`. |

### Accessibility

Top-level `accessibilityOptions`; the full API is in [accessibility](19-accessibility.md).

| Option | Type | Default | Notes |
| --- | --- | --- | --- |
| `accessibilityOptions.enabledByDefault` | `boolean` | `false` | Enable overlays immediately instead of waiting for Tab. |
| `accessibilityOptions.debug` | `boolean` | `false` | Show the overlay divs. |
| `accessibilityOptions.activateOnTab` | `boolean` | `true` | Activate overlays on Tab. |
| `accessibilityOptions.deactivateOnMouseMove` | `boolean` | `true` | Deactivate overlays when the mouse moves. |

### WebGL-only options

| Option | Type | Default | Notes |
| --- | --- | --- | --- |
| `context` | `WebGL2RenderingContext \| null` | `null` | Use an existing context. |
| `powerPreference` | `'high-performance' \| 'low-power'` | `undefined` | Omitted, PixiJS passes `'default'` to the context; `'default'` is not settable from user code. |
| `premultipliedAlpha` | `boolean` | `true` | Tells the compositor the buffer is premultiplied; changes blending math. |
| `preserveDrawingBuffer` | `boolean` | `false` | Required for `canvas.toDataURL()` / `canvas.toBlob()` to capture arbitrary frames. |
| `preferWebGLVersion` | `1 \| 2` | `2` | WebGL1 is a legacy fallback. |
| `multiView` | `boolean` | `false` | Render to multiple canvases from one renderer. |
| `useBackBuffer` | `boolean` | `false` | Render to an intermediate texture. Required for advanced blend modes and filters that sample the backdrop; enables `antialias` on the back buffer independently of the context. |

### WebGPU-only options

| Option | Type | Default | Notes |
| --- | --- | --- | --- |
| `powerPreference` | `'high-performance' \| 'low-power'` | `undefined` | Hint for `requestAdapter()`. |
| `forceFallbackAdapter` | `boolean` | `false` | Software adapter; testing only. |
| `gpu` | `{ adapter, device }` | — | Pre-created `GPUAdapter` + `GPUDevice`, e.g. shared with another engine. |

### Garbage collection

Times in milliseconds.

| Option | Type | Default | Notes |
| --- | --- | --- | --- |
| `gcActive` | `boolean` | `true` | Unified renderer garbage collector. |
| `gcMaxUnusedTime` | `number` | `60000` | How long a resource can go unused before collection. |
| `gcFrequency` | `number` | `30000` | How often the sweep runs. |

The older `TextureGCSystem` / `RenderableGCSystem` options still work but log deprecation warnings:

| Option | Deprecated since | Replacement |
| --- | --- | --- |
| `textureGCActive` | 8.15.0 | `gcActive` |
| `textureGCMaxIdle` | 8.15.0 | `gcMaxUnusedTime` (old value in frames; new in ms) |
| `textureGCCheckCountMax` | 8.15.0 | `gcFrequency` (frames → ms) |
| `textureGCAMaxIdle` | 8.3.0 | `textureGCMaxIdle` (typo fix) → now `gcMaxUnusedTime` |
| `renderableGCActive` | 8.15.0 | `gcActive` |
| `renderableGCMaxUnusedTime` | 8.15.0 | `gcMaxUnusedTime` |
| `renderableGCFrequency` | 8.15.0 | `gcFrequency` |

### Per-renderer overrides

`webgl`, `webgpu` and `canvasOptions` merge over the top-level options once the selected renderer is known, and are stripped before the options reach the renderer:

```ts
import type { Application } from "pixi.js";

declare const app: Application;

await app.init({
  antialias: false,
  webgl: { antialias: true, useBackBuffer: true },
  webgpu: { antialias: true },
});
```

If WebGL wins, the renderer sees `antialias: true` + `useBackBuffer: true`; if WebGPU wins, just `antialias: true`.
