# Init and Configuration

## phy.init()

Boots the physics engine backend. Must be called before any other phy method.

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `type` | String | — | Backend: `'OIMO'`, `'AMMO'`, `'RAPIER'`, `'JOLT'`, `'HAVOK'`, `'PHYSX'` |
| `worker` | Boolean | `false` | Run physics in a Web Worker. Recommended to free the main thread. |
| `compact` | Boolean | `false` | Use LZMA-compressed `.bin` files from `/compact/` folder. |
| `callback` | Function | — | Called when the physics engine is fully loaded and ready. |
| `scene` | Object3D | — | The three.js scene. phy adds its internal `phy_scene` group to it. |
| `renderer` | WebGLRenderer | — | The three.js renderer. Needed for envmap and KTX2 texture support. |
| `path` | String | `''` | Override the default resource path for backend files. |
| `envmap` | String | `''` | URL to an HDR/EXR/HDRJPG environment map. |
| `usePmrem` | Boolean | — | Use PMREMGenerator for envmap processing. |
| `useBackground` | Boolean | `true` | Apply envmap as scene background. |
| `useLocal` | Boolean | `false` | Load backend files relative to `import.meta.url` (for bundlers). |
| `useModule` | Boolean | `false` | Use ES module worker (`type: 'module'`). Needed with `useLocal`. |
| `useDecal` | Boolean | `false` | Enable decal support. |
| `devMode` | Boolean | `false` | Load source files instead of minified builds. |

### Worker vs Direct Mode

**Worker mode** (`worker: true`): Physics runs off the main thread. Uses `postMessage` to communicate. Best for complex simulations. Requires backend `.min.js` or `.bin` files to be accessible at runtime.

**Direct mode** (`worker: false`): Physics runs on the main thread. Simpler debugging but can block rendering. Loads backend via `<script>` tag or ES module import.

### Compact Mode

When `compact: true`, phy loads `.bin` files from the `/compact/` folder instead of `.js` files from `/build/`. The `.bin` files are LZMA-compressed and smaller but take longer to decompress on first load.

Available compact files: `Oimo.bin`, `Oimo.module.bin`, `Ammo.bin`, `Ammo.module.bin`, `Physx.bin`, `Physx.module.bin`, `Havok.bin`, `Havok.module.bin`, `Rapier.bin`, `Rapier.module.bin`, `Jolt.bin`, `Jolt.module.bin`.

### Vite Configuration

```js
// vite.config.js
import { defineConfig } from 'vite';
export default defineConfig({
  optimizeDeps: {
    exclude: ['phy-engine'],
  },
});
```

Then use `useLocal: true, useModule: true` in init:

```js
phy.init({ type: 'HAVOK', worker: true, useLocal: true, useModule: true, scene, callback: onReady });
```

## phy.set()

Configures global simulation settings. Call after `phy.init()` callback fires.

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `fps` | Number | `60` | Physics step frequency. |
| `substep` | Number | `1` | Substeps per frame for accuracy. Higher = more accurate, more CPU. |
| `gravity` | Array | `[0, -9.81, 0]` | Gravity vector `[x, y, z]`. |
| `fixe` | Boolean | `true` | Fixed timestep mode. |
| `full` | Boolean | `false` | Full velocity tracking (14 floats per body vs 8). |
| `worldScale` | Number | `1` | World scale factor. All positions/sizes are scaled internally. |
| `jointVisible` | Boolean | `false` | Show joint debug visualization. |

### Examples

```js
// Standard Earth gravity
phy.set({ fps: 60, substep: 2, gravity: [0, -9.81, 0] });

// Zero gravity
phy.set({ gravity: [0, 0, 0] });

// High precision simulation
phy.set({ fps: 120, substep: 4 });

// Scaled world (e.g., 1 unit = 10 meters)
phy.set({ worldScale: 10 });
```

## phy.start()

Begins the physics simulation. Call after adding initial objects.

```js
phy.start();
```

## Animation Loop

```js
function animate(stamp) {
    phy.doStep(stamp);  // gates physics step to configured FPS
    phy.step();          // syncs three.js objects with physics state
    renderer.render(scene, camera);
}
renderer.setAnimationLoop(animate);
```

- `phy.doStep(stamp)` — checks if enough time has elapsed for the next physics step. Pass the animation loop timestamp.
- `phy.step()` — reads the physics array and updates all Object3D positions, rotations, velocities. Must be called every frame.

In Worker mode with internal timeout (`isTimeout: true`), `doStep` may be handled by the worker. Check `outsideStep` to determine if you need to call it manually.

## Multiple Instances

For multiple independent physics scenes, use `phy2`:

```js
import { phy2 } from 'phy-engine';

const motor1 = new phy2();
const motor2 = new phy2();

motor1.init({ type: 'HAVOK', worker: true, scene, callback: () => motor1.start() });
motor2.init({ type: 'PHYSX', worker: true, scene, callback: () => motor2.start() });
```

Each instance has its own scene group, physics state, and animation loop. Call `doStep()` and `step()` on each instance separately.

## Lifecycle Methods

| Method | Description |
|--------|-------------|
| `phy.pause(true/false)` | Pause/resume simulation. |
| `phy.getPause()` | Returns current pause state. |
| `phy.reset(callback)` | Full reset — clears all bodies, joints, rays, etc. Calls callback when done. |
| `phy.clear(callback)` | Alias for `reset()`. |
| `phy.dispose()` | Full cleanup — terminates worker, removes scene groups. |
| `phy.ready()` | Manually trigger ready callback. |

## Utility Accessors

| Method | Returns |
|--------|---------|
| `phy.getScene()` | The internal `phy_scene` group. |
| `phy.byName(name)` | Look up any simulation object by name. |
| `phy.getFps()` | Current FPS (string). |
| `phy.getMs()` | Current step time in ms (string). |
| `phy.getDelta()` | Delta time for current frame. |
| `phy.getElapsedTime()` | Total elapsed simulation time. |
| `phy.getSetting()` | Current settings object. |
| `phy.getTime()` | Current timestamp. |
| `phy.getVersion()` | phy-engine version string. |
