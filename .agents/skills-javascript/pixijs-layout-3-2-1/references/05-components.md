# Components

Built-in components from `@pixi/layout/components` combine PixiJS display objects with layout features including `backgroundColor`, `borderColor`, `borderRadius`, and `overflow`.

## LayoutContainer

Full flex container with background, border, and overflow support.

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

panel.addChild(child1, child2, child3);
```

### LayoutContainerOptions

| Field        | Type             | Description                                    |
|--------------|------------------|------------------------------------------------|
| `layout`     | `LayoutStyles`   | Layout styles applied on creation              |
| `trackpad`   | `TrackpadOptions` | Scroll behavior settings                       |
| `background` | `ContainerChild` | Custom background instead of default Graphics  |
| `children`   | `ContainerChild[]` | Initial children                              |

### Internal Structure

- `background` — Graphics object (or custom) for background/border rendering
- `overflowContainer` — Holds scrollable children
- `stroke` — Graphics for border rendering
- `_mask` — Graphics used as clip mask for overflow
- `containerMethods` — Bound Container methods that route to `overflowContainer`

Children added via `panel.addChild()` route to `overflowContainer`. Access original methods via `panel.containerMethods.addChild()`.

### Overflow Modes

| Value     | Description                                      |
|-----------|--------------------------------------------------|
| `visible` | Content shown outside bounds (default)           |
| `hidden`  | Content clipped, no scrolling                    |
| `scroll`  | Content clipped with touch/wheel scrolling       |

## LayoutView

Single-child wrapper. Manages one `slot` object and applies layout rules to it.

```ts
import { LayoutView } from '@pixi/layout/components';
import { Sprite } from 'pixi.js';

const view = new LayoutView({
    slot: new Sprite(texture),
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

### LayoutViewOptions

| Field        | Type             | Description                                    |
|--------------|------------------|------------------------------------------------|
| `slot`       | `Container`      | Internal display object managed by the view    |
| `layout`     | `LayoutStyles`   | Layout styles                                  |
| `trackpad`   | `TrackpadOptions` | Scroll settings                                |
| `background` | `ContainerChild` | Custom background                              |

Layout is split between container (positioning, size, background) and slot (objectFit, objectPosition, isLeaf).

## PixiJS Layout Wrappers

Pre-built LayoutView wrappers for common PixiJS types:

| Component              | Wraps                  |
|------------------------|------------------------|
| `LayoutSprite`         | `Sprite`               |
| `LayoutNineSliceSprite`| `NineSliceSprite`      |
| `LayoutTilingSprite`   | `TilingSprite`         |
| `LayoutAnimatedSprite` | `AnimatedSprite`       |
| `LayoutGifSprite`      | `GifSprite`            |
| `LayoutGraphics`       | `Graphics`             |
| `LayoutText`           | `Text`                 |
| `LayoutBitmapText`     | `BitmapText`           |
| `LayoutHTMLText`       | `HTMLText`             |
| `LayoutMesh`           | `Mesh`                 |
| `LayoutMeshRope`       | `MeshRope`             |
| `LayoutMeshPlane`      | `MeshPlane`            |

```ts
import { LayoutSprite, LayoutText } from '@pixi/layout/components';

const icon = new LayoutSprite({
    texture,
    layout: {
        width: 64,
        height: 64,
        objectFit: 'contain',
        backgroundColor: 0x333333,
        borderRadius: 4,
    },
});

const label = new LayoutText({
    text: 'Hello',
    style: { fontSize: 16, fill: 0xffffff },
    layout: {
        objectFit: 'contain',
        backgroundColor: 0x222222,
        padding: 8,
    },
});
```

## Re-exported PixiJS Classes

Standard PixiJS classes re-exported with constructor-level layout support:

```ts
import { Sprite, Text, Graphics } from '@pixi/layout/components';

const sprite = new Sprite({ texture, layout: { width: 100, height: 100 } });
const text = new Text({ text: 'Hi', layout: true });
```

These are the original PixiJS classes with `this.layout` set after construction. They do **not** include background/border/overflow features — use `LayoutSprite` etc. for those.

## Custom Backgrounds

Provide a custom background instead of the internal Graphics:

```ts
const panel = new LayoutContainer({
    layout: { width: 300, height: 300 },
    background: new Sprite(texture),
});
```

When a custom background is provided, automatic `backgroundColor`, `borderColor`, and `borderRadius` styling is disabled. The background is positioned and sized according to layout rules.

## Trackpad Customization

Scroll behavior for `overflow: 'scroll'`:

| Option              | Type      | Default | Description                                    |
|---------------------|-----------|---------|------------------------------------------------|
| `maxSpeed`          | `number`  | `400`   | Max scroll velocity (px/frame)                 |
| `constrain`         | `boolean` | `true`  | Constrain within content bounds                |
| `disableEasing`     | `boolean` | `false` | Disable momentum scrolling                     |
| `xEase`             | `ScrollSpring` | —  | Custom x-axis spring                           |
| `yEase`             | `ScrollSpring` | —  | Custom y-axis spring                           |
| `xConstrainPercent` | `number`  | `0`     | Overflow % allowed on x-axis (negative = off)  |
| `yConstrainPercent` | `number`  | `0`     | Overflow % allowed on y-axis (negative = off)  |

```ts
const panel = new LayoutContainer({
    layout: { overflow: 'scroll' },
    trackpad: {
        maxSpeed: 400,
        constrain: true,
        disableEasing: false,
        xEase: new ScrollSpring({ max: 200, damp: 0.7, springiness: 0.15 }),
    },
});
```
