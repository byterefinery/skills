# ProgressBar / CircularProgressBar

## ProgressBar

Linear progress bar with background, fill, and optional nine-slice scaling.

### Constructor

```ts
const bar = new ProgressBar(options?: ProgressBarOptions);
```

### Options (`ProgressBarOptions`)

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `bg` | `GetViewSettings` | `Texture.WHITE` | Background view |
| `fill` | `GetViewSettings` | `Texture.WHITE` | Fill view (clipped by progress) |
| `fillPaddings` | `FillPaddings` | `{top:0, right:0, bottom:0, left:0}` | Fill inset from bg edges |
| `nineSliceSprite` | `NineSliceSprite` | — | Nine-slice for bg and fill |
| `progress` | `number` | `0` | Initial progress (0–100) |

### NineSliceSprite Type

```ts
type NineSliceSprite = {
    bg: [number, number, number, number];     // [left, top, right, bottom]
    fill: [number, number, number, number];
};
```

### FillPaddings Type

```ts
type FillPaddings = {
    top?: number;
    right?: number;
    bottom?: number;
    left?: number;
};
```

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `progress` | `number` | Current progress (0–100, clamped) |
| `innerView` | `Container` | Container holding bg and fill |

### Example

```ts
const bar = new ProgressBar({
    bg: new Graphics().rect(0, 0, 200, 12).fill(0x333333),
    fill: new Graphics().rect(0, 0, 200, 12).fill(0x3366ff),
    fillPaddings: { top: 2, right: 2, bottom: 2, left: 2 },
    progress: 0,
});

bar.progress = 65; // 0–100

// Texture-based with nine-slice
const bar = new ProgressBar({
    bg: 'bar_bg.png',
    fill: 'bar_fill.png',
    nineSliceSprite: {
        bg: [5, 5, 5, 5],
        fill: [5, 5, 5, 5],
    },
    progress: 50,
});
```

### Progress Clamping

Progress is automatically clamped:
- Values below 0 → 0
- Values above 100 → 100
- Values are rounded to integers

### How Fill Works

The fill is clipped using a `NineSliceSprite` mask. The mask width is calculated as:

```
maskWidth = (fillWidth / 100) * progress
```

The fill extends full width but only the masked portion is visible.

## CircularProgressBar

Arc-based circular progress indicator using Graphics arc drawing.

### Constructor

```ts
const circular = new CircularProgressBar(options?: MaskedProgressBarOptions);
```

### Options (`MaskedProgressBarOptions`)

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `backgroundColor` | `ColorSource` | — | Background arc color (undefined = invisible) |
| `fillColor` | `ColorSource` | `0xffffff` | Fill arc color |
| `lineWidth` | `number` | `5` | Stroke width for both arcs |
| `radius` | `number` | `50` | Arc radius |
| `value` | `number` | — | Initial progress value |
| `backgroundAlpha` | `number` | `1` | Background arc alpha |
| `fillAlpha` | `number` | — | Fill arc alpha |
| `cap` | `'butt' \| 'round' \| 'square'` | — | Line cap style |

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `progress` | `number` | Current progress (0–100) |
| `innerView` | `Container` | Container holding bg and fill graphics |

### Example

```ts
const circular = new CircularProgressBar({
    backgroundColor: 0x333333,
    backgroundAlpha: 0.5,
    fillColor: 0x3366ff,
    lineWidth: 8,
    radius: 50,
    value: 0,
    cap: 'round',
});

circular.progress = 75; // 0–100

// Without background
const minimal = new CircularProgressBar({
    fillColor: 0x3366ff,
    lineWidth: 4,
    radius: 30,
    cap: 'butt',
});
minimal.progress = 50;
```

### Arc Drawing

- The arc starts at the top (−90°) and sweeps clockwise
- End angle: `(360 / 100) * progress` degrees from start
- At `progress = 0` with `fillAlpha = 0`, the fill is cleared entirely
- Progress is clamped to 0–100

### Centering

Position the circular progress bar at its center:

```ts
circular.position.set(400, 300);
// Arc is drawn centered at (0, 0) in local space
```

To add text in the center:

```ts
const label = new Text({
    text: '75%',
    style: { fill: 0xffffff, fontSize: 16, align: 'center' },
});
label.anchor.set(0.5);
circular.addChild(label);
```
