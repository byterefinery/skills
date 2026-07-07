# Manifest

## pixiManifest

Generates a PixiJS-compatible manifest file listing all processed assets.

### Import

```ts
import { pixiManifest } from '@assetpack/core/manifest';
```

### Options

```ts
pixiManifest({
    output: 'manifest.json',       // Output path (relative to output dir)
    createShortcuts: false,        // Add basename aliases
    trimExtensions: false,         // Remove extensions from aliases
    includeMetaData: true,         // Include tags in data field
    includeFileSizes: false,       // false | 'gzip' | 'raw'
    nameStyle: 'short',            // 'short' | 'relative'
    legacyMetaDataOutput: true,    // Put all tags in data.tags
    srcSortOptions: {              // Sort src array
        order: 'descending',       // 'ascending' | 'descending'
        collatorOptions: {},       // Intl.Collator options
    },
});
```

### Default Options

```ts
{
    output: 'manifest.json',
    createShortcuts: false,
    trimExtensions: false,
    includeMetaData: true,
    legacyMetaDataOutput: true,
    includeFileSizes: false,
    nameStyle: 'short',
}
```

### Tags

| Tag | Scope | Description |
|---|---|---|
| `{m}` | folder | Creates a bundle entry in the manifest |
| `{mIgnore}` | both | Excludes asset from manifest |

### Manifest Format

```json
{
    "bundles": [
        {
            "name": "default",
            "assets": [
                {
                    "alias": ["hero", "hero.png", "png"],
                    "src": ["hero.png", "hero.webp"],
                    "data": {
                        "tags": { "nc": false },
                        "family": "MyFont"
                    }
                }
            ]
        },
        {
            "name": "bundle",
            "assets": [
                {
                    "alias": ["bundle/sprite1", "sprite1"],
                    "src": ["bundle/sprite1.png"],
                    "data": { "tags": {} }
                }
            ]
        }
    ]
}
```

### Alias Generation

With `createShortcuts: true` and `trimExtensions: true`:

```
Path: ui/button.png
Aliases: ["ui/button.png", "ui/button", "button.png", "button"]
```

With both `false`:

```
Path: ui/button.png
Aliases: ["ui/button.png"]
```

### File Sizes

When `includeFileSizes: 'gzip'` or `'raw'`:

```json
{
    "src": [
        "hero.png",
        { "src": "hero.webp", "progressSize": 12.5 }
    ]
}
```

Sizes are in kilobytes. Use `texturePackerManifestMod` to include atlas texture sizes.

### Bundle Names

- `nameStyle: 'short'` — uses folder basename (e.g., `bundle`)
- `nameStyle: 'relative'` — uses full relative path (e.g., `scenes/bundle`)
- Duplicate short names are auto-renamed to relative paths with a warning

---

## spineAtlasManifestMod

Removes atlas texture references from the manifest (since the atlas handles loading them).

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
- Removes any manifest entries for textures referenced by atlases
- Rewrites the manifest

---

## texturePackerManifestMod

Augments manifest with atlas texture sizes. See [04-texture-packer.md](references/04-texture-packer.md).

### Import

```ts
import { texturePackerManifestMod } from '@assetpack/core/texture-packer';
```

### Usage

```ts
pipes: [
    pixiManifest({ includeFileSizes: 'gzip' }),
    texturePackerManifestMod({ includeFileSizes: 'gzip' }),
],
```
