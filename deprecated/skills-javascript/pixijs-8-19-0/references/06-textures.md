# Textures

## Texture

A Texture wraps a `TextureSource` and defines the visible region (frame), UVs, anchor, and borders.

### Creation

```ts
import { Texture, ImageSource } from 'pixi.js';

// From loaded asset (via Assets)
const texture = await Assets.load('assets/image.png');

// From cache (after loading)
const texture = Texture.from('assets/image.png');

// From ImageSource
const image = new Image();
image.src = 'image.png';
image.onload = () => {
    const source = new ImageSource({ resource: image });
    const texture = new Texture({ source });
};

// From canvas
const canvas = document.createElement('canvas');
canvas.width = 100;
canvas.height = 100;
const ctx = canvas.getContext('2d');
ctx.fillStyle = 'red';
ctx.fillRect(0, 0, 100, 100);

const canvasSource = new CanvasSource({ resource: canvas });
const texture = new Texture({ source: canvasSource });

// From video
const video = document.createElement('video');
video.src = 'video.mp4';
const videoSource = new VideoSource({ resource: video });
const texture = new Texture({ source: videoSource });

// Empty texture
const empty = Texture.EMPTY;

// White texture
const white = Texture.WHITE;
```

### TextureOptions

```ts
interface TextureOptions {
    source?: TextureSource;        // The texture source
    label?: string;                // Debug label
    frame?: Rectangle;             // Visible rectangle
    orig?: Rectangle;              // Original texture area
    trim?: Rectangle;              // Trimmed area
    defaultAnchor?: { x: number; y: number }; // Default anchor
    defaultBorders?: TextureBorders; // Default 9-slice borders
    rotate?: number;               // Rotation in atlas (groupD8)
    dynamic?: boolean;             // True if frame/UVs change at runtime
}
```

### Properties

| Property | Type | Description |
|---|---|---|
| `source` | `TextureSource` | Underlying texture data |
| `width` | `number` | Display width |
| `height` | `number` | Display height |
| `frame` | `Rectangle` | Visible frame rectangle |
| `orig` | `Rectangle` | Original area |
| `trim` | `Rectangle` | Trimmed area |
| `defaultAnchor` | `Point` | Default anchor point |
| `defaultBorders` | `TextureBorders` | Default 9-slice borders |
| `rotate` | `number` | Atlas rotation (groupD8) |
| `valid` | `boolean` | Whether texture is valid/loaded |
| `readOnly` | `boolean` | Whether texture is read-only |

### Texture Events

```ts
texture.on('update', (texture) => {
    // Texture frame/UVs changed
    sprite.onViewUpdate(); // Manually update sprite
});

texture.on('destroy', (texture) => {
    // Texture destroyed
});
```

### Destroy

```ts
texture.destroy();

// Also destroy the source
texture.destroy(true);
```

## TextureSource Types

v8 replaced `BaseTexture` with specialized TextureSource classes:

### TextureSource

Vanilla source for render targets and manual uploads.

```ts
import { TextureSource } from 'pixi.js';

const source = new TextureSource({
    width: 256,
    height: 256,
    format: 'bgra8unorm',
    type: 'f32',
    resolution: 1,
    scaleMode: 'linear',    // 'linear' | 'nearest'
    wrapMode: 'clamp-to-edge', // 'clamp-to-edge' | 'repeat' | 'mirror-repeat'
    autoGenerateMipmaps: false,
    alphaMode: 'premultiplied-alpha', // 'premultiplied-alpha' | 'straight-alpha' | 'none'
    anisotropicLevel: 1,
    style: new TextureStyle(),
});

const texture = new Texture({ source });
```

### ImageSource

For image resources (ImageBitmap, HTMLImageElement).

```ts
import { ImageSource } from 'pixi.js';

const source = new ImageSource({
    resource: imageElement, // HTMLImageElement | ImageBitmap
    alphaMode: 'premultiplied-alpha',
    scaleMode: 'linear',
    wrapMode: 'clamp-to-edge',
});
```

### CanvasSource

For canvas elements.

```ts
import { CanvasSource } from 'pixi.js';

const source = new CanvasSource({
    resource: canvasElement, // HTMLCanvasElement
    autoResize: true,        // Auto-resize when canvas changes
});
```

### VideoSource

For video elements. Auto-updates when video plays.

```ts
import { VideoSource } from 'pixi.js';

const source = new VideoSource({
    resource: videoElement, // HTMLVideoElement
    autoLoad: true,         // Auto-load video
    autoPlay: false,        // Auto-play video
    updateLoadedMetadata: false,
});

// VideoSource auto-updates GPU texture when video frame changes
```

### BufferImageSource

For raw buffer data.

```ts
import { BufferImageSource } from 'pixi.js';

const buffer = new Uint8Array(256 * 256 * 4); // RGBA
const source = new BufferImageSource({
    resource: buffer,
    width: 256,
    height: 256,
    format: 'bgra8unorm',
});
```

### CompressedSource

For compressed textures (DDS, KTX, KTX2, Basis).

```ts
import { CompressedSource } from 'pixi.js';

// Loaded via Assets with format detection
const texture = await Assets.load('texture.ktx2');
// Returns a Texture with CompressedSource
```

