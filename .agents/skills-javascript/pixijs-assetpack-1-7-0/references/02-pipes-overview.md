# Pipes Overview

## Pipe Interface

Every pipe is an `AssetPipe` object with a consistent interface:

```ts
interface AssetPipe<OPTIONS, TAGS, INTERNAL_TAGS> {
    folder?: boolean;                              // true = runs on folders
    name: string;                                  // Unique pipe name
    defaultOptions: OPTIONS;                       // Default configuration
    tags?: Record<TAGS, string>;                   // Tag name → filename tag
    internalTags?: Record<INTERNAL_TAGS, string>;  // Internal tags (excluded from manifest)

    // Lifecycle hooks
    start?(asset: Asset, options: OPTIONS, pipeSystem: PipeSystem): Promise<void>;
    test?(asset: Asset, options: OPTIONS): boolean;
    transform?(asset: Asset, options: OPTIONS, pipeSystem: PipeSystem): Promise<Asset[]>;
    finish?(asset: Asset, options: OPTIONS, pipeSystem: PipeSystem): Promise<void>;
}
```

### Lifecycle

1. **`start()`** — called once at the beginning, before any assets are processed. Use for setup.
2. **`test()`** — called for each asset. Return `true` to process, `false` to skip.
3. **`transform()`** — processes the asset. Return an array of new `Asset` objects (can be zero, one, or many).
4. **`finish()`** — called once after all assets are processed. Use for cleanup or post-processing.

### Pipe Ordering

Pipes run sequentially. Each pipe sees the output of the previous pipe. Typical ordering:

```
1. Font conversion (webfont, sdf, msdf)
2. Audio conversion (audio, ffmpeg)
3. Texture packing (texturePacker)
4. Mipmap generation (mipmap, spineAtlasMipmap)
5. Image compression (compress, spineAtlasCompress, texturePackerCompress)
6. JSON minification (json)
7. Cache busting (cacheBuster, texturePackerCacheBuster, spineAtlasCacheBuster)
8. Manifest generation (pixiManifest)
9. Manifest modifications (spineAtlasManifestMod, texturePackerManifestMod)
```

### multiPipe

Group multiple pipes into a single logical unit:

```ts
import { multiPipe } from '@assetpack/core';

const pipeline = multiPipe({
    pipes: [
        compress({ png: true, webp: true }),
        mipmap({ resolutions: { default: 1, low: 0.5 } }),
    ],
});

export default {
    pipes: [pipeline, json(), cacheBuster(), pixiManifest()],
};
```

## Built-in Tags

| Tag | Scope | Description |
|---|---|---|
| `{copy}` | both | Force direct copy to output, skip all processing |
| `{ignore}` | both | Exclude entirely from processing and output |

## Creating Custom Pipes

```ts
import { Asset, AssetPipe, createNewAssetAt } from '@assetpack/core';

function myCustomPipe(): AssetPipe {
    return {
        folder: false,
        name: 'my-custom-pipe',
        defaultOptions: {
            quality: 80,
        },
        tags: {
            skip: 'skip',       // {skip} tag in filename
        },
        test(asset: Asset, options) {
            // Only process .png files that don't have the skip tag
            return asset.extension === '.png' && !asset.allMetaData.skip;
        },
        async transform(asset: Asset, options) {
            // Create a new asset with modified content
            const newAsset = createNewAssetAt(asset, asset.filename);
            newAsset.buffer = /* processed buffer */;
            return [newAsset];
        },
    };
}
```

### Utility Functions

```ts
// Create a new asset at the same location as the source
import { createNewAssetAt } from '@assetpack/core';
const newAsset = createNewAssetAt(sourceAsset, 'new-filename.png');

// Check if a file has one of the given extensions
import { checkExt } from '@assetpack/core';
checkExt(asset.path, '.png', '.jpg', '.jpeg');

// Strip tags from a filename
import { stripTags } from '@assetpack/core';
stripTags('hero{tps}.png'); // → 'hero.png'

// Swap file extension
import { swapExt } from '@assetpack/core';
swapExt('image.png', '.webp'); // → 'image.webp'

// Find assets matching a predicate
import { findAssets } from '@assetpack/core';
findAssets((a) => a.extension === '.png', rootAsset, true);

// Get content hash
import { getHash } from '@assetpack/core';
getHash(buffer); // CRC32 hash string

// Path utilities
import { path } from '@assetpack/core';
path.basename('/path/to/file.png');  // 'file.png'
path.dirname('/path/to/file.png');   // '/path/to'
path.extname('/path/to/file.png');   // '.png'
path.trimExt('/path/to/file.png');   // '/path/to/file'
path.joinSafe('a', 'b', 'c');        // 'a/b/c'
path.relative('/base', '/base/x.png'); // 'x.png'
path.normalizeTrim('./path/');        // './path'
path.isAbsolute('/path');             // true
```

### PipeSystem

```ts
// Access the pipe system from within a pipe
async transform(asset, options, pipeSystem) {
    pipeSystem.outputPath;    // Output directory
    pipeSystem.entryPath;     // Entry directory
    pipeSystem.pipes;         // Array of all pipes
    pipeSystem.pipeHash;      // Pipes indexed by name

    // Get another pipe by name
    const compressPipe = pipeSystem.getPipe('compress');

    // Access internal metadata keys
    pipeSystem.internalMetaData; // { copy: 'copy', ignore: 'ignore', ... }
}
```
