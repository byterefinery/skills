---
name: pixijs-assetpack-1-7-0
description: >
  AssetPack v1.7.0 — configurable asset pipeline for the web, designed for PixiJS but framework-agnostic.
  Use when optimizing, transforming, or bundling web assets: image compression (PNG, JPG, WebP, AVIF, BC7, ASTC, Basis, ETC),
  mipmap generation, texture atlas/spritesheet packing, cache-busting filename hashing, JSON minification,
  audio conversion (FFmpeg), font conversion (WOFF2, SDF, MSDF), Spine atlas processing, and PixiJS manifest generation.
  Covers programmatic API, CLI, config file (.assetpack.js), pipe plugin system, tags in filenames,
  assetSettings per-file overrides, caching, watch mode, and Vite integration.
metadata:
  tags:
    - assets
    - optimization
    - build-tool
    - image-compression
    - texture-packing
    - spritesheet
    - manifest
    - pixi
    - mipmap
    - font
    - spine
    - ffmpeg
    - javascript
---

# pixijs-assetpack 1.7.0

## Overview

AssetPack is a plugin-based asset pipeline that transforms, compresses, and bundles assets for web delivery. It processes an entire directory tree through a sequence of pipes (plugins), each operating on files or folders matching specific criteria. Tags embedded in filenames (e.g., `folder{tps}/`) or set via `assetSettings` control which pipes process which assets.

### Architecture

AssetPack uses three structural layers:

1. **Asset Tree** — The entry directory is scanned into an `Asset` tree. Each asset tracks its file path, buffer contents, hash, state (added/modified/deleted/normal), and metadata extracted from filename tags. Assets form both a file hierarchy (`parent`/`children`) and a transform hierarchy (`transformParent`/`transformChildren`).

2. **Pipe System** — Pipes are plugins that run sequentially. Each pipe has `test()` (should this asset be processed?), `transform()` (produce new assets), optional `start()` and `finish()` lifecycle hooks. Pipes can be grouped with `multiPipe()`. The final pipe is always `finalCopyPipe` which writes output files.

3. **Cache** — An asset graph is persisted to `.assetpack/` so incremental builds only reprocess changed files. Cache is invalidated on first run or when `cache: false`.

### Core Concepts

- **Pipes run in order** — each pipe transforms assets before the next pipe sees them
- **Tags control targeting** — `{tps}` marks a folder for texture packing, `{nc}` skips compression, `{m}` creates a manifest bundle
- **Data tags carry values** — `{family=MyFont}` passes data to the manifest
- **AssetSettings override per-file** — set pipe options for specific globs without filename tags
- **Caching is incremental** — only modified/added assets are reprocessed on subsequent runs
- **Watch mode for dev** — `assetpack.watch()` monitors filesystem and reprocesses changes

### Installation

```bash
npm install @assetpack/core
```

### Exports

```ts
// Core
import { AssetPack } from '@assetpack/core';

// Image processing
import { compress, mipmap } from '@assetpack/core/image';

// Texture packing
import { texturePacker, texturePackerCompress, texturePackerCacheBuster, texturePackerManifestMod } from '@assetpack/core/texture-packer';

// Manifest generation
import { pixiManifest } from '@assetpack/core/manifest';

// Cache busting
import { cacheBuster } from '@assetpack/core/cache-buster';

// Audio / FFmpeg
import { audio, ffmpeg } from '@assetpack/core/ffmpeg';

// Fonts
import { webfont, sdfFont, msdfFont } from '@assetpack/core/webfont';

// Spine atlas processing
import { spineAtlasCompress, spineAtlasMipmap, spineAtlasCacheBuster, spineAtlasManifestMod } from '@assetpack/core/spine';

// JSON minification
import { json } from '@assetpack/core/json';

// PixiJS opinionated preset (all pipes pre-configured)
import { pixiPipes } from '@assetpack/core/pixi';
```

## Usage

### Config File (.assetpack.js)

