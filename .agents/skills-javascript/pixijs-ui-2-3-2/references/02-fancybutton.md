# FancyButton

Full-featured button with state views, text, icon, animations, and content fitting.

## Constructor

```ts
const button = new FancyButton(options?: ButtonOptions);
```

## Options (`ButtonOptions`)

### State Views

| Option | Type | Description |
|--------|------|-------------|
| `defaultView` | `string \| Texture \| Container \| Sprite \| Graphics` | View shown in default state |
| `hoverView` | same | View shown on hover (desktop only) |
| `pressedView` | same | View shown when pressed |
| `disabledView` | same | View shown when disabled |

Views cascade: if `pressedView` is not set, `hoverView` is used; if not set, `defaultView` is used.

Pass a string (texture name) or `Texture` instance to enable `NineSliceSprite` via the `nineSliceSprite` option.

### Content

| Option | Type | Description |
|--------|------|-------------|
| `text` | `string \| number \| Text \| BitmapText \| HTMLText` | Button label |
| `icon` | `string \| Texture \| Container` | Icon view |

### Layout

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `padding` | `number` | `0` | Content inset from view edges |
| `scale` | `number` | `1` | Overall button scale |
| `anchor` | `number` | `0` | Anchor point (both axes) |
| `anchorX` | `number` | `0` | Horizontal anchor |
| `anchorY` | `number` | `0` | Vertical anchor |
| `offset` | `Offset` | `{}` | Per-state view offset |
| `textOffset` | `Offset` | `{}` | Per-state text offset |
| `iconOffset` | `Offset` | `{}` | Per-state icon offset |

### Base Scaling/Anchoring

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `defaultTextScale` | `Pos \| number` | `{x:1, y:1}` | Base text scale for fitting calc |
| `defaultIconScale` | `Pos \| number` | `{x:1, y:1}` | Base icon scale for fitting calc |
| `defaultTextAnchor` | `Pos \| number` | `{x:0.5, y:0.5}` | Base text anchor |
| `defaultIconAnchor` | `Pos \| number` | `{x:0.5, y:0.5}` | Base icon anchor |

### Content Fitting

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `contentFittingMode` | `'default' \| 'fill' \| 'none'` | `'default'` | How content fits inside view |

- **`'default'`** — Scale text/icon down to fit inside the button view (with padding). Does not scale up.
- **`'fill'`** — Scale text/icon to fill the available space, scaling up if needed.
- **`'none'`** — No auto-scaling. Content keeps its natural size.

### NineSlice

| Option | Type | Description |
|--------|------|-------------|
| `nineSliceSprite` | `[number, number, number, number]` | `[leftWidth, topHeight, rightWidth, bottomHeight]` for NineSliceSprite. Only works with texture strings or Texture instances. |

### Animations

```ts
animations: {
    default?: { props: AnimationData; duration?: number };
    hover?: { props: AnimationData; duration?: number };
    pressed?: { props: AnimationData; duration?: number };
    disabled?: { props: AnimationData; duration?: number };
}
```

`AnimationData` supports: `x`, `y`, `width`, `height`, `scale: {x, y}`.

Animations use `tweedle.js` tweens. Requires `Ticker.shared.add(() => Group.shared.update())`.

## Offset Type

```ts
type Offset = {
    x?: number;
    y?: number;
    default?: { x?: number; y?: number };
    hover?: { x?: number; y?: number };
    pressed?: { x?: number; y?: number };
    disabled?: { x?: number; y?: number };
};
```

Per-state offsets adjust the position of views, text, or icons for each button state.

## Properties

