# Assets Integration

## Overview

PixiJS Sound registers a `soundAsset` extension that integrates with `PIXI.Assets`. Audio files loaded through Assets are automatically registered with the sound library using the file's basename as the alias.

## Automatic Registration

```ts
import { Assets } from 'pixi.js';
import { sound } from '@pixi/sound';

// Import @pixi/sound to register the extension
import '@pixi/sound';

// Load audio — auto-registered as 'explosion'
const soundObj = await Assets.load('assets/explosion.mp3');

// Play by alias
sound.play('explosion');
```

## Alias Resolution

The alias is derived from the URL:

| URL | Alias |
|---|---|
| `assets/explosion.mp3` | `explosion` |
| `assets/music.ogg` | `music` |
| `sfx/laser.wav` | `laser` |

Override with explicit alias:

```ts
Assets.add({
    alias: ['my-explosion'],
    src: 'assets/explosion.mp3',
});

const soundObj = await Assets.load('my-explosion');
sound.play('my-explosion');
```

## Manifest Loading

```ts
await Assets.load({
    name: 'game-assets',
    assets: [
        { alias: 'explosion', src: 'assets/explosion.mp3' },
        { alias: 'music', src: 'assets/music.mp3' },
        { alias: 'sfx', src: 'assets/sfx-pack.mp3' },
    ],
});

sound.play('explosion');
sound.play('music');
```

## Unloading

Sounds loaded via Assets are automatically unregistered when unloaded:

```ts
// Unload removes from sound library
await Assets.unload('assets/explosion.mp3');

// Or by alias
await Assets.unload('explosion');
```

## Loading Options

Pass Sound options through Assets data:

```ts
const soundObj = await Assets.load({
    src: 'assets/music.mp3',
    data: {
        loop: true,
        volume: 0.8,
        preload: true,
        sprites: {
            intro: { start: 0, end: 15 },
            main: { start: 15, end: 55 },
        },
        loaded(err, soundObj) {
            if (!err) soundObj.play();
        },
    },
});
```

## Format Support

The soundAsset extension detects supported formats via `utils.supported`. Supported extensions:

- `ogg`, `oga`, `opus`
- `m4a`
- `mp3`, `mpeg`
- `wav`
- `aiff`
- `wma`
- `mid`
- `caf`

Data URIs with `audio/mpeg` and `audio/ogg` MIME types are also supported.

## Extension Registration

The `soundAsset` extension is automatically registered when importing `@pixi/sound`. It registers:

- **Asset detection** — Adds supported audio extensions to the format list
- **Load parser** — High priority parser that handles audio file loading
- **Unload handler** — Removes sounds from the library on unload

## Manual vs Assets Loading

| Approach | When to Use |
|---|---|
| `sound.add()` | Full control, custom options, dynamic sounds |
| `Assets.load()` | Integrated with other assets, manifest loading, auto-cleanup |
| `Sound.from()` | Creating standalone Sound objects (not registered) |

## Example: Full Game Setup

```ts
import { Application, Assets } from 'pixi.js';
import { sound } from '@pixi/sound';

// Initialize app
const app = new Application();
await app.init({ width: 800, height: 600 });
document.body.appendChild(app.canvas);

// Load all game assets
await Assets.load({
    name: 'game',
    assets: [
        // Audio
        { alias: 'bgm', src: 'assets/bgm.mp3' },
        { alias: 'sfx', src: 'assets/sfx-pack.mp3' },
        // Sprites
        { alias: 'player', src: 'assets/player.png' },
        { alias: 'enemy', src: 'assets/enemy.png' },
    ],
});

// Play background music
sound.play('bgm', { loop: true, volume: 0.6 });

// Play SFX
sound.play('sfx', 'laser');
```
