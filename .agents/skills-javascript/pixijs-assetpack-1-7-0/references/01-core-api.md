# AssetPack Core API

## AssetPack Class

The main entry point. Creates an asset pipeline from config.

```ts
import { AssetPack } from '@assetpack/core';

const assetpack = new AssetPack({
    entry: './raw-assets',      // Required: source directory
    output: './public/assets',  // Required: output directory
    ignore: ['**/*.html'],      // Glob patterns to skip
    cache: true,                // Enable incremental caching (default)
    cacheLocation: '.assetpack', // Cache directory (default)
    logLevel: 'info',           // 'verbose' | 'info' | 'warn' | 'error'
    strict: false,              // Throw on pipe failures
    pipes: [],                  // Array of pipe plugins
    assetSettings: [],          // Per-file/glob overrides
});
```

### Methods

```ts
// One-shot build — processes all assets and resolves when done
await assetpack.run();

// Watch mode — monitors filesystem for changes
// Returns a promise that resolves after the first transform completes
const rootAsset = await assetpack.watch((root) => {
    // Called after each subsequent transform
    console.log('Updated', root);
});

// Stop watching
await assetpack.stop();
```

### Properties

```ts
assetpack.config;      // The resolved config object
assetpack.rootAsset;   // Root Asset node (available after run/watch)
```

## Asset Class

Represents a file or directory in the asset tree.

```ts
import type { Asset } from '@assetpack/core';

// Properties
asset.path;                    // Full path to the file/folder
asset.filename;                // Basename (e.g., 'hero.png')
asset.extension;               // Extension (e.g., '.png')
asset.directory;               // Directory path
asset.isFolder;                // Whether this is a directory
asset.state;                   // 'added' | 'modified' | 'deleted' | 'normal'
asset.skip;                    // If true, skip processing this asset
asset.transformName;           // Name of the pipe that transformed this asset

// Metadata (from filename tags + assetSettings)
asset.metaData;                // Tags on this asset only
asset.inheritedMetaData;       // Tags inherited from parent folders
asset.allMetaData;             // Combined: inherited + own tags
asset.settings;                // Per-file pipe settings from assetSettings

// Transform hierarchy
asset.transformParent;         // Parent in transform tree
asset.transformChildren;       // Children created by transforms
asset.rootTransformAsset;      // Root of the transform tree

// File hierarchy
asset.parent;                  // Parent in file tree
asset.children;                // Children in file tree
asset.rootAsset;               // Root of the file tree

// Content
asset.buffer;                  // File contents as Buffer (lazy-loaded)
asset.hash;                    // Content hash (CRC32)

// Transform stats
asset.stats;                   // { date, duration, success, error? }

// Methods
asset.addChild(child);
asset.removeChild(child);
asset.addTransformChild(child);
asset.skipChildren();                              // Mark all descendants to skip
asset.getFinalTransformedChildren();               // Leaf nodes of transform tree
asset.markParentAsModified();                      // Bubble modified state up
asset.releaseBuffers();                            // Free transform children buffers
asset.releaseChildrenBuffers();                    // Free all descendant buffers
asset.getPublicMetaData(internalPipeData);         // Non-internal metadata
asset.getInternalMetaData(internalPipeData);       // Internal pipe metadata only
```

## AssetPackConfig

```ts
interface AssetPackConfig {
    entry?: string;              // Required: source directory
    output?: string;             // Required: output directory
    ignore?: string[];           // Glob patterns to exclude
    cache?: boolean;             // Enable caching (default: true)
    cacheLocation?: string;      // Cache directory (default: '.assetpack')
    logLevel?: string;           // 'verbose' | 'info' | 'warn' | 'error' (default: 'info')
    strict?: boolean;            // Throw on failures (default: false)
    pipes?: (AssetPipe | AssetPipe[])[];  // Plugin array
    assetSettings?: AssetSettings[];       // Per-file overrides
}

interface AssetSettings {
    files: string[];                              // Glob patterns
    settings?: Record<string, any>;               // Pipe-specific options
    metaData?: Record<string, any>;               // Tags to apply
}
```

### assetSettings Example

```js
export default {
    entry: './raw-assets',
    output: './public/assets',
    pipes: [
        compress({ png: { quality: 80 }, webp: { quality: 60 } }),
        mipmap({ resolutions: { default: 1, low: 0.5 } }),
    ],
    assetSettings: [
        // High quality for UI assets
        {
            files: ['**/ui/*.png'],
            settings: {
                compress: {
                    png: { quality: 95 },
                    webp: false,
                },
            },
        },
        // Mark a folder for texture packing without renaming
        {
            files: ['**/characters'],
            metaData: {
                tps: true,
            },
        },
        // Skip mipmaps for icons
        {
            files: ['**/icons/*.png'],
            metaData: {
                nomip: true,
            },
        },
    ],
};
```

## Caching

AssetPack caches the asset graph to `.assetpack/` by default. The cache name is derived from the config (pipe names, options, entry/output paths). Changing any config detail invalidates the cache.

- **First run**: cache not found → output directory is cleared, full build
- **Subsequent runs**: cache found → only `added`/`modified` assets are processed
- **`cache: false`**: output directory and cache are cleared every run
- **`cacheLocation`**: change the cache directory path

### Cache Invalidation Triggers

- Pipe array changes (add/remove/reorder pipes)
- Pipe options change
- Entry or output path changes
- Manual deletion of `.assetpack/` directory
- File additions, modifications, or deletions in the entry directory

## Watch Mode

```ts
const assetpack = new AssetPack(config);

// watch() returns a promise resolving after first transform
await assetpack.watch((root) => {
    // Called after every subsequent transform
    console.log('Assets updated');
});

// Stop watching
await assetpack.stop();
```

Watch mode uses `chokidar` internally. It detects file additions, modifications, and deletions. Only changed assets and their dependents are reprocessed.

## CLI

```bash
# Run with default .assetpack.js config
assetpack

# Custom config file
assetpack -c ./my-config.js

# Watch mode
assetpack -w

# Watch with custom config
assetpack -c ./dev.js -w
```

The CLI searches for `.assetpack.js` in the current directory and parent directories (using `find-up`). Both CommonJS and ESM configs are supported.

### Package.json Scripts

```json
{
    "scripts": {
        "prebuild": "assetpack",
        "build": "vite build",
        "watch:assets": "assetpack -w",
        "dev": "npm run watch:assets & vite"
    }
}
```
