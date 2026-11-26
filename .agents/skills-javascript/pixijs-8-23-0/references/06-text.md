# Text

## Contents

- [scene-text](#scene-text)
  - [Update cost comparison](#update-cost-comparison)
- [Text](#text-1)
  - [Constructor options](#constructor-options)
  - [TextStyle](#textstyle)
  - [Sharing a TextStyle](#sharing-a-textstyle)
  - [Gradient and pattern fills](#gradient-and-pattern-fills)
- [BitmapText](#bitmaptext)
  - [Options](#options)
  - [Dynamic fonts](#dynamic-fonts)
  - [BitmapFont.install](#bitmapfontinstall)
  - [Loaded bitmap fonts (FNT / XML) and MSDF](#loaded-bitmap-fonts-fnt--xml-and-msdf)
- [HTMLText](#htmltext)
  - [Size now, pixels later](#size-now-pixels-later)
  - [Fonts must come through Assets](#fonts-must-come-through-assets)
- [split-text](#split-text)
  - [Options](#options-1)
  - [Segments](#segments)
  - [SplitBitmapText fonts](#splitbitmaptext-fonts)

## scene-text

Choosing between `Text`, `BitmapText`, `HTMLText`, `SplitText` and `SplitBitmapText`, what each update costs, and the defaults every text object shares.

All text classes take an options object: `new Text({ text, style })`. The v7 positional `(string, style)` form still runs but is deprecated and logs a warning. A `Text` with no `fill` is black (`TextStyle` defaults: `fill: 'black'`, `fontSize: 26`, `fontFamily: 'Arial'`), which is invisible on the default black canvas.

| Variant           | Use for                                                           | Trade-off                                                              | Sub-page |
| ----------------- | ----------------------------------------------------------------- | ---------------------------------------------------------------------- | -------- |
| `Text`            | Styled labels that change rarely                                  | Each change is a canvas redraw + GPU upload                           | [text.md](06-text.md) |
| `BitmapText`      | Scores, timers, anything that changes every frame                 | Limited styling; glyph atlas; crisp scaling needs MSDF                | [bitmap-text.md](06-text.md) |
| `HTMLText`        | Real HTML/CSS markup (`<b>`, `<i>`, `<br>`, nested styles)        | Texture appears a few frames after first render; size is known immediately | [html-text.md](06-text.md) |
| `SplitText`       | Per-character animation with rich styling                         | Each char is a full `Text`; expensive for long strings                | [split-text.md](06-text.md) |
| `SplitBitmapText` | Per-character animation on long strings or dynamic content        | Inherits BitmapText limits                                            | [split-text.md](06-text.md) |

- Inline coloured tags (`<red>Warning:</red>`): `Text` or `HTMLText` with `tagStyles`.
- Arabic, Indic, other shaped scripts, or emoji: `Text` or `HTMLText`. `BitmapText` draws one glyph per grapheme, so it cannot join or shape scripts. CJK works with a dynamic `BitmapText` (glyphs are rasterised on first use), but a pre-built `.fnt` font drops any glyph it lacks.
- Custom font: `await Assets.load({ src: 'font.woff2', data: { family: 'MyFont' } })` first, then `style.fontFamily: 'MyFont'`; works for `Text` and `HTMLText` ([fonts](10-assets.md)).
- `BitmapFont.install` pre-generates an atlas before you create any `BitmapText`; without it, the first `BitmapText` with a new `fontFamily` generates the atlas lazily. MSDF fonts (from msdf-bmfont or AssetPack) stay sharp at any size and load with `Assets.load('font.fnt')`. No extra import is needed in any build: Assets registers the bitmap-font loader and `BitmapText` registers its own render pipes.

### Update cost comparison

| Update trigger      | Text | BitmapText | HTMLText | SplitText                     | SplitBitmapText          |
| ------------------- | ---- | ---------- | -------- | ----------------------------- | ------------------------ |
| Changing `.text`    | High | Very low   | High     | Very high (N text re-renders) | Low (N quad repositions) |
| Changing `.style`   | High | Medium     | High     | Very high                     | Medium                   |
| Moving, rotating, scaling | Free | Free | Free     | Free                          | Free                     |

"High" = new canvas draw + GPU upload; "Very low" = quad reposition only. Put strings that change most frames (scores, timers, counters) in `BitmapText` or `SplitBitmapText`. The `text` setter of `Text`, `BitmapText` and `HTMLText` ignores a value equal to the current string, so assigning every frame costs nothing until the value changes (an equality guard adds nothing); `SplitText` and `SplitBitmapText` rebuild on every assignment.


---

## Text

Canvas `Text`: constructor options, `TextStyle` defaults and less obvious fields, `tagStyles`, sharing a style, and gradient or pattern fills.

```ts
import { Text } from "pixi.js";

const label = new Text({
  text: "Hello PixiJS",
  style: {
    fontSize: 36,
    fill: 0xffffff,
    stroke: { color: "#4a1850", width: 5 },
    dropShadow: { color: "#000000", blur: 4, distance: 6 },
    padding: 6,
  },
  anchor: 0.5,
});

const pixel = new Text({
  text: "PIXEL",
  style: { fontFamily: "monospace", fontSize: 16, fill: 0xffffff },
  textureStyle: { scaleMode: "nearest" },
});
```

### Constructor options

`new Text({...})` takes `CanvasTextOptions`: the base `TextOptions` plus `textureStyle` and `autoGenerateMipmaps`.

| Option                | Default | Notes |
| --------------------- | ------- | ----- |
| `text`                | `''`    | `string \| number \| { toString(): string }`; `'\n'` breaks a line. |
| `style`               | `new TextStyle()` | A `TextStyle` or its options. |
| `anchor`              | `0`     | `[0, 1]`; `0.5` centers. |
| `resolution`          | `null` (auto) | Pixel density of the rasterized texture; `null` follows the renderer's resolution (setting `null` at runtime re-enables auto, though the interface type is `number`). |
| `roundPixels`         | `false` | Snap rendered x/y to whole pixels. |
| `textureStyle`        | `undefined` | Scale mode for the generated texture (`nearest` or `linear`); every other `TextureStyle` field is ignored. |
| `autoGenerateMipmaps` | `TextureSource.defaultOptions.autoGenerateMipmaps` | Better quality when drawn smaller than native size. |

### TextStyle

Defaults when a property is omitted: `fill: 'black'`, `fontSize: 26`, `fontFamily: 'Arial'`, `whiteSpace: 'pre'`, `wordWrap: false` (`wordWrapWidth: 100`), `padding: 0`, no stroke or shadow. A partial `dropShadow` object is merged with `{ alpha: 1, angle: Math.PI / 6, blur: 0, color: 'black', distance: 5 }`. `stroke` is an object, `{ color, width }`.

Fields whose behaviour is easy to get wrong:

- `padding`: the canvas is sized from the text metrics, so a heavy stroke or drop shadow is clipped at the edges; raise `padding` to enlarge the texture.
- `breakWords` breaks mid-word only with `wordWrap: true`. `align` (`'left' | 'center' | 'right' | 'justify'`) affects only multi-line text.
- `whiteSpace`: `'normal' | 'pre' | 'pre-line'`. `textBaseline`: `'alphabetic' | 'top' | 'hanging' | 'middle' | 'ideographic' | 'bottom'`. `leading` adds pixels on top of `lineHeight`.
- `trim` crops transparent padding after rasterization (expensive).
- `filters` in the style are applied to the generated texture at bake time, cheaper than filters on the `Text` node for static strings.
- `tagStyles` maps tag names to style overrides: `text: "<red>Warning:</red> <b>overloaded</b>"` with `tagStyles: { red: { fill: 0xff0000 }, b: { fontWeight: "bold" } }`. Tags are parsed only when `tagStyles` has entries; otherwise `<` is literal. Nested tags inherit from outer ones.

Load web fonts with `await Assets.load({ src: "my-font.woff2", data: { family: "MyFont" } })` before creating the `Text`, then set `fontFamily: "MyFont"`; the `data` fields and the derived-name rule are in [fonts](10-assets.md).

### Sharing a TextStyle

```ts
import { BitmapText, Text, TextStyle } from "pixi.js";

const style = new TextStyle({ fontSize: 24, fill: 0xffffff });
const title = new Text({ text: "Title", style });
const label = new BitmapText({ text: "Label", style });

style.fill = 0xff0000;
title.destroy();
```

One `TextStyle` instance can back any number of `Text`, `BitmapText` and `HTMLText` objects; changing it re-renders all of them. `destroy()` detaches the text from the style without destroying it; `destroy({ style: true })` and `destroy(true)` destroy the shared instance ([scene-container](03-scene-graph.md#destroy)).

### Gradient and pattern fills

`fill` accepts any `FillInput` that `Graphics` accepts: a color, a `FillGradient`, a `FillPattern`, a `Texture`, or a `FillStyle` object (`{ color, alpha, texture, fill }`). A number array is one RGB(A) color (0-1 components), never gradient stops; v7's `fill: ['#ff0', '#f00']` gradient becomes `new FillGradient(...)`:

```ts
import { Assets, FillGradient, FillPattern, Text } from "pixi.js";

const gradient = new FillGradient({
  end: { x: 0, y: 1 },
  colorStops: [
    { color: 0xff0000, offset: 0 },
    { color: 0x0000ff, offset: 1 },
  ],
});
const title = new Text({ text: "Gradient", style: { fontSize: 64, fill: gradient } });

const pattern = new FillPattern({ texture: await Assets.load("bricks.png"), repetition: "repeat" });
const label = new Text({ text: "PixiJS", style: { fontSize: 64, fill: pattern, stroke: { fill: pattern, width: 10 } } });
```

Canvas-rendered text ignores the pattern's `textureSpace`; the texture tiles in the text's pixel space at its native size. Use `pattern.setTransform(matrix)` to scale, rotate or offset the tiles ([scene-graphics](05-graphics.md#gradients-and-patterns)).


---

## BitmapText

`BitmapText`: dynamic atlases and what shares them, `BitmapFont.install` and `dynamicFill`, loaded `.fnt` fonts, MSDF, and the options it ignores.

```ts
import { Application, BitmapText } from "pixi.js";

declare const app: Application;

const score = new BitmapText({ text: "Score: 0", style: { fontFamily: "Arial", fontSize: 32, fill: 0xffffff } });
app.stage.addChild(score);

app.ticker.add(() => {
  score.text = `Score: ${Math.floor(performance.now() / 100)}`;
});
```

A text change only repositions glyph quads: no canvas redraw, no GPU upload.

### Options

`BitmapText` takes the base `TextOptions` (`text`, `style`, `anchor`, `roundPixels`) with these differences from [Text](06-text.md):

- `style` is the same `TextStyle`, with `fill` defaulting to `0xffffff`. `fontFamily`, `fontSize`, `fill`, `stroke`, `align`, `wordWrap`, `wordWrapWidth` and `lineHeight` are respected; gradient fills and style `filters` are not.
- `resolution` is accepted but ignored, and a non-null value (constructor or `text.resolution = 2`) logs a warning. Resolution belongs to the font: `BitmapFont.install({ resolution })`, or install at a larger `fontSize` and scale the text down.
- There is no `textureStyle` or `autoGenerateMipmaps`; set the atlas texture style with `BitmapFont.install({ textureStyle })`.

### Dynamic fonts

A system `fontFamily` with no install generates an atlas lazily on first use. Without a stroke or drop shadow the atlas is shared by `fontFamily`, weight, style and variant (a solid fill is applied as a tint, so every colour reuses it). A stroke or drop shadow ties the atlas to the `TextStyle` object itself: pass one shared `TextStyle` instance (or `BitmapFont.install` the style) to every stroked BitmapText, or each one builds its own atlas. `fontSize` is not part of the key: glyphs are rasterised once at a fixed base size and scaled to each `fontSize`, so very small sizes can look soft; install a font at the target size for crisp small text. Missing characters are rasterised on first use (a canvas draw plus upload), so any script without complex shaping works, CJK included; pre-warm with `chars`. There is no shaping (one glyph per grapheme), so Arabic, Indic and other joined scripts render as isolated forms: use `Text` or `HTMLText` for them.

### BitmapFont.install

```ts
import { BitmapFont, BitmapFontManager, BitmapText } from "pixi.js";

BitmapFont.install({
  name: "UIFont",
  chars: BitmapFontManager.ALPHANUMERIC,
  resolution: window.devicePixelRatio,
  padding: 8,
  textureStyle: { scaleMode: "nearest" },
  dynamicFill: true,
  style: { fontFamily: "Arial", fontSize: 32, fill: 0xffffff, stroke: { color: "#000000", width: 2 } },
});

const hp = new BitmapText({ text: "100", style: { fontFamily: "UIFont", fill: "red" } });
```

The installed fill is baked into the glyphs unless the style is tintable (white fill, no stroke, no shadow or a black one) or you pass `dynamicFill: true`. Without `dynamicFill` here, the stroke makes the style non-tintable, so `fill: "red"` would be ignored and the text would render white with a black stroke. With `dynamicFill: true` the per-instance fill applies and also tints the stroke (a black stroke stays black).

| Option         | Default | Notes |
| -------------- | ------- | ----- |
| `chars`        |         | String, nested ranges, or `BitmapFontManager.ALPHA` / `NUMERIC` / `ALPHANUMERIC` / `ASCII`. A pre-warm list, not a whitelist: other characters are generated on first use. |
| `resolution`   | `1`     | Atlas resolution; `window.devicePixelRatio` for HiDPI. |
| `padding`      | `4`     | Glyph padding in the atlas; raise it to stop bleeding at large scales. |
| `skipKerning`  | `false` | Skip kerning data to save memory and install time. |
| `textureStyle` |         | Atlas `TextureStyle` options, e.g. `{ scaleMode: 'nearest' }` for pixel fonts. |
| `dynamicFill`  | auto    | Render glyphs white and colour them with each BitmapText's `style.fill`; on automatically when the style is tintable. The way to colour bitmap text without an atlas per colour. |

### Loaded bitmap fonts (FNT / XML) and MSDF

```ts
import { Assets, BitmapText } from "pixi.js";

await Assets.load("fonts/arcade.fnt");
const arcade = new BitmapText({ text: "HIGH SCORE", style: { fontFamily: "arcade", fontSize: 36 } });
```

AngelCode BMFont `.fnt` / `.xml` files load through Assets with no extra import; [AssetPack](https://pixijs.io/assetpack/) generates them from a `.ttf` / `.otf`. `style.fontFamily` must be the `face` name declared inside the file (read it with `(await Assets.load<BitmapFont>(url)).fontFamily`) or the exact key it was loaded under, not the file name; on a mismatch BitmapText silently builds a dynamic font from a system font of that name. A loaded font draws only the glyphs it contains and silently skips missing ones; for user-generated content fall back to a dynamic font, `Text` or `HTMLText`.

MSDF / SDF fonts (from AssetPack or msdf-bmfont) are detected automatically when the `.fnt` declares a `distanceField` section; they render through a custom fragment shader and stay crisp at any scale.


---

## HTMLText

`HTMLText`: what `HTMLTextStyle` drops and adds, fonts it can see, and its asynchronous texture with synchronous size.

```ts
import { Application, HTMLText } from "pixi.js";

declare const app: Application;

const rich = new HTMLText({
  text: "<b>Bold</b>, <i>italic</i> and <warning>Low power</warning>",
  style: {
    fontSize: 24,
    fill: 0xffffff,
    wordWrap: true,
    wordWrapWidth: 400,
    tagStyles: { warning: { fill: 0xff3333, fontWeight: "bold" } },
  },
});
rich.x = (app.screen.width - rich.width) / 2;
app.stage.addChild(rich);

rich.style.addOverride("text-decoration: underline");
```

- `HTMLTextStyle` is `TextStyle` minus `leading`, `textBaseline`, `trim` and `filters` (unsupported by the SVG path). It adds `cssOverrides`, set with `style.addOverride("css-property: value")`, for CSS with no `TextStyle` equivalent (`text-decoration`, `text-transform`, `text-shadow`, anything supported inside SVG `<foreignObject>`).
- `tagStyles` maps custom or standard tag names to style overrides; nested tags inherit from outer ones. Standard `<b>`, `<i>`, `<u>`, `<br>` work as in HTML. Wrapping is done by the browser's layout, so CSS hyphenation, justification and RTL work when the font and CSS support them.
- Options are those of [Text](06-text.md), including `resolution`, `textureStyle` (scale mode only) and `autoGenerateMipmaps`. The last two are also instance properties, but they are read only when a new texture is generated (a text, style or resolution change); `onViewUpdate()` alone does not regenerate it.

### Size now, pixels later

`width`/`height` are measured synchronously from the HTML, so layout code can use them right after construction; waiting a tick before positioning gains nothing. Only the pixels are asynchronous: HTMLText renders to an SVG image, then a texture, and that work starts the first time the object is rendered while visible; the texture shows up a few frames later. A `visible = false` HTMLText never starts it, so hiding it and revealing on the next tick just delays the text further. To fade it in, keep it visible with `alpha = 0`.

### Fonts must come through Assets

HTMLText is drawn as an SVG image, which cannot see the page's fonts. It embeds only fonts loaded with `Assets.load` (fetched and inlined as base64 `@font-face`). A font from a CSS `@font-face` rule or a Google Fonts `<link>` renders in `Text` but falls back to a default font in HTMLText. Load it with `await Assets.load({ src: "fonts/Hero.woff2", data: { family: "Hero" } })` and use `fontFamily: "Hero"`. Cross-origin font files also need CORS headers (`Access-Control-Allow-Origin`), or the embed fails.


---

## split-text

`SplitText` and `SplitBitmapText`: text split into `lines`, `words` and `chars` you can animate one by one, and what rebuilds them.

`SplitText` wraps canvas `Text`: every character is a full `Text` with its own canvas and GPU texture, so a 40-character string makes 40 text renders. `SplitBitmapText` has the same API but wraps `BitmapText`, so each character reuses the glyph atlas; use it for long strings, many instances, or text that changes often. Both are new in v8 and their API may still change.

### Options

```ts
import { SplitText } from "pixi.js";

const full = new SplitText({
  text: "Animate\nEvery Character",
  style: { fontSize: 48, fill: "white", stroke: { color: "black", width: 2 } },
  autoSplit: true,
  lineAnchor: 0.5,
  wordAnchor: { x: 0, y: 0.5 },
  charAnchor: { x: 0.5, y: 1 },
  x: 100,
  y: 200,
});

full.chars.forEach((char, i) => {
  char.onRender = () => {
    char.y = Math.sin(performance.now() / 200 + i) * 5;
  };
});
```

Both classes are a `Container` (not a `ViewContainer`), so unlike `Text` they take no top-level `anchor`, `resolution`, `roundPixels`, `textureStyle` or `autoGenerateMipmaps`; those belong to the per-character text objects.

| Option       | Type                                     | Default | Description |
| ------------ | ---------------------------------------- | ------- | ----------- |
| `text`       | `string`                                 | —       | Text content to render and segment. Required. |
| `style`      | `TextStyle \| Partial<TextStyleOptions>` | —       | The `TextStyle` a `Text` takes ([text](06-text.md)); for `SplitBitmapText`, the subset `BitmapText` respects ([bitmap-text](06-text.md)), with `fill` defaulting to `0xffffff`. Required. |
| `autoSplit`  | `boolean`                                | `true`  | Re-split when `text` or `style` changes; set `false` to batch updates and call `split.split()` manually. |
| `lineAnchor` | `number \| PointData`                    | `0`     | Normalized (0–1) transform origin of each line container, so per-line rotation and scale pivot there. |
| `wordAnchor` | `number \| PointData`                    | `0`     | The same for each word container. |
| `charAnchor` | `number \| PointData`                    | `0`     | The same for each character. |

`SplitText.defaultOptions` / `SplitBitmapText.defaultOptions` override these defaults globally.

### Segments

`lines` and `words` are `Container[]`; `chars` is `Text[]` (`BitmapText[]` for `SplitBitmapText`). With `autoSplit: true` the constructor splits synchronously, so all three are populated right after `new SplitText(...)`; with `autoSplit: false` call `split.split()` first. The arrays are managed: pushing to them is ignored and overwritten at the next split, so change content through `text`.

Assigning `text` (even the same string) or `style` with `autoSplit` on destroys every old line, word and char object, so held references, per-char `onRender` hooks and tweens die with them: re-read `split.chars` and re-attach animations after each change.

`SplitText.from(existingText)` and `SplitBitmapText.from(existingBitmapText, options?)` copy content and style, then split. `SplitBitmapText.from` discards the source's `tagStyles` with a warning, since bitmap text has none.

### SplitBitmapText fonts

```ts
import { BitmapFont, SplitBitmapText } from "pixi.js";

BitmapFont.install({ name: "GameFont", style: { fontFamily: "Arial", fontSize: 48 } });

const split = new SplitBitmapText({
  text: "Fast Animate",
  style: { fontFamily: "GameFont", fontSize: 48 },
});
```

A system `fontFamily` works without installing (a dynamic bitmap font is generated on first use); installing first avoids the first-render cost. It inherits `BitmapText`'s limits: no shaping (use `SplitText` for Arabic or Indic scripts), and a pre-built `.fnt` font silently skips glyphs it lacks, so `chars` indices may not line up with the source string. Dynamic and installed fonts generate missing glyphs (CJK included) on first use.
