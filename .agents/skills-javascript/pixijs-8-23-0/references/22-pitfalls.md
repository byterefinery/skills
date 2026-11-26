# Pitfalls that fail silently

Every line is the fix; its link owns the rule and the code. These run without errors and draw the wrong thing, and a Vite build doesn't type-check, so run `npx tsc --noEmit` to catch wrong option names. Read this file before or while writing PixiJS code, and check each group against the feature you built.

Each line is the fix; its link owns the rule and the code. These run without errors and draw the wrong thing, and a Vite build doesn't type-check, so run `npx tsc --noEmit` to catch wrong option names.

**App setup and the frame loop**
- `const app = new Application(); await app.init({ ... })`. Constructor options are ignored; until `init` resolves `app.renderer` is `undefined` and `app.canvas`/`app.screen` throw. [application](01-application.md#lifecycle-construct-init-render-destroy)
- Top-level `await` fails `vite build` on Vite 6 and older; wrap init in an async IIFE. [create](20-environments-builds.md#top-level-await-appinit-in-vite-production-builds)
- With `resizeTo`, lay out in `app.renderer.on('resize', (w, h) => ...)`; your own `window` resize listener reads the old `app.screen`. An element target also needs `new ResizeObserver(() => app.queueResize())`. [application](01-application.md#resizeplugin)
- Ticker callbacks receive the `Ticker`: `app.ticker.add((t) => (s.x += 2 * t.deltaTime))`. `deltaTime` is ~1 per 60 fps frame, `deltaMS` is milliseconds. [ticker](17-ticker.md#time-units)
- `app.ticker.update()` already renders, even with `autoStart: false`; skip the extra `app.render()`. [ticker](17-ticker.md#app-lifecycle-and-manual-rendering)
- Per-object frame logic: `obj.onRender = () => { ... }` (replaces v7 `updateTransform` overrides); it also runs while the object is invisible. Name subclass methods anything but `_onRender`. [ticker](17-ticker.md#per-object-onrender-hook)
- Read canvas pixels from a listener at `UPDATE_PRIORITY.UTILITY`, which runs after the render. [ticker](17-ticker.md#frame-order)

**Loading assets and textures**
- `await Assets.init({ basePath, manifest })` before the first `load`, `loadBundle` or `backgroundLoad`; a later `init` is dropped. [assets](10-assets.md#init-order)
- `Assets.load([a, b])` resolves an object keyed by URL or alias: read `res[a]`. [assets](10-assets.md#load-results-and-keys)
- A URL with no file extension (`?id=`, `blob:`, API route) needs `Assets.load({ src, parser: 'texture' })`; without it the result is `null` with only a warning. Audio files have no loader and also resolve `null`; play sound with `@pixi/sound` or `HTMLAudioElement`. [assets](10-assets.md#forcing-a-parser-with-parser)
- `Texture.from(url)` and `Sprite.from(url)` read the cache only (v7 fetched): `await Assets.load(url)` first. [scene-sprite](04-sprites.md#loading-before-creating)
- Wrap a `TextureSource` (`CanvasSource`, `texture.source`): `Sprite.from(source)` or `new Sprite(Texture.from(source))`; `new Sprite(source)` draws nothing. [scene-sprite](04-sprites.md#loading-before-creating)
- Show another region with `sprite.texture = new Texture({ source, frame: new Rectangle(...) })`, or create the texture with `dynamic: true` and call `texture.update()`. [scene-sprite](04-sprites.md#sub-textures-and-frames)
- After drawing into a source canvas, call `texture.source.update()`. [sprite](04-sprites.md#canvas-and-video-textures)
- Per-asset `data` (`scaleMode`, `resolution`) applies on the first load of a `src` only; set `texture.source.scaleMode` on the result instead. [assets](10-assets.md#data-per-asset)

**Sprites and animation**
- `AnimatedSprite`: `animationSpeed` is frames per 60 fps tick (12 fps is `0.2`), and it needs `autoPlay: true` or `play()`. It runs on `Ticker.shared`, so `app.ticker.stop()` doesn't pause it. [animated-sprite](04-sprites.md#options)
- Call `play()` after each `anim.textures = ...` swap; replay a finished one-shot with `gotoAndPlay(0)`. [animated-sprite](04-sprites.md#switching-animations)
- Rotate or scale about a point with `origin`; `pivot` also moves the object, and `anchor` (0-1) shifts only the texture. [scene-sprite](04-sprites.md#anchor-vs-pivot)

**Graphics**
- Shape first, then style: `new Graphics().rect(0, 0, 100, 50).fill(0xff0000).stroke({ width: 2, color: 0x000000 })`. `beginFill`, `drawRect` and `lineStyle` are v7. [scene-graphics](05-graphics.md#shape-then-style)
- `FillGradient`: options object, every colour stop set before the first draw, `textureSpace: 'global'` for pixel coordinates (the default `'local'` is 0-1 across the shape). [scene-graphics](05-graphics.md#gradients-and-patterns)
- Draw-time transforms apply in call order, the reverse of Canvas 2D: `rotateTransform(a).translateTransform(x, y)`. [scene-graphics](05-graphics.md#draw-time-transforms)
- Stroke `alignment` is `1` inside, `0` outside (inverted from v7). [scene-graphics](05-graphics.md#strokes)
- Animate a stable `Graphics` by its transform; `clear()` and redraw every frame re-tessellates. [scene-graphics](05-graphics.md#keep-geometry-stable)

**Drawing into textures (paint, eraser, scratch-off, fog of war, baking)**
- The render root's own `blendMode` is ignored: put an `'erase'` brush inside a plain `Container` and pass the wrapper to `renderer.render({ container: wrapper, target, clear: false })`. `clear: false` keeps earlier strokes. [blend-modes](13-blend-modes.md#inheritance-and-render-roots)
- `'erase'` clears everything under it in the same target, background included; give the erasable layer its own `RenderTexture` and erase into that. [blend-modes](13-blend-modes.md#erase-and-paint-out-layers)
- Brush coordinates are texture pixels: `sprite.toLocal(e.global)` plus the anchor offset. [blend-modes](13-blend-modes.md#erase-and-paint-out-layers)
- `generateTexture({ target, frame: new Rectangle(...) })`: `frame` is a real `Rectangle` (a plain object throws `copyTo is not a function`), and the capture ignores the target's own position, scale and rotation. [renderers](02-renderers.md#generating-a-texture-from-a-container)
- A `cacheAsTexture(true)` container shows changes to its children only after `updateCacheTexture()`. [performance](18-performance.md#cacheastexture-for-performance)

**Particles**
- Fill a `ParticleContainer` with `addParticle(...particles)`; the `particles` option draws nothing until `update()`. Type it `new ParticleContainer<Particle>(...)` to reach `tint` and `alpha`. [scene-particle-container](08-particles.md#the-particles-option-draws-nothing-on-its-own)
- Mark every property you change per frame in `dynamicProperties`: `position`, `rotation`, `vertex` (scale, anchor), `color` (tint, alpha), `uvs` (texture). A static one changes only after `update()`, and v7's `tint`/`scale` keys are ignored. [scene-particle-container](08-particles.md#dynamicproperties-and-update)
- All particles share one texture source (frames of one atlas). Give the container `boundsArea` (its bounds are empty, so culling and filters skip it) and `hitArea` plus `eventMode` for pointer events. [scene-particle-container](08-particles.md#bounds-and-hit-testing)

**Filters and blend modes**
- Assign a new array to change filters: `c.filters = [...(c.filters ?? []), blur]`. [filters](12-filters.md)
- Custom GLSL: `Filter.from({ gl: { vertex: defaultFilterVert, fragment }, resources })`. In the fragment sample `uTexture`, get 0-1 coordinates from `vTextureCoord * uInputSize.xy / uOutputFrame.zw` (both `highp`), and keep colour premultiplied (invert with `vec4(c.a - c.rgb, c.a)`). [filters](12-filters.md#custom-filter)
- On the WebGPU renderer (`preference: 'webgpu'`) every filter needs a `gpu` program too, or all filters on that container are skipped. The Canvas renderer skips filters. [filters](12-filters.md#webgpu-needs-a-wgsl-program-too)
- Effects that reach past the shape (glow, wave, outline) need `padding`; a full-screen stage filter needs `app.stage.filterArea = app.screen`; use `resolution: 'inherit'` on a high-DPI renderer. [filters](12-filters.md#filter-options)
- `DisplacementFilter` takes a `Sprite` that is on the stage; animate the distortion by moving that sprite (map texture `addressMode = 'repeat'`). A `TilingSprite`'s `tilePosition` is never read. [filters](12-filters.md#built-in-filters)
- A filtered container composites with its last filter's `blendMode`: `new BlurFilter({ strength: 8, blendMode: 'add' })`. [blend-modes](13-blend-modes.md#filtered-containers)
- Modes beyond `normal`/`add`/`multiply`/`screen`/`erase`/`min`/`max` need `import 'pixi.js/advanced-blend-modes'` and, on WebGL, `app.init({ useBackBuffer: true })`. [blend-modes](13-blend-modes.md#advanced-blend-modes)

**Text**
- `new Text({ text, style: { fill: 0xffffff } })`: the default fill is black, invisible on the default black background. [scene-text](06-text.md)
- Strings that change every frame (score, timer, FPS) go in `BitmapText`; each `Text` change redraws a canvas and re-uploads it. [scene-text](06-text.md#update-cost-comparison)
- Load web fonts with `await Assets.load({ src, data: { family } })` before creating text; `HTMLText` sees only fonts loaded this way. [html-text](06-text.md#fonts-must-come-through-assets)
- Raise `style.padding` when a stroke or drop shadow is clipped. [text](06-text.md#textstyle)

**Input**
- Give every listening object `eventMode = 'static'` (the default `'passive'` never fires its own listeners) and `cursor = 'pointer'` (v7 `buttonMode`). [events](11-events.md#eventmode)
- Clicks on empty canvas: `app.stage.eventMode = 'static'` and `app.stage.hitArea = app.screen`. A plain `Container` is hit only on its children; give it a `hitArea` to cover the gaps. [events](11-events.md#hit-testing)
- `visible = false` and `renderable = false` remove an object from hit testing; an invisible target uses `alpha = 0` or a `hitArea`. [scene-container](03-scene-graph.md#hiding)
- Buttons listen to `pointertap` (`click` is mouse only, `tap` touch only); a double click is `e.detail === 2`. [events](11-events.md#event-types)
- Drag with `globalpointermove` (plain `pointermove` fires only over the object), end on `pointerup` and `pointerupoutside`, convert with `parent.toLocal(e.global)`, and keep points with `p.copyFrom(e.global)` (event objects are reused). [events](11-events.md#drag)
- Stop page scroll with a native `app.canvas.addEventListener('wheel', (e) => e.preventDefault(), { passive: false })`. [events](11-events.md#wheel)

**Scene order, coordinates and masks**
- `zIndex` orders siblings only and sorts at the next render; call `parent.sortChildren()` before reading `children`. [scene-container](03-scene-graph.md#zindex-and-sortablechildren)
- Depth-sort across parents with `new RenderLayer({ sortableChildren: true })` and `layer.attach(obj)`; attach again after reparenting, and hide or move the objects themselves (the layer's own `visible`, `alpha` and position do nothing). [layers](03-scene-graph.md)
- Add a mask as a child of the masked `Container`; a `Sprite` mask reads the red channel unless `setMask({ mask, channel: 'alpha' })`. [masking](03-scene-graph.md)
- Map pointers into rotated or scaled containers with `container.toLocal(e.global)`; `getBounds()` returns `Bounds`, so hit-test with `getBounds().rectangle.contains(x, y)`. [scene-container](03-scene-graph.md#bounds-and-coordinate-conversion)
- `Matrix` methods apply in call order and `a.append(b)` applies `b` first; Container-style is `scale().rotate().translate()`, applied with `setFromMatrix`. [math](15-maths.md#matrix)
- Copy points with `copyFrom(p)` or `set(x, y)`; `pixi.js/math-extras` methods return a new point, so update in place with `pos.add(v, pos)`. [math](15-maths.md#point-and-observablepoint)
- `Color` reads a plain `number[]` as 0-1 (`[180, 60, 90]` is white); pass 0-255 as a `Uint8Array`, and alpha as `'#rrggbbaa'` (`0xRRGGBBAA` throws). [color](16-color.md#input-ranges)

**Teardown**
- Destroy a subtree with `destroy({ children: true })` and free loaded files with `Assets.unload(key)`. `destroy(true)` also destroys shared textures, atlases and `GraphicsContext`s, and every later render of another user throws. [scene-container](03-scene-graph.md#destroy)
- Call `app.destroy()` after `init` resolves (in React effects, chain it on the init promise); pass `releaseGlobalResources: true` when re-creating an app in the same tab. [application](01-application.md#lifecycle-construct-init-render-destroy)
- Destroy textures you create (`generateTexture`, canvases) with `texture.destroy(true)`; defer a destroy from inside `onRender` with `app.ticker.addOnce(() => obj.destroy())`. [performance](18-performance.md#teardown-and-memory), [scene-container](03-scene-graph.md#destroy)

**Renderers and builds**
- `Application` picks WebGL unless `preference: 'webgpu'`. The Canvas renderer skips filters and draws nothing for `Mesh`. [renderers](02-renderers.md#what-the-canvas-renderer-skips)
- `pixi.js/math-extras`, `pixi.js/prepare`, `pixi.js/gif` and `pixi.js/advanced-blend-modes` work only after a side-effect import; with `skipExtensionImports: true`, also import `pixi.js/events`, `pixi.js/filters`, `pixi.js/accessibility` and `pixi.js/dom`. [environments](20-environments-builds.md#custom-builds)