## RenderTexture

Off-screen rendering target. Extends Texture.

### Creation

```ts
import { RenderTexture } from 'pixi.js';

// Create render texture
const renderTexture = RenderTexture.create({
    width: 256,
    height: 256,
    resolution: 2,
    format: 'bgra8unorm',
    autoGenerateMipmaps: true,
    dynamic: true, // Allow resizing
});

// Render to it
renderer.render({
    target: renderTexture,
    container: scene,
});

// Use as sprite texture
const sprite = new Sprite({ texture: renderTexture });
```

### Resize

```ts
renderTexture.resize(512, 512);
renderTexture.resize(512, 512, 2); // With resolution
```

### Mipmaps

```ts
// After rendering, update mipmaps manually
renderer.render({ target: renderTexture, container: scene });
renderTexture.source.updateMipmaps();
```

## Spritesheet

Texture atlas with frame data and optional animations.

### Loading

```ts
import { Assets } from 'pixi.js';

// Load spritesheet
const sheet = await Assets.load('assets/spritesheet.json');

// Access textures
const texture = sheet.textures['frame1.png'];
const texture = sheet.textures['frame2.png'];

// Access animations (array of textures)
const walkFrames = sheet.animations['walk'];
const idleFrames = sheet.animations['idle'];
```

### Spritesheet Data Format

```ts
interface SpritesheetData {
    frames: {
        [name: string]: {
            frame: { x: number; y: number; w: number; h: number };
            rotated?: boolean;
            trimmed?: boolean;
            sourceSize?: { w: number; h: number };
            spriteSourceSize?: { x: number; y: number; w?: number; h?: number };
            anchor?: { x: number; y: number };
            borders?: TextureBorders;
        };
    };
    animations?: {
        [name: string]: string[]; // Array of frame names
    };
    meta: {
        image?: string;
        scale?: string | number;
        // ...
    };
}
```

### Manual Spritesheet

```ts
import { Spritesheet } from 'pixi.js';

const texture = await Assets.load('atlas.png');
const data = {
    frames: {
        'frame1.png': {
            frame: { x: 0, y: 0, w: 64, h: 64 },
        },
    },
    animations: {
        'run': ['frame1.png', 'frame2.png', 'frame3.png'],
    },
    meta: { image: 'atlas.png' },
};

const sheet = new Spritesheet(texture.source, data);
await sheet.parse();

// Access textures
const texture = sheet.textures['frame1.png'];
```

## Compressed Textures

Support for DDS, KTX, KTX2, and Basis formats.

```ts
// Import required modules
import 'pixi.js/dds';   // DDS format
import 'pixi.js/ktx';   // KTX format
import 'pixi.js/ktx2';  // KTX2 format
import 'pixi.js/basis'; // Basis Universal

// Load compressed textures
const texture = await Assets.load('texture.ktx2');
const texture = await Assets.load('texture.dds');
const texture = await Assets.load('texture.basis');

// Works with format detection and resolution preference
await Assets.init({
    texturePreference: {
        resolution: window.devicePixelRatio,
        format: ['avif', 'webp', 'png'],
    },
});
```

## Prepare System

Textures loaded via `Assets` still need GPU upload. Use the `prepare` plugin to pre-upload before first render.

```ts
import 'pixi.js/prepare';

const app = new Application();
await app.init();

// Don't start rendering yet
app.stop();

// Add content to stage
app.stage.addChild(graphics);

// Upload to GPU before first render (avoids stutter)
await app.renderer.prepare.upload(app.stage);

// Now start rendering
app.start();
```

## Texture Matrix

For animating texture UVs (e.g., scrolling textures on sprites):

For animating texture UVs (e.g., scrolling textures on sprites):

```ts
import { TextureMatrix } from 'pixi.js';

const textureMatrix = new TextureMatrix(texture);
textureMatrix.registerPluginView(sprite);

// Animate
textureMatrix.uvo = 0.5;  // Center
textureMatrix.uvs = 0.01; // Scroll speed

app.ticker.add(() => {
    textureMatrix.update();
});
```

## Texture Pool

Internal pool for render-to-texture operations. Managed automatically.

```ts
import { TexturePool } from 'pixi.js';

// Get texture from pool (used internally by filters)
const texture = TexturePool.getOptimalTexture(512, 512, renderer);

// Return to pool
TexturePool.returnTexture(texture);
```

## Texture Performance Tips

- **Use spritesheets** — reduces texture switches and draw calls
- **Reuse textures** — one texture shared across many sprites
- **Use appropriate resolution** — don't load 4K textures for small sprites
- **Use compressed formats** — KTX2/Basis for production builds
- **Use `scaleMode: 'nearest'`** for pixel art
- **Use `wrapMode: 'clamp-to-edge'`** to avoid edge artifacts
- **Set `autoGenerateMipmaps: true`** for textures that scale down
- **Use `alphaMode: 'straight-alpha'`** for textures with transparency
- **Avoid modifying texture frames** at runtime — create new textures instead
- **Use `dynamic: true`** only when you need to modify texture at runtime
