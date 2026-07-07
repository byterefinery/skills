# Advanced Usage

## pixiPipes Preset

The `pixiPipes()` helper returns a complete, pre-configured pipe array for PixiJS projects.

### Import

```ts
import { pixiPipes } from '@assetpack/core/pixi';
```

### Options

```ts
pixiPipes({
    cacheBust: true,                  // Enable cache-busting (default: true)
    resolutions: {                    // Resolution map (default: { default: 1, low: 0.5 })
        default: 1,
        low: 0.5,
    },
    compression: {                    // Compress options | false to disable
        jpg: true,
        png: true,
        webp: true,
    },
    texturePacker: {                  // Texture packer options
        texturePacker: {
            nameStyle: 'short',
        },
    },
    audio: {},                        // Audio/FFmpeg options
    manifest: {                       // Manifest options
        createShortcuts: true,
    },
});
```

### Expanded Pipe Order

```
1.  webfont()
2.  audio(options)
3.  texturePacker(options)
4.  mipmap(options)
5.  spineAtlasMipmap(options)
6.  compress(options)          [if compression !== false]
7.  spineAtlasCompress(options) [if compression !== false]
8.  texturePackerCompress(options) [if compression !== false]
9.  json()
10. cacheBuster()               [if cacheBust]
11. spineAtlasCacheBuster()     [if cacheBust]
12. texturePackerCacheBuster()  [if cacheBust]
13. pixiManifest(options)
14. spineAtlasManifestMod(options)
15. texturePackerManifestMod(options)
```

### Customizing

Add extra pipes before or after the preset:

```ts
import { pixiPipes } from '@assetpack/core/pixi';
import { sdfFont } from '@assetpack/core/webfont';

export default {
    entry: './raw-assets',
    output: './public/assets',
    pipes: [
        sdfFont({ font: { fontSize: 48, textureSize: [1024, 1024] } }),
        ...pixiPipes({
            resolutions: { high: 2, default: 1, low: 0.5 },
            compression: { png: true, webp: true, avif: true },
        }),
    ],
};
```

---

## Vite Plugin

Full Vite integration with watch mode in dev and one-shot in production:

```ts
// vite.config.mts
import { defineConfig, type Plugin, type ResolvedConfig } from 'vite';
import { AssetPack, type AssetPackConfig } from '@assetpack/core';
import { pixiPipes } from '@assetpack/core/pixi';

function assetpackPlugin(config?: Partial<AssetPackConfig>): Plugin {
    const apConfig: AssetPackConfig = {
        entry: './raw-assets',
        pipes: pixiPipes(),
        ...config,
    };
    let mode: string;
    let ap: AssetPack | undefined;

    return {
        name: 'vite-plugin-assetpack',
        configResolved(resolvedConfig) {
            mode = resolvedConfig.command;
            if (resolvedConfig.publicDir && !apConfig.output) {
                const publicDir = resolvedConfig.publicDir.replace(process.cwd(), '');
                apConfig.output = `.${publicDir}/assets/`;
            }
        },
        async buildStart() {
            if (mode === 'serve') {
                if (ap) return;
                ap = new AssetPack(apConfig);
                void ap.watch();
            } else {
                await new AssetPack(apConfig).run();
            }
        },
        async buildEnd() {
            if (ap) {
                await ap.stop();
                ap = undefined;
            }
        },
    };
}

export default defineConfig({
    plugins: [
        assetpackPlugin({
            entry: './src/assets',
        }),
    ],
});
```

---

## GitHub Actions

Cache the `.assetpack` directory to speed up CI builds:

```yaml
name: AssetPack
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: npm ci

      # Generate hash from asset filenames
      - name: Generate hash
        id: hash-names
        run: echo "NAMES_HASH=$(find ./raw-assets -type f | sort | md5sum | cut -d' ' -f1)" >> $GITHUB_ENV

      # Cache .assetpack directory
      - name: Cache assetpack
        uses: actions/cache@v4
        with:
          path: .assetpack
          key: ${{ runner.os }}-assetpack-${{ hashFiles('**/package-lock.json') }}-${{ hashFiles('raw-assets/**/*') }}-${{ env.NAMES_HASH }}
          restore-keys: ${{ runner.os }}-assetpack-${{ hashFiles('**/package-lock.json') }}

      - run: npm run build
```

---

## Custom Pipes

Create a custom pipe for any transformation:

```ts
import { Asset, AssetPipe, createNewAssetAt, checkExt } from '@assetpack/core';
import sharp from 'sharp';

function resizeToSquare(): AssetPipe {
    return {
        folder: false,
        name: 'resize-to-square',
        defaultOptions: { size: 256 },
        tags: {
            square: 'square',
        },
        test(asset: Asset, options) {
            return asset.allMetaData.square && checkExt(asset.path, '.png', '.jpg');
        },
        async transform(asset: Asset, options) {
            const { size } = options;
            const buffer = await sharp(asset.buffer)
                .resize(size, size, { fit: 'contain', background: { r: 0, g: 0, b: 0, alpha: 0 } })
                .toBuffer();

            const newAsset = createNewAssetAt(asset, asset.filename);
            newAsset.buffer = buffer;
            return [newAsset];
        },
    };
}
```

---

## Tag System Deep Dive

### Tag Syntax

```
filename{tag}.ext          → simple tag
filename{tag=value}.ext    → data tag
filename{tag=v1&v2}.ext    → multi-value tag
filename{tag1}{tag2}.ext   → multiple tags
```

### Tag Extraction

Tags are extracted from filenames during asset tree construction. The `extractTagsFromFileName` utility parses curly-brace patterns and populates `asset.metaData`.

```ts
// filename: hero{tps}{nc}.png
asset.metaData = { tps: true, nc: true };

// filename: MyFont{family=MyFont}.ttf
asset.metaData = { family: 'MyFont' };

// filename: sprite{quality=high&fast}.png
asset.metaData = { quality: ['high', 'fast'] };
```

### Tag Inheritance

Tags on parent folders are inherited by children via `inheritedMetaData`. `allMetaData` combines inherited and own tags (own tags override inherited).

```
raw-assets/
├── ui{nc}/           ← {nc} on folder
│   ├── button.png    ← inherits {nc}
│   └── icon.png      ← inherits {nc}
└── hero.png          ← no {nc}
```

### Internal Tags

Tags listed in a pipe's `internalTags` are excluded from the manifest `data` field but still accessible internally. Built-in internal tags: `copy`, `ignore`.

### Data Tags in Manifest

When `includeMetaData: true` in `pixiManifest()`, data tags appear in the manifest:

```json
{
    "data": {
        "family": "MyFont",
        "tags": { "wf": true }
    }
}
```

With `legacyMetaDataOutput: false`, only internal tags go into `data.tags`, and other tags go directly into `data`.
