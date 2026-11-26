# Progress — ProgressBar / CircularProgressBar

## ProgressBar

Linear fill bar: a `bg` track with a `fill` that is masked to the current progress percentage.

### Options (`ProgressBarOptions`)

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `bg` | view | `Texture.WHITE` | Track background (string, Texture, Sprite, Graphics) |
| `fill` | view | `Texture.WHITE` | Fill, masked to progress |
| `fillPaddings` | `{ top?, right?, bottom?, left? }` | all `0` | Inset of the fill from the track edges |
| `nineSliceSprite` | `{ bg: [l,t,r,b], fill: [l,t,r,b] }` | — | Nine-slice scaling (texture names/Texture instances only) |
| `progress` | `number` | `0` | Initial progress, 0–100 |
| + `ContainerOptions` | | | Passed through to the container |

### API

| Member | Type | Description |
|--------|------|-------------|
| `progress` | `number` | Get/set current progress (clamped 0–100, rounded; NaN → 0) |
| `innerView` | `Container` | Holds bg (index 0) and fill (index 1) |
| `width` / `height` / `setSize` | — | Resize bg and fill; with `nineSliceSprite` set, fill is resized by the `fillPaddings` |

### Behaviour

- The fill is masked by a `NineSliceSprite` mask sized to `(progress - progressStart)` — `progressStart` is used by the double slider to render a range (fill between two values).
- Using the **same Sprite instance for `bg` and `fill`** logs a warning and is a no-op.
- Progress values above 100 clamp to 100, below 0 clamp to 0.

### Example

```ts
const bar = new ProgressBar({
    bg: 'slider_bg.png',
    fill: 'slider.png',
    fillPaddings: { top: 2, right: 2, bottom: 2, left: 2 },
    progress: 50,
});
bar.progress = 65; // 0–100
```

## CircularProgressBar

Arc-based progress indicator drawn with `Graphics` strokes (no textures).

### Options (`MaskedProgressBarOptions`)

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `radius` | `number` | `50` | Arc radius |
| `lineWidth` | `number` | `5` | Stroke width (bg and fill) |
| `backgroundColor` | `ColorSource` | — | Track colour (omitted ⇒ track hidden) |
| `backgroundAlpha` | `number` | — | Track alpha (only applies when `backgroundColor` is set) |
| `fillColor` | `ColorSource` | `0xffffff` | Progress colour |
| `fillAlpha` | `number` | — | Progress alpha |
| `cap` | `'butt' \| 'round' \| 'square'` | — | Line cap for the fill stroke |
| `value` | `number` | — | Initial progress (0–100; `0` is accepted) |
| + `ContainerOptions` | | | Passed through to the container |

### API

| Member | Type | Description |
|--------|------|-------------|
| `progress` | `number` | Get/set current progress (clamped 0–100, NaN → 0) |
| `innerView` | `Container` | Holds `bgCircle` and `fillCircle` graphics |

### Behaviour

- The arc starts at **12 o'clock** (−90°) and sweeps clockwise to `value` percent of 360°.
- When no `backgroundColor` is given, the background stroke is drawn with near-zero alpha (kept in the scene graph but invisible).
- With `fillAlpha: 0` and `progress: 0`, the fill is cleared entirely.

### Example

```ts
const circular = new CircularProgressBar({
    backgroundColor: 0x000000,
    backgroundAlpha: 0.5,
    lineWidth: 10,
    fillColor: 0xffffff,
    radius: 50,
    value: 50,
    cap: 'round',
});
circular.progress = 100;
```