| Property | Type | Description |
|----------|------|-------------|
| `state` | `'default' \| 'hover' \| 'pressed' \| 'disabled'` | Current button state |
| `text` | `string` | Button text content |
| `padding` | `number` | Content padding |
| `offset` | `Offset` | View offsets |
| `textOffset` | `Offset` | Text offsets |
| `iconOffset` | `Offset` | Icon offsets |
| `defaultTextScale` | `Pos` | Base text scale |
| `defaultIconScale` | `Pos` | Base icon scale |
| `defaultTextAnchor` | `Pos` | Base text anchor |
| `defaultIconAnchor` | `Pos` | Base icon anchor |
| `contentFittingMode` | `ContentFittingMode` | Content fitting mode |
| `enabled` | `boolean` | Button enabled state |
| `anchor` | `ObservablePoint` | Button anchor point |
| `innerView` | `Container` | Container holding all inner views |
| `defaultView` | `Container \| undefined` | Current default view |
| `hoverView` | `Container \| undefined` | Current hover view |
| `pressedView` | `Container \| undefined` | Current pressed view |
| `disabledView` | `Container \| undefined` | Current disabled view |
| `textView` | `PixiText \| undefined` | Current text view |
| `iconView` | `Container \| undefined` | Current icon view |

## Events (Signals)

All signals use `typed-signals`. Subscribe with `.connect(handler)`.

| Signal | Parameters | Description |
|--------|-----------|-------------|
| `onPress` | `(btn?: FancyButton, e?: FederatedPointerEvent)` | Button pressed (tap/click) |
| `onDown` | `(btn, e)` | Pointer down on button |
| `onUp` | `(btn, e)` | Pointer up (inside or outside) |
| `onUpOut` | `(btn, e)` | Pointer up outside button |
| `onHover` | `(btn, e)` | Mouse hover (desktop only) |
| `onOut` | `(btn, e)` | Mouse leaves button |

## Methods

| Method | Description |
|--------|-------------|
| `setState(state, force?)` | Set button state, optionally forcing update |
| `removeView(viewType)` | Remove a view (`'defaultView'`, `'hoverView'`, `'pressedView'`, `'disabledView'`, `'textView'`, `'iconView'`) |
| `anchor.set(x, y)` | Set anchor point |

## State Machine

```
default ←→ hover ←→ pressed
  ↑           ↓         ↓
  └───────────disabled──┘
```

- On `pointerdown`: transitions to `pressed`
- On `pointerup`: transitions to `hover` (desktop) or `default` (mobile)
- On `pointerout`: transitions to `default`
- On `pointertap` (press): transitions to `hover` (desktop) or `default` (mobile)
- Setting `enabled = false`: transitions to `disabled`

## Examples

### Graphics-based Button

```ts
const button = new FancyButton({
    defaultView: new Graphics().roundRect(0, 0, 120, 40, 8).fill(0x3366ff),
    hoverView: new Graphics().roundRect(0, 0, 120, 40, 8).fill(0x5588ff),
    pressedView: new Graphics().roundRect(0, 0, 120, 40, 8).fill(0x2244cc),
    text: new Text({ text: 'Submit', style: { fill: 0xffffff, fontSize: 16 } }),
    padding: 10,
});
```

### Texture-based with NineSlice

```ts
const button = new FancyButton({
    defaultView: 'button_default.png',
    hoverView: 'button_hover.png',
    nineSliceSprite: [10, 10, 10, 10],
    text: 'Click',
});
```

### Animated Button

```ts
const button = new FancyButton({
    defaultView: 'button.png',
    text: 'Animated',
    animations: {
        hover: { props: { scale: { x: 1.1, y: 1.1 } }, duration: 100 },
        pressed: { props: { scale: { x: 0.9, y: 0.9 }, y: 5 }, duration: 100 },
        default: { props: { scale: { x: 1, y: 1 }, y: 0 }, duration: 100 },
    },
});
```

### Button with Icon

```ts
const button = new FancyButton({
    defaultView: 'button_bg.png',
    text: 'Save',
    icon: 'save_icon.png',
    iconOffset: { x: -30, y: 0 },
    textOffset: { x: 15, y: 0 },
});
```

### Dynamic Text Update

```ts
button.text = 'New Label';
// Text auto-refits to the active view
```

### Disable/Enable

```ts
button.enabled = false; // Switches to disabled state view
button.enabled = true;  // Switches back to default state view
```
