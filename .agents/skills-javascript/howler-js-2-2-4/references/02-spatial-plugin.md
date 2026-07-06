# Spatial Plugin

The spatial plugin adds stereo panning and 3D positional audio. It requires Web Audio — all spatial methods silently no-op on HTML5 Audio.

## Stereo Panning

### Per-Sound Stereo

Set `stereo` in constructor or call `stereo(pan)` on a Howl:

```js
const leftSound = new Howl({
  src: ['ambient.mp3'],
  stereo: -1.0,  // full left
});

const rightSound = new Howl({
  src: ['ambient.mp3'],
  stereo: 1.0,   // full right
});

// Change at runtime
leftSound.stereo(-0.5);
```

Range: `-1.0` (full left) to `1.0` (full right), `0` (center).

Under the hood, uses `StereoPannerNode` when available, falling back to `PannerNode` with `equalpower` panning model.

### Global Stereo

```js
Howler.stereo(0.3);  // pan all current Howls slightly right
```

Future Howls are not affected unless explicitly set.

## 3D Spatial Positioning

### Sound Position

Set the 3D position of a sound source relative to the listener:

```js
const sound = new Howl({
  src: ['effect.mp3'],
  pos: [10, 0, -5],  // x=10, y=0, z=-5
});

// Move at runtime
sound.pos(5, 2, -3);
```

Coordinates use a right-handed system. Default z is `-0.5`.

### Listener Position

The listener is the "camera" or player position. All spatial sounds are relative to it:

```js
Howler.pos(0, 0, 0);  // listener at origin
```

### Listener Orientation

Set which direction the listener is facing:

```js
Howler.orientation(
  0, 0, -1,   // forward vector (facing -Z)
  0, 1, 0     // up vector (Y is up)
);
```

Default: forward `(0, 0, -1)`, up `(0, 1, 0)`.

### Source Orientation

Set which direction a directional sound source is pointing:

```js
sound.orientation(0, 0, -1);  // pointing toward -Z
```

Combined with `pannerAttr` cone settings, this creates directional audio that gets quieter when the source points away from the listener.

## Panner Attributes

Configure the `PannerNode` properties that control how 3D position affects volume:

```js
sound.pannerAttr({
  coneInnerAngle: 360,       // degrees — no volume reduction inside this angle
  coneOuterAngle: 360,       // degrees — full reduction outside this angle
  coneOuterGain: 0,          // gain outside coneOuterAngle (0-1)
  distanceModel: 'inverse',  // 'linear' | 'inverse' | 'exponential'
  maxDistance: 10000,        // max distance before volume stops decreasing
  refDistance: 1,            // distance at which volume = 1.0
  rolloffFactor: 1,          // rate of volume decrease with distance
  panningModel: 'HRTF',      // 'HRTF' | 'equalpower'
});
```

### Distance Models

| Model | Behavior |
|---|---|
| `linear` | Volume decreases linearly with distance. `rolloffFactor` range: 0–1. |
| `inverse` | Standard 1/d falloff. `rolloffFactor` range: 0–∞. |
| `exponential` | Volume = 1 / (1 + `rolloffFactor` × (distance - `refDistance`) / `refDistance`). |

### Panning Models

| Model | Behavior |
|---|---|
| `HRTF` | Head-related transfer function. More realistic but CPU-intensive. |
| `equalpower` | Simple equal-power panning. Less realistic but faster. |

### Cone Directional Audio

Create a directional sound (like a spotlight of audio):

```js
sound.pannerAttr({
  coneInnerAngle: 90,    // full volume within 90° cone
  coneOuterAngle: 180,   // fade to coneOuterGain between 90° and 180°
  coneOuterGain: 0.1,    // 10% volume outside the cone
});
sound.orientation(0, 0, -1);  // cone points toward -Z
```

## Spatial Events

| Event | Callback | Trigger |
|---|---|---|
| `stereo` | `(id)` | Stereo pan changed |
| `pos` | `(id)` | 3D position changed |
| `orientation` | `(id)` | Source orientation changed |

Register via constructor or `on()`:

```js
new Howl({
  src: ['sound.mp3'],
  onstereo: (id) => console.log('stereo changed'),
  onpos: (id) => console.log('position changed'),
  onorientation: (id) => console.log('orientation changed'),
});
```

## Spatial Constructor Options

| Option | Type | Default | Description |
|---|---|---|---|
| `stereo` | `Number` | `null` | Stereo pan -1.0 to 1.0 |
| `pos` | `Array` | `null` | 3D position `[x, y, z]` |
| `orientation` | `Array` | `[1, 0, 0]` | Source direction `[x, y, z]` |
| `pannerAttr` | `Object` | *(defaults)* | Panner node attributes |

## Typical Use Cases

### Surround Sound / Ambient

```js
const ambience = new Howl({
  src: ['forest.mp3'],
  loop: true,
  stereo: 0,
  volume: 0.3,
});
ambience.play();
```

### Game Enemy Warning

```js
const warning = new Howl({
  src: ['warning.mp3'],
  pos: [enemyX, 0, enemyZ],
  pannerAttr: {
    distanceModel: 'exponential',
    rolloffFactor: 2,
    maxDistance: 50,
  },
});
```

### Dialogue Left/Right

```js
const dialogue = new Howl({
  src: ['line.mp3'],
  stereo: speakerLeft ? -0.8 : 0.8,
});
```

## Important Notes

- **Web Audio only** — All spatial methods check `self._webAudio` and return early on HTML5 Audio. Check `Howler.usingWebAudio` before depending on spatial features.

- **PannerNode is created lazily** — The panner node is created on first call to `stereo()`, `pos()`, or `pannerAttr()`. Calling `pos()` after `stereo()` switches from `StereoPannerNode` to `PannerNode`.

- **Coordinate scale** — The meaning of coordinate units depends on your `refDistance` and `rolloffFactor`. A sound at position `[100, 0, 0]` with default `refDistance: 1` will be nearly inaudible. Scale your coordinates to match your scene.

- **Listener defaults** — Default listener position is `[0, 0, 0]` and orientation is forward `(0, 0, -1)` with up `(0, 1, 0)`. Update `Howler.pos()` and `Howler.orientation()` to match your camera/player.
