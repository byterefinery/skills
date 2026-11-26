# Sprites

## Contents

- [scene-sprite](#scene-sprite)
  - [Anchor vs pivot](#anchor-vs-pivot)
  - [Loading before creating](#loading-before-creating)
  - [Sub-textures and frames](#sub-textures-and-frames)
  - [Destroying a sprite with a shared texture](#destroying-a-sprite-with-a-shared-texture)
- [Sprite](#sprite)
  - [Canvas and video textures](#canvas-and-video-textures)
- [AnimatedSprite](#animatedsprite)
  - [Options](#options)
  - [Switching animations](#switching-animations)
  - [Replaying a one-shot](#replaying-a-one-shot)
  - [Per-frame timing from a spritesheet](#per-frame-timing-from-a-spritesheet)
  - [Factories](#factories)
- [TilingSprite](#tilingsprite)
  - [Non-power-of-two and atlas textures](#non-power-of-two-and-atlas-textures)
- [NineSliceSprite](#nineslicesprite)
  - [Options and resizing](#options-and-resizing)
  - [Texture-defined borders](#texture-defined-borders)
  - [Panel texture drawn with Graphics](#panel-texture-drawn-with-graphics)

## scene-sprite

`Sprite` and `Texture`: loading before creating, sub-textures and frames, shared-texture destroy, and which sprite variant to use.

| Variant           | Use for                                                        | Sub-page                                                 |
| ----------------- | -------------------------------------------------------------- | -------------------------------------------------------- |
| `Sprite`          | One texture at a position                                      | [sprite.md](04-sprites.md)                      |
| `AnimatedSprite`  | Frame animation from a `Texture[]` or spritesheet; a `Sprite` subclass | [animated-sprite.md](04-sprites.md)    |
| `NineSliceSprite` | Resizable panels and buttons with fixed corners (v7's `NineSlicePlane`, now an options object: `new NineSliceSprite({ texture, leftWidth, topHeight, rightWidth, bottomHeight })`) | [nineslice-sprite.md](04-sprites.md)  |
| `TilingSprite`    | Repeating or scrolling backgrounds (`tilePosition`)            | [tiling-sprite.md](04-sprites.md)        |

Thousands of identical sprites belong in a `ParticleContainer` ([scene-particle-container](08-particles.md)).

### Anchor vs pivot

`Sprite.anchor` is normalized `[0, 1]` and shifts only the texture draw origin; the position does not move. `Container.pivot` is pixel-space and shifts both the transform origin and the visual position. Center a sprite with `anchor.set(0.5)`. To rotate or scale around another local point without moving the sprite, set `origin` (pixel-space, inherited from `Container`), not `pivot`.

### Loading before creating

`Sprite.from(id)` and `Texture.from(url)` only read the Assets cache; neither fetches (v7's `Texture.from(url)` loaded the image). An unloaded key logs a "not found in the Cache" warning and the sprite draws nothing. `await Assets.load(url)` first; it returns the texture, so pass that to `new Sprite(texture)`.

The `Sprite`, `TilingSprite` and `NineSliceSprite` constructors accept only a `Texture` or an options object. A `TextureSource` (`CanvasSource`, `VideoSource`, `ImageSource`, or a source you built) type-checks as an options object and silently gives an empty sprite (`Texture.EMPTY`) sized like the source. Wrap it: `Sprite.from(source)`, `new Sprite(Texture.from(source))`, or `new Sprite({ texture: new Texture({ source }) })`.

### Sub-textures and frames

A sub-region of an image is a new `Texture` that shares the image's `TextureSource`:

```ts
import { Rectangle, Sprite, Texture } from "pixi.js";

declare const sheet: Texture;

const region = new Texture({
  source: sheet.source,
  frame: new Rectangle(0, 0, 50, 50),
  dynamic: true,
});
const sprite = new Sprite(region);

region.frame.x = 50;
region.update();

sprite.texture = new Texture({ source: sheet.source, frame: new Rectangle(50, 0, 50, 50) });
```

- `frame` is in the source's pixel units (`source.width/height`) and `texture.frame` is readonly: mutate its `x/y/width/height`; assigning a new `Rectangle` fails tsc (TS2540).
- A sprite listens for its texture's `update` event only if `texture.dynamic` was already `true` when the texture was assigned to it. Setting `dynamic = true` later, then `update()`, changes nothing on screen; there is no event, and `onViewUpdate` is protected. Pass `dynamic: true` to the constructor before handing the texture to sprites, or assign a fresh `Texture` to `sprite.texture` (always works, and keeps other users of the old texture unchanged).
- Pass `frame` at construction. A texture created without one (`new Texture({ source })`, most loaded or generated textures) resets `frame.width/height` to the full source on every `update()`.
- `texture.source.update()` re-uploads changed pixels (canvas redraws); `texture.update()` only recomputes the frame/UVs.

### Destroying a sprite with a shared texture

`sprite.destroy(true)` (or a parent's `destroy(true)`) also destroys the texture and its `TextureSource`, so every other sprite on the same spritesheet or `Assets`-loaded image makes the next render throw. Call `sprite.destroy()`, then `Assets.unload(key)` once nothing draws from it; full option rules in [scene-container](03-scene-graph.md#destroy).


---

## Sprite

`Sprite` construction, `Sprite.from`, anchor fallback, `visualBounds`, `roundPixels`, and canvas or video textures.

```ts
import { Sprite, type Texture } from "pixi.js";

declare const texture: Texture;
declare const canvas: HTMLCanvasElement;

const sprite = new Sprite({ texture, anchor: 0.5, x: 100, y: 200, tint: 0xffcc00, roundPixels: true });
const ephemeral = Sprite.from(canvas, true);
```

- `texture` defaults to `Texture.EMPTY`. `anchor` (normalized `[0, 1]`, default `0`) falls back to `texture.defaultAnchor` when unset. Anchor vs `pivot`: [scene-sprite](04-sprites.md#anchor-vs-pivot).
- `Sprite.from(source, skipCache?)` accepts a `Texture` or a `TextureSourceLike` (canvas, video, cache key; a string is a cache lookup only, see [scene-sprite](04-sprites.md#loading-before-creating)). `skipCache` keeps ephemeral textures out of the global cache.
- `roundPixels: true` snaps rendering coordinates to integers for crisp pixel art. Apply per sprite, or globally via `TextureStyle.defaultOptions.scaleMode = 'nearest'` + `roundPixels: true` on the renderer.
- `sprite.visualBounds` (`minX`, `maxX`, `minY`, `maxY`) is the rectangle the sprite actually draws in local space, accounting for anchor and texture trim. Both it and `getLocalBounds()` are anchor-aware; they differ only for trimmed textures (`getLocalBounds()` uses the untrimmed `orig` size).
- Changing the displayed region (sub-textures, `dynamic: true`, the readonly `frame`, `texture.update()`): [scene-sprite](04-sprites.md#sub-textures-and-frames).

### Canvas and video textures

Pixels drawn into a canvas after the texture was uploaded do not appear until `texture.source.update()`:

```ts
import { Sprite, Texture } from "pixi.js";

const canvas = document.createElement("canvas");
const sprite = new Sprite(Texture.from(canvas));

canvas.getContext("2d")!.fillRect(0, 0, 10, 10);
sprite.texture.source.update();
```

A video is loaded with `await Assets.load('clip.mp4')` and the returned texture passed to `new Sprite(texture)`; on mobile, start playback from a user gesture to satisfy autoplay policies ([video](10-assets.md)).


---

## AnimatedSprite

`AnimatedSprite` frame animation: options and their defaults, speed units, swapping animations, one-shot replay, ticker, per-frame timing and the cache-only factories.

```ts
import { AnimatedSprite, Assets, type Spritesheet } from "pixi.js";

const sheet = await Assets.load<Spritesheet>("character.json");

const walk = new AnimatedSprite({
  textures: sheet.animations["walk"],
  animationSpeed: 12 / 60,
  autoPlay: true,
  anchor: 0.5,
});
```

Load the spritesheet first and take frames from `sheet.animations[key]`. `Texture.from(name)` on an unloaded frame returns `undefined` (with a "not found in the Cache" warning) and the `AnimatedSprite` constructor throws "Cannot read properties of undefined (reading 'texture')"; unlike `Sprite`, it does not fall back to `Texture.EMPTY`.

### Options

Two constructor forms: `new AnimatedSprite(frames, autoUpdate?)` and `new AnimatedSprite({ textures, ...options })`. The options form also takes every `SpriteOptions` field except `texture`.

| Option           | Default | Notes |
| ---------------- | ------- | ----- |
| `textures`       | —       | Required. A `Texture[]`, or `FrameObject[]` (`{ texture, time }`, `time` in **milliseconds**; `0.1` flips frames almost instantly). |
| `animationSpeed` | `1`     | For `Texture[]`: frames advanced per 60 fps tick, scaled by `ticker.deltaTime`. `1` is 60 frames per second, far too fast for most art; N fps is `N / 60` (12 fps → `0.2`). For `FrameObject[]`: a multiplier on each frame's `time`. Negative reverses. |
| `autoPlay`       | `false` | Without it or a `play()` call, only the first frame shows. |
| `autoUpdate`     | `true`  | Plays on `Ticker.shared`, not `app.ticker`, so `app.ticker.stop()` does not pause it. Set `false` and call `sprite.update(ticker)` from `app.ticker`, a custom ticker or game logic. |
| `loop`           | `true`  | `false` for one-shots; then `onComplete` fires at the end. |
| `onComplete`, `onFrameChange(currentFrame)`, `onLoop` | `null` | End of a non-looping run; every displayed-texture change; each wrap of a looping run. |
| `updateAnchor`   | `false` | Copies the current texture's `defaultAnchor` onto the sprite's anchor on every frame change (per-frame pivots, e.g. pinning to a foot), overriding any anchor you set. |

`play()`, `stop()`, `gotoAndStop(i)`, `gotoAndPlay(i)`; `totalFrames` and `playing` are readonly. The `currentFrame` setter throws outside `[0, totalFrames - 1]`, so the last frame is `totalFrames - 1`.

### Switching animations

```ts
import { AnimatedSprite, Spritesheet } from "pixi.js";

declare const hero: AnimatedSprite;
declare const sheet: Spritesheet;

hero.textures = sheet.animations["run"];
hero.play();
```

Assigning `textures` stops playback and jumps to frame 0, even when `autoPlay` was set; the sprite freezes on the first frame of the new animation unless you call `play()` after each swap.

### Replaying a one-shot

A finished one-shot stays on its last frame, and `play()` resumes from there: it only re-fires `onComplete` on the next tick without replaying. Replay with `gotoAndPlay(0)` (`GifSprite.play()`, by contrast, does rewind). When a pooled effect is done, `destroy()` it without `true`: `destroy(true)` destroys every frame texture and the shared atlas (see [scene-container](03-scene-graph.md#destroy)).

### Per-frame timing from a spritesheet

Spritesheets loaded via `Assets.load` expose per-frame `duration` values at `sheet.data.frames[key].duration` (Aseprite exports carry it; the `SpritesheetFrameData` type does not declare it). Build a `FrameObject[]` from them for pre-authored timing:

```ts
import { AnimatedSprite, Assets, Texture, type FrameObject } from "pixi.js";

const sheet = await Assets.load("0123456789.json");
const frames: FrameObject[] = [];
for (let i = 0; i < 10; i++) {
  const key = `0123456789 ${i}.ase`;
  frames.push({ texture: Texture.from(key), time: sheet.data.frames[key].duration });
}
const sprite = new AnimatedSprite(frames);
```

### Factories

- `AnimatedSprite.fromFrames(aliases)` builds textures via `Texture.from` from cached frame names; the spritesheet must already be loaded.
- `AnimatedSprite.fromImages(urls)` does the same for image URLs (`Texture.from(url)` per entry). It fetches nothing: `await Assets.load(urls)` first, or the constructor throws "Cannot read properties of undefined (reading 'texture')".


---

## TilingSprite

`TilingSprite` options (`tilePosition`, `tileScale`, `tileRotation`, `applyAnchorToTexture`), cache-only `from`, and how it tiles non-power-of-two and atlas textures.

```ts
import { Application, Assets, TilingSprite, type Texture } from "pixi.js";

declare const app: Application;

const texture = await Assets.load<Texture>("grass.png");
const bg = new TilingSprite({ texture, width: app.screen.width, height: app.screen.height });
app.stage.addChild(bg);

app.ticker.add((ticker) => {
  bg.tilePosition.x -= 1 * ticker.deltaTime;
});
```

Pass a loaded texture: the default is `Texture.EMPTY` (from `TilingSprite.defaultOptions`), so a TilingSprite without one draws nothing. `TilingSprite.from(source, options?)` takes a `Texture` or a cached alias; the alias form reads the Assets cache only, so `await Assets.load('pattern.png')` first or the sprite draws `Texture.EMPTY`.

| Option                 | Default          | Notes |
| ---------------------- | ---------------- | ----- |
| `width`, `height`      | `texture.width` / `texture.height` | The visible tiling region. Resize with these or `setSize(w, h)`. |
| `tilePosition`         | `{ x: 0, y: 0 }` | Offset of the pattern inside the region; animate it to scroll. |
| `tileScale`            | `{ x: 1, y: 1 }` | Scales the tiles only. Use it to make tiles larger; `scale` stretches the sprite region too. |
| `tileRotation`         | `0`              | Radians, applied to the texture before tiling; the region stays axis-aligned. |
| `anchor`               | `0`              | Origin of the region, not of the pattern. |
| `applyAnchorToTexture` | `false`          | By default the region's top-left always maps to texture `(0, 0)`; `true` shifts the texture origin by the anchor, so the pattern stays centered on the anchor as it scales. |
| `roundPixels`          | `false`          | Snaps the sprite's position, not the tile pattern. |

`TilingSprite.defaultOptions` is merged with every constructor's options. `containsPoint` tests the anchor-offset tiling region, so a TilingSprite works as a clickable background.

### Non-power-of-two and atlas textures

Resizing textures to power-of-two is unnecessary in v8. Non-power-of-two textures and spritesheet sub-frames tile correctly: `TilingSprite` sets the shared source's `addressMode` to `'repeat'` and, where hardware wrapping is unavailable (WebGL1 NPOT, sub-frames), wraps in its own shader. The only cost is that such a sprite no longer batches. Because the source's `addressMode` is changed, other sprites drawing the same source also sample with `repeat`.


---

## NineSliceSprite

`NineSliceSprite` panels: border options and fallbacks, resizing with `width`/`height`, texture-defined borders, and a panel texture baked from `Graphics`.

```ts
import { Assets, NineSliceSprite, type Texture } from "pixi.js";

const texture = await Assets.load<Texture>("panel.png");

const panel = new NineSliceSprite({
  texture,
  leftWidth: 20,
  topHeight: 20,
  rightWidth: 20,
  bottomHeight: 20,
  width: 400,
  height: 200,
});
panel.setSize(600, 300);
```

### Options and resizing

| Option | Default | Notes |
| ------ | ------- | ----- |
| `leftWidth`, `topHeight`, `rightWidth`, `bottomHeight` | `10` | Unscaled border sizes; fall back to `texture.defaultBorders` when not passed. Mutable at runtime; the geometry rebuilds on the next render. |
| `width`, `height` | `texture.width` / `texture.height` (else `100`) | Size of the stretched panel; modifies vertices, not UVs. |
| `anchor`, `roundPixels` | `0`, `false` | As on `Sprite`. `roundPixels` avoids sub-pixel seams at slice boundaries in pixel-art UI. |

Resize with `width`/`height` or `setSize(w, h)`, never `scale`: `scale` stretches the whole geometry, corners included. The corners stay fixed while the panel is at least `leftWidth + rightWidth` wide and `topHeight + bottomHeight` tall; below that, all borders shrink proportionally.

Keep each pair of opposing borders smaller than the texture dimension. If `leftWidth + rightWidth >= texture.width` (or `topHeight + bottomHeight >= texture.height`), no texture pixels are left for the center strip, so it is filled by stretching the seam between the two borders instead of the texture's middle.

`originalWidth` / `originalHeight` are readonly getters returning `texture.width` / `texture.height`, e.g. `panel.setSize(panel.originalWidth, panel.originalHeight)` to reset.

`NineSliceSprite.defaultOptions` is mutable, but only its `texture` field is read as a fallback. Border defaults come from `texture.defaultBorders` (per texture) or `NineSliceGeometry.defaultOptions` (global), and size defaults fall back to `texture.width` / `texture.height` or `NineSliceGeometry.defaultOptions.width` / `.height`.

### Texture-defined borders

```ts
import { NineSliceSprite, Texture, type TextureSource } from "pixi.js";

declare const baseSource: TextureSource;

const texture = new Texture({
  source: baseSource,
  defaultBorders: { left: 15, top: 15, right: 15, bottom: 15 },
});
const panel = new NineSliceSprite({ texture, width: 400, height: 200 });
```

`defaultBorders` is a readonly `Texture` property: pass it to the `Texture` constructor, or set `borders` on the spritesheet frame data so `Assets.load` bakes it in. The sprite picks it up when no explicit border values are passed.

### Panel texture drawn with Graphics

```ts
import { Application, Graphics, NineSliceSprite, Rectangle } from "pixi.js";

declare const app: Application;

const shape = new Graphics()
  .roundRect(0, 0, 48, 48, 12)
  .fill(0x223344)
  .stroke({ width: 2, color: 0xffffff, alignment: 1 });
const texture = app.renderer.generateTexture({ target: shape, frame: new Rectangle(0, 0, 48, 48) });
shape.destroy();

const panel = new NineSliceSprite({
  texture,
  leftWidth: 14,
  topHeight: 14,
  rightWidth: 14,
  bottomHeight: 14,
  width: 300,
  height: 120,
});
app.stage.addChild(panel);
```

Make the borders at least the corner radius plus the stroke width. `frame` must be a `Rectangle`; a plain `{ x, y, width, height }` throws `copyTo is not a function`. `alignment: 1` keeps the stroke inside the frame.
