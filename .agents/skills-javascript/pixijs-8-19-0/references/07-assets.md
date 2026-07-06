# Assets

## Assets Manager

Unified asset loading, resolving, caching, and format detection.

### Initialization

```ts
import { Assets } from 'pixi.js';

// Basic init
await Assets.init();

// With base path
await Assets.init({
    basePath: 'https://cdn.example.com/assets/',
});

// With manifest
await Assets.init({
    basePath: 'assets/',
    manifest: {
        bundles: [
            {
                name: 'game-screen',
                assets: [
                    { alias: 'hero', src: 'hero.{png,webp,avif}' },
                    { alias: 'map', src: 'map.json' },
                    { alias: 'bg', src: 'bg.png' },
                ],
            },
        ],
    },
});

// With format detection preferences
await Assets.init({
    basePath: 'assets/',
    texturePreference: {
        resolution: window.devicePixelRatio,
        format: ['avif', 'webp', 'png', 'jpg'],
    },
});

// With search params (cache busting)
await Assets.init({
    defaultSearchParams: { version: '1.0.0' },
});
```

### Loading

```ts
// Load single asset
const texture = await Assets.load('assets/sprite.png');

// Load multiple assets
const assets = await Assets.load([
    'assets/sprite1.png',
    'assets/sprite2.png',
    'assets/data.json',
]);

// Load with progress callback
const texture = await Assets.load('assets/sprite.png', (progress) => {
    console.log(`Loading: ${Math.round(progress * 100)}%`);
});

// Load by alias
Assets.add({ alias: 'hero', src: 'assets/hero.png' });
const texture = await Assets.load('hero');

// Load bundle
await Assets.init({ manifest: 'manifest.json' });
const bundle = await Assets.loadBundle('game-screen');

// Load bundle with progress
await Assets.loadBundle('game-screen', (progress) => {
    updateLoadingBar(progress);
});
```

### Accessing Loaded Assets

```ts
// Get by URL
const texture = Assets.get('assets/sprite.png');

// Get by alias
const texture = Assets.get('hero');

// Check if loaded
const hasAsset = Assets.has('assets/sprite.png');

// Get bundle
const bundle = Assets.getBundle('game-screen');
```

### Adding Assets Manually

```ts
// Add single asset mapping
Assets.add({ alias: 'hero', src: 'assets/hero.png' });

// Add multiple
Assets.add([
    { alias: 'bg', src: 'assets/bg.png' },
    { alias: 'ui', src: 'assets/ui.json' },
]);

// Add with multiple aliases
Assets.add({ alias: ['hero', 'player', 'character'], src: 'assets/hero.png' });
```

### Removing Assets

```ts
// Remove single
Assets.remove('assets/sprite.png');

// Remove by alias
Assets.remove('hero');

// Remove bundle
Assets.removeBundle('game-screen');

// Clear all
Assets.reset();
```

## Bundles

Groups of assets loaded together.

```ts
// Define bundles
await Assets.init({
    manifest: {
        bundles: [
            {
                name: 'level-1',
                assets: [
                    { alias: 'level-bg', src: 'levels/1/bg.{png,webp}' },
                    { alias: 'level-enemy', src: 'levels/1/enemy.png' },
                    { alias: 'level-data', src: 'levels/1/data.json' },
                ],
            },
            {
                name: 'level-2',
                assets: [
                    { alias: 'level-bg', src: 'levels/2/bg.{png,webp}' },
                    { alias: 'level-boss', src: 'levels/2/boss.png' },
                ],
            },
        ],
    },
});

// Load a bundle
const assets = await Assets.loadBundle('level-1');

// Access assets
const bg = assets['level-bg'];
const enemy = assets['level-enemy'];

// Unload a bundle (free memory)
await Assets.unloadBundle('level-1');
```

## Manifest

JSON manifest defining asset bundles.

```json
{
    "bundles": [
        {
            "name": "game-assets",
            "assets": [
                {
                    "alias": "hero",
                    "src": "characters/hero.{png,webp,avif}"
                },
                {
                    "alias": "hero-spritesheet",
                    "src": "characters/hero-atlas.json"
                },
                {
                    "alias": "bg-music",
                    "src": "audio/bg-music.mp3"
                },
                {
                    "alias": "level-config",
                    "src": "config/level.json"
                }
            ]
        }
    ]
}
```

