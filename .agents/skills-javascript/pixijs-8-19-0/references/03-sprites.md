# Sprites

## Sprite

The primary display object for rendering textures. Extends `ViewContainer`.

### Creation

```ts
import { Sprite, Texture } from 'pixi.js';

// From texture
const sprite = new Sprite({ texture });

// Static from method (texture must be loaded first)
const sprite = Sprite.from('assets/image.png'); // Only works if loaded via Assets

// With options
const sprite = new Sprite({
    texture: Texture.from('sprite.png'),
    anchor: 0.5,            // Center anchor
    anchor: { x: 0.5, y: 0.5 }, // Separate x/y anchor
    roundPixels: true,      // Crisp pixel rendering
    x: 100,
    y: 200,
});

// With size
const sprite = new Sprite({
    texture,
    width: 200,
    height: 100,
});
```

### Properties

| Property | Type | Description |
|---|---|---|
| `texture` | `Texture` | The texture to display |
| `anchor` | `ObservablePoint` | Origin point (0-1 range) |
| `roundPixels` | `boolean` | Round position to whole pixels |
| `width` | `number` | Display width (scales texture) |
| `height` | `number` | Display height (scales texture) |
| `trimmed` | `boolean` | Whether texture is trimmed |
| `rotated` | `boolean` | Whether texture is rotated in atlas |

### Anchor

```ts
// Center anchor
sprite.anchor.set(0.5);
sprite.anchor.set(0.5, 0.5);

// Top-right anchor
sprite.anchor.set(1, 0);

// Bottom-left anchor
sprite.anchor.set(0, 1);
```

### Texture Swapping

```ts
// Direct swap
sprite.texture = newTexture;

// If texture was modified after creation, call:
sprite.onViewUpdate();

// For frequent swaps, set dynamic on the texture:
const texture = new Texture({ source, dynamic: true });
```

## AnimatedSprite

Frame-by-frame animation from a sequence of textures.

### Creation

```ts
import { AnimatedSprite } from 'pixi.js';

// From texture array
const animatedSprite = new AnimatedSprite({
    textures: [texture1, texture2, texture3],
    animationSpeed: 0.1,  // Speed multiplier (default: 1)
    loop: true,           // Loop animation (default: true)
    autoPlay: true,       // Start playing immediately
    updateAnchor: true,   // Update anchor from frame data
});

// From spritesheet animations
const sheet = await Assets.load('character.json');
const animatedSprite = new AnimatedSprite({
    textures: sheet.animations['walk'],
    animationSpeed: 0.15,
    loop: true,
    autoPlay: true,
});

// With custom frame timing
const customSprite = new AnimatedSprite({
    textures: [
        { texture: frame1, time: 100 },
        { texture: frame2, time: 200 },
        { texture: frame3, time: 300 },
    ],
});
```

### Control

```ts
animatedSprite.play();    // Start/resume
animatedSprite.stop();    // Pause
animatedSprite.reset();   // Reset to first frame

// Properties
animatedSprite.animationSpeed = 0.5; // Slower
animatedSprite.loop = false;         // Play once
animatedSprite.currentFrame = 5;     // Jump to frame

// Callbacks
animatedSprite.onComplete = () => {
    console.log('Animation finished');
};
animatedSprite.onFrameChange = (frame: number) => {
    console.log('Frame:', frame);
};
animatedSprite.onLoop = () => {
    console.log('Animation looped');
};

// Current state
animatedSprite.totalFrames; // Total frame count
animatedSprite.currentFrame; // Current frame index
animatedSprite.isPlaying; // boolean
```

## TilingSprite

Repeats a texture across a rectangular area. Ideal for backgrounds and scrolling textures.

### Creation

```ts
import { TilingSprite } from 'pixi.js';

const tilingSprite = new TilingSprite({
    texture: Texture.from('pattern.png'),
    width: 800,
    height: 600,
    tilePosition: { x: 0, y: 0 },
    tileScale: { x: 1, y: 1 },
    tileRotation: 0,
    anchor: 0.5,
    roundPixels: true,
});
```

### Scrolling

```ts
// Scroll the texture
app.ticker.add(() => {
    tilingSprite.tilePosition.x += 1;
    tilingSprite.tilePosition.y += 0.5;
});

// Scale the tile pattern
tilingSprite.tileScale.set(2, 2);

// Rotate the tile pattern
tilingSprite.tileRotation = Math.PI / 4;

// Reset tile transform
tilingSprite.tileTransform.identity();
```

### Properties

| Property | Type | Description |
|---|---|---|
| `texture` | `Texture` | Texture to tile |
| `tilePosition` | `PointData` | Offset of tiling pattern |
| `tileScale` | `PointData` | Scale of each tile |
| `tileRotation` | `number` | Rotation of tile pattern |
| `tileTransform` | `Transform` | Full tile transform matrix |

## NineSliceSprite

Nine-slice scaling for UI elements (buttons, panels). Preserves corners and edges while stretching the center.

### Layout

```
    A (left)              B (right)
  +-------+--------------+-------+
C |   1   |     2        |   3   |  top (C)
  |       |              |       |
  |   4   |     5        |   6   |
  |       |              |       |
D |   7   |     8        |   9   |  bottom (D)
  +-------+--------------+-------+
  Corners (1,3,7,9) never scale
  Edges (2,4,6,8) scale in one direction
  Center (5) scales in both directions
```

### Creation

```ts
import { NineSliceSprite } from 'pixi.js';

const button = new NineSliceSprite({
    texture: Texture.from('button.png'),
    leftWidth: 20,
    topHeight: 20,
    rightWidth: 20,
    bottomHeight: 20,
    width: 200,
    height: 60,
    anchor: 0.5,
});

// Resize — corners stay fixed, center stretches
button.width = 400;
button.height = 80;
```

### Properties

| Property | Type | Description |
|---|---|---|
| `texture` | `Texture` | Source texture |
| `leftWidth` | `number` | Left border width (A) |
| `rightWidth` | `number` | Right border width (B) |
| `topHeight` | `number` | Top border height (C) |
| `bottomHeight` | `number` | Bottom border height (D) |
| `anchor` | `ObservablePoint` | Anchor point |

### Using Texture Borders

```ts
// Set default borders on texture (for reuse)
texture.defaultBorders = { left: 20, top: 20, right: 20, bottom: 20 };

// NineSliceSprite picks up defaultBorders automatically
const button = new NineSliceSprite({ texture });
```

## Sprite Performance Tips

- **Reuse textures** — one texture shared across many sprites is much faster than unique textures
- **Use spritesheets** — packed textures reduce texture switches and draw calls
- **Enable batching** — sprites with same texture/blendMode/tint batch together automatically
- **Use `roundPixels: true`** for pixel art or crisp rendering
- **Avoid frequent texture swaps** — each swap may break batching; use `dynamic: true` on texture if needed
- **Prefer `AnimatedSprite`** over manual texture swapping for frame animations
- **Use `TilingSprite`** for repeating backgrounds instead of many overlapping sprites
- **Use `NineSliceSprite`** for scalable UI instead of stretching regular sprites
