# Advanced Topics

## Extension System

PixiJS uses an extension system for modular features.

### Extension Types

```ts
enum ExtensionType {
    Application = 'application',           // Application plugins
    WebGLPipes = 'webgl-pipes',            // WebGL render pipes
    WebGLPipesAdaptor = 'webgl-pipes-adaptor',
    WebGLSystem = 'webgl-system',          // WebGL systems
    WebGPUPipes = 'webgpu-pipes',          // WebGPU render pipes
    WebGPUPipesAdaptor = 'webgpu-pipes-adaptor',
    WebGPUSystem = 'webgpu-system',        // WebGPU systems
    CanvasSystem = 'canvas-system',        // Canvas systems
    CanvasPipes = 'canvas-pipes',
    CanvasPipesAdaptor = 'canvas-pipes-adaptor',
    Asset = 'asset',                       // Asset extensions
    LoadParser = 'load-parser',            // Asset loaders
    ResolveParser = 'resolve-parser',      // URL resolvers
    CacheParser = 'cache-parser',          // Cache parsers
    DetectionParser = 'detection-parser',  // Format detection
    MaskEffect = 'mask-effect',            // Mask effects
    BlendMode = 'blend-mode',              // Custom blend modes
    TextureSource = 'texture-source',      // Texture source types
    TextureUploaderWebGL = 'texture-uploader-webgl',
    TextureUploaderWebGPU = 'texture-uploader-webgpu',
    Environment = 'environment',           // Environment adapters
    ShapeBuilder = 'shape-builder',        // Shape builders
    Batcher = 'batcher',                   // Custom batchers
}
```

### Creating an Extension

```ts
import { ExtensionType, extensions } from 'pixi.js';

class MyExtension {
    // Static extension metadata
    public static extension = {
        type: ExtensionType.WebGLSystem,
        name: 'mySystem',
        priority: 0, // Higher = initialized first
    } as const;

    // System interface
    public renderer: Renderer;

    public init(renderer: Renderer): void {
        this.renderer = renderer;
    }

    public destroy(): void {
        this.renderer = null;
    }
}

// Register
extensions.add(MyExtension);

// Or with override
extensions.add({
    type: ExtensionType.WebGLSystem,
    name: 'mySystem',
    ref: MyExtension,
});
```

### Application Plugin

```ts
import { ApplicationPlugin, ExtensionType, extensions } from 'pixi.js';

class MyPlugin {
    public static extension = ExtensionType.Application;

    public static init(options: Partial<ApplicationOptions>): void {
        // `this` is the Application instance
        Object.defineProperty(this, 'myFeature', {
            value: () => console.log('Feature!'),
        });
    }

    public static destroy(): void {
        // Cleanup
    }
}

extensions.add(MyPlugin);
```

### Mixin

Add properties/methods to a class:

```ts
import { extensions, Container } from 'pixi.js';

extensions.mixin(Container, {
    myProperty: 'default',
    myMethod() {
        console.log('My method on', this);
    },
});

// Now all Containers have myProperty and myMethod
const container = new Container();
container.myMethod();
```

## Custom Render Pipes

Render pipes handle the rendering of specific display object types.

### WebGL Pipe

```ts
import { RenderPipe, ExtensionType, extensions } from 'pixi.js';

class MyRenderPipe extends RenderPipe<MyView> {
    public static extension = {
        type: ExtensionType.WebGLPipes,
        name: 'my-pipe',
    } as const;

    public packRenderable(renderable: MyView): void {
        // Prepare renderable for batching
    }

    public transformRenderable(renderable: MyView, delta: number): void {
        // Transform renderable
    }

    public sort(): void {
        // Sort renderables
    }

    public destroy(): void {
        super.destroy();
    }
}

extensions.add(MyRenderPipe);
```

### Pipe Adaptor

```ts
class MyPipeAdaptor {
    public static extension = {
        type: ExtensionType.WebGLPipesAdaptor,
        name: 'my-pipe',
    } as const;

    public init(pipe: MyRenderPipe): void {
        // Initialize pipe-specific WebGL state
    }

    public upload(renderable: MyView): void {
        // Upload renderable data to GPU
    }

    public destroy(): void {
        // Cleanup
    }
}

extensions.add(MyPipeAdaptor);
```

## Custom Shaders

### Shader.from()

