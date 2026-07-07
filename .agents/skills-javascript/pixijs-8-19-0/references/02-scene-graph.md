# Scene Graph

## Container

`Container` is the base class for all display objects. Everything in the scene graph extends Container (directly or via `ViewContainer`).

### Creation

```ts
import { Container } from 'pixi.js';

// Empty container
const container = new Container();

// With options
const container = new Container({
    x: 100,
    y: 200,
    rotation: Math.PI / 4,
    scale: { x: 2, y: 2 },
    alpha: 0.8,
    tint: 0xff0000,
    visible: true,
    renderable: true,
    blendMode: 'normal',
    children: [sprite1, sprite2],
    boundsArea: new Rectangle(0, 0, 500, 500),
    isRenderGroup: false,
});
```

### Child Management

```ts
// Add children
container.addChild(sprite);
container.addChild(sprite1, sprite2, sprite3); // Multiple
container.addChildAt(sprite, 0); // Insert at index
const added = container.addChild<Sprite>(new Sprite(texture)); // Typed

// Remove children
container.removeChild(sprite);
container.removeChild(sprite1, sprite2); // Multiple
container.removeChildAt(0);
container.removeChildren(); // All children
container.removeChildren(2); // From index 2
container.removeChildren(2, 5); // From index 2, count 5

// Reparent (move to this container, keeping world transform)
container.reparentChild(child);
container.reparentChildAt(child, index);

// Access children
container.children; // Read-only array
container.children[0];
container.getChildByName('label'); // Search by label (alias for getChildByLabel)
container.getChildByLabel('label'); // Search by label
container.getChildByLabel('label', true); // Recursive search
container.getChildrenByLabel(/^enemy/); // Regex search (all matching)
container.getChildAt(0);
container.getChildIndex(sprite); // Get index
container.setChildIndex(sprite, 0); // Reorder
container.swapChildren(a, b);

// Check containment
container.contains(sprite); // boolean
```

### Transform Properties

