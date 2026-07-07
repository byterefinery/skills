---
name: pixijs-layout-3-2-1
description: >
  PixiJS Layout v3.2.1 — Yoga-powered flexbox layout system for PixiJS. Use when building responsive 2D
  UIs, dashboards, menus, or any layout-driven scene with PixiJS. Covers enabling layout on Containers,
  Sprites, Text, and Graphics via the `layout` property; flexbox properties (flexDirection, justifyContent,
  alignItems, flexWrap, gap, flexGrow, flexShrink, flexBasis); sizing (width, height, minWidth,
  maxWidth, minHeight, maxHeight, aspectRatio, intrinsic); positioning (absolute, relative, static,
  top/left/right/bottom insets); object fitting (objectFit, objectPosition); styling (backgroundColor,
  borderColor, borderRadius, overflow); LayoutContainer and LayoutView components with scrolling;
  LayoutSystem configuration (autoUpdate, debug, throttle); Yoga config customization; and runtime APIs
  (computedLayout, computedPixiLayout, realX/Y, forceUpdate, layout events).
  Requires pixi.js v8 and yoga-layout v3 as peer dependencies.
metadata:
  tags:
    - layout
    - flexbox
    - ui
    - pixi
    - yoga
    - javascript
---

# pixijs-layout 3.2.1

## Overview

PixiJS Layout adds CSS-style flexbox layouting to PixiJS using Facebook's Yoga engine. It works as a PixiJS extension — importing `@pixi/layout` registers mixins on `Container`, `Text`, and `ViewContainer`, and installs the `LayoutSystem` into the renderer.

### Architecture

1. **Mixins** — Extends `Container`, `AbstractText`, and `ViewContainer` with a `layout` property. Setting `container.layout = { ... }` creates a `Layout` instance backed by a Yoga node and overrides `updateLocalTransform` so layout position/scale composites with manual transforms.

2. **LayoutSystem** — A PixiJS renderer system that runs in the `prerender` phase. It traverses the scene graph, recalculates dirty layouts, and applies computed transforms. Auto-update is on by default; disable with `autoUpdate: false`.

3. **Layout** — Per-object layout controller. Holds the Yoga node, computed layout box, and PixiJS-specific offsets. Exposes `style`, `computedLayout`, `computedPixiLayout`, `realX/Y`, `forceUpdate()`, and `destroy()`.

4. **Components** — Optional `LayoutContainer` (multi-child flex container with background/border/overflow) and `LayoutView` (single-slot wrapper with objectFit/objectPosition). Re-exported PixiJS classes (`Sprite`, `Text`, `Graphics`) accept `layout` in the constructor.

### Key Concepts

- **Opt-in** — Only objects with `layout` set participate in layout. Siblings without layout are unaffected.
- **Containers vs leaf nodes** — Containers (`Container`) manage children via flexbox. Leaf nodes (`Sprite`, `Text`, `Graphics`, `ViewContainer`) use `objectFit`/`objectPosition` to fit content inside their layout box. Set `isLeaf: true` on a Container to make it behave like a leaf.
- **Intrinsic sizing** — Leaf nodes default to `width: 'intrinsic'`, `height: 'intrinsic'`, which uses the PixiJS object's bounds. Has a performance cost (throttled bound checks). Use fixed pixel sizes for performance.
- **Positioning** — `x`/`y` on layout-enabled objects are offsets from the computed layout position, not absolute positions. Use `layout.realX`/`layout.realY` for the true position.
- **Visibility** — Hidden (`visible = false`) layout objects are excluded from layout calculations.

## Usage

### Installation

```bash
npm install @pixi/layout
# peer dependencies: pixi.js ^8, yoga-layout ^3
```

### Basic Setup

Import `@pixi/layout` **before** creating the Application so mixins and the LayoutSystem register:

```ts
import '@pixi/layout';
import { Application, Container, Sprite, Assets } from 'pixi.js';

const app = new Application();
await app.init({ background: '#1099bb', resizeTo: window });
document.body.appendChild(app.canvas);

const texture = await Assets.load('bunny.png');

// Stage layout — fill screen, center content
app.stage.layout = {
    width: app.screen.width,
    height: app.screen.height,
    justifyContent: 'center',
    alignItems: 'center',
};

// Flex container with wrapping
const container = new Container({
    layout: {
        width: '80%',
        height: '80%',
        gap: 4,
        flexWrap: 'wrap',
        justifyContent: 'center',
        alignContent: 'center',
    },
});
app.stage.addChild(container);

// Leaf sprites — intrinsic size from texture
for (let i = 0; i < 10; i++) {
    const bunny = new Sprite({ texture, layout: true });
    container.addChild(bunny);
}
```

### Enabling/Disabling Layout

```ts
// Enable with styles
container.layout = { width: 300, height: 200, flexDirection: 'column' };

// Enable with defaults
sprite.layout = true;

// Disable
sprite.layout = null; // or false
```

### Updating Styles

Partial updates merge with existing styles:

```ts
sprite.layout = { width: 200, objectFit: 'cover' };
```

### LayoutContainer — Full-Featured Container

For backgrounds, borders, overflow, and scrolling, use `LayoutContainer` from the components sub-path:

