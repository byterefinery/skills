---
name: pixijs-8-19-0
description: >
  PixiJS v8.19.0 — high-performance 2D rendering library for WebGL and WebGPU. Use when working with PixiJS,
  pixi.js, canvas rendering, sprites, graphics drawing, text rendering, particle systems, mesh rendering,
  filters/shaders, texture management, asset loading, or any 2D graphics built with the PixiJS API.
  Covers Application setup, Container scene graph, Sprite/AnimatedSprite/TilingSprite/NineSliceSprite,
  Graphics with GraphicsContext, Text/BitmapText/HTMLText, Assets manager, Events system, Filters,
  Mesh geometry, ParticleContainer, Ticker animation loop, Color utilities, RenderTextures,
  custom shaders, WebGPU/WebGL renderers, and performance optimization.
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

# pixijs 8.19.0

## Overview

PixiJS is a fast, lightweight 2D rendering library that abstracts WebGL and WebGPU behind an intuitive scene-graph API. It uses a single-package structure with an extension system for modular features. v8 introduced async initialization (`app.init()`), replaced `BaseTexture` with `TextureSource`, overhauled the Graphics API (shape-first, then fill/stroke), unified shaders for WebGL/WebGPU, and added WebGPU renderer support alongside WebGL and Canvas fallbacks.

### Core Architecture

PixiJS is organized around three layers:

1. **Scene Graph** — `Container` is the base class for everything. `Sprite`, `Graphics`, `Text`, `Mesh`, `ParticleContainer`, and other display objects extend it (directly or via `ViewContainer`). Containers hold children, manage transforms, and support effects (filters, masks).

2. **Rendering Pipeline** — The renderer auto-detects the best backend (WebGL > WebGPU > Canvas). It uses a pipe-based architecture where each display object type has a dedicated render pipe (`SpritePipe`, `GraphicsPipe`, `MeshPipe`, etc.). A `Batcher` groups compatible objects into single draw calls.

3. **Asset System** — `Assets` is a unified loader/resolver/cache that handles textures (PNG, JPG, WebP, AVIF, SVG, video), JSON, text, fonts, spritesheets, and bitmap fonts. Supports bundles, manifests, format detection, and resolution preferences.

### Key Principles

- **Async initialization** — `Application` and renderers must be awaited: `await app.init(options)`
- **Options objects** — constructors accept a single options object, not positional arguments
- **Texture-first** — textures are loaded via `Assets.load()`, then referenced by string key or `Texture.from()`
- **Shape-then-fill** — Graphics API: build shape first (`.rect()`, `.circle()`), then apply fill/stroke (`.fill()`, `.stroke()`)
- **Extensions** — features register via `extensions.add()` with `ExtensionType` metadata
- **RenderGroups** — containers can become independent render roots for GPU-level transforms (efficient for scrolling/panning)
- **No inheritance from leaf nodes** — `Sprite`, `Graphics`, `Mesh` etc. cannot have children; wrap in `Container`
- **Ticker callbacks** — receive `Ticker` instance, not delta time: `ticker.add((ticker) => { sprite.rotation += ticker.deltaTime })`

### Import Patterns

```ts
// Full import (includes all default extensions)
import { Application, Sprite, Graphics, Text, Assets } from 'pixi.js';

// Manual imports for smaller bundles
import 'pixi.js/app';
import 'pixi.js/sprite';
import 'pixi.js/graphics';
import 'pixi.js/text';
import 'pixi.js/text-bitmap';
import 'pixi.js/text-html';
import 'pixi.js/filters';
import 'pixi.js/mesh';
import 'pixi.js/sprite-tiling';
import 'pixi.js/sprite-nine-slice';
import 'pixi.js/events';
import 'pixi.js/particle-container';
import 'pixi.js/prepare';
import 'pixi.js/advanced-blend-modes';
import 'pixi.js/unsafe-eval';
import 'pixi.js/dds';
import 'pixi.js/ktx';
import 'pixi.js/ktx2';
import 'pixi.js/basis';

// Not imported by default — add manually when needed
import 'pixi.js/advanced-blend-modes';
import 'pixi.js/unsafe-eval';
import 'pixi.js/prepare';
import 'pixi.js/math-extras';
import 'pixi.js/dds';
import 'pixi.js/ktx';
import 'pixi.js/ktx2';
import 'pixi.js/basis';
```

