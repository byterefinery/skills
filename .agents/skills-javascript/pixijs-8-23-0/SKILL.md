---
name: pixijs-8-23-0
description: >-
  PixiJS v8.23.0 (npm package pixi.js) reference for building fast 2D graphics, games and
  interactive apps on WebGL, WebGPU or Canvas. Use before writing, fixing or porting any PixiJS
  code, from a one-line change to a whole app. Covers Application init, resize and destroy;
  Container scene graph with RenderLayer and RenderGroup; Sprite, Texture, AnimatedSprite,
  TilingSprite, NineSliceSprite; shape-first Graphics with SVG; Text, BitmapText, HTMLText,
  SplitText; Mesh and MeshRope; ParticleContainer; Assets loading, bundles and spritesheets;
  Ticker; pointer events and dragging; filters and custom GLSL or WGSL shaders; blend modes and
  erasing; RenderTexture; Color, Point, Matrix; DOMContainer, GifSprite, HTMLSource;
  accessibility; performance and teardown; Web Workers; custom builds; v7 to v8 migration.
license: MIT
metadata:
  tags:
    - graphics
    - rendering
    - webgl
    - webgpu
    - canvas
    - 2d
    - game-dev
    - javascript
---

# pixijs 8.23.0

## Overview

PixiJS v8.23.0 (package `pixi.js`, MIT) is a fast, lightweight 2D engine that renders a `Container` scene graph to WebGL, WebGPU or a Canvas fallback, with an asset loader, unified pointer events, filters/shaders, and Web Worker support. Every version-specific claim in this skill comes from the pixijs v8.23.0 repository — its official skill references (`skills/pixijs`), `examples/` (107 runnable samples), and `src/__docs__` — so the reference files and the pitfalls below are exact for this version.

The v8 model, where it differs from v7 (full checklist in [21-migration-v7-to-v8](references/21-migration-v7-to-v8.md)):

- **Async initialization** — `new Application()` takes no options; `await app.init({ ... })` creates the renderer.
- **Options objects** — constructors take a single options object, not positional arguments (v7 positional calls still render but log deprecation warnings).
- **Shape-first Graphics** — build the shape, then style it: `.rect(0, 0, 100, 50).fill(0xff0000).stroke({ width: 2, color: 0x000000 })`.
- **`TextureSource` replaces `BaseTexture`** — it is `texture.source`; `Texture.from(url)` and `Sprite.from(url)` read the cache only, so `await Assets.load(url)` first.
- **Ticker callbacks receive the `Ticker`** — `app.ticker.add((t) => { s.x += 2 * t.deltaTime })`; `deltaTime` ≈ 1 per 60 fps frame, `deltaMS` is milliseconds.
- **Leaf nodes have no children** — `Sprite`, `Graphics`, `Text`, `Mesh` cannot `addChild`; wrap in a `Container`.
- **Renamed APIs** — `app.view` → `app.canvas`, `container.name` → `container.label`, `getBounds()` returns `Bounds` (use `.rectangle`), `onRender` replaces v7 `updateTransform` overrides, `cacheAsTexture(true)` is a method.

## Usage

### Read before you write

1. List every reference file your task touches — each class you construct, options object you pass, effect you build, symptom you fix. A whole app usually lists four to eight (an eraser paint app: application, assets, sprites, events, blend-modes; a game: application, assets, sprites, events, ticker, text).
2. Read each listed file before writing the code for that part, even for a one-line change — open the file itself; a grep hit is a fragment that drops the rule and the exception beside it.
3. Done when every file on the list has been opened. Then check the Gotchas below against each feature you built.

No file fits: scan the References list below, or fetch the class's API page from the v8 docs (`https://pixijs.download/release/docs/<module>.<Class>.html.md` — the module for a class is listed in `https://pixijs.download/release/docs/llms.txt`). Vite does not type-check, so run `npx tsc --noEmit` to catch wrong option names.

### Quick start

From the v8.23.0 README (works verbatim):

```ts
import { Application, Assets, Sprite } from 'pixi.js';

(async () => {
    const app = new Application();
    await app.init({ background: '#1099bb', resizeTo: window });
    document.body.appendChild(app.canvas);

    const texture = await Assets.load('https://pixijs.com/assets/bunny.png');
    const bunny = new Sprite(texture);
    bunny.anchor.set(0.5);
    bunny.x = app.screen.width / 2;
    bunny.y = app.screen.height / 2;
    app.stage.addChild(bunny);

    app.ticker.add((time) => {
        bunny.rotation += 0.1 * time.deltaTime;
    });
})();
```

Install with `npm install pixi.js`, or scaffold a project with `npm create pixi.js@latest`. TypeScript 5 needs no extra setup (PixiJS brings `@webgpu/types`); on TypeScript 6/7 use `@types/web` in `types` instead of the `dom` lib. Project setup details in [20-environments-builds](references/20-environments-builds.md).

## Gotchas

These fail silently — they run without errors and draw the wrong thing, and a Vite build doesn't type-check, so run `npx tsc --noEmit` to catch wrong option names. The full list of 55 traps, grouped by feature, is in [22-pitfalls](references/22-pitfalls.md). The most frequent:

