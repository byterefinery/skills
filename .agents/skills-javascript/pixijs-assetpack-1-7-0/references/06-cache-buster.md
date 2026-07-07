# Cache Buster

## cacheBuster

Appends content hashes to filenames for cache invalidation.

### Import

```ts
import { cacheBuster } from '@assetpack/core/cache-buster';
```

### Usage

```ts
cacheBuster()  // No options
```

### Behavior

- Processes all non-folder assets
- Computes CRC32 hash of file contents
- Inserts hash into the filename before the extension
- Preserves the original filename structure

### Example

```
Input:  hero.png
Output: hero-a1b2c3d4.png

Input:  hero@2x.webp
Output: hero-a1b2c3d4@2x.webp

Input:  characters.json
Output: characters-a1b2c3d4.json
```

### Placement in Pipe Array

Must come after all generation/compression pipes but before manifest generation:

```ts
pipes: [
    mipmap({ /* ... */ }),
    compress({ /* ... */ }),
    json(),
    cacheBuster(),                    // ← Hash all files
    // Atlas fixers (if using atlases):
    texturePackerCacheBuster(),
    spineAtlasCacheBuster(),
    // Manifest (last):
    pixiManifest(),
    spineAtlasManifestMod(),
    texturePackerManifestMod(),
],
```

---

## texturePackerCacheBuster

Fixes atlas JSON references after cache-busting renamed the atlas images.

### Import

```ts
import { texturePackerCacheBuster } from '@assetpack/core/texture-packer';
```

### Usage

Must come immediately after `cacheBuster()`:

```ts
pipes: [
    cacheBuster(),
    texturePackerCacheBuster(),  // ← Must follow cacheBuster
],
```

### Behavior

- Finds all texture packer JSON files
- Looks up the cache-busted texture filename in the asset tree
- Updates `meta.image` to the new hashed filename
- Updates `related_multi_packs` references
- Renames the JSON file with its own new hash
- Rewrites the file on disk

---

## spineAtlasCacheBuster

Fixes Spine atlas references after cache-busting renamed the atlas textures.

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
- For each texture referenced in the atlas, finds the cache-busted version
- Replaces the texture name in the atlas with the hashed filename
- Renames the atlas file with its own new hash
- Rewrites the file on disk
