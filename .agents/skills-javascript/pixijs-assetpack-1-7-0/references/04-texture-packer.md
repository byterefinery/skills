# Texture Packer

## texturePacker

Generates texture atlases (spritesheets) from folders of images. Uses the PixiJS spritesheet format.

### Import

```ts
import { texturePacker } from '@assetpack/core/texture-packer';
```

### Options

```ts
texturePacker({
    texturePacker: {
        padding: 2,                    // Pixels between sprites
        nameStyle: 'relative',         // 'short' | 'relative'
        textureFormat: 'png',          // 'png' | 'jpg'
        fixedSize: false,              // Fixed atlas size
        powerOfTwo: false,             // Power-of-2 dimensions
        width: 1024,                   // Atlas width
        height: 1024,                  // Atlas height
        allowTrim: true,               // Trim transparent edges
        allowRotation: true,           // Rotate sprites to fit better
        alphaThreshold: 0.1,           // Alpha threshold for trimming
        removeFileExtension: false,    // Strip extensions from frame names
        autodetectAnimations: true,    // Group numeric-suffix files as animations
        sharpOptions: {},              // Sharp resize options
    },
    resolutionOptions: {
        template: '@%%x',              // Resolution label template
        resolutions: {                 // Resolution name → scale
            default: 1,
            low: 0.5,
        },
        fixedResolution: 'default',    // Resolution for {fix} tag
        maximumTextureSize: 4096,      // Max atlas size before splitting
    },
    addFrameNames: false,              // Add frame names to manifest data
});
```

### Default Options

```ts
{
    resolutionOptions: {
        template: '@%%x',
        resolutions: { default: 1, low: 0.5 },
        fixedResolution: 'default',
        maximumTextureSize: 4096,
    },
    texturePacker: {
        padding: 2,
        nameStyle: 'relative',
    },
    addFrameNames: false,
}
```

### Tags

| Tag | Scope | Description |
|---|---|---|
| `{tps}` | folder | Mark folder for texture packing |
| `{jpg}` | folder | Save atlas as JPG instead of PNG |
| `{fix}` | both | Use only `fixedResolution` |
| `{nomip}` | both | Skip mipmap generation for this atlas |

### Behavior

- Only processes folders marked with `{tps}` tag
- Scans for `*.jpg`, `*.png`, `*.gif` files inside the folder
- Skips children of the folder (they're processed internally)
- Generates atlas image + JSON manifest in PixiJS spritesheet format
- If atlas exceeds `maximumTextureSize`, splits into multiple sheets with `related_multi_packs`
- `autodetectAnimations: true` groups `idle01.png`, `idle02.png`, etc. into animation frames
- `nameStyle: 'short'` uses basename for frame names (risk of clashes across folders)
- `nameStyle: 'relative'` uses relative path (safe but longer names)

### Example

```
Input:
  characters{tps}/
  ├── idle01.png
  ├── idle02.png
  └── attack.png

Output:
  characters.png          (atlas image)
  characters.json         (spritesheet JSON)
  characters@0.5x.png     (0.5x atlas)
  characters@0.5x.json    (0.5x JSON)
```

---

## texturePackerCompress

Compresses generated atlas images into additional formats. Must match `compress()` options.

### Import

```ts
import { texturePackerCompress } from '@assetpack/core/texture-packer';
```

### Options

Same as `compress()` but without `jpg`:

```ts
texturePackerCompress({
    png: { quality: 90 },
    webp: { quality: 80, alphaQuality: 80 },
    avif: false,
    bc7: false,
    astc: false,
    basis: false,
    etc: false,
});
```

### Behavior

- Processes JSON files from texture-packed folders
- For each enabled format, creates a new JSON with updated `meta.image` reference
- The atlas image filename is swapped to match the compressed format
- `related_multi_packs` references are updated accordingly

### Example

```
Input:  characters.json (meta.image: "characters.png")
Output: characters.png.json   (meta.image: "characters.png")
        characters.webp.json  (meta.image: "characters.webp")
```

---

## texturePackerCacheBuster

Updates atlas JSON files after cache-busting has renamed the atlas images.

### Import

```ts
import { texturePackerCacheBuster } from '@assetpack/core/texture-packer';
```

### Usage

Must come immediately after `cacheBuster()` in the pipe array:

```ts
pipes: [
    // ... generation pipes ...
    cacheBuster(),
    texturePackerCacheBuster(),   // Fix atlas JSON references
    // ... manifest pipes ...
],
```

### Behavior

- Finds all atlas JSON files
- Looks up the cache-busted texture filename
- Updates `meta.image` and `related_multi_packs` in the JSON
- Renames the JSON file with its new hash
- Rewrites the file on disk

---

## texturePackerManifestMod

Augments the manifest file with correct file sizes for texture atlases.

### Import

```ts
import { texturePackerManifestMod } from '@assetpack/core/texture-packer';
```

### Usage

Must come after `pixiManifest()`:

```ts
pipes: [
    pixiManifest({ includeFileSizes: 'gzip' }),
    texturePackerManifestMod({ includeFileSizes: 'gzip' }),
],
```

### Options

```ts
texturePackerManifestMod({
    output: 'manifest.json',        // Must match pixiManifest output
    includeFileSizes: false,        // false | 'gzip' | 'raw'
});
```

### Behavior

- Reads the generated manifest
- Finds all atlas JSON entries
- Adds the atlas texture size to the `progressSize` of the JSON entry
- Rewrites the manifest