### Quick Start

```ts
import { Application, Sprite, Assets, Graphics, Text } from 'pixi.js';

const app = new Application();
await app.init({
    width: 800,
    height: 600,
    backgroundColor: 0x1099bb,
    antialias: true,
    resolution: window.devicePixelRatio,
    preference: 'webgl', // or 'webgpu', 'canvas', or ['webgpu', 'webgl']
});

document.body.appendChild(app.canvas);

// Load and display a texture
const texture = await Assets.load('assets/sprite.png');
const sprite = new Sprite({ texture, anchor: 0.5 });
sprite.position.set(400, 300);
app.stage.addChild(sprite);

// Draw graphics
const graphics = new Graphics();
graphics.rect(0, 0, 100, 100).fill(0xff0000).stroke({ width: 2, color: 0xffffff });
graphics.position.set(100, 100);
app.stage.addChild(graphics);

// Create text
const text = new Text({
    text: 'Hello PixiJS!',
    style: { fontSize: 24, fill: 0xffffff, fontFamily: 'Arial' }
});
text.position.set(400, 500);
app.stage.addChild(text);
```

## Usage

### Application Lifecycle

```ts
const app = new Application();
await app.init({
    width: 800,
    height: 600,
    backgroundColor: 0x1099bb,
    antialias: true,
    resolution: window.devicePixelRatio,
    preference: 'webgl',
    autoStart: true,       // Start render loop automatically
    sharedTicker: true,    // Use shared ticker
    resizeTo: window,      // Auto-resize to element
    autoDensity: true,     // Adjust resolution on resize
});

app.stage.addChild(sprite);
// app.render() called automatically by TickerPlugin

// Manual rendering (if autoStart: false)
app.ticker.add(() => {
    app.render();
});

// Cleanup
app.destroy(true, true); // Remove canvas, destroy everything
```

### Container Hierarchy

```ts
const container = new Container({
    x: 100,
    y: 100,
    rotation: Math.PI / 4,
    scale: { x: 2, y: 2 },
    alpha: 0.8,
    tint: 0xff0000,
    visible: true,
    blendMode: 'normal',
});

container.addChild(sprite1, sprite2);
container.removeChild(sprite1);
container.removeChildAt(0);
container.removeChild(sprite1, sprite2); // Multiple
container.removeChildren(); // All

// Access children
container.children[0];
container.getChildByName('my-sprite'); // Uses label property
container.getChildAt(0);

// Transform shortcuts
container.x = 100;
container.y = 200;
container.angle = 45; // Degrees
container.rotation = Math.PI / 4; // Radians
container.scale.set(2); // Uniform
container.pivot.set(50, 50); // Center of rotation
container.origin.set(50, 50); // Alternative to pivot (doesn't move position)
container.skew.set(0.1, 0.2);

// Bounds
container.width = 200; // Sets scale.x based on measured bounds
container.height = 100; // Sets scale.y
container.getBounds(); // Returns Bounds object
container.getBounds().rectangle; // Rectangle

// RenderGroup (GPU-level transforms for efficient scrolling)
container.enableRenderGroup();
container.disableRenderGroup();
container.isRenderGroup; // boolean
```

### Display Objects Quick Reference

| Class | Purpose | Key Properties |
|---|---|---|
| `Sprite` | Single texture display | `texture`, `anchor` |
| `AnimatedSprite` | Frame-by-frame animation | `textures`, `animationSpeed`, `loop`, `play()`, `stop()` |
| `TilingSprite` | Repeating texture pattern | `tilePosition`, `tileScale`, `tileRotation` |
| `NineSliceSprite` | Scalable UI with fixed corners | `leftWidth`, `topHeight`, `rightWidth`, `bottomHeight` |
| `Graphics` | Vector drawing (shapes, paths) | `context` (GraphicsContext), fluent API |
| `Text` | Canvas-rendered text | `text`, `style` (TextStyle) |
| `BitmapText` | Pre-rendered bitmap font text | `text`, `style`, faster than Text |
| `HTMLText` | HTML/CSS rich text | `text`, `style` (HTMLTextStyle), tag support |
| `Mesh` | Custom geometry + shader | `geometry`, `shader`, `texture` |
| `MeshPlane` | Grid of quads | `texture`, `width`, `height`, `verticesX/Y` |
| `MeshRope` | Chain of linked quads | `texture`, `points` |
| `ParticleContainer` | High-performance particles | `particles`, `dynamicProperties` |
| `DOM` | Embed HTML elements in scene | `view` (HTMLElement) |

