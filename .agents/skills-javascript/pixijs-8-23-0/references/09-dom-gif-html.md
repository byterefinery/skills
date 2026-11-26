# DOM containers, GIF and HTML sources

## Contents

- [scene-dom-container](#scene-dom-container)
  - [Imports](#imports)
  - [What the pipe writes](#what-the-pipe-writes)
  - [Click-through overlays (pointer-events)](#click-through-overlays-pointer-events)
  - [Detaching and destroy](#detaching-and-destroy)
  - [The DOM container root](#the-dom-container-root)
- [scene-gif](#scene-gif)
  - [The side-effect import](#the-side-effect-import)
  - [Loading](#loading)
  - [GifSprite options and playback](#gifsprite-options-and-playback)
  - [Cleanup](#cleanup)
- [html-source](#html-source)
  - [Browser support and feature detection](#browser-support-and-feature-detection)
  - [HTMLSource (live element)](#htmlsource-live-element)
  - [ElementImageSource (immutable snapshot)](#elementimagesource-immutable-snapshot)
  - [Auto-detection via Texture.from](#auto-detection-via-texturefrom)
  - [Cleanup](#cleanup-1)

## scene-dom-container

`DOMContainer`: HTML elements over the canvas driven by the scene graph; imports, what the pipe overwrites, click-through, detaching, and the shared root.

```ts
import { Application, DOMContainer } from "pixi.js";

declare const app: Application;

const input = document.createElement("input");
input.placeholder = "Enter name...";
input.style.width = "160px";

const dom = new DOMContainer({ element: input, anchor: 0.5 });
dom.position.set(app.screen.width / 2, app.screen.height / 2);
app.stage.addChild(dom);
```

`DOMContainer` is EXPERIMENTAL in v8 and may change between minor releases. It is a leaf (`allowChildren = false`): nest HTML inside its element, and put PixiJS siblings beside it in a plain `Container`. `element` defaults to a new `<div>`; `anchor` (default `0`, top-left) is relative to the element's own size, so `0.5` centers it on its position. Not available in Web Workers.

### Imports

Import the class from `pixi.js`; the default browser bundle registers the `DOMPipe`. Add a bare `import "pixi.js/dom";` only when you set `skipExtensionImports: true` (custom builds); without it there, `DOMContainer` still imports but has no pipe, so elements never appear or follow the scene graph. `import { DOMContainer } from "pixi.js/dom"` fails under strict TypeScript (TS7016): the subpath ships no type declarations.

### What the pipe writes

The pipe writes the world transform to the element as a CSS `matrix(...)`, shifted by `anchor` relative to its `offsetWidth`/`offsetHeight`, and writes `alpha` (including inherited parent alpha) to `style.opacity`.

- Every render it overwrites the element's inline `transform`, `transformOrigin` and `opacity`, so CSS transforms, opacity or transitions set on that element are lost. Put them on a child element inside it.
- Size the element with CSS (`element.style.width = "160px"`). `dom.width`/`dom.height` read `offsetWidth`/`offsetHeight`, and setting them changes `dom.scale`, which stretches the element (text and borders included) instead of resizing its layout box.
- `tint`, `filters`, `mask` and `blendMode` are accepted (inherited from `Container`) but do nothing: the element lives outside the WebGL/WebGPU pipeline. Use CSS on the element instead (`dom.element.style.filter = "blur(4px)"`, `mix-blend-mode`).

### Click-through overlays (pointer-events)

```ts
import { Application, DOMContainer } from "pixi.js";

declare const app: Application;

const css = document.createElement("style");
css.textContent = ".click-through { pointer-events: none !important; }";
document.head.appendChild(css);

const label = document.createElement("div");
label.textContent = "Lives: 3";
label.classList.add("click-through");

const dom = new DOMContainer({ element: label });
app.stage.addChild(dom);
```

The shared root `<div>` is `pointer-events: none`, but each time the pipe attaches an element (first render, and again after every hide/show or remove/add) it sets the element's inline `position = "absolute"` and `pointerEvents = "auto"`. An inline `element.style.pointerEvents = "none"` (even with `"important"` priority) set before that is silently replaced, and the overlay keeps swallowing clicks meant for the canvas. Use a stylesheet rule with `!important`, as above; it beats the inline value and survives re-attach.

### Detaching and destroy

The element is detached on the next render when the `DOMContainer` or any ancestor gets `visible = false`, when the `DOMContainer` itself is removed from its parent, or when it or an ancestor is destroyed. Restoring visibility re-attaches it.

Removing only an ancestor (`panel.removeFromParent()`) does NOT detach it: the element stays on the page, and later renders re-append it even after a manual `element.remove()`. To close a panel that holds DOM overlays, call `panel.destroy({ children: true })`, set `panel.visible = false`, or remove or destroy each `DOMContainer` itself.

`dom.destroy()` removes the element from its parent node and nulls internal references but preserves the element itself, so `const el = dom.element; dom.destroy(); document.body.appendChild(el);` re-uses it.

### The DOM container root

Every attached element lives in one shared root `<div>` with `z-index: 1000`, exposed as `app.domContainerRoot`. All `DOMContainer` elements render above canvas content; you can't interleave them between PixiJS draws.

On the first render that has an attached `DOMContainer`, the pipe appends the root to the canvas's parent node (unless the root already has a parent). The root is `position: absolute; top: 0; left: 0` and is translated by the canvas's viewport position (`getBoundingClientRect().left/top`), recomputed only when the canvas's CSS size changes. If the canvas's parent (or an ancestor between it and the page) is positioned (`position: relative/absolute`) and offset from the page origin, that offset is applied twice and every overlay is misplaced by it. Append the root to `document.body` yourself before the first render so it is positioned against the page:

```ts
import { Application } from "pixi.js";

declare const app: Application;

document.getElementById("game-wrapper")!.appendChild(app.canvas);
document.body.appendChild(app.domContainerRoot);
```


---

## scene-gif

Animated GIFs: the `pixi.js/gif` import, loading a `GifSource` and its load options, `GifSprite` playback, sharing, and cleanup.

```ts
import "pixi.js/gif";
import { Application, Assets } from "pixi.js";
import { GifSprite, type GifSource } from "pixi.js/gif";

declare const app: Application;

const source = await Assets.load<GifSource>({ src: "animation.gif", data: { fps: 12, scaleMode: "nearest" } });

const gif = new GifSprite({ source, anchor: 0.5, animationSpeed: 1 });
gif.position.set(app.screen.width / 2, app.screen.height / 2);
app.stage.addChild(gif);
```

### The side-effect import

`pixi.js/gif` calls `extensions.add(GifAsset)`, registering `.gif` (and `data:image/gif` URLs) with the asset loader. Without it, `Assets.load` warns "could not be loaded" and resolves `null`. `GifSprite` and `GifSource` are exported from `pixi.js/gif`, not `pixi.js`.

Keep the bare `import "pixi.js/gif";` line. A named import registers the loader only if a value from it survives compilation: TypeScript and bundlers delete `import { GifSource } from "pixi.js/gif"` when `GifSource` is used only as a type annotation, so the loader is never registered and `source.textures` throws on `null`.

### Loading

`Assets.load` on a GIF returns a `GifSource` (frame textures plus timing), not a `Texture`: pass it to `GifSprite`, or read `source.textures[0]` for a still frame. Each frame is a separate canvas texture; for long, performance-critical animations a spritesheet with `AnimatedSprite` uses one atlas and batches better.

Options in `data` go to `GifSource.from` (`GifBufferOptions`, which extends `CanvasSourceOptions`, so any canvas-source field works):

| Option                | Default    | Purpose |
| --------------------- | ---------- | ------- |
| `fps`                 | `30`       | Sets the delay, `1000 / fps` ms, for every frame the file gives no delay. The only place this fallback can be set; it is baked into the source at load, so a GIF already in the cache keeps its old timing (load it under a different alias or `Assets.unload` it first) |
| `scaleMode`           | `'linear'` | `'nearest'` for pixel art |
| `resolution`          | `1`        | Resolution of the decoded frame textures |
| `autoGenerateMipmaps` | `false`    | Mipmaps for downscaling |

The loader matches `.gif` extensions and `data:image/gif` URIs. A GIF URL without an extension needs the parser forced: `Assets.load({ src, parser: "gif", data: { fps: 24 } })` (see [assets](10-assets.md#forcing-a-parser-with-parser)).

### GifSprite options and playback

`new GifSprite(source)` is shorthand for `new GifSprite({ source })`. `GifSpriteOptions` extends `Omit<SpriteOptions, 'texture'>` (the texture is set from `source.textures[0]` and swapped per frame), so `anchor`, `tint`, `roundPixels` and the rest apply.

| Option           | Default    | Notes |
| ---------------- | ---------- | ----- |
| `source`         | —          | Required. Shareable across many `GifSprite`s, each with independent playback. |
| `autoPlay`       | `true`     | `false` waits for `gif.play()`. |
| `loop`           | `true`     | `false` stops on the last frame and fires `onComplete`. |
| `animationSpeed` | `1`        | Multiplier on the GIF's frame timing (elapsed ticker ms × speed). |
| `autoUpdate`     | `true`     | Plays on `Ticker.shared` (not `app.ticker`), so `app.ticker.stop()` does not pause a GIF. With `false`, call `gif.update(ticker)` yourself, e.g. from `app.ticker` so pausing the app pauses the GIF. |
| `fps`            | `30`       | No effect: stored but never read. Set the fallback frame rate with `Assets.load({ src, data: { fps } })`. |
| `onComplete`, `onLoop`, `onFrameChange(frame)` | `null` | End of a non-looping run; each wrap; each displayed-frame change. |
| `scaleMode`      | `'linear'` | Deprecated since 8.13.0; pass `scaleMode` in the load `data`. |

`play()`, `stop()`; `currentFrame` is zero-based and writable; `playing` (readonly), `progress` (0-1), `totalFrames`, `duration` (ms). For a still frame, construct with `autoPlay: false` (or `stop()`) and set `currentFrame`.

`clone()` copies `source`, `autoUpdate`, `loop`, `autoPlay`, `animationSpeed` and the callbacks only; it starts at frame 0 and does not copy position, scale, anchor, tint or other Sprite state.

### Cleanup

```ts
import { Assets } from "pixi.js";
import type { GifSprite } from "pixi.js/gif";

declare const gif: GifSprite;

gif.destroy();
await Assets.unload("animation.gif");
```

`gif.destroy()` (or `destroy(false)`) destroys the sprite but keeps the `GifSource` and its decoded frames. `Assets.unload("animation.gif")` destroys the source and drops it from the cache; it does no reference counting, so call it only after the last `GifSprite` using the source is destroyed. Prefer it over `destroy(true)` for loaded GIFs: `destroy(true)` destroys the shared source (breaking every other `GifSprite` on it) and leaves it cached, so a later `Assets.load` of the same URL returns it and `new GifSprite(source)` throws "Cannot read properties of null (reading '0')". Never do both: `Assets.unload` after `destroy(true)` throws.


---

## html-source

Live DOM elements (`HTMLSource`) or frozen snapshots (`ElementImageSource`) as texture sources, via the experimental HTML-in-Canvas browser APIs.

Both are `TextureSource`s, not display objects: put them on screen with `Sprite.from(source)` or `new Sprite(Texture.from(source))`, slice them into `Texture` frames, or map them onto a `Mesh`. `HTMLSource` mirrors a live element's pixels into the GPU while the element stays editable and clickable in the browser; `ElementImageSource` wraps an immutable snapshot that never repaints. Not available in Web Workers (no DOM). For HTML layered *above* the canvas instead, see [scene-dom-container](09-dom-gif-html.md).

```ts
import { Application, Sprite } from "pixi.js";
import { HTMLSource } from "pixi.js/html-source";

const app = new Application();
await app.init({ resizeTo: window });
document.body.appendChild(app.canvas);

// The element must be inside the Pixi canvas.
const form = document.createElement("form");
form.innerHTML = '<input value="still editable" />';
app.canvas.appendChild(form);

const source = new HTMLSource({ resource: form });
const sprite = Sprite.from(source);
app.stage.addChild(sprite);
```

Three rules every use needs:

- **Import from `pixi.js/html-source`, not `pixi.js`.** The classes and their WebGL/WebGPU `'html'` uploaders are exported only there. Importing anything from that path runs `extensions.add(...)` (the module is marked side-effectful, so bundlers keep it); without it the renderer has no `'html'` uploader and these sources never render. A bare `import "pixi.js/html-source"` is needed only when you import nothing else from it.
- **The element must be inside the canvas.** `app.canvas.appendChild(el)` before constructing the source; an element elsewhere (e.g. `document.body`) makes the constructor throw. Chrome before 155 also requires a direct child.
- **`new Sprite(source)` draws nothing.** It type-checks, but `new Sprite(x)` converts `x` only when it is a `Texture`; any `TextureSource` (`HTMLSource`, `ElementImageSource`, `CanvasSource`, ...) is spread as options and the sprite keeps `Texture.EMPTY` ([scene-sprite](04-sprites.md#loading-before-creating)).

### Browser support and feature detection

Marked EXPERIMENTAL in PixiJS v8; the API may change between minor releases. Chrome turns the browser API on by default from Chrome 157; earlier Chrome needs the origin trial or a flag, and other browsers lack it. Where it's missing, the texture uploader throws on first render, so feature-detect first:

```ts
import type { HTMLSourceCanvas } from "pixi.js/html-source";

const canvas = app.canvas as HTMLSourceCanvas;
if (!canvas.requestPaint) {
  // Fall back to a static image, DOMContainer overlay, or a message.
}
```

Cast `app.canvas` to `HTMLSourceCanvas` for the typed `requestPaint`, `captureElementImage`, `updateElementGeometry` and `clearElementGeometry` members. `source.requestPaint()` returns `false` when the browser lacks the API.

The missing-API error is `[HTMLSource] WebGLRenderingContext.texElementSubImage2D is not available...` on WebGL or `[HTMLSource] GPUQueue.drawElementImageToTexture is not available...` on WebGPU. The uploaders use `texElementSubImage2D`/`drawElementImageToTexture` in Chrome 155+ and fall back to the older `texElementImage2D`/`copyElementImageToTexture` signatures in Chrome 150-154 and earlier.

### HTMLSource (live element)

Options: every `TextureSourceOptions` key (`resolution`, `scaleMode`, `addressMode`, `label`, ...) plus:

| Option             | Default | Notes |
| ------------------ | ------- | ----- |
| `resource`         | —       | Required. The live `Element`; the source sets `drawable` on it. |
| `canvas`           | inferred | The owning `HTMLSourceCanvas`. Must be the element's nearest `<canvas>` ancestor, or the constructor throws. |
| `autoLayout`       | `true`  | Sets `content="drawable"` (plus the pre-Chrome-155 `layoutsubtree`) on the owning canvas; the browser only lays out and paints canvas descendants when it is present. Set `false` if you write `<canvas content="drawable">` yourself. |
| `autoUpdate`       | `true`  | Listen for the canvas `paint` event and re-upload when the element repaints. `false` for a static, captured-once texture. |
| `autoRequestPaint` | `true`  | Request one initial paint after construction. |

Change defaults for every `HTMLSource` through the static `HTMLSource.defaultOptions` (e.g. `HTMLSource.defaultOptions.autoUpdate = false`).

`source.isReady` is `false` until the first paint lands, then `true`; it is `true` immediately when `autoUpdate` is `false`. `resourceWidth`/`resourceHeight` report the element's real-pixel size (`offsetWidth`/`offsetHeight`).

In Chrome 155+ the element can be nested: each `drawable` element captures its subtree minus nested `drawable` descendants, so a panel and a button inside it can be separate sources. WebGPU in Chrome 156 still throws for nested ones (WebGL accepts them).

#### Continuous animation with requestPaint

The browser repaints canvas children only on demand. A static element updates on `paint` events by itself, but content that changes every frame never re-uploads unless something triggers a paint. Set `autoRequestPaint: false` and call `requestPaint()` in your ticker:

```ts
declare const clock: HTMLElement; // a child of app.canvas
const source = new HTMLSource({ resource: clock, autoRequestPaint: false });

app.ticker.add(() => {
  clock.textContent = new Date().toLocaleTimeString();
  source.requestPaint(); // re-snapshot the DOM this frame
});
```

#### Hit testing with updateElementGeometry

WebGL and WebGPU never tell the browser where the element was drawn. In Chrome 155+ the element is not hit-testable and has no accessibility bounds until you call `canvas.updateElementGeometry(element, { canvasTransform })`, where `canvasTransform` maps the element's border box to canvas CSS pixels; setting `element.style.transform` no longer aligns hit testing there, and you shouldn't set both. Older builds use the element's CSS `transform` (element at the canvas origin, `transform-origin: 0 0`). Call it whenever the sprite moves:

```ts
declare const sprite: Sprite;
declare const form: HTMLFormElement;
const canvas = app.canvas as HTMLSourceCanvas;

app.ticker.add(() => {
  const { a, b, c, d, tx, ty } = sprite.getGlobalTransform();
  const transform = new DOMMatrix([a, b, c, d, tx, ty]).translate(
    -sprite.anchor.x * sprite.texture.width,
    -sprite.anchor.y * sprite.texture.height,
  );

  if (canvas.updateElementGeometry) {
    canvas.updateElementGeometry(form, { canvasTransform: transform }); // Chrome 155+
  } else {
    form.style.transform = transform.toString(); // older builds; needs transform-origin: 0 0
  }
});
```

The snippet assumes one world unit per CSS pixel (`resolution: 1` or `autoDensity: true`).

### ElementImageSource (immutable snapshot)

```ts
declare const element: HTMLElement;
const canvas = app.canvas as HTMLSourceCanvas;
const snapshot = canvas.captureElementImage!(element);

const source = new ElementImageSource({ resource: snapshot, autoClose: true });
const sprite = Sprite.from(source);
```

`captureElementImage()` freezes an element's current pixels into an immutable `ElementImage`. There is no owning canvas, no `paint` listener and no repaint lifecycle, so the source is ready the moment it is constructed. Use it for a frozen copy that outlives its element or is passed around (transitions, "shatter" or trail effects).

Options: `TextureSourceOptions` plus `resource` (required `ElementImage`) and `autoClose` (default `false`): call `snapshot.close()` when the source is destroyed. Set `autoClose: true` only when the source owns the snapshot exclusively; destroying one source closes a snapshot that other sources still use (use-after-free). For a shared snapshot leave it off and call `snapshot.close()` once, after the last source is destroyed.

### Auto-detection via Texture.from

A generic HTML element or an `ElementImage` passed to `Texture.from`/`Sprite.from` resolves to `HTMLSource` / `ElementImageSource` at the lowest texture-source priority (`-10`), so they only claim a resource no other built-in source handles. Image, video and canvas elements are deliberately rejected; they have dedicated, faster sources. Construct the source explicitly when you need options (`autoUpdate`, `autoClose`) or non-HTML elements such as SVG.

### Cleanup

`HTMLSource.destroy()` detaches the canvas `paint` listener and nulls its canvas reference. `ElementImageSource.destroy()` closes the snapshot when `autoClose` was set; otherwise call `snapshot.close()` yourself to release the memory.
