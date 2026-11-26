# Scene graph and Container

## Contents

- [scene-core-concepts](#scene-core-concepts)
  - [The scene graph](#the-scene-graph)
  - [Container vs leaf](#container-vs-leaf)
  - [Where each concept lives](#where-each-concept-lives)
  - [Which reference covers which leaf](#which-reference-covers-which-leaf)
- [scene-container](#scene-container)
  - [Adding and removing children](#adding-and-removing-children)
  - [Transform properties](#transform-properties)
  - [Hiding](#hiding)
  - [zIndex and sortableChildren](#zindex-and-sortablechildren)
  - [Bounds and coordinate conversion](#bounds-and-coordinate-conversion)
  - [Sizing](#sizing)
  - [Container events](#container-events)
  - [Per-frame updates](#per-frame-updates)
  - [Destroy](#destroy)
- [transforms](#transforms)
  - [The three matrices](#the-three-matrices)
  - [Global, local, and screen coordinates](#global-local-and-screen-coordinates)
  - [Cumulative alpha](#cumulative-alpha)
  - [Scale 0](#scale-0)
- [render-groups](#render-groups)
  - [What it saves](#what-it-saves)
  - [Render groups vs cacheAsTexture](#render-groups-vs-cacheastexture)
- [layers](#layers)
  - [Attach, don't add](#attach-dont-add)
  - [What the layer does not control](#what-the-layer-does-not-control)
  - [Reparenting detaches](#reparenting-detaches)
  - [Sorted layers (depth / y-sort across parents)](#sorted-layers-depth--y-sort-across-parents)
- [masking](#masking)
  - [Mask type selection](#mask-type-selection)
  - [Sprite masks: channel](#sprite-masks-channel)
  - [Inverse masks](#inverse-masks)
  - [Removing a mask](#removing-a-mask)
- [constructor-options](#constructor-options)
  - [Options with non-obvious behaviour](#options-with-non-obvious-behaviour)

## scene-core-concepts

The v8 scene graph as a whole: containers vs leaves, render order, and which reference owns each concept and display object.

### The scene graph

A tree rooted at `app.stage`. Every display object is a `Container` subclass; v7's `DisplayObject` is gone, so type parameters and base classes use `Container`. Earlier siblings draw behind later ones. Nothing is culled unless you run a culler ([performance](18-performance.md#culling)).

### Container vs leaf

Only a `Container` (or a `RenderLayer`, through `attach`) groups other nodes. `Sprite` and its variants, `Graphics`, `Text` and its variants, `Mesh` and its variants, `ParticleContainer`, `DOMContainer` and `GifSprite` are leaves with `allowChildren = false`: `sprite.addChild(...)` logs a deprecation warning and is scheduled to become an error, and `ParticleContainer.addChild` throws (it holds `Particle` data objects via `addParticle`, see [scene-particle-container](08-particles.md)). To group a leaf with other nodes or with its mask, make them children of a plain `Container`.

### Where each concept lives

- Transforms, `pivot`/`origin`, `toGlobal`/`toLocal`, bounds, `zIndex`, hiding (`visible`/`renderable`/`alpha`), container events, `destroy`: [scene-container](03-scene-graph.md). `worldTransform` is stale until the next render; read positions with `toGlobal`/`getGlobalPosition`.
- The three matrices, screen vs global coordinates, cumulative alpha, scale 0: [transforms](03-scene-graph.md).
- One draw order across different parents, or a draw order decoupled from the hierarchy: `RenderLayer`, see [layers](03-scene-graph.md).
- A large subtree that pans or fades as a whole: `isRenderGroup: true`, see [render-groups](03-scene-graph.md).
- Clipping: set `container.mask`; a `Graphics`/`Container` mask uses the stencil buffer, a `Sprite` mask an alpha filter (red channel by default), a number a `ColorMask`. Clear with `container.mask = null`. Inverse masks, channels and teardown: [masking](03-scene-graph.md).
- `blendMode`: [blend-modes](13-blend-modes.md). Culling and `cacheAsTexture`: [performance](18-performance.md).
- Constructor options every node shares, and the ones that misbehave as options: [constructor-options](03-scene-graph.md).

### Which reference covers which leaf

| Leaf | Primary use | Reference |
| --- | --- | --- |
| `Sprite`, `NineSliceSprite`, `TilingSprite`, `AnimatedSprite` | A texture at a position; resizable panels; repeating backgrounds; frame animation | [scene-sprite](04-sprites.md) |
| `Text` / `BitmapText` / `HTMLText` / `SplitText` / `SplitBitmapText` | Text | [scene-text](06-text.md) |
| `Graphics` | Vector shapes, paths, fills, strokes (backed by a `GraphicsContext`) | [scene-graphics](05-graphics.md) |
| `Mesh` / `MeshSimple` / `MeshPlane` / `MeshRope` / `PerspectiveMesh` | Custom geometry, deformed or path-following textures, 2D perspective | [scene-mesh](07-mesh.md) |
| `ParticleContainer` + `Particle` | Thousands of lightweight sprites | [scene-particle-container](08-particles.md) |
| `DOMContainer` | An HTML element positioned by the scene graph | [scene-dom-container](09-dom-gif-html.md) |
| `GifSprite` | Animated GIF playback (`pixi.js/gif`) | [scene-gif](09-dom-gif-html.md) |


---

## scene-container

`Container`: children, transforms, hiding, `zIndex`, bounds and coordinate conversion, sizing, container events, and `destroy` options.

Only a `Container` holds children; `Sprite`, `Graphics`, `Text` and `Mesh` are leaves (see [scene-core-concepts](03-scene-graph.md#container-vs-leaf)). Constructor options, including `isRenderGroup` and `boundsArea`, and the ones that misbehave as options (`cacheAsTexture`, `width` before `children`): [constructor-options](03-scene-graph.md). `cullable` / `cullArea`: [performance](18-performance.md#culling). v7 names: `cacheAsBitmap = true` is the method `cacheAsTexture(true)` ([performance](18-performance.md#cacheastexture-for-performance)); `name` / `getChildByName` are deprecated aliases of `label` / `getChildByLabel`.

### Adding and removing children

- `addChild(a, b, c)` accepts any number of children and returns the first one. Children render in array order: index 0 is drawn first (behind).
- `removeChildren(beginIndex?, endIndex?)` removes `[beginIndex, endIndex)` and returns the removed array. In 8.22 it is only correct with `beginIndex = 0`: with a non-zero start it splices `endIndex` items instead of `endIndex - beginIndex`, dropping extra children from the array without events while their `parent` still points here. For a middle range, loop `removeChildAt(beginIndex)` (endIndex - beginIndex) times.
- `addChildAt` with a child that already belongs to the same container silently moves it to the new index. No `added` / `childAdded` / `removed` / `childRemoved` events fire, because the parent-child relationship didn't change.
- `reparentChild` / `reparentChildAt` move a child while preserving its world transform, but they read `worldTransform`, which only a render updates; if either container was created or moved since the last render, the child jumps. Then compute it yourself (position only; rotation/scale are not carried):

  ```ts
  const g = child.getGlobalPosition();
  newParent.addChild(child);
  newParent.toLocal(g, undefined, child.position);
  ```

- `replaceChild(old, next)` swaps a child in place, copying the old child's local transform. `child.removeFromParent()` detaches a child without a parent reference.
- `getChildByLabel(label, deep?)` returns the first match by string or `RegExp` (`true` searches recursively); it is typed `Container | null`, so under strict TS null-check it and cast before using leaf members. `getChildAt<Sprite>(i)` takes a type argument instead. `getChildrenByLabel(label, deep?, out?)` returns all matches.

### Transform properties

```ts
obj.position.set(100, 200);
obj.scale = 2; // sets both axes
obj.angle = 45; // degrees; rotation is radians, and they stay in sync
obj.origin.set(50, 50);
```

- `position`, `scale`, `pivot`, `origin`, `skew` are `ObservablePoint`s; copy into them with `set` / `copyFrom` (see [math](15-maths.md#point-and-observablepoint)).
- `pivot` sets the point in local space that maps to `position` in parent space; rotation and scale happen around it, and changing it shifts the drawing.
- `origin` (v8.11+) rotates and scales around a local point without that shift: the object stays where `position` puts it. Set one of `pivot` or `origin` on a container, never both; they compound.
- `alpha` and `tint` multiply down through children. `blendMode`: [blend-modes](13-blend-modes.md). The three matrices and cumulative alpha: [transforms](03-scene-graph.md).

### Hiding

What each way of hiding keeps (transforms still update in every case):

| Setting             | Drawn | Counted in `getBounds()` | Hit-tested / pointer events | Accessibility element |
| ------------------- | ----- | ------------------------ | --------------------------- | --------------------- |
| `visible = false`   | no    | no                       | no                          | no                    |
| `renderable = false`| no    | yes                      | no                          | yes                   |
| `alpha = 0`         | no    | yes                      | yes                         | yes                   |

For an invisible click target use `alpha = 0`, or a `hitArea` on an interactive container; `renderable = false` silently stops pointer events.

### zIndex and sortableChildren

```ts
ground.zIndex = 0;
player.zIndex = 10; // world re-sorts before the next render; no sortableChildren needed
world.addChild(ground, player);
```

Assigning a non-zero `zIndex` to a child (or adding a child that already has one) sets `sortableChildren = true` and marks the parent for a re-sort before the next render; you do not need to set `sortableChildren` yourself. The flag only matters if you want sorting on before any child has a `zIndex`. Equal `zIndex` values keep their insertion order. The sort happens during the next render: until then `children` (and `getChildIndex`) still show the old order, so call `sortChildren()` first if you read the order right after changing `zIndex`. `sortChildren()` does nothing unless a `zIndex` changed since the last sort; to reorder without `zIndex`, use `setChildIndex`, `addChildAt` or `swapChildren`.

`zIndex` orders siblings only. A sprite with `zIndex = 1000` inside container A still draws below every child of a container B that comes after A. For one depth order across different parents (e.g. y-sorting units from several groups), attach them to a `RenderLayer` created with `sortableChildren: true` and set `obj.zIndex = obj.y` every frame; see [layers](03-scene-graph.md).

### Bounds and coordinate conversion

```ts
container.getBounds().rectangle.contains(x, y);
const global = container.toGlobal(new Point(10, 20));
const fromOther = container.toLocal({ x: 0, y: 0 }, otherSprite);
```

`getBounds()` returns a `Bounds` object, not a `Rectangle`: `x`, `y`, `width`, `height` work, but `contains` and APIs that need a `Rectangle` take `.rectangle` (`getBounds().contains` throws "is not a function"). The signature is `getBounds(skipUpdate?: boolean, bounds?: Bounds)`; pass a `Bounds` as the second arg to avoid allocating. `getLocalBounds()` measures in the container's own space.

`toGlobal(point)` converts this container's local space to scene-root space. `toLocal(point, from?)` converts from another container's local space (or global space if `from` is omitted). `getGlobalPosition()` is `parent.toGlobal(position)`: the global location of the pivot point, which differs from `toGlobal({ x: 0, y: 0 })` when `pivot` or `origin` is set. All three accept an output point and compute fresh values even before the first render. `worldTransform` (and anything passed `skipUpdate = true`, `reparentChild`, hit testing) reflects only the last render: before the first render it is identity, and after a move it lags until the next frame.

### Sizing

`setSize(w, h)` adjusts `scale` so the container's current bounds fit the requested pixel size, in one operation; `getSize()` reads it back. It is a one-time scale calculation, not a stored size: on an empty container (or one whose content is added later, including `width`/`height` passed in the constructor options alongside `children`) the scale stays 1 and the content shows at natural size. Add the content first, then call `setSize` (again after content changes). Setting `.width` and `.height` individually works the same way, but each assignment re-measures; prefer `setSize` when changing both axes.

### Container events

These need no `eventMode`; they are not pointer events.

| Event            | Fires on                              | Arguments                   |
| ---------------- | ------------------------------------- | --------------------------- |
| `childAdded`     | the parent receiving the child        | `(child, container, index)` |
| `childRemoved`   | the parent losing the child           | `(child, container, index)` |
| `added`          | the child that was attached           | `(parent)`                  |
| `removed`        | the child that was detached           | `(parent)`                  |
| `destroyed`      | the destroyed container               | `(container)`               |
| `visibleChanged` | the container whose `visible` flipped | `(visible)`                 |

`destroyed` fires after internal cleanup but before listeners are removed, so by the time your handler runs `position`, `scale`, `pivot`, `origin`, `skew`, and `parent` have already been nulled, and `children` has been emptied (length 0, but the array reference itself is not nulled). Capture any data you need from the container _before_ calling `destroy()`, not inside the handler. With `{ children: true }` the parent's `destroyed` fires before any child is destroyed (each child's own `destroyed` follows), and on a Sprite the `texture` is still set inside the handler; the texture options run after it.

### Per-frame updates

`container.onRender = (renderer) => { ... }` runs once per render while the container is attached to the rendered scene, even when `visible = false`, `renderable = false` or culled; it stops when the container leaves the rendered scene and resumes when re-added. Set it to `null` to stop. In a subclass, assign it in the constructor. It replaces v7 `updateTransform` overrides; rules and naming traps: [ticker](17-ticker.md#per-object-onrender-hook).

### Destroy

```ts
container.destroy(); // this node only; children are orphaned, not destroyed

container.destroy({ children: true }); // whole subtree; shared textures survive

container.destroy({
  children: true,
  texture: true, // only when no other object uses these textures
  textureSource: true,
});
```

By default `destroy()` unlinks this container from its parent and removes (but does not destroy) its children: they become parentless and stay alive if you still reference them. `{ children: true }` recursively destroys every descendant and keeps textures, graphics contexts and text styles; it is the safe call for killing a subtree. Add `texture: true` / `textureSource: true` only for textures nothing else uses (`generateTexture` results, canvases you made). Any options object, `{ children: true }` included, also skips the `GraphicsContext` each Graphics built for itself (only a no-argument `graphics.destroy()` frees it); add `context: true` when no Graphics in the subtree shares a context. A `cacheAsTexture` cache is released by `destroy()` automatically. Do not destroy objects from inside `onRender` or other render-time callbacks; defer with `app.ticker.addOnce(() => obj.destroy())`.

`destroy(true)` is not a shorthand for `{ children: true }`: a boolean sets every option, and it is passed down to every descendant, so it equals `{ children: true, texture: true, textureSource: true, context: true, style: true }`. Every Sprite in the subtree (including `AnimatedSprite`, `TilingSprite`, `NineSliceSprite`) destroys its texture and the texture's source (a whole spritesheet atlas, or a texture from `Assets.load`), every Graphics its `GraphicsContext` (even one shared through `new Graphics(context)`), every Text its `TextStyle`. The `destroy` call raises nothing; then every render throws `Cannot read properties of null` while another object still uses a destroyed texture or context, a loaded `Spritesheet` stays cached with a dead atlas, and text sharing a destroyed style draws wrong. For textures loaded through `Assets`, destroy the nodes with `{ children: true }` and release the files with `Assets.unload(url)` once nothing draws from them.


---

## transforms

The three transform matrices, screen vs global coordinates, cumulative alpha, and scale 0. Transform properties, `pivot` vs `origin`, `toGlobal`/`toLocal` and `worldTransform` freshness are in [scene-container](03-scene-graph.md#transform-properties); matrix math is in [math](15-maths.md).

### The three matrices

```ts
container.localTransform; // from this node's own position/scale/rotation/pivot/skew
container.groupTransform; // relative to the nearest ancestor render group
container.worldTransform; // relative to the scene root; what the renderer consumes
```

Moving a render group's root leaves its descendants' `groupTransform` unchanged, which is what makes [render groups](03-scene-graph.md) cheap. All three are recomputed during a render. For a live value call `getGlobalTransform()`, `toGlobal()` or `getGlobalPosition()`.

### Global, local, and screen coordinates

- **Local**: relative to the object's parent. `container.x` / `position.set()` always operate here.
- **Global** (world): relative to the scene root. `toGlobal()`, `toLocal()` and `getGlobalPosition()` convert between local and global.
- **Screen**: relative to the canvas element's top-left in CSS pixels.

Global and screen diverge when the canvas is CSS-scaled. The event system maps pointer events into canvas space, so `event.global` is already global. For raw DOM coordinates read `event.client` (or `event.nativeEvent`); for the last pointer position outside a handler read `app.renderer.events.pointer.global`.

### Cumulative alpha

`container.alpha` is local; the product with every ancestor's alpha is `container.getGlobalAlpha()`, which walks the parents and is always current. `getGlobalAlpha(true)` reads the render-time cached value instead.

### Scale 0

`scale.set(0)` collapses the matrix, so `toLocal` and every inverse transform divide by zero. Hide with `visible = false`, or animate to a tiny non-zero scale such as `0.01`.


---

## render-groups

What `isRenderGroup` saves, when to use it, and how it differs from `cacheAsTexture`.

A render group is a `Container` whose subtree has its own instruction set, with child transforms stored relative to the group. The group's own transform, alpha and tint are applied as one matrix/color, so moving, scaling or fading the group root does not recompute any descendant.

```ts
const world = new Container({ isRenderGroup: true }); // thousands of entities
const hud = new Container({ isRenderGroup: true });
app.stage.addChild(world, hud);

world.x = 100; // updates one group matrix; the children are not recomputed
```

Flag a container with `isRenderGroup: true` at construction, or call `enableRenderGroup()` at runtime. The root container passed to `renderer.render()` (`app.stage`) is a render group already.

### What it saves

v8 recomputes transforms only for containers that changed and their descendants, with or without render groups; an unchanged subtree costs nothing per frame, so a static subtree gains nothing from a group. The win is a large subtree whose root moves as a whole: without a group, moving a container recomputes every descendant; with one, only the group matrix changes (see [transforms](03-scene-graph.md#the-three-matrices)).

Good fits: a game world with thousands of entities that scrolls or zooms, a HUD or menu that slides, scales or fades as a unit, parallax strips.

Bad fits:

- Small subtrees (a dozen children): the overhead outweighs the save.
- Structure that changes every frame (children added or removed): each structural change rebuilds the group's instruction list. Children animating their own transforms is fine.
- One group per entity, or groups nested several levels deep: each group draws separately and cannot batch with objects outside it. Use one group per subsystem (world, HUD) and keep the children plain containers.

Most scenes need no explicit groups beyond the root; add one when moving a large subtree shows up in CPU profiles.

### Render groups vs cacheAsTexture

- `cacheAsTexture()` rasterizes the subtree once and draws that texture; for subtrees that are visually static ([performance](18-performance.md#cacheastexture-for-performance)).
- `isRenderGroup` keeps normal drawing, so children stay sharp and can animate; for subtrees whose structure is stable but whose root moves.


---

## layers

`RenderLayer`: drawing an object at a different place in the render order than its scene-graph parent, including depth sorting across parents.

### Attach, don't add

An object keeps its logical parent (for transforms) and is drawn at the layer's position in the scene instead of its parent's:

```ts
const world = new Container();
const hud = new RenderLayer();
app.stage.addChild(world, hud);

const player = new Sprite(playerTexture);
world.addChild(player); // logical parent: moving world moves the player
hud.attach(player); // draw order: drawn where hud sits, on top of world

world.x = 100; // player still moves with world
```

- Membership is `layer.attach(a, b, ...)`, `layer.detach(obj)`, `layer.detachAll()`. `RenderLayer` overrides `addChild` / `removeChild` to throw; the object still needs a real `Container` parent.
- A layer and the objects it attaches must be in the same render group; otherwise an attached object renders without its correct transform composition. With `world` as `new Container({ isRenderGroup: true })`, add the layer to `world`, not to `app.stage`.

### What the layer does not control

An attached object takes its transform, `alpha`, `tint` and `visible` from its logical parent chain, never from the layer. Setting `visible = false`, `renderable = false`, `alpha`, `tint`, a position or `filters` on the `RenderLayer` itself silently does nothing to what it draws. To hide a whole layer, put it inside a plain `Container` and toggle that container (an invisible ancestor of the layer does hide its attached objects), or toggle the objects themselves:

```ts
const uiRoot = new Container();
const uiLayer = new RenderLayer();
uiRoot.addChild(uiLayer);
app.stage.addChild(uiRoot);
uiRoot.visible = false; // hides everything attached to uiLayer
```

Filters on an ancestor `Container` capture its children into a texture, but layer-attached children skip that capture: they are drawn at the layer's position. Put the filter on the attached object itself.

### Reparenting detaches

Removing an object from its scene-graph parent (`removeChild`) clears its layer attachment. Moving it to a different parent with `addChild` or `reparentChild` removes it from the old parent first, so it is silently detached too and draws at its new place in the scene graph. Re-adding does not re-attach it; call `layer.attach(obj)` again after every reparent.

### Sorted layers (depth / y-sort across parents)

```ts
import { Application, Container, Graphics, RenderLayer } from "pixi.js";

declare const app: Application;

const heroes = new Container();
const monsters = new Container();
const depthLayer = new RenderLayer({ sortableChildren: true });
app.stage.addChild(heroes, monsters, depthLayer);

const knight = heroes.addChild(new Graphics().rect(-20, -60, 40, 60).fill(0x3366cc));
const orc = monsters.addChild(new Graphics().rect(-25, -70, 50, 70).fill(0x669933));
knight.position.set(120, 180);
orc.position.set(140, 160);
depthLayer.attach(knight, orc);

// Larger y draws in front. Re-run every frame so later moves re-sort.
app.ticker.add(() => {
  for (const unit of depthLayer.renderLayerChildren) unit.zIndex = unit.y;
});
```

This replaces the tempting `sortFunction: (a, b) => a.y - b.y` plus a per-frame `sortRenderLayerChildren()`, which never re-sorts the drawing:

- Sorting is off by default (`RenderLayer` `sortableChildren` defaults to `false`); without it attached objects draw in attach order and their `zIndex` is ignored by the layer.
- The layer sorts only when its render group rebuilds the draw list. Assigning a new `zIndex` to an attached object triggers that rebuild; changing `x` / `y` does not. Drive the order through `zIndex`; the default `sortFunction` compares `zIndex`.
- A custom `sortFunction` runs only at a rebuild, so it goes stale for moving objects. `sortRenderLayerChildren()` reorders `renderLayerChildren`, but the draw order changes only at the next rebuild (attach/detach, add/remove, a `zIndex` change).
- A non-zero `zIndex` on an attached object (set before or after it is added to its logical parent) also sets `sortableChildren = true` on that parent; harmless.
- If all the objects share one parent, skip the layer: `child.zIndex = child.y` on that parent's children sorts them (see [scene-container](03-scene-graph.md#zindex-and-sortablechildren)).


---

## masking

Clipping with `container.mask` / `setMask`: which mask type each object selects, sprite-mask channels, inverse masks, and removing a mask.

```ts
const photoGroup = new Container();
photoGroup.addChild(new Sprite(await Assets.load("photo.png")));

const mask = new Graphics().circle(100, 100, 80).fill(0xffffff); // fill color is ignored; only the shape counts
photoGroup.mask = mask;
photoGroup.addChild(mask);
```

Put the mask in the masked object's coordinate space, normally as a child of the masked `Container`, so its transform tracks the subtree. A `Sprite`, `Text` or other leaf cannot hold the mask as a child (`allowChildren = false`); wrap it in a `Container` as above.

### Mask type selection

The type is picked from what you assign:

| Mask object           | Type used   | Cost                                   |
| --------------------- | ----------- | -------------------------------------- |
| Number (e.g., `0xF`)  | ColorMask   | Cheapest: bitmask on RGBA channels     |
| Graphics or Container | StencilMask | Medium: extra draws into the stencil buffer (rectangle masks too) |
| Sprite                | AlphaMask   | Most expensive: a filter pass          |

Many simultaneous sprite masks degrade performance significantly; use a `Graphics` shape when the visual result allows. `ScissorMask` is exported but not registered as a mask effect in 8.22; it cannot be selected.

### Sprite masks: channel

A sprite (alpha) mask reads the texture's **red channel** by default: high red is visible, zero red hidden. For a mask whose shape is in its transparency (a PNG with an alpha gradient), select the alpha channel:

```ts
const maskSprite = new Sprite(await Assets.load("alpha-gradient.png"));
photoGroup.setMask({ mask: maskSprite, channel: "alpha" }); // 'red' (default) | 'alpha'
photoGroup.addChild(maskSprite);
```

### Inverse masks

`setMask({ mask, inverse: true })` shows everything outside the mask shape:

```ts
const holeMask = new Graphics().circle(100, 100, 80).fill(0xffffff);
const container = new Container();
container.setMask({ mask: holeMask, inverse: true });
container.addChild(holeMask);
```

Both alpha (sprite) and stencil masks support inverse on WebGL and WebGPU. The Canvas renderer supports only `Graphics` masks, without inverse; `Sprite` and other `Container` masks are skipped with a warning.

### Removing a mask

```ts
container.mask = null;
mask.destroy();

// Sprite masks: clear the mask before destroying its texture
photoGroup.mask = null;
maskSprite.destroy({ texture: true, textureSource: true });
```

Clear with `container.mask = null`; `setMask({ mask: null })` does not work due to an internal falsy check. Remove the mask reference before destroying the mask, the masked object, or (for sprite masks) the mask's texture. A sprite mask whose texture is destroyed while still assigned renders as empty and, in debug builds, logs `[MaskFilter] The mask texture was destroyed while the mask is still in use. Remove the mask before destroying its texture.`


---

## constructor-options

The options object every `Container` subclass accepts, and the options that misbehave when passed there.

v8 constructors take one options object: prefer `new X({ ... })` over assigning properties line by line, except for values computed after construction (`app.screen` sizes), properties whose runtime change is the point, and objects received from elsewhere. v7 constructor patterns: [migration-v8](21-migration-v7-to-v8.md).

```ts
const group = new Container({
  x: 100,
  y: 200,
  scale: 2, // number or PointData; also pivot and origin
  skew: { x: 0, y: 0 }, // radians; PointData only, like position
  angle: 45, // degrees; rotation is radians
  alpha: 0.8,
  tint: 0xff8800,
  blendMode: "add",
  label: "world",
  children: [background, player],
  isRenderGroup: true,
  zIndex: 10,
  boundsArea: new Rectangle(0, 0, 800, 600),
  filters: new BlurFilter(2), // one filter or an array
  mask: maskGraphics,
  onRender: (renderer) => {},
});
```

The constructor copies every field of the options object onto the instance except `children`, `parent` and `effects`, so any public property is a valid option. Event options (`eventMode`, `hitArea`, `cursor`, `interactiveChildren`, `on*` handlers), accessibility options (`accessible*`, `tabIndex`) and culling options (`cullable`, `cullArea`, `cullableChildren`) are mixed into `ContainerOptions` too; they are documented in [events](11-events.md), [accessibility](19-accessibility.md) and [performance](18-performance.md).

### Options with non-obvious behaviour

- `children`: added with `addChild` after construction. `parent`: the new node is added to it during construction. `label` (default `null`): the key for `getChildByLabel` / `getChildrenByLabel`.
- `width` / `height`: set `scale` from the bounds measured at construction. On a plain `Container`, options are applied before `children` are added, so `new Container({ width: 200, children: [g] })` measures nothing and leaves scale at 1. The same applies to a `Graphics` drawn after construction. Call `setSize()` after the content exists. `Sprite` is the exception: it applies `width` / `height` after its texture is set.
- `boundsArea`: `getBounds()` returns this rectangle instead of measuring every child.
- `sortableChildren` (default `false`) is set automatically when a child gets a non-zero `zIndex`; see [scene-container](03-scene-graph.md#zindex-and-sortablechildren).
- `visible` / `renderable` differ in what they keep (bounds, hit testing, accessibility); see the hiding table in [scene-container](03-scene-graph.md#hiding).
- `filters` (default `null`) work on WebGL/WebGPU only. `mask` takes a `Container`, a number (`ColorMask`) or `null`, and picks stencil/alpha/color mask by type.
- `onRender` is called each render while attached to the rendered scene, even when invisible.
- `cacheAsTexture`: never pass it in options. It is a method; `cacheAsTexture: true` is a type error, and at runtime it overwrites the method with the boolean so a later `container.cacheAsTexture(false)` throws. Call `container.cacheAsTexture(true)` after construction.
- `setMask` is typed on `EffectsMixinConstructor` but is also a method, not data. Use `mask: ...` in options or call `setMask(...)` later.
- `interactive`: a convenience boolean for `eventMode`; `true` sets `eventMode = 'static'`, `false` sets `eventMode = 'passive'`.
- `effects` is silently dropped (the constructor passes `effects: true` to `assignWithIgnore`).
- `autoGarbageCollect` (advanced, from `ViewContainerOptions`): leave at its default.
