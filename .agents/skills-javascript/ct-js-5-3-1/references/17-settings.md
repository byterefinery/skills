# Settings

## Render Settings

The `settings` object provides runtime render options.

### `settings.targetFps`

Target framerate. Cap to preserve battery or provide smoother lower FPS.

```js
settings.targetFps = 30; // Cap at 30 FPS
```

### `settings.viewMode`

Viewport scaling mode:

| Mode | Description |
|---|---|
| `'asIs'` | No viewport management; canvas at top-left |
| `'fastScale'` | Proportional fill, no resolution change |
| `'fastScaleInteger'` | Integer scaling (x2, x3, x4) |
| `'expand'` | Fill screen, camera expands |
| `'scaleFit'` | Proportional with letterboxing |
| `'scaleFill'` | Fill screen, no letterboxing (camera expands) |

```js
// Toggle between fast and quality scaling
if (settings.viewMode === 'fastScale') {
    settings.viewMode = 'scaleFit';
} else {
    settings.viewMode = 'fastScale';
}
```

### `settings.highDensity`

Enable high-DPI (retina) rendering:

```js
settings.highDensity = true;  // Enable
settings.highDensity = false; // Disable
```

Only visible on high-DPI screens. May impact performance on mobile.

### `settings.fullscreen`

Enter/exit fullscreen:

```js
settings.fullscreen = true;  // Enter fullscreen
settings.fullscreen = false; // Exit fullscreen
```

In web builds, can only be changed in pointer events (user interaction required).

### `settings.isDebug`

Read-only. `true` when running in ct.js IDE.

### `settings.isProduction`

Read-only. `true` when running in production (browser or desktop build).

### `settings.preventDefault`

Prevent default browser behavior for pointer/keyboard events:

```js
settings.preventDefault = true; // Prevent zoom, scroll, etc.
```

### `settings.pixelart`

Read-only. Whether pixelated rendering is enabled.

## Game Pause

```js
// Pause
pixiApp.ticker.speed = 0;

// Resume
pixiApp.ticker.speed = 1;

// Slow motion
pixiApp.ticker.speed = 0.5;
```

When `speed` is 0, `u.time` becomes 0, effectively freezing all gameplay that uses `u.time`.

## Gotchas

- **`settings.fullscreen` requires user interaction** — in web builds, can only be toggled inside pointer events.
- **Always provide fullscreen exit** — or players get stuck.
- **`settings.highDensity` is screen-dependent** — only visible on high-DPI screens.
- **`settings.viewMode` resizes viewport** — changing it triggers a full viewport recalculation.
- **`'expand'` and `'scaleFill'` change camera dimensions** — camera width/height expand to fill screen.
- **`'fastScaleInteger'` for pixel art** — ensures crisp integer scaling without interpolation.
- **`settings.isDebug` vs `settings.isProduction`** — can be overridden with "Force production tasks" in IDE.
- **`pixiApp.ticker.speed` is the pause mechanism** — not a `settings` property. Set directly on the ticker.
- **`u.time` becomes 0 when paused** — all gameplay using `u.time` freezes. Use `u.timeUi` for pause-independent logic.
- **`settings.preventDefault` default is `true`** — prevents accidental zoom/scroll in browsers.
- **`settings.targetFps` caps the ticker** — `pixiApp.ticker.maxFPS` under the hood.