```js
import { compress, mipmap, pixiManifest, cacheBuster } from '@assetpack/core';

export default {
    entry: './raw-assets',
    output: './public/assets',
    cache: true,
    cacheLocation: '.assetpack',
    logLevel: 'info',
    strict: false,
    ignore: ['**/*.html'],
    pipes: [
        mipmap({
            template: '@%%x',
            resolutions: { high: 2, default: 1, low: 0.5 },
            fixedResolution: 'default',
        }),
        compress({
            png: { quality: 90 },
            jpg: {},
            webp: { quality: 80, alphaQuality: 80 },
            avif: false,
        }),
        json(),
        cacheBuster(),
        pixiManifest({
            output: 'manifest.json',
            createShortcuts: true,
            includeMetaData: true,
        }),
    ],
};
```

### Programmatic API

```ts
import { AssetPack } from '@assetpack/core';
import { compress, mipmap, pixiManifest } from '@assetpack/core';

const assetpack = new AssetPack({
    entry: './raw-assets',
    output: './public/assets',
    pipes: [
        mipmap({ resolutions: { default: 1, low: 0.5 } }),
        compress({ png: true, jpg: true, webp: true }),
        pixiManifest(),
    ],
});

// One-shot build
await assetpack.run();

// Watch mode (dev)
await assetpack.watch((root) => {
    console.log('Transform complete', root);
});
assetpack.stop();
```

### CLI

```json
{
    "scripts": {
        "prebuild": "assetpack",
        "watch:assets": "assetpack -w",
        "watch": "npm run watch:assets & vite"
    }
}
```

```bash
assetpack                    # Run with .assetpack.js config
assetpack -c ./custom.js     # Custom config file
assetpack -w                 # Watch mode
```

### PixiJS Preset (pixiPipes)

The `pixiPipes()` helper returns a pre-configured pipe array optimized for PixiJS projects:

```js
import { pixiPipes } from '@assetpack/core/pixi';

export default {
    entry: './raw-assets',
    output: './public/assets',
    pipes: [
        ...pixiPipes({
            cacheBust: true,
            resolutions: { default: 1, low: 0.5 },
            compression: { jpg: true, png: true, webp: true },
            texturePacker: { texturePacker: { nameStyle: 'short' } },
            audio: {},
            manifest: { createShortcuts: true },
        }),
    ],
};
```

This expands to: `webfont()`, `audio()`, `texturePacker()`, `mipmap()`, `spineAtlasMipmap()`, `compress()`, `spineAtlasCompress()`, `texturePackerCompress()`, `json()`, `cacheBuster()`, `spineAtlasCacheBuster()`, `texturePackerCacheBuster()`, `pixiManifest()`, `spineAtlasManifestMod()`, `texturePackerManifestMod()`.

### Vite Integration

```ts
// vite.config.mts
import { defineConfig, type Plugin } from 'vite';
import { AssetPack, type AssetPackConfig } from '@assetpack/core';

function assetpackPlugin(): Plugin {
    const apConfig: AssetPackConfig = {
        entry: './raw-assets',
        pipes: [],
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
        buildStart: async () => {
            if (mode === 'serve') {
                if (ap) return;
                ap = new AssetPack(apConfig);
                void ap.watch();
            } else {
                await new AssetPack(apConfig).run();
            }
        },
        buildEnd: async () => {
            if (ap) {
                await ap.stop();
                ap = undefined;
            }
        },
    };
}

export default defineConfig({ plugins: [assetpackPlugin()] });
```

### Tags in Filenames

Tags are embedded in filenames using curly braces. They control which pipes process which assets:

