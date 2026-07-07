# Ticker

## Ticker Class

Frame-based update loop with delta time tracking.

### Time Units

| Property | Type | Description |
|---|---|---|
| `deltaTime` | `number` | Dimensionless scalar (~1.0 at 60 FPS) |
| `deltaMS` | `number` | Milliseconds since last frame (capped, scaled) |
| `elapsedMS` | `number` | Raw milliseconds (uncapped, unscaled) |
| `lastTime` | `number` | Timestamp (performance.now() format) |
| `FPS` | `number` | Current frames per second |
| `elapsedMS` | `number` | Total elapsed time |

### Shared Ticker

Global ticker instance, used by default by Application.

```ts
import { Ticker } from 'pixi.js';

// Add listener
Ticker.shared.add((ticker) => {
    // Frame-independent animation
    sprite.rotation += 0.1 * ticker.deltaTime;

    // Time-based animation
    sprite.x += (100 / 1000) * ticker.deltaMS; // 100px per second
});

Ticker.shared.start();
Ticker.shared.stop();
```

### System Ticker

Low-priority ticker for background updates.

```ts
Ticker.system.add((ticker) => {
    // Background updates
});
Ticker.system.start();
```

### Custom Ticker

```ts
const ticker = new Ticker();

ticker.add((ticker) => {
    sprite.rotation += 0.1 * ticker.deltaTime;
});

ticker.start();
ticker.stop();
ticker.destroy();
```

### Auto Start

```ts
const ticker = new Ticker();
ticker.autoStart = true; // Automatically starts when first listener added

ticker.add((ticker) => {
    // Starts automatically
});
```

### Update Priority

Higher priority values run earlier.

```ts
import { UPDATE_PRIORITY } from 'pixi.js';

// Constants:
// UPDATE_PRIORITY.HIGH = 50
// UPDATE_PRIORITY.NORMAL = 0
// UPDATE_PRIORITY.LOW = -50

// High priority (runs first)
ticker.add(
    (ticker) => { physics.update(ticker.deltaTime); },
    undefined,
    UPDATE_PRIORITY.HIGH
);

// Normal priority (default)
ticker.add((ticker) => { game.update(ticker); });

// Low priority (runs last)
ticker.add(
    (ticker) => { ui.update(ticker); },
    undefined,
    UPDATE_PRIORITY.LOW
);
```

### One-Time Updates

```ts
// Runs once on next frame
ticker.addOnce((ticker) => {
    console.log('Runs once');
});
```

### Removing Listeners

```ts
const callback = (ticker) => {
    sprite.rotation += 0.1 * ticker.deltaTime;
};

ticker.add(callback);

// Remove specific callback
ticker.remove(callback);

// Remove all
ticker.removeListeners();
```

### Speed Control

```ts
// Normal speed
ticker.speed = 1;

// Slow motion
ticker.speed = 0.5;

// Fast forward
ticker.speed = 2;

// Pause (no time advancement)
ticker.speed = 0;
```

### FPS Capping

```ts
// Minimum FPS (maximum frame time)
ticker.minFPS = 60; // Cap at 60fps (skip frames if slower)

// Target FPS
Ticker.targetFPMS = 0.06; // 60 FPS (frames per millisecond)
```

## Animation Patterns

### Frame-Independent Movement

```ts
// Using deltaTime (scalar)
ticker.add((ticker) => {
    sprite.x += 100 * ticker.deltaTime; // 100 units per frame at target FPS
});

// Using deltaMS (milliseconds)
ticker.add((ticker) => {
    sprite.x += (100 / 1000) * ticker.deltaMS; // 100 pixels per second
});
```

### Rotation

```ts
ticker.add((ticker) => {
    sprite.rotation += 0.5 * ticker.deltaTime; // 0.5 radians per frame
    sprite.angle += 30 * ticker.deltaTime;     // 30 degrees per frame
});
```

### Pulsing Scale

```ts
ticker.add((ticker) => {
    const time = ticker.elapsedMS / 1000;
    sprite.scale.set(1 + Math.sin(time * 2) * 0.2);
});
```

### Easing

```ts
const start = ticker.lastTime;
const duration = 1000; // 1 second

ticker.add((ticker) => {
    const elapsed = ticker.elapsedMS - start;
    const progress = Math.min(elapsed / duration, 1);

    // Ease out cubic
    const eased = 1 - Math.pow(1 - progress, 3);

    sprite.x = startX + (endX - startX) * eased;
    sprite.alpha = 1 - eased;
});
```

### Tweening

```ts
function tween(obj: any, props: Record<string, number>, duration: number) {
    const startValues: Record<string, number> = {};
    const startTime = Ticker.shared.lastTime;

    Object.keys(props).forEach(key => {
        startValues[key] = obj[key];
    });

    const update = (ticker: Ticker) => {
        const elapsed = ticker.elapsedMS - startTime;
        const progress = Math.min(elapsed / duration, 1);

        Object.keys(props).forEach(key => {
            obj[key] = startValues[key] + (props[key] - startValues[key]) * progress;
        });

        if (progress >= 1) {
            Ticker.shared.remove(update);
        }
    };

    Ticker.shared.add(update);
}

// Usage
tween(sprite, { x: 400, y: 300, alpha: 0 }, 1000);
```

## TickerPlugin

Built-in Application plugin that manages the render loop.

```ts
// Enabled by default with Application
const app = new Application();
await app.init({
    autoStart: true,    // TickerPlugin starts automatically
    sharedTicker: true, // Use Ticker.shared
});

// Manual control
app.start();  // Start rendering
app.stop();   // Stop rendering
```

## Performance Tips

- **Use `deltaTime`** for frame-independent animations (scalar, ~1.0 at 60fps)
- **Use `deltaMS`** for time-based calculations (actual milliseconds)
- **Avoid heavy work in ticker** — keep callbacks lightweight
- **Use priorities** — HIGH for physics, LOW for UI
- **Remove unused listeners** — prevents memory leaks
- **Use `addOnce`** for one-time updates
- **Share ticker** — use `Ticker.shared` instead of multiple tickers
- **Set `minFPS`** to cap frame time and prevent spiral of death
- **Use `speed`** for slow motion / fast forward effects
- **Don't create/destroy objects in ticker** — use object pools