| Property | Type | Description |
|---|---|---|
| `x`, `y` | `number` | Position (alias for `position.x/y`) |
| `position` | `ObservablePoint` | Position in parent's local space |
| `rotation` | `number` | Rotation in radians |
| `angle` | `number` | Rotation in degrees |
| `scale` | `ObservablePoint` | Scale factors (default: 1, 1) |
| `pivot` | `ObservablePoint` | Center of rotation/scale/skew |
| `origin` | `ObservablePoint` | Origin point (doesn't move position) |
| `skew` | `ObservablePoint` | Skew factors in radians |
| `width` | `number` | Width (sets scale.x based on bounds) |
| `height` | `number` | Height (sets scale.y based on bounds) |

```ts
// Position
container.position.set(100, 200);
container.x = 100;
container.y = 200;

// Rotation
container.rotation = Math.PI / 4; // Radians
container.angle = 45; // Degrees

// Scale
container.scale.set(2); // Uniform
container.scale.set(2, 1.5); // Non-uniform
container.scale.x = 2;

// Pivot (center of rotation)
container.pivot.set(50, 50);

// Origin (alternative to pivot)
container.origin.set(50, 50);

// Skew
container.skew.set(0.1, 0.2);

// Size (computed from bounds)
container.width = 200;
container.height = 100;
```

### Appearance Properties

| Property | Type | Description |
|---|---|---|
| `alpha` | `number` | Relative opacity (0-1, default: 1) |
| `tint` | `ColorSource` | Color tint (default: 0xFFFFFF) |
| `visible` | `boolean` | Visibility + transform updates (default: true) |
| `renderable` | `boolean` | Render control only (default: true) |
| `blendMode` | `BLEND_MODES` | Blend mode (default: 'normal') |
| `cullable` | `boolean` | Can be culled by Culler |
| `cullArea` | `Rectangle` | Custom cull area |
| `cullableChildren` | `boolean` | Whether children can be culled |

### Blend Modes

Built-in: `'normal'`, `'add'`, `'multiply'`, `'screen'`, `'erase'`, `'inherit'`

Advanced (requires `import 'pixi.js/advanced-blend-modes'`):
`'overlay'`, `'darken'`, `'lighten'`, `'color-dodge'`, `'color-burn'`, `'hard-light'`, `'soft-light'`, `'difference'`, `'exclusion'`, `'hue'`, `'saturation'`, `'color'`, `'luminosity'`

### Bounds

```ts
// Get bounds (returns Bounds object, not Rectangle)
const bounds = container.getBounds();
const rect = bounds.rectangle; // Get as Rectangle

// Local bounds (object's own coordinate space)
const localBounds = container.getLocalBounds();

// Fast bounds (skips invisible/hidden children)
const fastBounds = container.getFastGlobalBounds();

// Set custom bounds area (optimization for large child counts)
container.boundsArea = new Rectangle(0, 0, 500, 500);

// Set size (width + height with one bounds calculation — more efficient)
container.setSize(200, 100);
const size = container.getSize(); // { width: 200, height: 100 }
```

### Coordinate Conversion

```ts
// Global to local
const localPoint = container.toLocal(globalX, globalY);
const localPoint = container.toLocal(globalPoint);

// Local to global
const globalPoint = container.toGlobal(localX, localY);
const globalPoint = container.toGlobal(localPoint);

// From another container's space
const point = container.toLocal(otherContainer.x, otherContainer.y, otherContainer);
```

### Matrix Transforms

```ts
// Local transform (from container's own properties)
const localMatrix = container.localTransform;

// World transform (absolute in scene)
const worldMatrix = container.worldTransform;

// Group transform (relative to render group)
const groupMatrix = container.groupTransform;

// Relative group transform
const relativeGroupMatrix = container.relativeGroupTransform;
```

## RenderGroup

RenderGroups are independent render roots with GPU-level transforms. Ideal for scrolling/panning large areas.

```ts
// Enable
container.enableRenderGroup();
container.isRenderGroup; // true

// Disable
container.disableRenderGroup();

// Or via constructor
const rg = new Container({ isRenderGroup: true });

// Nested render groups
const uiLayer = new Container({ isRenderGroup: true });
const gameLayer = new Container({ isRenderGroup: true });
app.stage.addChild(gameLayer, uiLayer);
```

### When to Use RenderGroups

- **Game world panning** — move the entire world without recalculating child transforms
- **UI overlay** — separate UI from game rendering
- **Scrolling lists** — efficient scrolling of many items
- **Layer separation** — independent rendering passes for different scene layers

### When NOT to Use RenderGroups

- **Per-child** — each RenderGroup is a separate draw pass; too many groups hurt performance
- **Small containers** — overhead exceeds benefit
- **Batched content** — RenderGroups break batching

## Lifecycle Events

```ts
container.on('added', (parent) => {
    console.log('Added to:', parent);
});

container.on('removed', (oldParent) => {
    console.log('Removed from:', oldParent);
});

container.on('childAdded', (child, container, index) => {
    console.log(`Child ${child} added at index ${index}`);
});

container.on('childRemoved', (child, container, index) => {
    console.log(`Child ${child} removed from index ${index}`);
});

container.on('visibleChanged', (visible) => {
    console.log('Visibility:', visible);
});

container.on('destroyed', (container) => {
    console.log('Destroyed');
});
```

## onRender Hook

Use `onRender` for per-frame logic (replaces v7's `updateTransform` override):

```ts
const container = new Container();
container.onRender = () => {
    // Called every frame before rendering
    // Good for: custom positioning, animation logic, etc.
};
```

## Destroy

```ts
// Basic destroy
container.destroy();

// Destroy with children
container.destroy({ children: true });

// Full cleanup
container.destroy({
    children: true,
    texture: true,
    textureSource: true,
    context: true,
});
```

## Culling

Manual culling system (not automatic in v8):

```ts
import { Culler } from 'pixi.js';

// Enable culling on container
container.cullable = true;
container.cullArea = new Rectangle(0, 0, 400, 400); // Optional: custom cull area
container.cullableChildren = false; // Don't cull children individually

// Cull before rendering
const view = new Rectangle(0, 0, 800, 600);
Culler.shared.cull(container, view);

// Or use CullerPlugin for automatic culling
import { CullerPlugin } from 'pixi.js';
extensions.add(CullerPlugin);
```

## Effects

Containers support filters and masks:

```ts
// Filters
container.filters = [
    new BlurFilter({ strength: 8 }),
    new ColorMatrixFilter(),
];
container.filterArea = new Rectangle(0, 0, 200, 200); // Optimization

// Mask (Graphics or Sprite)
const mask = new Graphics();
mask.circle(100, 100, 50).fill(0xffffff);
container.mask = mask;
container.addChild(mask); // Mask must be a child

// Inverse mask (render everything OUTSIDE the mask)
container.setMask({ mask: maskGraphics, inverse: true });

// MaskFilter (filter-based masking, alternative to container.mask)
import { MaskFilter } from 'pixi.js';
container.filters = [new MaskFilter(maskSprite)];
```

## Cache as Texture

Cache a container as a texture for performance (replaces v7's `cacheAsBitmap`).

```ts
// Enable caching
container.cacheAsTexture(true);

// With config options
container.cacheAsTexture({
    resolution: 2,
    antialias: true,
});

// Update after changes
container.updateCacheTexture();

// Disable caching
container.cacheAsTexture(false);

// Access cached texture
const cachedTexture = container._cacheTexture;
```

### Gotchas

- Cached items render at actual size, ignoring transforms (e.g., 50% scale still caches at 100%)
- Filters may not behave as expected — wrap in parent container and cache the parent
- Don't apply to containers over 4096x4096 (GPU memory limit)
- Each cached texture consumes GPU memory
- Cache updates only when the containing scene is rendered

## Sorting

```ts
// Enable child sorting
container.sortableChildren = true;

// Set z-index (depth)
child1.zIndex = 1;
child2.zIndex = 10;

// Manual re-sort
container.sortChildren();

// Custom sort
container.sortChildren = (a, b) => a.zIndex - b.zIndex;
```

Use sparingly — sorting is expensive for large child counts.

## RenderLayer

Decouple render order from scene graph hierarchy. Objects maintain their logical parent for transforms but render at the layer's position in the scene graph.

```ts
import { RenderLayer } from 'pixi.js';

const layer = new RenderLayer();
stage.addChild(layer);

// Attach — render at layer's position, keep logical parent
layer.attach(sprite);

// Detach — render at original scene graph position
layer.detach(sprite);

// Sorting within layer
layer.sortableChildren = true;
sprite.zIndex = 10;
layer.sortRenderLayerChildren();

// Reposition layer
stage.addChildAt(layer, 0); // Render first
```

### Gotchas

- Objects re-added to a parent don't auto-reattach to their previous layer — call `layer.attach()` explicitly
- Removing a parent container removes all its children from layers automatically
- Layer position in scene graph determines render priority relative to other layers

## Container Mixins

Container includes these mixin capabilities:

- **childrenHelperMixin** — `getChildByName`, `getChildAt`, `removeChildAt`, etc.
- **effectsMixin** — `filters`, `mask` support
- **findMixin** — `getChildByName` with recursive search
- **getFastGlobalBoundsMixin** — Fast bounds calculation
- **getGlobalMixin** — `getGlobalPosition`
- **measureMixin** — `width`, `height`, `getSize()`, `setSize()`
- **onRenderMixin** — `onRender` hook
- **sortMixin** — `sortableChildren`, `sortDirty`, `sortChildren`
- **toLocalGlobalMixin** — `toLocal()`, `toGlobal()`
- **cacheAsTextureMixin** — `cacheAsTexture()`
- **collectRenderablesMixin** — Internal renderable collection
- **cullingMixin** — `cullable`, `cullArea`, `cullableChildren`