- `const app = new Application(); await app.init({ ... })` — constructor options are ignored; `app.renderer`/`canvas`/`screen` throw until init resolves. [01-application](references/01-application.md)
- Wrap init in an async IIFE — top-level `await` fails `vite build` on Vite 6 and older. [20-environments-builds](references/20-environments-builds.md)
- `Texture.from(url)` and `Sprite.from(url)` read the cache only — `await Assets.load(url)` first. [04-sprites](references/04-sprites.md)
- Graphics is shape-first: `.rect(...).fill(...).stroke({ width, color })`; `beginFill`, `drawRect` and `lineStyle` are v7. [05-graphics](references/05-graphics.md)
- The render root's own `blendMode` is ignored — wrap an `'erase'` brush in a plain `Container`, render with `clear: false` into its own `RenderTexture`. [13-blend-modes](references/13-blend-modes.md)
- Fill a `ParticleContainer` with `addParticle(...)`; the `particles` option draws nothing until `update()`. [08-particles](references/08-particles.md)
- `AnimatedSprite` needs `autoPlay: true` or `play()`; `animationSpeed` is frames per 60 fps tick (12 fps = `0.2`). [04-sprites](references/04-sprites.md)
- Give interactive objects `eventMode = 'static'` — the default `'passive'` never fires their own listeners; drag with `globalpointermove`. [11-events](references/11-events.md)
- Assign a new array to change filters: `c.filters = [...(c.filters ?? []), f]`; WebGPU needs a WGSL `gpu` program on every filter. [12-filters](references/12-filters.md)
- `zIndex` sorts at the next render — call `parent.sortChildren()` before reading `children`; a mask is a child of the masked container. [03-scene-graph](references/03-scene-graph.md)
- `new Text({ text, style: { fill: 0xffffff } })` — default fill is black; strings that change every frame go in `BitmapText`. [06-text](references/06-text.md)
- Ticker callbacks receive the `Ticker`: `app.ticker.add((t) => (s.x += 2 * t.deltaTime))`; `app.ticker.update()` already renders. [17-ticker](references/17-ticker.md)
- Teardown: `destroy({ children: true })`, `Assets.unload(key)`, `app.destroy()` after init — pass `releaseGlobalResources: true` when re-creating an app in the same tab. [18-performance](references/18-performance.md)

## References

- [22-pitfalls](references/22-pitfalls.md) — read first: 55 silent-failure traps grouped by feature (app setup, assets, sprites, graphics, textures, particles, filters, text, input, scene order, teardown, builds)
- [01-application](references/01-application.md) — Application init, options and defaults, resize, resolution, plugins, destroy
- [02-renderers](references/02-renderers.md) — WebGL/WebGPU/Canvas selection, `renderer.render()` options, RenderTexture, generateTexture, interop
- [03-scene-graph](references/03-scene-graph.md) — Container, transforms, RenderGroup, RenderLayer, masks, zIndex, bounds, hiding, destroy
- [04-sprites](references/04-sprites.md) — Sprite, Texture/TextureSource, sub-textures, canvas/video textures, AnimatedSprite, TilingSprite, NineSliceSprite
- [05-graphics](references/05-graphics.md) — shapes, fills/strokes, gradients, texture fills, SVG import/export, SmoothGraphics, v7 name ports
- [06-text](references/06-text.md) — Text/TextStyle, BitmapText, HTMLText, SplitText, fonts, per-frame text cost
- [07-mesh](references/07-mesh.md) — Mesh, MeshGeometry, MeshSimple, MeshPlane, MeshRope, PerspectiveMesh, UVs
- [08-particles](references/08-particles.md) — ParticleContainer, Particle, dynamicProperties, update, emitters, pools
- [09-dom-gif-html](references/09-dom-gif-html.md) — DOMContainer over the canvas, GifSprite, HTMLSource
- [10-assets](references/10-assets.md) — Assets load/add/unload, parsers, bundles, manifests, spritesheets, fonts, video, SVG, compressed textures, progress
- [11-events](references/11-events.md) — eventMode, pointer events, click/tap, drag, hitArea, cursor, wheel
- [12-filters](references/12-filters.md) — built-in filters, Filter.from GLSL/WGSL, uniforms, padding, filterArea, multi-pass
- [13-blend-modes](references/13-blend-modes.md) — standard and advanced modes, erase and paint-out, filtered containers
- [14-custom-rendering](references/14-custom-rendering.md) — Shader.from, GlProgram/GpuProgram, UniformGroup, textures as resources, custom pipes, 3D textures
- [15-maths](references/15-maths.md) — Point/ObservablePoint, Matrix, Rectangle and hit areas, math-extras vectors
- [16-color](references/16-color.md) — Color/ColorSource input ranges, conversions, tint, alpha, premultiply
- [17-ticker](references/17-ticker.md) — frame order, deltaTime/deltaMS, priorities, FPS capping, onRender, manual loops
- [18-performance](references/18-performance.md) — teardown, GCSystem, PrepareSystem, cacheAsTexture, batching, culling, pooling
- [19-accessibility](references/19-accessibility.md) — accessible, accessibleTitle, tabIndex, accessibilityOptions
- [20-environments-builds](references/20-environments-builds.md) — Web Workers, Node/SSR, strict CSP, custom builds, create pixi.js, tsconfig
- [21-migration-v7-to-v8](references/21-migration-v7-to-v8.md) — v7 to v8 port checklist: imports, init, Graphics, Text, events, shaders, cleanup
