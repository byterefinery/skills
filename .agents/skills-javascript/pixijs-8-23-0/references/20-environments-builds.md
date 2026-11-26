# Environments and builds

## Contents

- [environments](#environments)
  - [Web Worker with OffscreenCanvas](#web-worker-with-offscreencanvas)
  - [Custom builds](#custom-builds)
  - [CSP-compliant setup](#csp-compliant-setup)
  - [Custom adapter](#custom-adapter)
  - [Routing asset requests through `adapter.fetch`](#routing-asset-requests-through-adapterfetch)
- [create](#create)
  - [Scaffolding](#scaffolding)
  - [Top-level `await app.init()` in Vite production builds](#top-level-await-appinit-in-vite-production-builds)
  - [TypeScript setup](#typescript-setup)

## environments

Running PixiJS v8 outside a standard browser page (Web Workers, Node/SSR, strict CSP), custom adapters, and custom tree-shaken builds.

`DOMAdapter` abstracts every piece of DOM access PixiJS does (canvas creation, Image loading, fetch, XML parsing). Call `DOMAdapter.set(...)` before `app.init()`: the renderer reads the adapter during `init()`, while `new Application()` only creates the stage. v7's `settings.ADAPTER = X` is gone with the `settings` object; use `DOMAdapter.set(X)`. Image textures are the exception to the adapter: by default they are fetched inside a Web Worker that bypasses `adapter.fetch` (see [Routing asset requests](#routing-asset-requests-through-adapterfetch)).

### Web Worker with OffscreenCanvas

Transfer an OffscreenCanvas from the main thread, then initialize PixiJS in the worker. The main thread owns sizing, because the worker has no `window`:

```ts
// main.ts
const canvas = document.createElement("canvas");
document.body.appendChild(canvas);

const offscreen = canvas.transferControlToOffscreen();
const worker = new Worker(new URL("./worker.ts", import.meta.url), { type: "module" });

function measure() {
  canvas.style.width = `${window.innerWidth}px`; // CSS size; the worker can't set it
  canvas.style.height = `${window.innerHeight}px`;
  return { width: window.innerWidth, height: window.innerHeight, dpr: window.devicePixelRatio };
}

worker.postMessage({ type: "init", canvas: offscreen, ...measure() }, [offscreen]);
window.addEventListener("resize", () => worker.postMessage({ type: "resize", ...measure() }));
```

```ts
// worker.ts
import { Application, DOMAdapter, WebWorkerAdapter } from "pixi.js";

DOMAdapter.set(WebWorkerAdapter);

const app = new Application();
let ready: Promise<void> | undefined;

self.onmessage = async ({ data }: MessageEvent) => {
  if (data.type === "init") {
    ready = app.init({ canvas: data.canvas, width: data.width, height: data.height, resolution: data.dpr });
  } else if (data.type === "resize") {
    await ready; // a resize can arrive before init resolves
    app.renderer.resize(data.width, data.height, data.dpr);
  }
};
```

Pass the worker as `new URL("./worker.ts", import.meta.url)`: Vite and webpack only bundle a worker referenced that way, and a bare `"worker.ts"` string 404s in a production build. The WebWorkerAdapter uses `OffscreenCanvas` instead of `document.createElement('canvas')` and `@xmldom/xmldom` for XML parsing. To follow an element instead of the window, observe it with a `ResizeObserver` on the main thread and post the same message.

Not available inside a Web Worker:

- `DOMContainer`, the accessibility system and pointer events: the worker loads none of them (`app.renderer.events` is undefined). Forward input from the main thread yourself.
- `resizeTo`: `window` is a ReferenceError in a worker and there is no element to measure. Resize by message as above.
- `devicePixelRatio`: undefined in a worker; pass it from the main thread. Passing the worker's undefined `devicePixelRatio` as `resolution` makes `init` throw "Failed to set the 'width' property on 'OffscreenCanvas'".
- `autoDensity`: ignored on an `OffscreenCanvas`, which has no `style`. Without the main thread setting the placeholder canvas's CSS size, it displays at backing-store size (2x on a 2x screen).
- Anything that needs `Image` or `document`. `WebWorkerAdapter.createImage()` (and so `DOMAdapter.get().createImage()`) calls `new Image()`, which throws `Image is not defined`. That rules out `HTMLText` (draws nothing, error in the console), an `.svg` loaded as a texture, `renderer.extract.image()` (use `extract.base64()`, `extract.canvas()` or `extract.pixels()`), and image loading with `preferCreateImageBitmap: false`. SVG parsed into Graphics (`parseAsGraphicsContext`, `graphics.svg(svgString)`) calls `document` and throws too.

What does work: PNG/JPG/WebP through `Assets.load` (decoded with `createImageBitmap`; leave `preferCreateImageBitmap` at its default `true`), textures built from an `ImageBitmap`, canvas `Text`, filters, and `DOMAdapter.get().createCanvas()` (an `OffscreenCanvas`). Web fonts load through `self.fonts` in workers whose browser exposes `WorkerGlobalScope.fonts`.

```ts
import { Assets, Texture } from "pixi.js";

const texture = await Assets.load<Texture>("texture.png");

const blob = await (await fetch("texture.png")).blob();
const fromBlob = Texture.from(await createImageBitmap(blob));
```

### Custom builds

`skipExtensionImports: true` (deprecated alias `manageImports: false`) shrinks the bundle by skipping two things during `init`: the dynamic import of the environment extension set and any registered renderer loader extensions. The browser set is accessibility, dom (`DOMContainer`), events, spritesheet, rendering and filters, but the main `pixi.js` entry imports rendering and spritesheet itself, so only accessibility, `DOMContainer`, events and filters go missing. Everything else still registers itself: importing `Application` registers `ResizePlugin` and `TickerPlugin`; `Graphics`, `Text`, `BitmapText`, `HTMLText`, `Mesh`, `TilingSprite`, `NineSliceSprite` and `ParticleContainer` each register their own render pipes when imported; sprites, masks and spritesheet loading keep working.

What breaks: pointer events (`renderer.events` is undefined, `.on('pointerdown')` never fires), filters (rendering anything with `filters` set throws), accessibility, and `DOMContainer`. Import the ones you use before `init`:

```ts
import "pixi.js/events";
import "pixi.js/filters";
import { Application } from "pixi.js";

const app = new Application();
await app.init({ skipExtensionImports: true });
```

Add `"pixi.js/accessibility"` and `"pixi.js/dom"` as needed, or `import "pixi.js/browser"` for the whole browser set; `"pixi.js/webworker"` is the worker set (filters on top of the main entry; no accessibility, dom or events, which need the DOM). These subpath entries register statically and synchronously instead of through the dynamic import at renderer init. Opt-in subpaths (`pixi.js/advanced-blend-modes`, `pixi.js/unsafe-eval`, `pixi.js/prepare`, `pixi.js/gif`, compressed-texture loaders) need an explicit import with or without this option.

`loadEnvironmentExtensions(skip)` is the helper `init` uses (`false` loads the defaults, `true` skips them); call it yourself when bootstrapping a custom environment. It replaces `autoDetectEnvironment(add)` (deprecated since 8.1.6), which still exists as a shim forwarding to `loadEnvironmentExtensions(!add)`.

### CSP-compliant setup

PixiJS uses `new Function()` to generate uniform, UBO and shader-resource sync functions and the ParticleContainer update function. Under a Content Security Policy that blocks `unsafe-eval`, renderer init throws "Current environment does not allow unsafe-eval, please use pixi.js/unsafe-eval module to enable support." (the browser may log its own CSP violation first). Import the polyfill before any renderer init:

```ts
import "pixi.js/unsafe-eval";
import { Application } from "pixi.js";
```

The name refers to the CSP directive it works around: it does not enable eval, it installs static polyfills for shader, UBO, uniform and particle buffer sync so PixiJS no longer needs it.

### Custom adapter

For Node.js, headless testing or SSR, implement the full `Adapter` interface: `createCanvas`, `createImage`, `getCanvasRenderingContext2D`, `getWebGLRenderingContext`, `getNavigator`, `getBaseUrl`, `getFontFaceSet`, `fetch`, `parseXML`. Browser globals such as `CanvasRenderingContext2D` and `WebGLRenderingContext` don't exist in Node, so return the canvas library's classes; node-canvas has no WebGL, so only the canvas renderer (`preference: "canvas"`) can run on it:

```ts
import { DOMAdapter } from "pixi.js";
import type { Adapter } from "pixi.js";
import { createCanvas, Image, CanvasRenderingContext2D as NodeContext2D } from "canvas";
import { DOMParser } from "@xmldom/xmldom";

class NoWebGL {}

const HeadlessAdapter: Adapter = {
  createCanvas: (width, height) => createCanvas(width ?? 0, height ?? 0),
  createImage: () => new Image(),
  getCanvasRenderingContext2D: () => NodeContext2D as unknown as typeof CanvasRenderingContext2D,
  getWebGLRenderingContext: () => NoWebGL as unknown as typeof WebGLRenderingContext,
  getNavigator: () => ({ userAgent: "HeadlessAdapter", gpu: null }),
  getBaseUrl: () => "file://",
  getFontFaceSet: () => null,
  fetch: (url, options) => fetch(url, options),
  parseXML: (xml) => new DOMParser().parseFromString(xml, "text/xml"),
};

DOMAdapter.set(HeadlessAdapter);
```

`DOMAdapter.get()` returns the current adapter. Create canvases through `DOMAdapter.get().createCanvas()` instead of `document.createElement("canvas")` in code that may run in a worker or under a custom adapter; its `createImage()` is not worker-safe, since every built-in adapter returns `new Image()`.

### Routing asset requests through `adapter.fetch`

An adapter's `fetch` sees JSON, text, SVG, bitmap-font, GIF and HTMLText font loads, but not image textures by default: those load in a Web Worker that calls the worker's own global `fetch`, so a custom `fetch` (auth headers, logging, offline cache) never runs for images and no error is raised. Turn workers off before loading so images go through the adapter:

```ts
import { Assets, BrowserAdapter, DOMAdapter, type Adapter } from "pixi.js";

const AuthAdapter: Adapter = {
  ...BrowserAdapter,
  fetch: (url, options) =>
    BrowserAdapter.fetch(url, { ...options, headers: { Authorization: "Bearer token" } }),
};

DOMAdapter.set(AuthAdapter);
Assets.setPreferences({ preferWorkers: false }); // or Assets.init({ preferences: { preferWorkers: false } })
```

Setting `preferCreateImageBitmap: true` does not help; it is already the default. `preferCreateImageBitmap: false` loads images through `createImage()` (an `<img>`, so it fails inside a Web Worker) and calls no `fetch` at all. Details in [assets](10-assets.md).


---

## create

Scaffolding a PixiJS v8 project with `create pixi.js`, adding `pixi.js` to an existing project, and the TypeScript and Vite settings it needs.

### Scaffolding

```bash
npm create pixi.js@latest my-game -- --template bundler-vite
cd my-game
npm install
npm run dev
```

- With no arguments the CLI prompts for project name (default `pixi-project`), template category and variant (TypeScript or JavaScript). It never installs dependencies; it prints the `cd` + install + dev commands for the manager you ran it with.
- npm 7+ needs the `--` before CLI flags; without it npm consumes `--template` and the CLI falls back to the interactive prompt. `yarn create pixi.js`, `pnpm create pixi.js` and `bun create pixi.js` take the flags directly.
- `.` as the project name scaffolds into the current directory; the CLI refuses to overwrite conflicting files in a non-empty directory unless you confirm the prompt.
- Requires Node.js 18+ or 20+; `creation-web` and `framework-react` may need a newer Node, and the package manager warns ("engines") if so.
- In an existing project skip the CLI: `npm install pixi.js`. The templates add nothing to the library.

| Template | What you get |
| --- | --- |
| `bundler-vite` | Vite + TypeScript. The recommended default. |
| `bundler-vite-js` | Vite + JavaScript. |
| `bundler-webpack` / `bundler-webpack-js` | Webpack + TypeScript / JavaScript. |
| `bundler-esbuild` / `bundler-esbuild-js` | esbuild + TypeScript / JavaScript. |
| `bundler-import-map` | No bundler; a browser import map. |
| `creation-web` | Creation Engine web template: scene-based game scaffolding, AssetPack, sound and UI. |
| `framework-react` / `framework-react-js` | React + PixiJS via `@pixi/react`, TypeScript / JavaScript. |
| `extension-default` | Starter for a reusable PixiJS extension package. |

Run the CLI without arguments to see the current menu. In `bundler-vite`, `npm run build` runs `npm run lint && tsc && vite build` into `dist/`, so a lint or type error fails the build; it has no `preview` script (use `npx vite preview`). Other presets name their scripts differently; check `package.json`.

### Top-level `await app.init()` in Vite production builds

On Vite 6 and earlier, top-level `await` works in dev but `vite build` fails with "Top-level await is not available in the configured target environment", because the default build target is es2020. Wrap the init in an async IIFE, which works on every version:

```ts
import { Application } from "pixi.js";

(async () => {
  const app = new Application();
  await app.init({ resizeTo: window });
  document.body.appendChild(app.canvas);
})();
```

Vite 7+ builds top-level `await` as is, and on older Vite `build: { target: "es2022" }` (or later) also fixes it.

### TypeScript setup

PixiJS's type declarations depend on the WebGPU types; where they come from depends on the TypeScript version.

- **TypeScript 5:** no WebGPU types are built in, so PixiJS adds `@webgpu/types` for you. No setup needed.
- **TypeScript 6 and 7:** the WebGPU types are in the built-in `"dom"` library, but up to TypeScript 6.0.3 and 7.0.2 it lacks the WebGPU flag constants (`GPUBufferUsage`, `GPUColorWrite`, `GPUMapMode`, `GPUShaderStage`, `GPUTextureUsage`), so raw WebGPU code using them fails with `Cannot find name 'GPUTextureUsage'` (`TS2552`). Install `@types/web` 0.0.352 or later, drop `"dom"` from `lib`, and add `"@types/web"` to `types` alongside any existing entries:

```bash
npm install --save-dev @types/web
```

```json
{
  "compilerOptions": {
    "lib": ["esnext"],
    "types": ["@types/web"]
  }
}
```

On TypeScript 6 and 7, remove `"@webgpu/types"` from `types` (keep any other entries): it declares the built-in WebGPU types a second time, which with `skipLibCheck: false` produces dozens of conflicting-declaration errors inside `lib.dom.d.ts` and `@webgpu/types`. Adding it back for the flag constants only compiles with `skipLibCheck: true`.

Use `"moduleResolution": "bundler"` with a bundler (with `"module": "esnext"`), or `"nodenext"` otherwise. `"node"` (also called `"node10"`) ignores the `exports` field in PixiJS's `package.json`, so `import 'pixi.js/advanced-blend-modes'` and other subpath imports don't resolve; TypeScript 6 reports `TS2882` for them and deprecates the setting (`TS5107`), and TypeScript 7 removes it (`TS5108`).