### Events

```ts
// Enable interaction
sprite.eventMode = 'static'; // or 'auto', 'dynamic', 'passive', 'none'
sprite.hitArea = new Rectangle(0, 0, 100, 100); // Optional custom hit area

// Pointer events (unified mouse + touch)
sprite.on('pointerdown', (e) => {
    e.stopPropagation();
    console.log(e.global.x, e.global.y);
    console.log(e.getLocalPosition(sprite.parent));
});

sprite.on('pointerup', (e) => {});
sprite.on('pointermove', (e) => {});
sprite.on('pointerover', (e) => { sprite.cursor = 'pointer'; });
sprite.on('pointerout', (e) => { sprite.cursor = 'auto'; });
sprite.on('pointercancel', (e) => {});

// Click/tap
sprite.on('pointertap', (e) => {}); // Single tap/click
sprite.on('pointerupoutside', (e) => {});

// Wheel/scroll
sprite.on('wheel', (e) => {
    e.deltaY; // Scroll amount
    e.deltaMode;
});

// Global events (from EventBoundary dispatch)
app.renderer.events?.rootBoundary.dispatch.on('pointerdown', (e) => {
    // Fires for every pointer down, regardless of target
});
```

### Filters

```ts
// Apply filters to any container
sprite.filters = [
    new BlurFilter({ strength: 8, quality: 4 }),
    new ColorMatrixFilter(),
    new DisplacementFilter({ sprite: displacementSprite, scale: 5 }),
    new NoiseFilter({ strength: 0.5 }),
];

// Set filter area (optimization — only apply to specific region)
sprite.filterArea = new Rectangle(0, 0, 200, 200);

// ColorMatrixFilter effects
const colorMatrix = new ColorMatrixFilter();
colorMatrix.brightness(1.2);
colorMatrix.contrast(1.5);
colorMatrix.saturate(0.5);
colorMatrix.hue(90);
colorMatrix.gray();
colorMatrix.sepia();
colorMatrix.negative();
colorMatrix.tint(0xff0000);
colorMatrix.desaturate();

// Masking
const maskGraphics = new Graphics();
maskGraphics.circle(100, 100, 50).fill(0xffffff);
container.mask = maskGraphics;
container.addChild(maskGraphics);
```

## Gotchas