```ts
import { Shader, GlProgram, GpuProgram, UniformGroup } from 'pixi.js';

const shader = Shader.from({
    // WebGL
    gl: {
        vertex: vertexSource,
        fragment: fragmentSource,
        name: 'my-shader', // Optional: for debugging
    },

    // WebGPU
    gpu: {
        vertex: {
            source: wgslSource,
            entryPoint: 'mainVert',
        },
        fragment: {
            source: wgslSource,
            entryPoint: 'mainFrag',
        },
    },

    // Resources
    resources: {
        myUniforms: new UniformGroup({
            uTime: { value: 0, type: 'f32' },
            uResolution: { value: [800, 600], type: 'f32', size: 2 },
        }),
        myTexture: {
            texture: texture.source,
            style: texture.style,
        },
    },
});
```

### Uniform Types

| Type | WGSL | GLSL | Description |
|---|---|---|---|
| `'f32'` | `f32` | `float` | Single float |
| `'f32f32'` | `vec2<f32>` | `vec2` | Two floats |
| `'f32f32f32'` | `vec3<f32>` | `vec3` | Three floats |
| `'f32f32f32f32'` | `vec4<f32>` | `vec4` | Four floats |
| `'f32_2×2'` | `mat2x2<f32>` | `mat2` | 2×2 matrix |
| `'f32_3×3'` | `mat3x3<f32>` | `mat3` | 3×3 matrix |
| `'f32_4×4'` | `mat4x4<f32>` | `mat4` | 4×4 matrix |

### UniformGroup

```ts
const uniforms = new UniformGroup({
    uFloat: { value: 1.0, type: 'f32' },
    uVec2: { value: [1, 2], type: 'f32', size: 2 },
    uVec3: { value: [1, 2, 3], type: 'f32', size: 3 },
    uVec4: { value: [1, 2, 3, 4], type: 'f32', size: 4 },
    uMat3: { value: [1,0,0, 0,1,0, 0,0,1], type: 'f32', size: 9 },
});

// Update
uniforms.uniforms.uFloat = 2.0;
uniforms.update();
```

## Unsafe Eval

Dynamic shader compilation at runtime. Requires `import 'pixi.js/unsafe-eval'`.

```ts
import 'pixi.js/unsafe-eval';
import { Shader } from 'pixi.js';

// Dynamic shader (compiled at runtime)
const shader = Shader.from({
    gl: { vertex, fragment },
    gpu: { vertex: { source, entryPoint }, fragment: { source, entryPoint } },
    resources: { uniforms },
});
```

> ⚠️ Requires `unsafe-eval` CSP directive. Not available in strict CSP environments.

## WebGPU

### Checking Support

```ts
import { isWebGPUSupported } from 'pixi.js';

const supported = await isWebGPUSupported();

if (supported) {
    const renderer = await autoDetectRenderer({
        preference: 'webgpu',
        width: 800,
        height: 600,
    });
}
```

### WebGPU-Specific Options

```ts
const renderer = await autoDetectRenderer({
    webgpu: {
        antialias: true,
        alpha: true,
        device: gpuDevice, // Optional: provide your own GPU device
    },
});
```

## Performance Optimization

### Batching

PixiJS automatically batches compatible renderables. Factors that break batching:

- Different textures
- Different blend modes
- Different tint colors
- Different alpha values (in some cases)
- Filters
- Masks
- RenderGroup boundaries

**Tips:**
- Group same-texture sprites together
- Use spritesheets to reduce texture switches
- Minimize blend mode changes
- Use `GraphicsContext` sharing for repeated graphics

### RenderGroups

```ts
// Use RenderGroups for:
// - Game world panning (GPU-level transform)
// - UI overlay separation
// - Layer separation

const gameWorld = new Container({ isRenderGroup: true });
const uiLayer = new Container({ isRenderGroup: true });

app.stage.addChild(gameWorld, uiLayer);
```

### Caching

```ts
// Cache complex containers as textures
container.cacheAsTexture(true);

// Access cached texture
const texture = container._cacheTexture;
```

### Texture Optimization

```ts
// Use appropriate resolution
await Assets.init({
    texturePreference: {
        resolution: window.devicePixelRatio,
        format: ['avif', 'webp', 'png'],
    },
});

// Use compressed textures for production
import 'pixi.js/ktx2';
const texture = await Assets.load('texture.ktx2');

// Use nearest scaling for pixel art
const texture = new Texture({
    source: new ImageSource({
        resource: image,
        scaleMode: 'nearest',
    }),
});
```

### Memory Management

```ts
// Destroy unused assets
Assets.remove('unused-asset.png');

// Destroy bundles when done
await Assets.unloadBundle('level-1');

// Destroy textures
texture.destroy();
texture.destroy(true); // Also destroy source

// Destroy containers with children
container.destroy({ children: true, texture: true });

// Reset assets manager
Assets.reset();
```

### Prepare System

Pre-upload assets to GPU before display:

