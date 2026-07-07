# Spine Atlas Processing

AssetPack provides four plugins for Spine atlas files (`.atlas` format). They work together with the image pipes to process Spine animations.

## spineAtlasCompress

Compresses atlas-referenced images and updates the atlas file to reference compressed variants.

### Import

```ts
import { spineAtlasCompress } from '@assetpack/core/spine';
```

### Usage

```ts
// Must match compress() options
const compressOptions = {
    png: { quality: 90 },
    webp: { quality: 80, alphaQuality: 80 },
    avif: false,
    bc7: false,
    astc: false,
    basis: false,
    etc: false,
};

pipes: [
    compress(compressOptions),
    spineAtlasCompress(compressOptions),  // Same options!
],
```

### Tags

| Tag | Scope | Description |
|---|---|---|
| `{nc}` | both | Skip atlas compression |

### Behavior

- Processes `.atlas` files
- For each enabled format, creates a new `.atlas` with texture paths updated
- Example: `sprites.atlas` → `sprites.png.atlas`, `sprites.webp.atlas`
- The atlas text is rewritten with new texture extensions

---

## spineAtlasMipmap

Generates resolution variants of atlas files, rescaling coordinates to match.

### Import

```ts
import { spineAtlasMipmap } from '@assetpack/core/spine';
```

### Usage

```ts
// Must match mipmap() options
const mipmapOptions = {
    template: '@%%x',
    resolutions: { default: 1, low: 0.5 },
    fixedResolution: 'default',
};

pipes: [
    mipmap(mipmapOptions),
    spineAtlasMipmap(mipmapOptions),  // Same options!
],
```

### Tags

| Tag | Scope | Description |
|---|---|---|
| `{fix}` | both | Use only `fixedResolution` |
| `{nomip}` | both | Skip mipmap generation |

### Behavior

- Processes `.atlas` files
- Rescales all coordinate values (size, orig, bounds, offsets, scale) by the resolution factor
- Updates image references with the resolution template
- Example: `sprites.atlas` → `sprites.atlas`, `sprites@0.5x.atlas`

### Atlas Coordinate Rescaling

The plugin parses the atlas text line by line and applies:

- XY values (e.g., `size: 2019,463`) — multiplied by scale
- Scale values (e.g., `scale: 0.75`) — multiplied by scale
- Rect values (e.g., `bounds:2,270,804,737`) — all 4 values multiplied by scale
- Image names — resolution template inserted before extension

---

## spineAtlasCacheBuster

Fixes atlas references after cache-busting has renamed the atlas textures.

### Import

```ts
import { spineAtlasCacheBuster } from '@assetpack/core/spine';
```

### Usage

Must come after `cacheBuster()`:

```ts
pipes: [
    cacheBuster(),
    spineAtlasCacheBuster(),  // ← Must follow cacheBuster
],
```

### Behavior

- Finds all `.atlas` files
- For each texture in the atlas, finds the cache-busted version
- Replaces texture names with hashed filenames
- Renames the atlas file with its new hash
- Rewrites on disk

---

## spineAtlasManifestMod

Removes atlas texture entries from the manifest (atlases handle their own loading).

### Import

```ts
import { spineAtlasManifestMod } from '@assetpack/core/spine';
```

### Usage

Must come after `pixiManifest()`:

```ts
pipes: [
    pixiManifest(),
    spineAtlasManifestMod(),
],
```

### Behavior

- Reads the generated manifest
- Finds all `.atlas` files
- Removes manifest entries for textures referenced by atlases
- Rewrites the manifest

---

## Complete Spine Pipeline

```ts
import { compress, mipmap, pixiManifest } from '@assetpack/core';
import { spineAtlasCompress, spineAtlasMipmap, spineAtlasCacheBuster, spineAtlasManifestMod } from '@assetpack/core/spine';

const compressOptions = { png: true, webp: true };
const mipmapOptions = { resolutions: { default: 1, low: 0.5 } };

export default {
    entry: './raw-assets',
    output: './public/assets',
    pipes: [
        mipmap(mipmapOptions),
        spineAtlasMipmap(mipmapOptions),
        compress(compressOptions),
        spineAtlasCompress(compressOptions),
        cacheBuster(),
        spineAtlasCacheBuster(),
        pixiManifest(),
        spineAtlasManifestMod(),
    ],
};
```
