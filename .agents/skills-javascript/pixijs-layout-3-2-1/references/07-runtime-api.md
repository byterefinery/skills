# Runtime API

Runtime APIs available on layout-enabled objects for inspection and control.

## Layout Instance

```ts
const layout = container.layout; // Layout | null
```

## Computed Layout (Yoga)

Raw layout box from the Yoga engine:

```ts
const box = layout.computedLayout;
// { left: number, top: number, right: number, bottom: number, width: number, height: number }
```

These are logical layout coordinates. `left`/`top` define the position within the parent; `width`/`height` define the box size.

## Computed Pixi Layout

PixiJS-specific adjustments applied during `updateLocalTransform`:

```ts
const pixi = layout.computedPixiLayout;
// {
//   x: number,       // layout position x
//   y: number,       // layout position y
//   offsetX: number, // offset within layout box (leaf nodes)
//   offsetY: number,
//   scaleX: number,  // scale from objectFit (leaf nodes)
//   scaleY: number,
//   originX: number, // transform origin x
//   originY: number, // transform origin y
// }
```

For containers: `offsetX/Y` are 0 and `scaleX/Y` are 1. For leaf nodes: these encode the objectFit scaling and objectPosition offset.

## Real Position and Scale

True position/scale after layout is applied:

```ts
layout.realX;      // True x position
layout.realY;      // True y position
layout.realScaleX; // True x scale
layout.realScaleY; // True y scale
```

Unlike `position.x`/`position.y` (which are offsets from layout position) and `scale.x`/`scale.y` (which are multipliers on layout scale), these return the actual transformed values.

## Style

Read current layout styles:

```ts
const styles = layout.style;
// Readonly<LayoutStyles>
```

## Force Update

Force immediate recalculation during the next frame:

```ts
layout.forceUpdate();
```

Use when external modifications may have changed bounds that the layout system can't track.

## Invalidate Root

Mark the root layout as dirty:

```ts
layout.invalidateRoot();
layout.invalidateRoot(startContainer);
```

Traverses up to find the root layout node and marks it dirty. Called automatically when styles change or children are added/removed.

## Get Root

Find the root container of the layout tree:

```ts
const root = layout.getRoot();
const root = layout.getRoot(startContainer);
```

Traverses up the parent chain to find the topmost layout-enabled container.

## Layout Event

Each layout-enabled object emits a `layout` event when its layout is updated:

```ts
// Event listener
container.on('layout', (layout) => {
    const box = layout.computedLayout;
    console.log(`Position: ${box.left}, ${box.top}, Size: ${box.width}x${box.height}`);
});

// Callback property
container.onLayout = (layout) => {
    // Handle layout update
};
```

The event fires after `computedLayout` and `computedPixiLayout` are updated.

## Destroy

Clean up a layout:

```ts
layout.destroy();
```

Frees the Yoga node, removes event listeners, and marks the layout as destroyed. Called automatically when the target container is destroyed or when `container.layout = null`.

## Default Styles

Global defaults for all new layouts:

```ts
import { Layout } from '@pixi/layout';

// Current defaults
Layout.defaultStyle = {
    leaf: {
        width: 'intrinsic',
        height: 'intrinsic',
    },
    container: {
        width: 'auto',
        height: 'auto',
    },
    shared: {
        transformOrigin: '50%',
        objectPosition: 'center',
        flexShrink: 1,
        flexDirection: 'row',
        alignContent: 'stretch',
        flexWrap: 'nowrap',
        overflow: 'visible',
    },
};
```

Customize these to change behavior for all layout-enabled objects.

## Has Parent

Check if the layout node is attached to a parent:

```ts
layout.hasParent; // boolean
```

True when the layout-enabled object has a parent in the scene graph that is also layout-enabled (or an overflow container).

## Is Dirty

Internal flag indicating if layout needs recalculation:

```ts
layout._isDirty; // boolean
```

Set to `true` when styles change or children are added/removed. Cleared after layout is recalculated.