- **Async init required** — `new Application()` does nothing until `await app.init()`. Accessing `app.renderer` or `app.canvas` before init throws.
- **No children on leaf nodes** — `Sprite`, `Graphics`, `Mesh`, `Text` cannot have children. Wrap in `Container`.
- **Texture loading** — `Texture.from('url')` only works if the URL was already loaded via `Assets.load()`. For fresh loads, use `await Assets.load('url')`.
- **Ticker callback signature** — callbacks receive `Ticker` instance, not delta time. Use `ticker.deltaTime` (scalar) or `ticker.deltaMS` (milliseconds).
- **Graphics API order** — build shape first, then fill/stroke: `.rect(0, 0, 100, 100).fill(0xff0000)`, not `.fill().rect()`.
- **`container.name` is `container.label`** — v8 renamed the property.
- **`Application.view` is `Application.canvas`** — v8 renamed the property.
- **`container.getBounds()` returns `Bounds`** — not `Rectangle`. Use `.rectangle` property for Rectangle.
- **`cacheAsBitmap` → `cacheAsTexture()`** — now a method call: `container.cacheAsTexture(true)`.
- **`ParticleContainer` uses `Particle` objects** — not `Sprite`. Use `container.addParticle(particle)`, not `addChild()`.
- **`ParticleContainer` needs `boundsArea`** — it doesn't calculate bounds automatically.
- **`NineSlicePlane` renamed to `NineSliceSprite`**.
- **`TileSprite` renamed to `TilingSprite`**.
- **`SimpleMesh`/`SimplePlane`/`SimpleRope` renamed** — to `MeshSimple`, `MeshPlane`, `MeshRope`.
- **Blend modes** — basic modes (`normal`, `add`, `multiply`, `screen`, etc.) are built-in. Advanced modes require `import 'pixi.js/advanced-blend-modes'`.
- **Texture swapping** — when swapping a sprite's texture at runtime, the sprite may not update automatically. Call `sprite.onViewUpdate()` or set `texture.dynamic = true` at creation.
- **Filters break batching** — each filter forces a render-to-texture pass. Group filtered objects under one container to minimize passes.
- **RenderGroups don't batch** — turning every container into a RenderGroup hurts performance. Use at broad levels (UI layer, game world layer).
- **Mipmaps on RenderTextures** — must manually call `texture.source.updateMipmaps()` after rendering to the texture.
- **`TextStyle` is shared by reference** — modifying a shared style affects all Text instances using it. Clone with `{ ...style }` or `Object.assign({}, style)`.
- **`GraphicsContext` sharing** — multiple Graphics can share one context. Changes to the context affect all Graphics using it.
- **Culling is manual in v8** — use `Culler.shared.cull(container, viewRect)` or add `CullerPlugin` for automatic culling.
- **`container.alpha` is relative** — it's relative to parent's alpha. Parent alpha 0.5 + child alpha 0.5 = 25% effective opacity.
- **`container.visible` vs `container.renderable`** — `visible: false` skips transform updates too; `renderable: false` only skips drawing.
- **Event mode default is `passive`** — objects don't receive events by default. Set `eventMode: 'static'` or `'auto'`.
- **`TextStyle` fill accepts many formats** — hex number, CSS string, `FillGradient`, `FillPattern`, array of colors for gradient text.
- **`BitmapText` needs font loaded** — either via `Assets.load('font.fnt')` or dynamic generation with system font name.
- **`HTMLText` uses SVG foreignObject** — supports HTML tags and CSS but has security restrictions in some environments.
- **WebGPU not universally supported** — always provide fallback: `preference: ['webgpu', 'webgl']`.

## References

- [01-application-setup](references/01-application-setup.md) — Application, renderers (WebGL/WebGPU/Canvas), autoDetect, options, plugins, resize
- [02-scene-graph](references/02-scene-graph.md) — Container hierarchy, transforms, RenderGroup, lifecycle, bounds, culling, effects
- [03-sprites](references/03-sprites.md) — Sprite, AnimatedSprite, TilingSprite, NineSliceSprite, anchor, texture swapping
- [04-graphics](references/04-graphics.md) — Graphics, GraphicsContext, paths, fills, strokes, gradients, patterns, SVG import
- [05-text](references/05-text.md) — Text, TextStyle, BitmapText, HTMLText, fonts, word wrap, MSDF/SDF
- [06-textures](references/06-textures.md) — Texture, TextureSource types, RenderTexture, spritesheets, compressed textures
- [07-assets](references/07-assets.md) — Assets manager, loading, bundles, manifests, format detection, cache
- [08-events](references/08-events.md) — EventSystem, pointer events, hit areas, event modes, propagation, wheel
- [09-filters](references/09-filters.md) — Filter base, BlurFilter, ColorMatrixFilter, DisplacementFilter, custom filters, masks
- [10-mesh](references/10-mesh.md) — Mesh, MeshGeometry, MeshPlane, MeshRope, PerspectiveMesh, custom shaders
- [11-particles](references/11-particles.md) — ParticleContainer, Particle, dynamic properties, performance
- [12-ticker](references/12-ticker.md) — Ticker, animation loop, timing, priorities, shared vs system ticker
- [13-maths](references/13-maths.md) — Matrix, Point, shapes (Rectangle, Circle, Ellipse, Polygon), Color, constants
- [14-advanced](references/14-advanced.md) — Extensions, custom shaders, WebGPU, performance optimization, custom render pipes
