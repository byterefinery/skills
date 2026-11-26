# ScrollBox — Scrollable Container

A scrollable view that arranges a list of containers (via an internal `List`) and scrolls it with drag and mouse wheel. Items outside the visible area are not rendered by default (dynamic rendering).

## Options (`ScrollBoxOptions`)

`ScrollBoxOptions = { width?, height?, background?, type?, radius?, disableDynamicRendering?, disableEasing?, dragTrashHold?, globalScroll?, shiftScroll?, proximityRange?, proximityDebounce?, disableProximityCheck? } & Omit<ListOptions, 'children'>`

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `width` / `height` | `number` | `100` (or bg size) | Box dimensions; without them the box is not scrollable |
| `background` | `ColorSource` | — | Box background colour (Graphics roundRect, radius-corners). Unset ⇒ near-invisible bg (still draggable) |
| `type` | `ListType` | `'vertical'` | `vertical` \| `horizontal` \| `bidirectional` |
| `radius` | `number` | `0` | Corner radius of box and mask |
| `items` | `Container[]` | — | Initial items (each must have a size; missing size logs an error) |
| `disableDynamicRendering` | `boolean` | — | Keep off-screen items rendered (performance cost) |
| `disableEasing` | `boolean` | — | Disable the Trackpad easing (momentum) on wheel/drag |
| `dragTrashHold` | `number` | `10` | Pixels the pointer must move before a drag starts (so clicks on items still work) |
| `globalScroll` | `boolean` | `true` | Scroll on wheel even when the pointer is not over the box |
| `shiftScroll` | `boolean` | `false` | For `horizontal`/`bidirectional`: scroll horizontally only with shift held |
| `proximityRange` | `number` | `0` | Extra margin around the box that counts as "visible" for proximity events |
| `proximityDebounce` | `number` | `10` | Frames between proximity checks while scrolling |
| `disableProximityCheck` | `boolean` | — | Skip proximity checks entirely |
| + `ListOptions` (minus `children`) | | | `elementsMargin`, `padding`, `vertPadding`, `horPadding`, `topPadding`, `bottomPadding`, `leftPadding`, `rightPadding`, `maxWidth`, `maxHeight` |

## API

| Member | Description |
|--------|-------------|
| `list` | The internal `List` that arranges the items (public for tuning) |
| `items` | Get all inner items (`Container[]`) |
| `addItem(...items)` / `addItems(items)` | Add one or many items (batch adds arrange once) |
| `removeItem(itemID)` / `removeItems()` | Remove by index / remove all |
| `onScroll` | `Signal<(value: number \| {x, y}) => void>` — number for single-axis, `{x, y}` for bidirectional |
| `onProximityChange` | `Signal<({ item, index, inRange }) => void>` — fires when an item enters/leaves the visible range (proximityRange) |
| `isItemVisible(item, padding?)` | Check whether an item is inside the visible area (+ padding) |
| `scrollTop()` | Scroll to the first item (resets both axes) |
| `scrollBottom()` | Scroll to the last item (falls back to top when not scrollable) |
| `scrollTo(elementID)` | Scroll so the item at index `elementID` is visible |
| `scrollToPosition({ x?, y? })` | Scroll to a raw position (positive values map to negative trackpad offsets) |
| `scrollX` / `scrollY` | Get/set the raw (negative) scroll offsets |
| `scrollWidth` / `scrollHeight` | Content width/height (the inner List's size) |
| `width` / `height` / `setSize` / `getSize` | Resize the box (explicit sizes stop content-based sizing) |
| `setBackground(color?)` | Change the background colour |
| `resize(force?)` | Re-measure content and re-apply masks |
| `destroy(options?)` | Remove ticker callback, the **document wheel listener**, and pending timeouts |

## Behaviour & Gotchas

- **Dynamic rendering** — off-screen items get `renderable = false`. On `pointerdown` all items are rendered (so drags never show gaps); after release, a 2-second timeout hides off-screen items again. `disableDynamicRendering: true` disables all of it.
- **Global wheel listener** — `makeScrollable()` adds `document.addEventListener('wheel', ..., true)` (capture phase). It is removed only in `destroy()`. With `globalScroll` defaulting to `true`, any wheel event scrolls the box even without hover.
- **Drag uses a trackpad** — pointer moves feed a `Trackpad` (spring/easing) that clamps the List position into `[boxSize - contentSize, 0]`. Content that fits has a range of 0, so it cannot be dragged out of view.
- **Clicks vs drags** — items get `eventMode = 'static'`; if the drag exceeds `dragTrashHold`, the pressed child is released with a synthetic `mouseupoutside`/`pointerupoutside` so its click is reverted.
- **Bidirectional scroll emits `{x, y}`**; single-axis emits a number.
- **Width without explicit size** — when `width`/`height` are not set, the box sizes to its content on resize.
- **Proximity** — while scrolling, every `proximityDebounce` frames each item's visibility (with `proximityRange` padding) is re-checked; changes emit `onProximityChange` once per transition.

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
    proximityRange: 100,
});

scrollBox.addItem(container);
scrollBox.addItems([c1, c2]);

scrollBox.onScroll.connect((value) => console.log(value));
scrollBox.onProximityChange.connect(({ item, index, inRange }) => {
    if (inRange) highlight(item);
});

scrollBox.scrollTop();
scrollBox.scrollTo(5);
scrollBox.scrollToPosition({ x: 0, y: 200 });
```
