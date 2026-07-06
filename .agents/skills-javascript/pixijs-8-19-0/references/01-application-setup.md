# Application Setup

## Application Class

`Application` is the convenience entry point that bundles renderer creation, stage (root Container), canvas management, and plugin hooks.

```ts
import { Application } from 'pixi.js';

const app = new Application();
await app.init({
    width: 800,
    height: 600,
    backgroundColor: 0x1099bb,
    antialias: true,
    resolution: window.devicePixelRatio,
    preference: 'webgl', // 'webgl' | 'webgpu' | 'canvas' | string[]
    autoStart: true,     // Auto-start render loop
    sharedTicker: true,  // Use shared ticker
});

document.body.appendChild(app.canvas);
```

### Application Properties

| Property | Type | Description |
|---|---|---|
| `app.stage` | `Container` | Root display container |
| `app.renderer` | `Renderer` | The renderer instance |
| `app.canvas` | `HTMLCanvasElement` | The canvas element |
| `app.screen` | `Rectangle` | Visible area rectangle |
| `app.domContainerRoot` | `HTMLDivElement` | DOM container root (for DOM objects) |

### ApplicationOptions

```ts
interface ApplicationOptions {
    // Dimensions
    width?: number;           // Canvas width (default: 800)
    height?: number;          // Canvas height (default: 600)

    // Rendering
    backgroundColor?: ColorSource; // Background color (default: 0x000000)
    antialias?: boolean;     // Enable antialiasing
    resolution?: number;     // Resolution / device pixel ratio (default: 1)
    preference?: RendererPreference | RendererPreference[]; // Renderer preference
    powerPreference?: 'default' | 'low-power' | 'high-performance';

    // Canvas
    view?: HTMLCanvasElement; // Use existing canvas
    autoDensity?: boolean;    // Adjust resolution on resize
    clearBeforeRender?: boolean; // Clear canvas before each frame

    // Ticker
    autoStart?: boolean;      // Start render loop automatically (default: true)
    sharedTicker?: boolean;   // Use shared ticker (default: true)

    // Resize
    resizeTo?: HTMLElement | Window; // Auto-resize to element

    // Renderer-specific
    webgl?: Partial<WebGLOptions>;
    webgpu?: Partial<WebGPUOptions>;
    canvasOptions?: Partial<CanvasOptions>;

    // Events
    eventMode?: EventMode;
    eventFeatures?: Partial<EventSystemFeatures>;
}
```

## Renderer Types

PixiJS supports three rendering backends, auto-detected by preference:

### WebGL Renderer

Default and most widely supported. Uses WebGL 2 (falls back to WebGL 1).

```ts
const renderer = await autoDetectRenderer({
    width: 800,
    height: 600,
    preference: 'webgl',
    webgl: {
        antialias: true,
        alpha: true,
        preserveDrawingBuffer: false,
        stencil: true,
        preferWebGLVersion: 2, // 1 or 2
    }
});
```

### WebGPU Renderer

Next-generation GPU API. Better performance, compute shaders, better texture support.

```ts
const renderer = await autoDetectRenderer({
    width: 800,
    height: 600,
    preference: 'webgpu',
    webgpu: {
        antialias: true,
        alpha: true,
        device?: GPUDevice, // Optional: provide your own device
    }
});
```

### Canvas Renderer

Software fallback. No GPU required. Slower but universally available.

```ts
const renderer = await autoDetectRenderer({
    width: 800,
    height: 600,
    preference: 'canvas',
});
```

### Auto-Detection

```ts
// Try WebGPU first, fall back to WebGL, then Canvas
const renderer = await autoDetectRenderer({
    width: 800,
    height: 600,
    preference: ['webgpu', 'webgl', 'canvas'],
});

// Only WebGL and Canvas (exclude WebGPU)
const renderer = await autoDetectRenderer({
    width: 800,
    height: 600,
    preference: ['webgl', 'canvas'],
});
```

## Manual Rendering

When `autoStart: false`, manage the render loop manually:

```ts
const app = new Application();
await app.init({ autoStart: false });

// Option 1: Use requestAnimationFrame
function animate() {
    app.render();
    requestAnimationFrame(animate);
}
animate();

// Option 2: Use Ticker.shared
Ticker.shared.add(() => {
    app.render();
});
Ticker.shared.start();

// Option 3: Start/stop the app
app.start();  // Start rendering
app.stop();   // Stop rendering
```

## Plugins

Application plugins extend the Application instance:

```ts
import { ApplicationPlugin, ExtensionType, extensions } from 'pixi.js';

class MyPlugin {
    public static extension = ExtensionType.Application;

    public static init(options: Partial<ApplicationOptions>): void {
        // `this` is the Application instance
        Object.defineProperty(this, 'myFeature', {
            value: () => console.log('My feature!'),
        });
    }

    public static destroy(): void {
        // Cleanup
    }
}

extensions.add(MyPlugin);

const app = new Application();
await app.init();
app.myFeature(); // Works!
```

### Built-in Plugins

- `TickerPlugin` — manages the render loop via Ticker
- `ResizePlugin` — handles automatic resizing to a target element
- `CullerPlugin` — automatic culling of off-screen objects

## Resize Handling

```ts
// Auto-resize to window
const app = new Application();
await app.init({
    resizeTo: window,
    autoDensity: true, // Adjust resolution on resize
});

// Manual resize
app.renderer.resize(newWidth, newHeight);

// Resize to specific element
await app.init({ resizeTo: document.getElementById('game-container') });
```

## Destroy

```ts
// Basic cleanup (preserves canvas)
app.destroy();

// Full cleanup (removes canvas)
app.destroy(true, true);

// Detailed cleanup
app.destroy(
    { removeView: true },
    {
        children: true,
        texture: true,
        textureSource: true,
        context: true,
    }
);
```

## Custom Renderer Setup

For advanced use cases, create a renderer directly:

```ts
import { autoDetectRenderer } from 'pixi.js';

const renderer = await autoDetectRenderer({
    width: 800,
    height: 600,
    preference: 'webgl',
});

// Create your own stage
const stage = new Container();
stage.addChild(sprite);

// Render manually
renderer.render({ container: stage });

// Cleanup
renderer.destroy(true);
```

## Web Worker Support

PixiJS can run in web workers using `WebWorkerAdapter`:

```ts
import { DOMAdapter, WebWorkerAdapter } from 'pixi.js';

DOMAdapter.set(WebWorkerAdapter);
// Now PixiJS uses the worker adapter for canvas creation
```

## Performance Tips

- Set `resolution` to `window.devicePixelRatio` for crisp rendering on HiDPI displays
- Use `autoDensity: true` so resolution adjusts on resize
- Prefer WebGPU when available for better performance
- Disable `stencil` if you don't use stencil masks
- Use `preserveDrawingBuffer: false` unless you need to read back pixels
- Set `clearBeforeRender: false` if you manage clearing manually (advanced)
