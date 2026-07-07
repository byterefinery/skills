# Image Pipes

## compress

Compresses images using Sharp (for standard formats) and gpu-tex-enc (for GPU textures).

### Import

```ts
import { compress } from '@assetpack/core/image';
```

### Options

```ts
compress({
    // Standard formats (Sharp)
    png: { quality: 90 },       // Sharp PNG options | false | 'skip'
    jpg: {},                     // Sharp JPEG options | false | 'skip'
    webp: { quality: 80, alphaQuality: 80 },  // Sharp WebP options | false
    avif: false,                 // Sharp AVIF options | false (default: false)

    // GPU texture formats (gpu-tex-enc)
    bc7: false,                  // BC7 (DXT) compressed textures → .bc7.dds
    astc: false,                 // ASTC compressed textures → .astc.ktx
    basis: false,                // Basis Universal → .basis.ktx2
    etc: false,                  // ETC/ETC2 → .etc.ktx
});
```

### Default Options

```ts
{
    png: { quality: 90 },
    jpg: {},
    webp: { quality: 80, alphaQuality: 80 },
    avif: false,
    bc7: false,
    astc: false,
    basis: false,
    etc: false,
}
```

### Tags

| Tag | Scope | Description |
|---|---|---|
| `{nc}` | both | Skip compression for this asset |

### Behavior

- Processes `.png`, `.jpg`, `.jpeg` files
- Each enabled format produces a separate output file
- `png: 'skip'` excludes the original PNG from output (other formats still generated)
- `png: false` keeps the original PNG unchanged alongside compressed variants
- GPU texture formats require the `gpu-tex-enc` dependency (bundled with assetpack)

### Example

```
Input:  hero.png
Output: hero.png, hero.webp, hero.jpg
        (plus .bc7.dds, .astc.ktx etc. if GPU formats enabled)
```

---

## mipmap

Generates multiple resolution variants of images.

### Import

```ts
import { mipmap } from '@assetpack/core/image';
```

### Options

```ts
mipmap({
    template: '@%%x',            // Resolution label template
    resolutions: {               // Resolution name → scale factor
        high: 2,
        default: 1,
        low: 0.5,
    },
    fixedResolution: 'default',  // Resolution used when {fix} tag is present
    sharpOptions: {},            // Sharp resize options
});
```

### Default Options

```ts
{
    template: '@%%x',
    resolutions: { default: 1, low: 0.5 },
    fixedResolution: 'default',
    sharpOptions: {},
}
```

### Tags

| Tag | Scope | Description |
|---|---|---|
| `{fix}` | both | Use only `fixedResolution`, skip other resolutions |
| `{nomip}` | both | Skip mipmap generation entirely |

### Behavior

- Processes `.png`, `.jpg`, `.jpeg`, `.webp`, `.avif` files
- The original image is assumed to be at the largest resolution
- Lower resolutions are scaled down from the original
- Template `%%` is replaced with the resolution number (e.g., `@2x`, `@0.5x`)
- Resolution `1` produces no suffix (just the extension)

### Example

```
Input:  hero.png
Output: hero.png,        @1x (default, no suffix)
        hero@2x.png,     @2x (high)
        hero@0.5x.png    @0.5x (low)

Input:  title{fix}.png
Output: title.png        (only fixedResolution = default = 1x)

Input:  icon{nomip}.png
Output: icon.png         (original, no mipmaps)
```

### Resolution Template Examples

```ts
// Standard: @2x, @0.5x
template: '@%%x'

// Numeric: .2x, .5x
template: '.%%x'

// No separator: 2x, 5x
template: '%%x'
```

---

## Sharp Resize Options

The `sharpOptions` parameter accepts any Sharp resize options:

```ts
mipmap({
    sharpOptions: {
        kernel: 'lanczos3',   // 'cubic' | 'lanczos3' | 'lanczos2'
        fit: 'fill',          // Resize mode
        position: 'center',   // Position within bounds
    },
});
```