```ts
import 'pixi.js/prepare';

const app = new Application();
await app.init();

// Don't start rendering yet
app.stop();

// Add content to stage
app.stage.addChild(graphics);

// Upload to GPU before first render
await app.renderer.prepare.upload(app.stage);

// Now start rendering (no stutter)
app.start();
```

## DOM Objects

Embed HTML elements in the scene graph:

```ts
import { DOM } from 'pixi.js';

const div = document.createElement('div');
div.textContent = 'Hello DOM!';
div.style.cssText = 'color: white; font-size: 24px;';

const dom = new DOM({ view: div });
dom.position.set(100, 100);
app.stage.addChild(dom);
```

## Accessibility

```ts
import 'pixi.js/accessibility';

// Enable accessibility
sprite.accessible = true;
sprite.accessibleTitle = 'A red sprite';
sprite.accessibleDescription = 'A red square sprite';
```

## GIF Support

```ts
import 'pixi.js/gif';

const texture = await Assets.load('animation.gif');
const sprite = new Sprite({ texture });
// GIF textures auto-update
```

## Mixing PixiJS and Three.js

Share a single WebGL context between PixiJS (2D) and Three.js (3D):

```ts
import * as THREE from 'three';
import { WebGLRenderer as PixiRenderer } from 'pixi.js';

// Three.js creates the canvas and context
const threeRenderer = new THREE.WebGLRenderer({
    antialias: true,
    stencil: true, // Required for PixiJS masks
});
threeRenderer.setSize(WIDTH, HEIGHT);
document.body.appendChild(threeRenderer.domElement);

// PixiJS shares the context
const pixiRenderer = new PixiRenderer();
await pixiRenderer.init({
    context: threeRenderer.getContext(),
    width: WIDTH,
    height: HEIGHT,
    clearBeforeRender: false, // Don't clear Three.js content
});

// Render loop
function render() {
    threeRenderer.resetState();
    threeRenderer.render(scene, camera);

    pixiRenderer.resetState();
    pixiRenderer.render({ container: stage });

    requestAnimationFrame(render);
}
requestAnimationFrame(render);
```

### Gotchas

- Enable `stencil: true` on Three.js renderer for PixiJS masks
- Keep dimensions in sync when resizing
- Use `resetState()` when switching between renderers
- Set `clearBeforeRender: false` or `clear: false` in render call
- Textures are not shared between PixiJS and Three.js
- Works with other 3D engines (Babylon.js, PlayCanvas) that support state management

## Ecosystem

### Core Libraries

| Library | Purpose |
|---|---|
| [DevTools](https://pixijs.io/devtools/) | Browser extension for debugging scene graph, performance, textures |
| [PixiJS React](https://react.pixijs.io/) | React bindings (requires React 19+) |
| [Layout](https://layout.pixijs.io/) | Flexbox-style layout via Yoga engine |
| [Spine Integration](https://esotericsoftware.com/spine-pixi) | Skeletal animations |
| [Filters](https://github.com/pixijs/filters) | Extended filter collection (twist, grayscale, bloom, etc.) |
| [Sound](https://github.com/pixijs/sound) | WebAudio API playback with filters |
| [UI](https://github.com/pixijs/ui) | Pre-built UI components (buttons, sliders, scrollbox, etc.) |
| [AssetPack](https://pixijs.io/assetpack/) | Asset management, manifest generation, compressed textures |

### Creation Templates

Use `npm create pixi.js@latest` to scaffold projects with pre-configured setups for specific platforms and use cases.

## Accessibility

Opt-in accessibility system using DOM overlays for screen readers and keyboard navigation.

```ts
import 'pixi.js/accessibility';

// Enable on objects
const button = new Container();
button.accessible = true;
button.accessibleTitle = 'Start Game';
button.accessibleHint = 'Click to start the game';
button.accessibleType = 'button'; // HTML tag name for the overlay
button.tabIndex = 0;

// Configuration
const app = new Application();
await app.init({
    accessibilityOptions: {
        enabledByDefault: true,      // Enable on startup
        activateOnTab: false,        // Disable auto-activation via tab
        deactivateOnMouseMove: false, // Keep active with mouse use
        debug: true,                  // Show div overlays
    },
});

// Programmatic control
app.renderer.accessibility.setAccessibilityEnabled(true);
```

### Properties

| Property | Description |
|---|---|
| `accessible` | Enables accessibility for the object |
| `accessibleTitle` | Sets the title for screen readers |
| `accessibleHint` | Sets the `aria-label` |
| `accessibleText` | Alternative inner text for the div |
| `accessibleType` | Tag name (`'button'`, `'div'`, etc.) |
| `accessiblePointerEvents` | CSS `pointer-events` value |
| `tabIndex` | Keyboard focus order |
| `accessibleChildren` | Whether children are accessible |