```
raw-assets/
├── hero{tps}/                    # {tps} → texture pack this folder
│   ├── idle01.png
│   ├── idle02.png
│   └── attack.png
├── bg{nc}.png                    # {nc} → skip compression
├── logo{nomip}.png               # {nomip} → skip mipmap generation
├── title{fix}.png                # {fix} → use fixedResolution only
├── bundle{m}/                    # {m} → create manifest bundle
│   ├── sprite1.png
│   └── sprite2.png
├── icon{mIgnore}.png             # {mIgnore} → exclude from manifest
├── MyFont{family=MyFont}.ttf     # data tag → passed to manifest
├── audio{wf}.otf                 # {wf} → convert to WOFF2
├── char{msdf}.ttf                # {msdf} → generate MSDF font
└── skip{ignore}/                 # {ignore} → skip entirely
```

Multiple tags: `asset{tag1}{tag2}.png`. Data tags: `asset{tag1=value}.png`.

### AssetSettings (per-file overrides)

Set pipe options for specific file globs without modifying filenames:

```js
export default {
    entry: './raw-assets',
    output: './public/assets',
    pipes: [compress({ png: { quality: 90 }, webp: { quality: 80 } })],
    assetSettings: [
        {
            files: ['**/ui/*.png'],
            settings: {
                compress: {
                    png: { quality: 95 },
                    webp: false,
                },
            },
        },
        {
            files: ['**/icons{tps}'],
            metaData: {
                tps: true,
            },
        },
    ],
};
```

### GitHub Actions Caching

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
      - name: Cache .assetpack
        uses: actions/cache@v4
        with:
          path: .assetpack
          key: ${{ runner.os }}-assetpack-${{ hashFiles('raw-assets/**/*') }}
          restore-keys: ${{ runner.os }}-assetpack-
      - run: npm run build
