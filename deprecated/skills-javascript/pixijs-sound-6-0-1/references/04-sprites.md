# Sound Sprites

## Overview

Sound sprites divide a single audio file into named segments, similar to image spritesheets. Each sprite has a `start` and `end` time (in seconds) and an optional `speed` override. This reduces network requests by loading one file instead of many small ones.

## SoundSpriteData

```ts
interface SoundSpriteData {
    start: number;   // Start time in seconds
    end: number;     // End time in seconds
    speed?: number;  // Optional speed override (1 = 100%)
}
```

## Creating Sprites

### At Sound Creation

```ts
sound.add('sfx', {
    url: 'assets/sfx-pack.mp3',
    sprites: {
        laser:     { start: 0,    end: 0.2 },
        explosion: { start: 0.3,  end: 0.8 },
        ping:      { start: 1,    end: 1.5 },
        music:     { start: 2,    end: 12, speed: 0.8 },
    },
});
```

### After Creation via SoundLibrary

```ts
const sfx = sound.find('sfx');
sfx.addSprites({
    laser: { start: 0, end: 0.2 },
    explosion: { start: 0.3, end: 0.8 },
});
```

### Single Sprite

```ts
sfx.addSprites('ping', { start: 1, end: 1.5 });
```

## SoundSprite Object

Each sprite is a `SoundSprite` instance with these properties:

| Property | Type | Description |
|---|---|---|
| `parent` | `Sound` (readonly) | Parent Sound object |
| `start` | `number` (readonly) | Start time in seconds |
| `end` | `number` (readonly) | End time in seconds |
| `speed` | `number` (readonly) | Speed override, or parent's speed |
| `duration` | `number` (readonly) | Duration (`end - start`) |
| `loop` | `boolean` (readonly) | Loop flag |

### Accessing Sprites

```ts
const sprites = sfx.sprites;
const laser = sprites['laser'];

laser.start;     // 0
laser.end;       // 0.2
laser.duration;  // 0.2
laser.speed;     // undefined (uses parent)
```

### Playing Sprites

```ts
// Via SoundLibrary
sound.play('sfx', 'laser');

// Via Sound object
sfx.play('laser');

// Via SoundSprite object
sfx.sprites['laser'].play();
sfx.sprites['laser'].play((soundObj) => { /* complete */ });

// With additional options
sfx.play({ sprite: 'explosion', volume: 0.8, speed: 1.5 });
```

## Removing Sprites

```ts
// Remove single sprite
sfx.removeSprites('laser');

// Remove all sprites
sfx.removeSprites();
```

## Sprite Examples

### Game Sound Effects Pack

```ts
sound.add('game-sfx', {
    url: 'assets/game-sfx.mp3',
    sprites: {
        // Combat
        sword_swing:  { start: 0,    end: 0.15 },
        sword_hit:    { start: 0.2,  end: 0.35 },
        arrow_fire:   { start: 0.4,  end: 0.55 },
        arrow_hit:    { start: 0.6,  end: 0.75 },
        magic_cast:   { start: 0.8,  end: 1.2 },
        magic_hit:    { start: 1.3,  end: 1.6 },

        // UI
        click:        { start: 2,    end: 2.05 },
        hover:        { start: 2.1,  end: 2.15 },
        select:       { start: 2.2,  end: 2.3 },
        error:        { start: 2.4,  end: 2.6 },
        success:      { start: 2.7,  end: 2.9 },

        // Environment
        footsteps:    { start: 3,    end: 3.5 },
        door_open:    { start: 3.6,  end: 4.0 },
        wind:         { start: 4.1,  end: 6.1, speed: 0.5 },
    },
});

// Play effects
sound.play('game-sfx', 'sword_swing');
sound.play('game-sfx', 'magic_cast');
sound.play('game-sfx', 'click');
```

### Music with Intro/Outro Sprites

```ts
sound.add('track', {
    url: 'assets/track.mp3',
    loop: true,
    sprites: {
        intro: { start: 0, end: 15 },
        main:  { start: 15, end: 55 },
        outro: { start: 55, end: 70 },
    },
});

// Play intro, then loop main section
sound.play('track', 'intro', (soundObj) => {
    soundObj.play('main');
});
```

## Sprite vs Multiple Files

| Approach | Pros | Cons |
|---|---|---|
| **Sprites** | One HTTP request, lower latency, easier management | Must know exact timestamps, can't preload individual segments |
| **Multiple files** | Independent loading, can lazy-load | More HTTP requests, higher latency for first play |

Use sprites for:
- Game sound effect packs (many short SFX)
- UI sound libraries
- Audio where all segments are used frequently

Use separate files for:
- Large audio assets used independently
- Streaming/background music
- Dynamic content where segments aren't known at build time