```ts
import { LayoutContainer } from '@pixi/layout/components';

const panel = new LayoutContainer({
    layout: {
        width: 400,
        height: 300,
        padding: 16,
        gap: 8,
        flexDirection: 'column',
        overflow: 'scroll',
        backgroundColor: 0x202020,
        borderColor: 0xffffff,
        borderWidth: 2,
        borderRadius: 12,
    },
    trackpad: { maxSpeed: 400, constrain: true },
});
```

Add children via `panel.addChild()` (routes to the internal overflow container).

### LayoutView — Single-Child Wrapper

For styled leaf nodes with background/border:

```ts
import { LayoutSprite } from '@pixi/layout/components';

const image = new LayoutSprite({
    texture,
    layout: {
        width: 200,
        height: 200,
        objectFit: 'cover',
        objectPosition: 'center',
        backgroundColor: 0x444444,
        borderRadius: 8,
    },
});
```

### LayoutSystem Configuration

```ts
await app.init({
    layout: {
        autoUpdate: true,       // auto-recalc each frame (default: true)
        enableDebug: false,     // debug overlay (default: false)
        throttle: 100,          // ms throttle for intrinsic size checks (default: 100)
        debugModificationCount: 50, // min modifications for heatmap (default: 50)
    },
});

// Runtime debug toggle
app.renderer.layout.enableDebug(true);

// Manual update (when autoUpdate is false)
app.renderer.layout.update(app.stage);
```

### Runtime Inspection

```ts
// Computed layout box from Yoga
const box = sprite.layout.computedLayout;
// { left, top, right, bottom, width, height }

// PixiJS-specific offsets
const pixi = sprite.layout.computedPixiLayout;
// { x, y, offsetX, offsetY, scaleX, scaleY, originX, originY }

// True position/scale after layout
sprite.layout.realX;
sprite.layout.realY;
sprite.layout.realScaleX;
sprite.layout.realScaleY;

// Force recalculation
sprite.layout.forceUpdate();

// Layout event
sprite.on('layout', (layout) => {
    console.log('updated', layout.computedLayout);
});
```

### Custom Yoga Configuration

```ts
import { getYogaConfig } from '@pixi/layout';

const config = getYogaConfig();
config.setErrata(Errata.Classic);
config.setPointScaleFactor(1);
```

## Gotchas

- **Import order matters** — `import '@pixi/layout'` must come before `new Application()` so mixins and the LayoutSystem register.
- **`x`/`y` are offsets** — On layout-enabled objects, `position.x`/`position.y` are offsets from the computed layout position, not absolute coordinates. Use `layout.realX`/`layout.realY` for true position.
- **`scale` is relative to 1** — Layout applies its own scale. Manual `scale.x`/`scale.y` are multipliers on top of layout scale. Use `layout.realScaleX`/`layout.realScaleY` for true scale.
- **`overflow` requires LayoutContainer** — Properties like `overflow: 'scroll'`, `backgroundColor`, `borderColor`, and `borderRadius` only work on `LayoutContainer` or `LayoutView` components, not plain `Container` with `layout` set.
- **Intrinsic sizing has a cost** — `width: 'intrinsic'` triggers throttled bound checks. For many objects, use fixed pixel sizes (`width: texture.width`) instead.
- **Hidden objects excluded** — Setting `visible = false` on a layout object removes it from layout calculations entirely.
- **Leaf nodes can't have flex children** — `Sprite`, `Text`, `Graphics` are leaf nodes by default. Use `Container` for flex containers. Set `isLeaf: true` on a Container if you want it to behave like a leaf (objectFit/objectPosition).
- **Partial style updates merge** — Setting `container.layout = { width: 200 }` merges with existing styles; it doesn't reset to defaults.
- **`LayoutContainer` addChild routes internally** — Children added to `LayoutContainer` go into the `overflowContainer` child, not the container itself. Use `container.addChild()` (not direct manipulation of children array).
- **Default leaf sizing** — Leaf nodes default to `width: 'intrinsic'`, `height: 'intrinsic'`. Containers default to `width: 'auto'`, `height: 'auto'`.
- **`objectFit`/`objectPosition` are leaf-only** — These properties have no effect on containers. Use `isLeaf: true` if you need them on a Container.
- **Rotation/skew don't trigger relayout** — Rotating a layout-enabled container does not cause a layout recalculation. Layout position is computed, then rotation is applied on top.
- **Text wordWrap interaction** — For `Text` objects with `wordWrap: true`, layout sets `wordWrapWidth` to the computed layout width and adjusts it based on `objectFit` scaling.

## References

- [01-flexbox-styles](references/01-flexbox-styles.md) — flexDirection, justifyContent, alignItems, flexWrap, gap, flexGrow, flexShrink, flexBasis
- [02-sizing-dimensions](references/02-sizing-dimensions.md) — width, height, minWidth, maxWidth, minHeight, maxHeight, aspectRatio, intrinsic sizing
- [03-positioning](references/03-positioning.md) — position types, insets (top/left/right/bottom), absolute vs relative
- [04-object-fit-position](references/04-object-fit-position.md) — objectFit modes, objectPosition syntax, transformOrigin
- [05-components](references/05-components.md) — LayoutContainer, LayoutView, LayoutSprite, LayoutText, LayoutGraphics, trackpad scrolling
- [06-layout-system](references/06-layout-system.md) — LayoutSystem options, autoUpdate, debug renderer, manual updates, Yoga config
- [07-runtime-api](references/07-runtime-api.md) — computedLayout, computedPixiLayout, realX/Y, forceUpdate, layout events, defaultStyle
