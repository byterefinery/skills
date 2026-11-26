# Events

## EventSystem

PixiJS uses a federated event system with unified pointer events (mouse + touch).

### Configuration

```ts
const app = new Application();
await app.init({
    eventMode: 'passive', // Default event mode for all objects

    eventFeatures: {
        move: true,        // Pointer movement events
        click: true,       // Click/tap events
        wheel: true,       // Wheel/scroll events
        globalMove: false, // Global pointer movement
    },
});

// Access event system
const eventSystem = app.renderer.events;
```

### Event Modes

| Mode | Description |
|---|---|
| `'none'` | No interaction events |
| `'passive'` | Children receive events, container itself doesn't (default) |
| `'auto'` | Receives events when parent is interactive |
| `'static'` | Standard interaction events |
| `'dynamic'` | Like static + synthetic hover/enter/leave events |

```ts
// Enable interaction on a sprite
sprite.eventMode = 'static';

// Enable interaction on a container (children can also receive events)
container.eventMode = 'passive';
```

## Pointer Events

Unified events that work for both mouse and touch.

### Event Types

| Event | Description |
|---|---|
| `pointerdown` | Pointer pressed down |
| `pointerup` | Pointer released (over target) |
| `pointerupoutside` | Pointer released (outside target) |
| `pointermove` | Pointer moved |
| `pointerover` | Pointer entered target |
| `pointerout` | Pointer left target |
| `pointercancel` | Pointer canceled |
| `pointertap` | Single tap/click |
| `globalpointermove` | Global pointer movement |

### FederatedPointerEvent

```ts
sprite.on('pointerdown', (e: FederatedPointerEvent) => {
    // Global coordinates
    e.global.x;
    e.global.y;

    // Local coordinates (relative to target)
    e.getLocalPosition(sprite.parent);

    // Pointer info
    e.pointerId;
    e.isPrimary;      // Is this the primary pointer?
    e.button;         // Mouse button (0, 1, 2)
    e.buttons;        // Buttons currently pressed
    e.deltaX;         // Movement delta X
    e.deltaY;         // Movement delta Y
    e.ctrlKey;
    e.shiftKey;
    e.altKey;
    e.metaKey;

    // Stop propagation
    e.stopPropagation();

    // Prevent default
    e.preventDefault();
});
```

### Event Propagation

Events follow capture → target → bubble phases:

```ts
// Events bubble up the scene graph
child.on('pointerdown', (e) => {
    console.log('Child received event');
    // e.stopPropagation(); // Prevent bubbling
});

parent.on('pointerdown', (e) => {
    console.log('Parent received event (bubbled)');
});

// Global events (from EventBoundary dispatch)
app.renderer.events?.rootBoundary.dispatch.on('pointerdown', (e) => {
    // Fires for ALL pointer downs, regardless of target
    console.log('Global pointer down at:', e.global.x, e.global.y);
});
```

## Hit Areas

Custom hit detection areas:

```ts
// Rectangle hit area
sprite.hitArea = new Rectangle(0, 0, 100, 100);

// Circle hit area
sprite.hitArea = new Circle(50, 50, 50);

// Ellipse hit area
sprite.hitArea = new Ellipse(50, 50, 50, 30);

// Polygon hit area
sprite.hitArea = new Polygon([
    { x: 0, y: 0 },
    { x: 100, y: 0 },
    { x: 50, y: 100 },
]);

// RoundedRectangle hit area
sprite.hitArea = new RoundedRectangle(0, 0, 100, 100, 10);

// Triangle hit area
sprite.hitArea = new Triangle(0, 0, 100, 0, 50, 100);

// Remove hit area (uses natural bounds)
sprite.hitArea = null;
```

## Wheel Events

```ts
sprite.on('wheel', (e: FederatedWheelEvent) => {
    e.deltaY;     // Vertical scroll amount
    e.deltaX;     // Horizontal scroll amount
    e.deltaMode;  // 0 = pixels, 1 = lines, 2 = pages

    e.stopPropagation();
    e.preventDefault();
});
```

## Cursor

```ts
// Set cursor
sprite.cursor = 'pointer';
sprite.cursor = 'grab';
sprite.cursor = 'crosshair';

// Custom cursor image
sprite.cursor = "url('my-cursor.png'), auto";

// Dynamic cursor
sprite.on('pointerover', () => { sprite.cursor = 'pointer'; });
sprite.on('pointerout', () => { sprite.cursor = 'auto'; });

// Default cursor styles (applied to all interactive objects)
app.renderer.events.cursorStyles.default = "url('default.png'), auto";
app.renderer.events.cursorStyles.hover = "url('hover.png'), auto";

// Use named cursor style
sprite.cursor = 'hover'; // Uses cursorStyles.hover
```

## EventBoundary

For advanced event handling in large scenes:

```ts
import { EventBoundary } from 'pixi.js';

// Create custom event boundary
const boundary = new EventBoundary(container);

// Hit test at position
const hit = boundary.hitTest(x, y);

// Custom hit testing (for spatial hash optimization)
class CustomEventBoundary extends EventBoundary {
    hitTestRecursive(x, y, rootTarget, limit) {
        // Custom hit testing logic
        // e.g., use spatial hash to find candidates
    }
}
```

## Mouse Events

Mouse-specific events (available when pointer is a mouse):

```ts
// These are alias events that map to pointer events
sprite.on('mousedown', (e) => {});
sprite.on('mouseup', (e) => {});
sprite.on('mouseupoutside', (e) => {});
sprite.on('mousemove', (e) => {});
sprite.on('mouseover', (e) => {});
sprite.on('mouseout', (e) => {});
sprite.on('click', (e) => {});
sprite.on('rightclick', (e) => {});
sprite.on('rightdown', (e) => {});
sprite.on('middleclick', (e) => {});
sprite.on('middledown', (e) => {});
```

## Touch Events

Touch-specific events:

```ts
sprite.on('touchstart', (e) => {});
sprite.on('touchend', (e) => {});
sprite.on('touchendoutside', (e) => {});
sprite.on('touchmove', (e) => {});
sprite.on('touchcancel', (e) => {});
```

## Listening Styles

PixiJS supports three styles of event listening:

```ts
// EventEmitter style (recommended)
const handler = (e) => console.log('clicked');
sprite.on('pointerdown', handler);
sprite.once('pointerdown', handler); // One-time
sprite.off('pointerdown', handler);

// DOM-style events
sprite.addEventListener(
    'click',
    (event) => { console.log('Clicked!', event.detail); },
    { once: true },
);
sprite.removeEventListener('click', handler);

// Callback style
sprite.onclick = (event) => {
    console.log('Clicked!', event.detail);
};
```

## Checking Interactivity

```ts
if (sprite.isInteractive()) {
    // true if eventMode is 'static' or 'dynamic'
}
```

## Event Performance Tips

- **Use `eventMode: 'none'`** for objects that don't need interaction
- **Use `eventMode: 'passive'`** on containers that only pass events to children
- **Use custom `hitArea`** for precise hit detection (faster than bounds check)
- **Disable unused features** — `eventFeatures: { globalMove: false }` if not needed
- **Use `stopPropagation()`** to prevent unnecessary event bubbling
- **Avoid event listeners in render loop** — add/remove outside of ticker
- **Use EventBoundary dispatch** for global event listening instead of per-object listeners
- **Use `interactiveChildren: false`** on containers with no interactive children to skip crawling
