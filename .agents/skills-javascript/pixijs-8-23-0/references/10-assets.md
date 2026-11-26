# Assets

## Contents

- [assets](#assets-1)
  - [Init order](#init-order)
  - [Load results and keys](#load-results-and-keys)
  - [Supported file types](#supported-file-types)
  - [Forcing a parser with `parser`](#forcing-a-parser-with-parser)
  - [Load options and error handling](#load-options-and-error-handling)
  - [Init options, preferences and fetch routing](#init-options-preferences-and-fetch-routing)
  - [Sub-pages](#sub-pages)
- [Bundles](#bundles)
  - [Unloading](#unloading)
- [Manifests](#manifests)
- [Spritesheet](#spritesheet)
  - [JSON fields](#json-fields)
  - [`meta.scale` sets the resolution](#metascale-sets-the-resolution)
  - [Hand-built sheets](#hand-built-sheets)
  - [Cleanup](#cleanup)
- [Fonts](#fonts)
  - [Web fonts](#web-fonts)
  - [Bitmap fonts](#bitmap-fonts)
- [Video textures](#video-textures)
  - [Sound and autoplay](#sound-and-autoplay)
  - [CORS](#cors)
- [SVG loading](#svg-loading)
- [Compressed textures](#compressed-textures)
- [Resolution and format detection](#resolution-and-format-detection)
- [Progress tracking](#progress-tracking)
- [Caching](#caching)
  - [Unloading](#unloading-1)
- [Background loading](#background-loading)

## assets

The `Assets` singleton: init order, load result shapes, parsers and extension-less URLs, `LoadOptions` and errors, per-asset `data`, preferences and fetch routing, and which sub-page covers each format.

### Init order

```ts
import { Application, Assets, Sprite, Texture } from "pixi.js";

declare const app: Application;

await Assets.init({ basePath: "/static/", manifest: "manifest.json" });

const texture = await Assets.load<Texture>("bunny.png");
app.stage.addChild(new Sprite(texture));

const loaded = await Assets.load<Texture>(["hero.png", "enemy.png"]);
const hero = loaded["hero.png"];

Assets.add({ alias: "logo", src: "logo.webp" });
await Assets.load("logo");
const logo = new Sprite(Assets.get("logo"));
```

`Assets.init()` is optional, runs once, and must be awaited before any `load`, `loadBundle`, `backgroundLoad` or `unload`, because those call `init()` themselves when it has not run. A later `Assets.init({...})` only logs "AssetManager already initialized" and drops every option: `basePath` is not applied and the manifest's bundles are never registered (`loadBundle` of an unregistered name resolves `undefined` without an error). Put `basePath`, `manifest` and preferences in that one first call; afterwards change preferences with `Assets.setPreferences` and add bundles with `Assets.addBundle`.

### Load results and keys

- `Assets.load([...])` resolves to an object keyed by each requested URL or alias, never an array: `const [a, b] = await Assets.load([...])` fails tsc (TS2488) and throws "is not iterable". Read entries by key, or use `Object.values(result)`.
- A bare URL is cached under that exact string only. Register a short name with `Assets.add({ alias: "hero", src: "hero.png" })` before loading if you want `Assets.get("hero")`. v7's positional `Assets.add("bunny", "bunny.png")` was removed; use the options object.
- `Texture.from(url)` and `Sprite.from(url)` no longer fetch in v8; they read the cache that `Assets.load` fills ([scene-sprite](04-sprites.md#loading-before-creating)).
- `Assets.load()` caches until you unload. Between levels or screens, release with `Assets.unload` / `Assets.unloadBundle` ([caching](10-assets.md)).

### Supported file types

| Type                | Extensions                                                       | Parser ID                     | Loader | Notes |
| ------------------- | ---------------------------------------------------------------- | ----------------------------- | ------ | ----- |
| Textures            | `.png`, `.jpg`, `.jpeg`, `.webp`, `.avif`                        | `texture`                     | `loadTextures` | |
| SVG                 | `.svg`                                                           | `svg`                         | `loadSvg` | Texture or `GraphicsContext` ([svg](10-assets.md)) |
| Video textures      | `.mp4`, `.m4v`, `.webm`, `.ogg`, `.ogv`, `.h264`, `.avi`, `.mov` | `video`                       | `loadVideoTextures` | [video](10-assets.md) |
| Sprite sheets       | `.json` (Spritesheet format)                                     | `spritesheet`                 | `spritesheetAsset` | [spritesheet](10-assets.md) |
| Bitmap fonts        | `.fnt`, `.xml`                                                   | `bitmap-font`                 | `loadBitmapFont` | Registered by default ([fonts](10-assets.md)) |
| Web fonts           | `.ttf`, `.otf`, `.woff`, `.woff2`                                | `web-font`                    | `loadWebFont` | [fonts](10-assets.md) |
| JSON                | `.json`                                                          | `json`                        | `loadJson` | |
| Text                | `.txt`                                                           | `text`                        | `loadTxt` | |
| Compressed textures | `.basis`, `.dds`, `.ktx`, `.ktx2`                                | `basis`, `dds`, `ktx`, `ktx2` | | Each needs its side-effect import ([compressed-textures](10-assets.md)) |
| Animated GIFs       | `.gif`                                                           | `gif`                         | | Needs `import 'pixi.js/gif'`; returns a `GifSource` ([scene-gif](09-dom-gif-html.md)) |

There is no audio loader: `.mp3`/`.wav`/`.ogg` audio resolves `null` (`.ogg` is tried as video). Use `@pixi/sound` or another audio library.

### Forcing a parser with `parser`

The loader picks a parser by testing the URL string only: the extension of the path before `?` (`photo.png?v=3` works), or the MIME type of a `data:` URL. The server's `Content-Type` is never consulted. A URL no parser recognises (`https://cdn.example.com/image?id=42`, any `blob:` URL from `URL.createObjectURL`, `/api/assets/hero`, a content-hashed path with no suffix) is not fetched at all: `Assets.load` logs `[Assets] <url> could not be loaded as we don't know how to parse it, ensure the correct parser has been added` and resolves `null`. It does not throw and `onError` does not fire, so the failure surfaces later as a null texture. Set the top-level `parser` field (beside `src` and `data`, not inside `data`) to a Parser ID from the table:

```ts
import { Assets, Texture } from "pixi.js";

declare const blob: Blob;

const texture = await Assets.load<Texture>({ src: URL.createObjectURL(blob), parser: "texture" });

const config = await Assets.load({ alias: "config", src: "https://api.example.com/v1/config", parser: "json" });

const clip = await Assets.load<Texture>({
  src: "https://cdn.example.com/stream/xyz",
  parser: "video",
  data: { mime: "video/mp4" },
});
```

A URL with a recognised extension needs no `parser`. v7's `loadParser` field still works with the loader's name (`loadParser: "loadTextures"`) but logs a deprecation warning; use `parser: "texture"`.

### Load options and error handling

Two separate option sets:

1. **`LoadOptions`**: the second argument to `Assets.load` only. Controls error recovery, retries and progress across the whole call. `Assets.loadBundle(ids, onProgress)` takes only a progress function; passing an options object there throws "onProgress is not a function". Set bundle strategy and retries through `Assets.init({ loadOptions })` or `Loader.defaultOptions`.
2. **`data`**: a field on each asset descriptor, forwarded to that asset's parser.

```ts
import { Assets } from "pixi.js";

declare function updateBar(p: number): void;

await Assets.load(["hero.png", "enemy.png"], {
  onProgress: (p) => updateBar(p),
  onError: (err, url) => {
    const src = typeof url === "string" ? url : url.src;
    console.warn("failed:", src, err);
  },
  strategy: "retry",
  retryCount: 3,
  retryDelay: 250,
});
```

- `onProgress(progress)`: `[0, 1]` as assets in the call complete.
- `onError(error, url)`: typed `string | ResolvedAsset`, but the loader always passes the `ResolvedAsset`; the guard above keeps TypeScript happy.
- `strategy: 'throw' | 'skip' | 'retry'`, default `'throw'`. `'skip'` calls `onError` once and resolves without the failed asset (`undefined` for a single URL, key missing from the record for an array). `'retry'` reattempts the failed ones.
- `retryCount`, default `3`: retries per asset under `'retry'`, so an asset that keeps failing is attempted `retryCount + 1` times. `onError` fires after **every** failed attempt (not once at the end), then the call rejects as with `'throw'`. Count failures yourself to report only the final one.
- `retryDelay`, default `250` ms between retries.

Global defaults live on `Loader.defaultOptions`, or pass `loadOptions` to `Assets.init()`.

#### `data` per asset

| Asset type         | `data` shape | Key options |
| ------------------ | ------------ | ----------- |
| Texture (image)    | `TextureSourceOptions` | `resolution`, `scaleMode`, `alphaMode`, `autoGenerateMipmaps`, `antialias`, `addressMode` |
| SVG                | `{ parseAsGraphicsContext?, resolution? }` | Graphics mode; sharper raster |
| Video              | `VideoSourceOptions` | `autoPlay`, `loop`, `muted`, `playsinline`, `preload`, `updateFPS`, `crossorigin`, `mime` |
| Web font           | `LoadFontData` | `family`, `weights`, `style`, `display`, `unicodeRange`, `featureSettings` |
| Bitmap font        | none | Distance-field detection sets scale mode and mipmaps |
| Spritesheet        | `{ texture?, imageFilename?, ignoreMultiPack?, textureOptions?, cachePrefix? }` | `textureOptions` forwards `TextureSourceOptions` (e.g. `scaleMode`) to the atlas image; `texture` skips the image load; `imageFilename` overrides the referenced image; `ignoreMultiPack` skips multi-pack follow-ups; `cachePrefix` namespaces frame keys |
| GIF                | `GifBufferOptions` | `fps`, `scaleMode`, `resolution`, `autoGenerateMipmaps` |
| Compressed texture | `TextureSourceOptions` | `scaleMode`, `addressMode`, `autoGenerateMipmaps` |
| JSON / Text        | none | Returned as-is |

`data` applies only to the first load of a `src`. A later `Assets.load` of the same URL, under any alias and with different `data`, returns the cached asset built with the first options. Change a loaded texture's sampling on the result (`texture.source.scaleMode = "nearest"`), or `await Assets.unload(src)` before loading it with new `data`. Manifest and bundle entries carry `data` the same way.

### Init options, preferences and fetch routing

`Assets.init(options)` accepts, alongside `basePath`, `manifest` and `texturePreference` ([resolution](10-assets.md)):

- `defaultSearchParams`: string or `Record<string, any>` appended to every resolved URL (cache busting).
- `skipDetections: boolean`: skip browser format detection and treat every registered format (avif, webp, ...) as supported. Set `texturePreference.format` to the formats you actually ship, or the resolver may pick avif on a browser that can't decode it.
- `bundleIdentifier: BundleIdentifierOptions`: customise how bundle keys resolve so the same alias can live in several bundles.
- `loadOptions: Partial<LoadOptions>`: default `strategy`, `retryCount`, `retryDelay` and callbacks for every later `Assets.load`.
- `preferences: Partial<AssetsPreferences>`: `crossOrigin`, `preferWorkers`, `preferCreateImageBitmap`, `parseAsGraphicsContext`.

After init, `Assets.setPreferences({ crossOrigin: "anonymous", preferCreateImageBitmap: false })` pushes new preferences to every parser that supports them. `Assets.detections` lists the registered `FormatDetectionParser`s. `Assets.reset()` fully resets resolver, loader and cache; it is meant for tests, so a fresh `Assets.init` can run.

How an image (png/jpg/webp/avif) is fetched depends on these preferences:

| Preferences | Image request goes through |
| --- | --- |
| defaults (`preferWorkers: true`, `preferCreateImageBitmap: true`) | a Web Worker's own global `fetch`; `DOMAdapter.fetch`, a custom adapter and a patched `window.fetch` never see it |
| `preferWorkers: false` | `DOMAdapter.get().fetch(url)` on the main thread, then `createImageBitmap` |
| `preferCreateImageBitmap: false` | an `<img>` from `DOMAdapter.get().createImage()`, no fetch; `crossOrigin` applies only here |

To route image loads through a custom `DOMAdapter.fetch` (auth headers, request logging, offline cache), set `preferWorkers: false`. JSON, text, SVG, bitmap-font and GIF loads always use `DOMAdapter.get().fetch`.

### Sub-pages

| Read when                                                   | Sub-page |
| ----------------------------------------------------------- | -------- |
| Grouping assets per level or screen (`addBundle`, `loadBundle`, `unloadBundle`) | [bundles](10-assets.md) |
| Declaring all bundles up front in `Assets.init({ manifest })` | [manifests](10-assets.md) |
| `Assets.get`, `Assets.unload`, `Cache`, freeing memory between levels | [caching](10-assets.md) |
| Preloading the next level (`backgroundLoad`, `backgroundLoadBundle`) | [background](10-assets.md) |
| Loading bars (`onProgress`)                                 | [progress](10-assets.md) |
| Texture atlases, `Spritesheet`, `meta.scale`                | [spritesheet](10-assets.md) |
| Web fonts and bitmap fonts                                  | [fonts](10-assets.md) |
| Video textures, autoplay, sound                             | [video](10-assets.md) |
| SVG as texture or `Graphics`                                | [svg](10-assets.md) |
| `.ktx2`, `.basis`, `.dds`, `.ktx`                           | [compressed-textures](10-assets.md) |
| `@2x` files, `texturePreference`, format fallbacks          | [resolution](10-assets.md) |
| Animated GIFs                                               | [scene-gif](09-dom-gif-html.md) |


---

## Bundles

Named asset groups: `addBundle`, `loadBundle` result shapes and keys, unloading, and the silent failure of an unregistered bundle.

```ts
import { Assets, Sprite } from "pixi.js";

Assets.addBundle("level1", [
  { alias: "bg", src: "level1/background.png" },
  { alias: "config", src: "level1/config.json" },
]);

const resources = await Assets.loadBundle("level1", (progress) => console.log(progress));
const bg = Sprite.from("bg");
```

- `loadBundle(name)` returns a `Record<alias, asset>`, and each alias is also available via `Assets.get(alias)`. `loadBundle(["ui", "level1"])` loads in parallel and returns an object keyed by bundle name: `{ ui: {...}, level1: {...} }`.
- The second argument is only a progress function (`[0, 1]` across the bundle); an options object there throws ([assets](10-assets.md#load-options-and-error-handling)).
- Entries use the `{ alias, src, data? }` shape of `Assets.add()`. Inside the resolver they are stored under a combined key, `'level1-bg'` by default; the plain `'bg'` still resolves. Change the format with `bundleIdentifier` in `Assets.init()`.
- `loadBundle` of a name the resolver does not know resolves `undefined` with no error or warning; the failure shows up later as a missing texture. A common cause is an `Assets.init({ manifest })` that ran after a `load` and was ignored ([assets](10-assets.md#init-order)). Register bundles with `addBundle` or an `Assets.init` that runs first, and match names exactly.

### Unloading

```ts
import { Assets, type Container } from "pixi.js";

declare const level1Container: Container;

level1Container.destroy({ children: true });
await Assets.unloadBundle("level1");
```

`unloadBundle` destroys every asset in the bundle and removes the cached entries. Destroy or detach display objects that use them first, or the renderer hits freed GPU memory. There is no reference counting: if two bundles declare the same alias and `src`, the texture is loaded once and shared, and unloading either bundle destroys it, leaving the other bundle's alias broken until you reload it.


---

## Manifests

`Assets.init({ manifest })`: declaring every bundle up front, inline or from a URL.

```ts
import { Assets } from "pixi.js";

await Assets.init({
  manifest: {
    bundles: [
      { name: "load-screen", assets: [{ alias: "logo", src: "logo.png" }] },
      {
        name: "game",
        assets: [
          { alias: ["hero", "player"], src: "hero@{1,2}x.{webp,png}" },
          { alias: "tile", src: "tile.png", data: { scaleMode: "nearest" } },
        ],
      },
    ],
  },
});

await Assets.loadBundle("load-screen");
Assets.backgroundLoadBundle("game");
```

- `Assets.init()` runs once and must come before any load; a second or late call is ignored, so put `manifest`, `basePath` and preferences in one call ([assets](10-assets.md#init-order)). Calling `Assets.add` or `addBundle` before `init` also runs before format and resolution detection; call `init` first, then add ad-hoc assets.
- `manifest` may be an `AssetsManifest` object or a URL string (`manifest: "assets/manifest.json"`), which is loaded as JSON first, e.g. one generated by `@assetpack/core`.
- Each entry is an `UnresolvedAsset`: an `alias` may be an array (all names return the same asset), `src` takes format (`{webp,png}`) and resolution (`@{1,2}x`) patterns ([resolution](10-assets.md)), and `data` is forwarded to the parser.
- List a fallback format in `src` (`hero.{webp,png}`, not `hero.webp`); a single format leaves browsers without it nothing to fall back to.


---

## Spritesheet

Texture atlases with `Spritesheet`: the JSON fields Pixi reads, `meta.scale`, hand-built sheets and the cache, and cleanup.

```ts
import { AnimatedSprite, Assets, Sprite, type Spritesheet } from "pixi.js";

const sheet = await Assets.load<Spritesheet>("spritesheet.json");
const hero = new Sprite(sheet.textures["hero.png"]);
const walk = new AnimatedSprite({ textures: sheet.animations["walk"], animationSpeed: 0.15, autoPlay: true });
```

`Assets.load` of the JSON fetches it, loads the atlas image named by `meta.image` (relative to the JSON), runs `parse()`, caches every frame name, and returns the `Spritesheet`.

### JSON fields

```json
{
  "frames": {
    "hero.png": {
      "frame": { "x": 0, "y": 0, "w": 64, "h": 64 },
      "anchor": { "x": 0.5, "y": 0.5 },
      "borders": { "left": 10, "top": 10, "right": 10, "bottom": 10 }
    },
    "walk_01.png": {
      "frame": { "x": 64, "y": 0, "w": 64, "h": 64 },
      "rotated": true,
      "trimmed": true,
      "sourceSize": { "w": 80, "h": 80 },
      "spriteSourceSize": { "x": 8, "y": 8, "w": 64, "h": 64 }
    }
  },
  "animations": { "walk": ["walk_01.png", "walk_02.png"] },
  "meta": { "image": "spritesheet.png", "size": { "w": 512, "h": 256 }, "scale": "1" }
}
```

Per frame, `anchor` becomes the texture's `defaultAnchor` and `borders` its nine-slice `defaultBorders`. `rotated` frames are stored 90 degrees rotated (the parser swaps width/height); `trimmed` frames have `sourceSize` as the original size and `spriteSourceSize` as the trimmed region within it. `animations` maps names to ordered frame lists. When `meta.related_multi_packs` is present, the loader loads and links the related sheets, reachable through `sheet.linkedSheets`.

### `meta.scale` sets the resolution

In v8, `meta.scale` directly sets the texture source resolution (`"2"` means the atlas is @2x). If an atlas exported at @2x says `"1"`, frames render at double the intended size. Keep `meta.scale` equal to the atlas image's real resolution; TexturePacker sets it automatically.

### Hand-built sheets

```ts
import { Assets, Sprite, Spritesheet, type SpritesheetData, type Texture } from "pixi.js";

declare const spritesheetJsonData: SpritesheetData;

const texture = await Assets.load<Texture>("atlas.png");
const sheet = new Spritesheet({ texture, data: spritesheetJsonData });
await sheet.parse();

const frame = new Sprite(sheet.textures["hero.png"]);
```

`parse()` is async (sheets over 1000 frames are batched across frames); `sheet.textures` entries are undefined until it resolves. `parseSync()` exists for smaller sheets.

A hand-built sheet's frames exist only in `sheet.textures` and `sheet.animations`. Only `Assets.load` of the JSON adds frame names to the cache, so after a manual `parse()`, `Texture.from("hero.png")`, `Sprite.from("hero.png")` and `AnimatedSprite.fromFrames([...])` find nothing ("not found in the Cache"). The `cachePrefix` option likewise only affects the cache keys of a loaded sheet: `Assets.load({ src: "a.json", data: { cachePrefix: "a/" } })` caches frames as `"a/hero.png"`, while `sheet.textures` keeps the unprefixed names. Use it when two loaded atlases share frame names.

To reuse an already loaded atlas image with Assets, pass it as `data.texture`: `Assets.add({ alias: "atlas", src: "images/spritesheet.json", data: { texture: atlasTexture } })`.

### Cleanup

```ts
import { Assets, type Spritesheet } from "pixi.js";

declare const sheet: Spritesheet;

await Assets.unload("spritesheet.json");

sheet.destroy();
await Assets.unload("atlas.png");
```

A loaded sheet: `Assets.unload` its JSON after every sprite using its frames is destroyed; that destroys the frames and atlas and clears the cache. `sheet.destroy(true)` on a loaded sheet leaves the dead `Spritesheet` cached, and a later `Assets.load` of the same JSON throws "Cannot convert undefined or null to object". A hand-built sheet: `sheet.destroy()` destroys its frame textures, then unload its atlas (or `sheet.destroy(true)` if you made the atlas yourself).


---

## Fonts

Web fonts (`.ttf`, `.otf`, `.woff`, `.woff2`) and bitmap fonts (`.fnt`, `.xml`) through `Assets`: family names, `data` descriptors, cache keys and load order.

### Web fonts

```ts
import { Assets, Text } from "pixi.js";

await Assets.load({ src: "fonts/inter.woff2", data: { family: "Inter", weights: ["400", "700"] } });
const text = new Text({ text: "Hello", style: { fontFamily: "Inter", fontWeight: "700" } });
```

- Load the font before creating the `Text`. A `Text` created first rasterises with the browser's fallback font and is cached at that style; loading the font later doesn't repaint existing Text objects.
- Without `data.family`, the family name is derived from the filename: extension dropped, dashes and underscores become spaces, words title-cased (`fonts/titan-one.woff` → `'Titan One'`, `my_hero_font.woff` → `'My Hero Font'`). Use exactly that string in `fontFamily`, or set `data.family`.
- Fonts are registered with the browser's `FontFaceSet`, so DOM elements and `Text` can use them. `HTMLText` can use only fonts loaded this way ([html-text](06-text.md#fonts-must-come-through-assets)).
- An extension-less font URL needs `parser: "web-font"` (or `"bitmap-font"`) at the top level of the descriptor ([assets](10-assets.md#forcing-a-parser-with-parser)).

`data` fields map to `FontFace` descriptors:

| Field             | Purpose |
| ----------------- | ------- |
| `family`          | Override the derived family name |
| `weights`         | Weights to register, one `FontFace` per weight, all sharing the same URL: `'normal'`, `'bold'`, `'100'`–`'900'` |
| `style`           | `'normal'`, `'italic'`, `'oblique'` |
| `display`         | CSS `font-display` (`'auto'`, `'block'`, `'swap'`, `'fallback'`, `'optional'`) |
| `unicodeRange`    | Restrict the codepoints the font covers |
| `stretch`         | `'normal'`, `'condensed'`, `'expanded'`, ... |
| `variant`         | CSS font-variant value |
| `featureSettings` | OpenType features, e.g. `'"liga" 1, "dlig" 1'` |

### Bitmap fonts

```ts
import { Assets, BitmapText, type BitmapFont } from "pixi.js";

const font = await Assets.load<BitmapFont>({ alias: "arial", src: "fonts/arial.fnt" });
const text = new BitmapText({ text: "Score: 9999", style: { fontFamily: font.fontFamily, fontSize: 32 } });
```

- No side-effect import is needed in any build: Assets registers the bitmap-font loader and `BitmapText` registers its own render pipes. `pixi.js/text-bitmap` exists only for manual extension setups.
- `fontFamily` must match the `face` declared inside the `.fnt` or the key it was loaded under; a mismatch silently falls back to a dynamic font built from a system font.
- The cached asset is a `BitmapFont`. `Assets.get('arial')` and `Assets.get('arial-bitmap')` both return it, and `Assets.get('Arial-bitmap')` works if `fontFamily` matches.
- The parser sniffs text vs XML BMFont content. Page images named in the `.fnt` are resolved relative to the `.fnt` URL and loaded automatically; search params on the `.fnt` URL (cache busting) propagate to them.
- Distance-field metadata in the `.fnt` switches the atlas to `linear` scale mode and disables mipmaps automatically; SDF/MSDF fonts stay crisp at any size.


---

## Video textures

Video through `Assets.load`: `VideoSourceOptions` defaults, autoplay and sound, manual playback, upload rate, and CORS.

```ts
import { Assets, Sprite, type Texture, type VideoSource } from "pixi.js";

const texture = await Assets.load<Texture>({
  src: "city.mp4",
  data: { autoPlay: false, loop: true, preload: true, updateFPS: 30 },
});
const sprite = new Sprite(texture);

const video = (texture.source as VideoSource).resource;
video.play();
```

The result is a regular `Texture` wrapping a `VideoSource`; the sprite shows the current frame without any `update()` calls. Control playback (`play()`, `pause()`, `currentTime`, `paused`) on `texture.source.resource`, the `HTMLVideoElement`. List formats for fallback (`clip.{webm,mp4}`). An extension-less URL needs `parser: "video"` and `data: { mime: "video/mp4" }` ([assets](10-assets.md#forcing-a-parser-with-parser)).

`data` takes `VideoSourceOptions`; defaults come from `VideoSource.defaultOptions`:

| Option        | Default                | Purpose |
| ------------- | ---------------------- | ------- |
| `autoLoad`    | `true`                 | Start downloading as soon as it's assigned |
| `autoPlay`    | `true`                 | Start playing once `canplay` fires |
| `loop`        | `false`                | Restart at the end |
| `muted`       | `true`                 | Required for autoplay on most browsers |
| `playsinline` | `true`                 | Prevents iOS fullscreen takeover |
| `preload`     | `false`                | Await `canplaythrough` before resolving, so the first frame is uploaded before `play()` |
| `updateFPS`   | `0`                    | Texture re-upload rate; `0` re-uploads every render frame, `15` caps it at 15 per second for static-ish backgrounds |
| `crossorigin` | `true`                 | CORS mode for cross-origin URLs |
| `alphaMode`   | auto-detected          | `'no-premultiply-alpha'` for straight alpha |
| `mime`        | derived from extension | Force a MIME type when the URL lacks an extension |

### Sound and autoplay

```ts
import { Assets, type Container, type Texture, type VideoSource } from "pixi.js";

declare const playButton: Container;

const texture = await Assets.load<Texture>("intro.mp4");
const video = (texture.source as VideoSource).resource;

playButton.on("pointertap", () => {
  video.muted = false;
  video.currentTime = 0;
});
```

Browsers autoplay only muted video, and iOS only inline video, which is why `muted` and `playsinline` default to `true`. With `data: { muted: false }`, the autoplay `play()` call is blocked until the user has interacted with the page: the promise from `Assets.load` still resolves, the rejection is unhandled, and the video sits on its first frame. Keep it muted and unmute (or call `video.play()`) inside a pointer or key handler. `playsinline: false` lets iOS take the video fullscreen.

### CORS

WebGL cannot upload a cross-origin video unless the server sends `Access-Control-Allow-Origin`; the default `crossorigin: true` requests it in CORS mode. `data: { crossorigin: false }` is not a workaround: the load resolves, but every render throws "texImage2D ... The video element contains cross-origin data" and the sprite draws nothing. Serve the video with CORS headers or from the page's origin.


---

## SVG loading

`.svg` as a rasterized texture (default) or as a `GraphicsContext`, and what Graphics mode can't parse.

```ts
import { Assets, Graphics, Sprite, type GraphicsContext, type Texture } from "pixi.js";

const texture = await Assets.load<Texture>({ src: "icon.svg", data: { resolution: 2 } });
const sprite = new Sprite(texture);

const context = await Assets.load<GraphicsContext>({ src: "logo.svg", data: { parseAsGraphicsContext: true } });
const small = new Graphics(context);
const large = new Graphics(context);
large.scale.set(3);
```

- **Texture mode** (default): the browser rasterizes the SVG once at its native size, times `data.resolution` (pair with `autoGenerateMipmaps` for smooth downscaling). It batches like any sprite and has the browser's full SVG/CSS support, but pixelates when scaled past that resolution.
- **Graphics mode** (`data: { parseAsGraphicsContext: true }`): parsed into a `GraphicsContext` that several `Graphics` can share, crisp at any scale; higher initial parse cost, and `resolution` doesn't apply. `Assets.setPreferences({ parseAsGraphicsContext: true })` makes it the default for later loads unless an asset's `data` overrides it.
- Graphics mode uses the same parser as `graphics.svg()`; supported elements and attributes are in [scene-graphics](05-graphics.md#svg-import-and-export). Unsupported elements are skipped with a console warning, and gradients map to `FillGradient`. It does not read `<style>` blocks or class selectors at all; only presentation attributes and inline `style="..."` are parsed, so class-styled shapes render with the default black fill. Move styling inline, or use texture mode.
- An SVG that references external images (`<image href="...">`) cross-origin without CORS headers may fail to load; inline the image as base64 or serve it from the same origin.


---

## Compressed textures

DDS, KTX, KTX2 and Basis textures: the side-effect import each needs, resolver fallbacks, and renderer limits.

```ts
import "pixi.js/ktx2";
import { Assets } from "pixi.js";

Assets.add({ alias: "background", src: "background.{ktx2,webp,png}" });
const texture = await Assets.load("background");
```

- Each format registers its loader only through its side-effect import: `pixi.js/dds`, `pixi.js/ktx`, `pixi.js/ktx2` (with Basis Universal support), `pixi.js/basis`. Without it, no parser recognises the extension, so the load logs "don't know how to parse it" and resolves `null` ([assets](10-assets.md#forcing-a-parser-with-parser)). Import only the formats you use; each adds decoder code to the bundle.
- KTX2 + Basis is the usual choice for new projects; Basis transcodes to the GPU-native format at load time on a worker where supported, with nothing to await beyond `Assets.load`.
- List the compressed format first in the `src` pattern with a WebP/PNG fallback: the resolver falls back on browsers or hardware that can't sample it. The Canvas renderer can't sample compressed textures at all, so it needs that fallback too.
- On WebGL1 without extensions, some devices get an uncompressed Basis transcode, losing the memory savings. `await getSupportedCompressedTextureFormats()` (exported from `pixi.js`) lists what the device supports.


---

## Resolution and format detection

`texturePreference`, `@{1,2}x` and `{webp,png}` patterns in `src`, and how the resolver picks a file.

```ts
import { Assets } from "pixi.js";

await Assets.init({
  texturePreference: {
    resolution: window.devicePixelRatio,
    format: ["avif", "webp", "png"],
  },
});

Assets.add({ alias: "hero", src: "hero@{0.5,1,2}x.{avif,webp,png}" });
const texture = await Assets.load("hero");
```

- Patterns use braces (shell-style brace expansion). `hero@[1,2]x.png` is not recognised and the resolver tries to load that literal filename. Resolution and format patterns combine as a Cartesian product (3 × 3 = 9 candidates); the resolver picks the best match for both preferences.
- `texturePreference.resolution` is a single number (best-match threshold) or an array of acceptable resolutions. `format` is in preference order; the first one the browser supports wins. Format detection runs once during `Assets.init()`; `skipDetections` turns it off ([assets](10-assets.md#init-options-preferences-and-fetch-routing)).
- The resolution encoded in the filename sets the texture source's resolution, so `width`/`height` stay at logical size whichever file is chosen. A file at a known resolution without the suffix takes `data: { resolution: 2 }`.
- `Resolver.RETINA_PREFIX` (default `/@([0-9\.]+)x/`) changes the filename pattern, e.g. `/@([0-9\.]+)density/` for `hero@{1,2}density.png`.
- List a format every target browser supports as the last fallback (`hero.{avif,png}`); with only `hero.avif`, the load fails where AVIF isn't supported.
- A spritesheet's resolution comes from its JSON `meta.scale`, not the filename ([spritesheet](10-assets.md#metascale-sets-the-resolution)).


---

## Progress tracking

Progress callbacks on `Assets.load` and `Assets.loadBundle` for loading bars.

```ts
import { Assets, Graphics } from "pixi.js";

declare const loadingBar: Graphics;
declare function showGame(): void;

await Assets.loadBundle("level1", (progress) => {
  loadingBar.clear().rect(0, 0, progress * 400, 20).fill(0x66ccff);
});
showGame();
```

- `Assets.load(urls, onProgress)` takes the callback as its second argument, or inside `LoadOptions` as `{ onProgress, onError, strategy }` ([assets](10-assets.md#load-options-and-error-handling)). `Assets.loadBundle(name, onProgress)` takes only the function.
- The value is normalized `[0, 1]` across the whole call and fires after each asset resolves; every asset contributes an equal step (the third of four → `0.75`), so a three-asset bundle jumps `0 → 0.33 → 0.66 → 1`. Animate the bar toward the target for a smoother look. A single asset typically reports once, at `1`.
- `progress === 1` can fire slightly before the promise resolves. Treat the callback as UI only and continue after `await`.
- Progress is scoped per call; for one bar across several sequential loads, count completions yourself.
- Background loading reports no progress ([background](10-assets.md)).


---

## Caching

The `Assets` cache: lookup keys, `Assets.get` with arrays, unloading safely, and the low-level `Cache`.

- Everything loaded through `Assets` stays cached until unloaded. Repeated `Assets.load` calls for the same key return the same object, and concurrent calls share one load.
- `Assets.get(key)` is synchronous and returns `undefined` (with a "not found in the Cache" warning) when the key has not been loaded; `await Assets.load` first or use its return value. Get by the exact key you loaded: a bare URL is cached under that string only, so `Assets.get("hero")` misses unless you registered `Assets.add({ alias: "hero", src: "hero.png" })` first.
- `Assets.get([...])` returns an object keyed by array index (`"0"`, `"1"`), not by alias, so `all["hero"]` is `undefined`. For keyed access, call `Assets.load([...])` again (it returns cached entries without refetching) or `Assets.get(alias)` per key.

### Unloading

```ts
import { Assets, type Sprite } from "pixi.js";

declare const sprite: Sprite;

sprite.destroy();
await Assets.unload("hero.png");
```

`Assets.unload(id)` removes the asset from the cache, calls `destroy()` on the texture (releasing GPU memory), and removes loader-specific wrappers. A sprite still holding the texture renders `Texture.EMPTY` or crashes depending on the backend, so destroy display objects (or reassign their texture) first. Destroy them with plain `destroy()`, not `destroy(true)`, which destroys the shared texture under every other sprite ([scene-container](03-scene-graph.md#destroy)).

For level-based games, `Assets.unloadBundle(name)` after destroying the level's display objects; without unloading, GPU memory grows level after level until it hits browser limits. It has no reference counting: every asset in the bundle is destroyed, even if another bundle declares the same `src`, and that bundle's alias stays broken until reloaded.

The low-level `Cache` class (`import { Cache } from "pixi.js"`) backs `Assets.get` and exposes `has(key)`, `get(key)`, `set(key, value)` and `remove(key)`, for diagnostics or custom loader plugins.


---

## Background loading

`Assets.backgroundLoad` and `backgroundLoadBundle`: priming assets you will need soon without blocking.

```ts
import { Assets } from "pixi.js";

declare function showMenu(): void;
declare function startLevel(): void;

await Assets.loadBundle("menu");
showMenu();

Assets.backgroundLoadBundle("level1");

async function onStartClicked() {
  await Assets.loadBundle("level1");
  startLevel();
}
```

- Both calls return immediately (fire-and-forget) and queue assets one at a time, sequentially. `backgroundLoad` takes a URL, alias or array; `backgroundLoadBundle` needs a bundle already registered via a manifest or `addBundle`.
- An explicit `Assets.load()` or `Assets.loadBundle()` interrupts background loading safely: the current background asset finishes, then the explicit load takes priority. For an asset already in flight, the explicit load resolves immediately if background work finished, or waits for the in-progress load.
- Background loading is best-effort: always `await` the foreground `load`/`loadBundle` before using the assets.
- There is no progress callback; `backgroundLoadBundle("level2", onProgress)` reports nothing. For a visible bar, load in the foreground with `onProgress` ([progress](10-assets.md)).
