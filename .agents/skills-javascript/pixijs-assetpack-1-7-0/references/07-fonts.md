# Fonts

## webfont

Converts font files to WOFF2 format.

### Import

```ts
import { webfont } from '@assetpack/core/webfont';
```

### Usage

```ts
webfont()  // No options
```

### Supported Inputs

| Format | Description |
|---|---|
| `.otf` | OpenType Font |
| `.ttf` | TrueType Font |
| `.svg` | SVG Font |

### Output

Always produces `.woff2` files.

### Tags

| Tag | Scope | Description |
|---|---|---|
| `{wf}` | both | Convert to WOFF2 |
| `{family}` | file | Font family name (passed to manifest) |

### Example

```
Input:  Arial{wf}{family=Arial}.ttf
Output: Arial.woff2
```

The `family` data tag is passed to the manifest `data` field.

---

## sdfFont / msdfFont

Generate Signed Distance Field (SDF) or Multi-channel SDF (MSDF) bitmap fonts from TrueType files.

### Import

```ts
import { sdfFont, msdfFont } from '@assetpack/core/webfont';
```

### Usage

```ts
sdfFont({
    font: {
        fontSize: 42,              // Font size for distance field
        textureSize: [512, 512],   // Atlas dimensions (power-of-2 recommended)
        texturePadding: 2,         // Pixels between glyphs
        border: 0,                 // Edge padding
        distanceRange: 3,          // SDF range width
        roundDecimal: 0,           // Decimal places (0 for XML)
        charset: undefined,        // Character set (string or array)
        vector: false,             // Debug SVG output
        'smart-size': false,       // Shrink to smallest square
        pot: false,                // Force power-of-2
        square: false,             // Force square atlas
        rot: false,                // Allow 90° rotation
        rtl: false,                // RTL character fix
    },
});

msdfFont({
    font: { /* same options */ },
});
```

### Default Font Options

```ts
{
    fontSize: 42,
    textureSize: [512, 512],
    texturePadding: 2,
    border: 0,
    distanceRange: 3,
    roundDecimal: 0,
    vector: false,
    'smart-size': false,
    pot: false,
    square: false,
    rot: false,
    rtl: false,
}
```

### Supported Inputs

Only `.ttf` (TrueType) files.

### Output

Produces two files per input:

1. `.fnt` (XML BMFont format) or `.json` — font metrics
2. `.png` — texture atlas with glyph distance fields

### Tags

| Tag | Scope | Description |
|---|---|---|
| `{sdf}` | both | Generate SDF bitmap font |
| `{msdf}` | both | Generate MSDF bitmap font |
| `{family}` | file | Font family name |

### Behavior

- Generated textures are automatically marked `{nc}{nomip}{mIgnore}` (no compression, no mipmap, excluded from manifest)
- Font family defaults to the filename (without extension and tags)
- The `.fnt`/`.json` file is included in the manifest; the texture is not

### Example

```
Input:  MyFont{msdf}{family=MyFont}.ttf
Output: MyFont.fnt
        MyFont.png          (marked nc, nomip, mIgnore)
```

### SDF vs MSDF

- **SDF** (Signed Distance Field) — single-channel grayscale. Good scaling, but loses color information.
- **MSDF** (Multi-channel SDF) — RGB channels encode different distance directions. Better corner handling, supports colored glyphs.
- **PSDF** (Packed SDF) — intermediate option.

### PixiJS Usage

```ts
// Load the bitmap font
await Assets.load('fonts/MyFont.fnt');

// Use in BitmapText
const text = new BitmapText({
    text: 'Hello World!',
    style: {
        font: {
            name: 'MyFont',
            size: 32,
        },
    },
});
```
