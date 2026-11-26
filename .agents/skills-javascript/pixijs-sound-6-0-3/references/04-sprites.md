# Sound Sprites

A `SoundSprite` is a named segment of a longer audio file, defined by `start`/`end` times in seconds — the audio equivalent of an image spritesheet.

## SoundSpriteData

```ts
interface SoundSpriteData {
    start: number;   // start time in seconds (required)
    end: number;     // end time in seconds (required, must be after start)
    speed?: number;  // optional default instance speed for this sprite (1 = 100%)
    loop?: boolean;  // optional; loop this sprite
}
```

- `duration` is computed as `end - start` and asserted `> 0` ("End time must be after start time").
- Times are **absolute** positions in the parent file, not relative offsets.
- `loop` and `speed` are optional per-sprite overrides. Any extra keys you pass are copied onto the sprite object via `Object.assign`, but only `start`/`end`/`speed`/`loop` have documented behavior.

## Adding sprites

```ts
// At creation (Options.sprites)
sound.add('sfx', {
    url: 'assets/sfx-pack.mp3',
    sprites: {
        laser:     { start: 0,    end: 0.2 },
        'alien death': { start: 1, end: 2, loop: true },
        music:     { start: 1,    end: 10, speed: 0.8 },
    },
});

// One at a time (returns the SoundSprite)
const sprite = soundObj.addSprites('ping', { start: 11, end: 12, speed: 1.2 });

// Many at once (returns a Record<string, SoundSprite>)
soundObj.addSprites({
    ping:  { start: 11, end: 12 },
    boop:  { start: 13, end: 13.5 },
});
```

Adding a sprite whose alias is already taken fires `console.assert('Alias ... is already taken')`.

## The SoundSprite object

| Property | Notes |
|---|---|
| `parent` | the owning `Sound` (nulled by `destroy()`) |
| `start` | seconds |
| `end` | seconds |
| `speed` | default instance speed (1 = 100%); parent sound speed still multiplies |
| `loop` | whether to loop |
| `duration` | `end - start` |

```ts
sprite.play(complete?: CompleteCallback): IMediaInstance | Promise<IMediaInstance>;
sprite.destroy(): void;
```

`sprite.play()` calls `parent.play({ complete, speed, end, start, loop })`.

## Playing sprites

```ts
// By alias as the play() second argument
sound.play('sfx', 'laser');

// Or via the sprite option
sound.play('sfx', { sprite: 'explosion', volume: 0.8 });

// Or directly
soundObj.sprites['laser'].play();
```

Play-time resolution (from `Sound.play`):

- `start = sprite.start + (playOptions.start || 0)`
- `end = sprite.end`
- `speed = playOptions.speed ?? sprite.speed ?? 1` — an explicit play `speed` overrides the sprite's speed; otherwise the sprite speed applies, and the parent sound's speed multiplies on top.
- `loop = sprite.loop || playOptions.loop`

## Removing

```ts
soundObj.removeSprites('laser'); // one
soundObj.removeSprites();        // all
```