```

## Gotchas

- **Pipe order matters** — pipes run sequentially. `cacheBuster()` must come after all generation pipes (mipmap, compress, texturePacker). `texturePackerCacheBuster()` and `spineAtlasCacheBuster()` must follow `cacheBuster()` immediately. `pixiManifest()` should be the last pipe (before mod pipes).
- **Tags are stripped from output** — `{tps}`, `{nc}`, etc. are removed from filenames in the output directory. Use `stripTags()` utility if you need the clean name programmatically.
- **`{tps}` folder skips children** — when a folder is marked `{tps}`, its children are skipped by other pipes (the texture packer processes them internally). Do not add `{nc}` or `{nomip}` to individual images inside a `{tps}` folder.
- **`compress()` keeps originals by default** — if `png: false`, the original PNG is passed through. Use `png: 'skip'` to exclude the original entirely.
- **`texturePackerCompress` must match `compress` options** — the same compression options must be passed to both `compress()` and `texturePackerCompress()` so the atlas JSON references the correct compressed filenames.
- **`spineAtlasCompress` must match `compress` options** — same rule: pass identical options so atlas files reference correct compressed textures.
- **`spineAtlasMipmap` must match `mipmap` options** — pass the same `resolutions` and `template` so atlas coordinate rescaling matches the actual image resolutions.
- **`cacheBuster` renames files** — it appends a content hash to filenames. Atlas/manifest references are fixed by `texturePackerCacheBuster` and `spineAtlasCacheBuster` — these must follow `cacheBuster` in the pipe array.
- **`pixiManifest` output is relative** — `output: 'manifest.json'` writes to the output directory root. Use `output: './sub/manifest.json'` for subdirectories.
- **`texturePackerManifestMod` and `spineAtlasManifestMod` must follow `pixiManifest`** — they read the generated manifest and modify it in place. They share the same `output` path.
- **`{fix}` tag uses `fixedResolution`** — when `{fix}` is present, only one resolution is generated (the `fixedResolution` key from `resolutions`). The image is still resized to that resolution's scale.
- **`{nomip}` skips mipmap, not compression** — use `{nc}` to skip compression separately.
- **`{copy}` bypasses all pipes** — forces direct copy to output without any processing.
- **`{ignore}` excludes entirely** — the asset is not processed or copied.
- **`sdfFont`/`msdfFont` only work with `.ttf`** — the SDF/MSDF plugins require TrueType input. Use `webfont()` for OTF/SVG → WOFF2 conversion.
- **SDF/MSDF textures are marked `{nc}{nomip}{mIgnore}`** — the generated font textures cannot be recompressed or mipped (coordinates are baked in).
- **`webfont()` tag is `{wf}`** — not `{font}`. The SDF/MSDF plugins use `{sdf}` and `{msdf}` tags respectively.
- **`audio()` default output is dual-format** — it generates both `.mp3` (96kbps mono 48kHz) and `.ogg` (32kbps mono 22050Hz). Customize via `ffmpeg` options.
- **`ffmpeg()` requires inputs array** — empty `inputs` throws an error. Always specify which extensions to process.
- **Caching requires `cache: true`** — the default is `true`, but if you set `cache: false`, the output directory is wiped on every run.
- **Cache is invalidated on config change** — the cache name is generated from the config, so changing pipe options or order invalidates the cache.
- **`strict: true` throws on failures** — useful for CI. Default `false` logs errors but continues.
- **`logLevel` values** — `'verbose'`, `'info'`, `'warn'`, `'error'`. Default `'info'`.
- **`assetpack.watch()` returns a promise** — it resolves after the first transform completes. Use the callback for subsequent transforms.
- **`assetpack.rootAsset`** — access the root `Asset` node after processing. Useful for custom post-processing.
- **`json()` converts `.json5` to `.json`** — it parses JSON5 (comments, trailing commas) and outputs standard JSON.
- **`nameStyle: 'short'` in manifest** — bundle names use folder basename. `nameStyle: 'relative'` uses full relative path. Use `'relative'` if you have duplicate folder names.
- **`createShortcuts: true`** — adds basename aliases to manifest entries. E.g., `ui/button.png` gets alias `button.png` too.
- **`includeFileSizes` in manifest** — when `'gzip'` or `'raw'`, adds `progressSize` to each src for loading progress bars. `texturePackerManifestMod` must follow to include atlas texture sizes.
- **`maximumTextureSize` in texturePacker** — defaults to 4096. If the atlas exceeds this, it splits into multiple sheets with `related_multi_packs` references.
- **Texture packer `autodetectAnimations`** — groups files with numeric suffixes (e.g., `idle01.png`, `idle02.png`) into animation sequences in the JSON.
- **`addFrameNames: true` in texturePacker** — adds `frameNames` metadata to the asset, available in the manifest `data` field.

## References

- [01-core-api](references/01-core-api.md) — AssetPack class, Asset tree, PipeSystem, config options, caching, watch mode, programmatic API
- [02-pipes-overview](references/02-pipes-overview.md) — Pipe interface, multiPipe, pipe ordering, test/transform/start/finish lifecycle, internal tags
- [03-image-pipes](references/03-image-pipes.md) — compress (PNG/JPG/WebP/AVIF/BC7/ASTC/Basis/ETC), mipmap (resolutions, template, fix/nomip tags)
- [04-texture-packer](references/04-texture-packer.md) — texturePacker (atlases, resolutions, nameStyle), texturePackerCompress, texturePackerCacheBuster, texturePackerManifestMod
- [05-manifest](references/05-manifest.md) — pixiManifest (bundles, aliases, metadata, file sizes), spineAtlasManifestMod, texturePackerManifestMod
- [06-cache-buster](references/06-cache-buster.md) — cacheBuster (content hashing), texturePackerCacheBuster, spineAtlasCacheBuster
- [07-fonts](references/07-fonts.md) — webfont (WOFF2), sdfFont/MSDF (SDF/MSDF bitmap fonts), tags, options
- [08-audio-ffmpeg](references/08-audio-ffmpeg.md) — audio pipe, ffmpeg pipe, format conversion, compression options
- [09-spine](references/09-spine.md) — spineAtlasCompress, spineAtlasMipmap, spineAtlasCacheBuster, spineAtlasManifestMod
- [10-advanced](references/10-advanced.md) — pixiPipes preset, Vite plugin, CLI, GitHub Actions, custom pipes, AssetSettings, tag system deep dive
