# Sliders — Slider / DoubleSlider / SliderBase

Sliders extend `ProgressBar`: the `bg` track is also the drag surface (clicking/dragging anywhere on it moves the value), and the fill shows progress from `min` to `max`.

## Slider — Single Value

### Options (`SliderOptions`)

`SliderOptions = BaseSliderOptions & { slider, step?, value? }`

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `slider` | `Container \| string` | — | **Required.** Handle view (texture name or container) |
| `bg` | view | — | Track background (required by ProgressBar) |
| `fill` | view | — | Fill between track start and handle |
| `min` | `number` | `0` | Minimum value |
| `max` | `number` | `100` | Maximum value |
| `value` | `number` | `min` | Initial value |
| `step` | `number` | `1` | Snap interval (zero/non-finite falls back to 1) |
| `fillPaddings` | `{top?, right?, bottom?, left?}` | `{0,0,0,0}` | Fill inset from track edges |
| `nineSliceSprite` | `{bg: [l,t,r,b], fill: [l,t,r,b]}` | — | Nine-slice config for track and fill |
| `showValue` | `boolean` | — | Show a text label of the current value above the handle |
| `valueTextStyle` | `PixiTextStyle` | `{ fill: 0xffffff }` | Label style |
| `valueTextClass` | `Text \| BitmapText \| HTMLText` | `Text` | Label class |
| `valueTextOffset` | `{ x?, y? }` | `{0,0}` | Label offset from the handle |

### Signals

| Signal | Parameters | Description |
|--------|-----------|-------------|
| `onUpdate` | `(value: number)` | Fires while dragging **and** whenever `value` is set programmatically |
| `onChange` | `(value: number)` | Fires only when a drag is released |

### Properties

`value`, `min`, `max`, `step` (getters/setters — setting any of them re-lays the slider out), plus the `ProgressBar` surface (`bg`, `fill`, `width`, `height`).

### Behaviour

- Dragging snaps the raw value to the nearest multiple of `step`.
- The handle is centred on the progress position along the track; value is clamped to `[min, max]`.
- `width`/`height`/`setSize` also re-lay the slider out.

### Example

```ts
const slider = new Slider({
    bg: 'slider_bg.png',
    fill: 'slider.png',
    slider: 'slider_handle.png',
    min: 0,
    max: 100,
    value: 50,
    step: 5,
    showValue: true,
});

slider.onUpdate.connect((v) => console.log('dragging:', v));
slider.onChange.connect((v) => console.log('released:', v));
slider.value = 75;
```

## DoubleSlider — Range Selection

### Options (`DoubleSliderOptions`)

`DoubleSliderOptions = BaseSliderOptions & { slider1?, slider2?, value1?, value2? }`

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `slider1` | `Container \| string` | — | Left handle |
| `slider2` | `Container \| string` | — | Right handle |
| `value1` | `number` | `min` | Initial left value |
| `value2` | `number` | `max` | Initial right value |
| + all `BaseSliderOptions` | | | `min`, `max`, `bg`, `fill`, `fillPaddings`, `nineSliceSprite`, `showValue`, `valueTextStyle`, `valueTextClass`, `valueTextOffset` (no `step` snapping on the double slider) |

### Signals

| Signal | Parameters | Description |
|--------|-----------|-------------|
| `onUpdate` | `(value1: number, value2: number)` | Fires while dragging either handle |
| `onChange` | `(value1: number, value2: number)` | Fires when a drag is released |

### Behaviour

- The fill spans between the two handles (`progressStart` = value1, `progress` = value2).
- **Crossing is prevented** — `value1` is clamped to ≤ `value2`, `value2` to ≥ `value1` and ≤ `max`; on drag, the nearest handle wins.
- Initial out-of-order values are corrected (`value2 < value1` ⇒ `value2 = value1`), and values are clamped into `[min, max]` first.

### Example

```ts
const doubleSlider = new DoubleSlider({
    bg: 'slider_bg.png',
    fill: 'slider_progress.png',
    slider1: 'slider_handle.png',
    slider2: 'slider_handle.png',
    min: 0,
    max: 100,
    value1: 20,
    value2: 80,
});

doubleSlider.onChange.connect((v1, v2) => console.log(`range: ${v1} - ${v2}`));
```

## SliderBase (internal)

`SliderBase` is the shared base (extends `ProgressBar`): holds `slider1`/`slider2`, `min`/`max`/`step`, drag handling on the bg (`pointerdown`, `globalpointermove`, `pointerup`, `pointerupoutside`), and the value-label plumbing. Use `Slider` or `DoubleSlider` directly.

Notes from the implementation:

- The bg is the drag surface — `fill` gets `eventMode = 'none'` so it never intercepts.
- The step setter guards against zero/non-finite steps (falls back to 1) to avoid NaN snap arithmetic.
- `showValue` labels are anchored at (0.5) and follow their handle.