### Format Variants

Use `{...}` syntax for automatic format selection:

```ts
// Tries avif first, then webp, then png
{ alias: 'sprite', src: 'sprite.{avif,webp,png}' }

// With resolution variants
{ alias: 'sprite', src: 'sprite@{1,2}x.{png,webp}' }
// Generates: sprite.png, sprite@2x.png, sprite.webp, sprite@2x.webp
```

## Cache

```ts
import { Cache } from 'pixi.js';

// Get from cache
const texture = Cache.get('assets/sprite.png');

// Check existence
const exists = Cache.has('assets/sprite.png');

// Get all keys
const keys = Cache.keys();

// Remove from cache
Cache.remove('assets/sprite.png');

// Clear all
Cache.reset();
```

### Cache Parser

Custom cache parsing for custom data types:

```ts
import { CacheParser, ExtensionType, extensions } from 'pixi.js';

class MyCacheParser {
    public static extension = {
        type: ExtensionType.CacheParser,
        name: 'my-cache-parser',
    };

    public static test(url: string): boolean {
        return url.endsWith('.myformat');
    }

    public static parse(data: any, url: string): any {
        return data.processed;
    }
}

extensions.add(MyCacheParser);
```

## Loader

The underlying loader system (usually accessed via Assets).

```ts
import { Loader } from 'pixi.js';

// Direct loading (bypasses Assets)
const loader = new Loader();
const data = await loader.load('assets/data.json');
```

### Load Parsers

Built-in parsers:

| Parser | Formats | Extension Type |
|---|---|---|
| `loadTextures` | PNG, JPG, WebP, AVIF, GIF | LoadParser |
| `loadSVG` | SVG | LoadParser |
| `loadVideoTextures` | MP4, WebM, OGV | LoadParser |
| `loadJson` | JSON | LoadParser |
| `loadTxt` | TXT | LoadParser |
| `loadWebFont` | WOFF, WOFF2, TTF, OTF | LoadParser |
| `bitmapFontXMLParser` | FNT (XML) | LoadParser |
| `bitmapFontTextParser` | FNT (text) | LoadParser |

## Resolver

URL resolution and format detection.

```ts
import { Resolver } from 'pixi.js';

// Resolve URL with format detection
const resolved = await Assets.resolver.resolve('sprite.{png,webp}');
// Returns: { src: 'sprite.webp', ... } (best format for browser)

// Resolve with preferences
const resolved = await Assets.resolver.resolve({
    src: 'sprite.{png,webp}',
    preference: { format: ['webp', 'png'] },
});
```

## Format Detection

Automatic browser format detection on init.

```ts
// Auto-detects supported formats
await Assets.init();

// Detected formats available
const formats = Assets.detects;

// Skip detection (must set texturePreference manually)
await Assets.init({
    skipDetections: true,
    texturePreference: {
        format: ['webp', 'png'],
    },
});
```

## Background Loading

Load assets in background without blocking.

```ts
import { BackgroundLoader } from 'pixi.js';

const bgLoader = new BackgroundLoader();

// Queue assets for background loading
bgLoader.queue(['assets/sprite1.png', 'assets/sprite2.png']);

// Start background loading
bgLoader.start();

// Check progress
const progress = bgLoader.progress;

// Wait for completion
await bgLoader.completed;
```

## Asset Performance Tips

- **Use bundles** — group related assets for efficient loading
- **Use format variants** — `{png,webp,avif}` for automatic best-format selection
- **Use resolution variants** — `@{1,2}x` for HiDPI support
- **Use manifests** — centralize asset definitions
- **Unload unused bundles** — `Assets.unloadBundle()` to free memory
- **Use `basePath`** — avoid repeating paths
- **Preload critical assets** — load before showing content
- **Use progress callbacks** — show loading progress to users
- **Use `skipDetections: true`** in production if you control target formats
- **Cache parser for custom formats** — avoid re-parsing loaded data
