# ScrollBox

Scrollable container with dynamic rendering, drag scrolling, and wheel support.

## Constructor

```ts
const scrollBox = new ScrollBox(options?: ScrollBoxOptions);
```

## Options (`ScrollBoxOptions`)

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `background` | `ColorSource` | — | Background color (undefined = transparent) |
| `width` | `number` | `100` | Container width |
| `height` | `number` | `100` | Container height |
| `radius` | `number` | `0` | Corner radius (mask + background) |
| `type` | `ListType` | `'vertical'` | Scroll direction: `'vertical'`, `'horizontal'`, `'bidirectional'` |
| `elementsMargin` | `number` | — | Margin between items |
| `padding` | `number` | — | Padding (all sides) |
| `vertPadding` / `horPadding` | `number` | — | Vertical/horizontal padding |
| `topPadding` / `bottomPadding` / `leftPadding` / `rightPadding` | `number` | — | Individual padding |
| `maxWidth` | `number` | — | Max width for bidirectional layout |
| `disableDynamicRendering` | `boolean` | `false` | Always render all items (performance cost) |
| `disableEasing` | `boolean` | `false` | Disable scroll easing/inertia |
| `dragTrashHold` | `number` | `10` | Minimum drag distance to start scrolling |
| `globalScroll` | `boolean` | `true` | Scroll on wheel even when mouse not over |
| `shiftScroll` | `boolean` | `false` | Shift+wheel for horizontal scroll |
| `proximityRange` | `number` | `0` | Pre-load range in pixels |
| `proximityDebounce` | `number` | `10` | Frame debounce for proximity checks |
| `disableProximityCheck` | `boolean` | `false` | Disable proximity detection |
| `items` | `Container[]` | — | Initial items |

## Properties

| Property | Type | Description |
|----------|------|-------------|
| `items` | `Container[]` | All child containers |
| `list` | `List` | Internal List layout container |
| `scrollX` | `number` | Current horizontal scroll position (negated) |
| `scrollY` | `number` | Current vertical scroll position (negated) |
| `scrollWidth` | `number` | Total content width |
| `scrollHeight` | `number` | Total content height |
| `width` | `number` | Container width |
| `height` | `number` | Container height |

## Events (Signals)

| Signal | Parameters | Description |
|--------|-----------|-------------|
| `onScroll` | `(value: number \| {x, y})` | Fires on scroll. Number for unidirectional, `{x, y}` for bidirectional |
| `onProximityChange` | `({item, index, inRange})` | Fires when items enter/leave proximity range |

## Methods

| Method | Description |
|--------|-------------|
| `addItem(...items)` | Add one or more items. Returns first item added |
| `addItems(items)` | Add array of items |
| `removeItem(itemID)` | Remove item by index |
| `removeItems()` | Remove all items |
| `scrollTop()` | Scroll to top/start |
| `scrollBottom()` | Scroll to bottom/end |
| `scrollTo(elementID)` | Scroll to item by index |
| `scrollToPosition({x, y})` | Scroll to absolute position |
| `isItemVisible(item, padding?)` | Check if item is in visible area |
| `resize(force?)` | Recalculate layout and mask |
| `destroy(options?)` | Cleanup — removes wheel listener and ticker |

## Example

```ts
const scrollBox = new ScrollBox({
    background: 0x111111,
    width: 400,
    height: 300,
    radius: 10,
    type: 'vertical',
    elementsMargin: 10,
    padding: 10,
});

// Add items
for (let i = 0; i < 50; i++) {
    const item = new Graphics()
        .roundRect(0, 0, 360, 50, 5)
        .fill(0x333333);
    scrollBox.addItem(item);
}

// Scroll events
scrollBox.onScroll.connect((value) => {
    console.log('scroll Y:', value);
});

// Programmatic scroll
scrollBox.scrollTop();
scrollBox.scrollTo(25);
scrollBox.scrollY = -100;

// Cleanup
scrollBox.destroy();
```

## Dynamic Rendering

By default, items outside the visible area have `renderable = false`:

1. During scroll, all items are temporarily made renderable
2. After 2 seconds of no scrolling, hidden items are set to `renderable = false`
3. This saves GPU rendering for large lists

Set `disableDynamicRendering: true` to always render all items (useful for small lists or when items need continuous updates).

## Scroll Mechanics

- **Drag** — Pointer down + move scrolls with inertia (Trackpad spring physics)
- **Wheel** — Document-level wheel listener scrolls the box. Respects `globalScroll` and `shiftScroll` options
- **Easing** — Scroll has spring-based easing (configurable via `disableEasing`)
- **Bidirectional** — Both axes scroll independently with their own Trackpad axis

## Proximity Detection

With `proximityRange > 0`, items within range of the visible area trigger `onProximityChange`:

```ts
scrollBox.onProximityChange.connect(({ item, index, inRange }) => {
    if (inRange) {
        // Pre-load content, start animations, etc.
    }
});
```

Useful for lazy-loading textures, starting animations near viewport, or triggering effects.

## Bidirectional Layout

With `type: 'bidirectional'`, items wrap like CSS `inline-block`:

```ts
const scrollBox = new ScrollBox({
    type: 'bidirectional',
    width: 400,
    height: 300,
});

// Control wrap width
if (scrollBox.list) {
    scrollBox.list.maxWidth = 800; // Items wrap at 800px
}
```
