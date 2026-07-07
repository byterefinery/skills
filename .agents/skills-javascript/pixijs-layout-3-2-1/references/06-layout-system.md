# LayoutSystem

The LayoutSystem integrates layout management into the PixiJS rendering lifecycle.

## Initialization

```ts
import '@pixi/layout';
import { Application } from 'pixi.js';

const app = new Application();
await app.init({
    background: '#1099bb',
    resizeTo: window,
    layout: {
        autoUpdate: true,
        enableDebug: false,
        throttle: 100,
        debugModificationCount: 50,
    },
});
```

## LayoutSystemOptions

| Option                 | Type      | Default | Description                                                  |
|------------------------|-----------|---------|--------------------------------------------------------------|
| `autoUpdate`           | `boolean` | `true`  | Auto-recalculate layouts each frame                          |
| `enableDebug`          | `boolean` | `false` | Enable debug renderer at startup                             |
| `throttle`             | `number`  | `100`   | ms delay for batching intrinsic size recalculations          |
| `debugModificationCount` | `number` | `50`  | Min modifications before debug heatmap shows                 |

## Auto Update

When `autoUpdate: true`, the LayoutSystem hooks into the `prerender` phase. Each frame it:

1. Traverses the scene graph recursively
2. Finds nodes with active layouts
3. Checks for dirty flags and recalculates
4. Applies computed transforms
5. Optionally renders debug overlays

Intrinsic size checks are throttled to avoid expensive bound checks every frame.

## Manual Updates

When `autoUpdate: false`, trigger updates manually:

```ts
// Update entire stage
app.renderer.layout.update(app.stage);

// Update specific subtree
app.renderer.layout.update(container);
```

## Debug Renderer

Visualize layout regions (margin, padding, border, flex, content) with colored overlays.

```ts
// Enable at runtime
app.renderer.layout.enableDebug(true);

// Disable
app.renderer.layout.enableDebug(false);
```

The `enableDebug` method is async (dynamically loads the debug module). You typically don't need to await it.

### Debug Style Properties

When debug is enabled, per-node debug control:

| Property           | Description                                    |
|--------------------|------------------------------------------------|
| `debug`            | Show debug overlay for this node               |
| `debugHeat`        | Show heatmap (invalidation count) — default true |
| `debugDrawMargin`  | Draw margin region (default: true)             |
| `debugDrawPadding` | Draw padding region (default: true)            |
| `debugDrawBorder`  | Draw border region (default: true)             |
| `debugDrawFlex`    | Draw flex region (default: true)               |
| `debugDrawContent` | Draw content region (default: true)            |

```ts
// Show debug for this node only
container.layout = { debug: true };

// Show heatmap only (no boxes)
container.layout = { debugHeat: true };

// Disable heatmap for this node
container.layout = { debugHeat: false };
```

## Yoga Configuration

Customize the Yoga engine globally:

```ts
import { getYogaConfig } from '@pixi/layout';

const config = getYogaConfig();

// Errata mode — controls edge case handling
config.setErrata(Errata.Classic);

// Point scale factor
config.setPointScaleFactor(1);

// Use web-standard defaults
config.setUseWebDefaults(true);
```

Configuration changes affect all layouts globally. Set early in the application lifecycle.

## LayoutSystem Access

```ts
// After app.init()
const layoutSystem = app.renderer.layout;
```

## Lifecycle

The LayoutSystem is registered as both a WebGL and WebGPU system. It initializes by loading the Yoga WASM module asynchronously. The `init` method returns a promise that resolves when Yoga is ready.

## Destroy

```ts
layoutSystem.destroy();
```

Cleans up the debug renderer if it was enabled.
