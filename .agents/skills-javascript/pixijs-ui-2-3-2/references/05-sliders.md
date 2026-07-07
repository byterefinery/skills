# Slider / DoubleSlider

## Slider

Single-value slider with draggable handle, fill bar, and step snapping.

### Constructor

```ts
const slider = new Slider(options: SliderOptions);
```

### Options (`SliderOptions`)

Extends `BaseSliderOptions` (which extends `ProgressBarOptions`):

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `bg` | `GetViewSettings` | required | Background bar |
| `fill` | `GetViewSettings` | required | Fill bar (shows progress) |
| `slider` | `Container \| string` | required | Draggable handle |
| `min` | `number` | `0` | Minimum value |
| `max` | `number` | `100` | Maximum value |
| `value` | `number` | `min` | Initial value |
| `step` | `number` | `1` | Step increment (snaps to nearest) |
| `showValue` | `boolean` | `false` | Show value text above handle |
| `valueTextStyle` | `PixiTextStyle` | `{fill: 0xffffff}` | Style for value text |
| `valueTextClass` | `PixiTextClass` | `Text` | Text class for value display |
| `valueTextOffset` | `{x?: number, y?: number}` | `{}` | Offset for value text |
| `nineSliceSprite` | `NineSliceSprite` | — | Nine-slice config for bg/fill |

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `value` | `number` | Current slider value |
| `min` | `number` | Minimum value |
| `max` | `number` | Maximum value |
| `step` | `number` | Step increment |

### Events (Signals)

| Signal | Parameters | Description |
|--------|-----------|-------------|
| `onUpdate` | `(value: number)` | Fires during drag on every value change |
| `onChange` | `(value: number)` | Fires when slider is released |

### Example

```ts
const slider = new Slider({
    bg: new Graphics().rect(0, 0, 200, 10).fill(0x333333),
    fill: new Graphics().rect(0, 0, 200, 10).fill(0x3366ff),
    slider: new Graphics().circle(0, 0, 10).fill(0xffffff),
    min: 0,
    max: 100,
    value: 50,
    step: 5,
    showValue: true,
    valueTextOffset: { x: 0, y: -20 },
});

slider.onUpdate.connect((value) => {
    // During drag
    label.text = Math.round(value).toString();
});

slider.onChange.connect((value) => {
    // On release
    console.log('final value:', value);
});

// Set value programmatically
slider.value = 75;
```

## DoubleSlider

Range slider with two draggable handles and fill between them.

### Constructor

```ts
const doubleSlider = new DoubleSlider(options: DoubleSliderOptions);
```

### Options (`DoubleSliderOptions`)

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `bg` | `GetViewSettings` | required | Background bar |
| `fill` | `GetViewSettings` | required | Fill bar between handles |
| `slider1` | `Container \| string` | required | Left handle |
| `slider2` | `Container \| string` | required | Right handle |
| `min` | `number` | `0` | Minimum value |
| `max` | `number` | `100` | Maximum value |
| `value1` | `number` | `min` | Initial left value |
| `value2` | `number` | `max` | Initial right value |
| `showValue` | `boolean` | `false` | Show value text above handles |
| `valueTextStyle` | `PixiTextStyle` | `{fill: 0xffffff}` | Style for value text |
| `valueTextOffset` | `{x?: number, y?: number}` | `{}` | Offset for value text |

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `value1` | `number` | Left handle value |
| `value2` | `number` | Right handle value |
| `min` | `number` | Minimum value |
| `max` | `number` | Maximum value |

### Events (Signals)

| Signal | Parameters | Description |
|--------|-----------|-------------|
| `onUpdate` | `(value1: number, value2: number)` | Fires during drag |
| `onChange` | `(value1: number, value2: number)` | Fires on release |

### Example

```ts
const rangeSlider = new DoubleSlider({
    bg: new Graphics().rect(0, 0, 200, 10).fill(0x333333),
    fill: new Graphics().rect(0, 0, 200, 10).fill(0x3366ff),
    slider1: new Graphics().circle(0, 0, 10).fill(0xffffff),
    slider2: new Graphics().circle(0, 0, 10).fill(0xffffff),
    min: 0,
    max: 100,
    value1: 20,
    value2: 80,
    showValue: true,
});

rangeSlider.onChange.connect((v1, v2) => {
    console.log(`Range: ${v1} — ${v2}`);
});

// Set values
rangeSlider.value1 = 30;
rangeSlider.value2 = 70;
```

### Handle Selection Logic

When clicking the background bar:
- Click left of both handles → moves `slider1`
- Click right of both handles → moves `slider2`
- Click between handles → moves the closer handle

### Constraints

- `value1` cannot exceed `value2`
- `value2` cannot be less than `value1`
- Both values are clamped to `[min, max]`
- Setting `value1` to a value greater than `value2` clamps it to `value2`
- Setting `value2` to a value less than `value1` clamps it to `value1`

## SliderBase

Internal base class extending `ProgressBar`. Provides shared slider functionality:

- Background and fill management (inherited from ProgressBar)
- Slider handle creation and positioning
- Pointer event handling for dragging
- Min/max/step configuration
- Value text display

Not intended for direct use — use `Slider` or `DoubleSlider` instead.
