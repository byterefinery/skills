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

Views cascade: if `pressedView` is not set, `hoverView` is used; if not set, `defaultView` is used. `disabledView` falls back to `defaultView`.

Pass a string (texture name) or `Texture` instance to enable `NineSliceSprite` via the `nineSliceSprite` option. Setting a view to `null` removes it.

### Content

| Option | Type | Description |
|--------|------|-------------|
| `text` | `string \| number \| Text \| BitmapText \| HTMLText` | Button label (0 is a valid label) |
| `icon` | `string \| Texture \| Container` | Icon view |

### Layout

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `padding` | `number` | `0` | Content inset from view edges |
| `scale` | `number` | `1` | Overall button scale (applied to the container; animation scales go to the inner view) |
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
- **`'fill'`** — Scale text/icon to fill the available space (view minus padding), up or down.
- **`'none'`** — No auto-scaling. Content keeps its natural size (default scale/anchor only).

### NineSlice

| Option | Type | Description |
|--------|------|-------------|
| `nineSliceSprite` | `[number, number, number, number]` | `[leftWidth, topHeight, rightWidth, bottomHeight]` for NineSliceSprite. Only works when views are texture strings or Texture instances. When set, `width`/`height`/`setSize` resize the state views instead of the container. |

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

Animations tween the **inner view** with `tweedle.js`. When the `animations` option is present, the button adds its own `Ticker.shared` callback in the constructor and removes it in `destroy()` — no manual ticker registration. A state with no entry animates back to the original inner-view state.

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

Per-state offsets adjust the position of views, text, or icons for each button state. A state entry falls back to the `default` entry, which falls back to a plain `{x, y}`.

## Properties

| Property | Type | Description |
|----------|------|-------------|
| `state` | `'default' \| 'hover' \| 'pressed' \| 'disabled'` | Current button state |
| `text` | `string \| undefined` | Button text content (getter) |
| `padding` | `number` | Content padding |
| `offset` | `Offset` | View offsets |
| `textOffset` | `Offset` | Text offsets |
| `iconOffset` | `Offset` | Icon offsets |
| `defaultTextScale` | `Pos` | Base text scale |
| `defaultIconScale` | `Pos` | Base icon scale |
| `defaultTextAnchor` | `Pos` | Base text anchor |
| `defaultIconAnchor` | `Pos` | Base icon anchor |
| `contentFittingMode` | `ContentFittingMode` | Content fitting mode |
| `enabled` | `boolean` | Button enabled state (false → disabled state view) |
| `anchor` | `ObservablePoint` | Button anchor point |
| `innerView` | `Container` | Container holding all inner views (animation target) |
| `defaultView` | `Container \| undefined` | Current default view |
| `hoverView` | `Container \| undefined` | Current hover view |
| `pressedView` | `Container \| undefined` | Current pressed view |
| `disabledView` | `Container \| undefined` | Current disabled view |
| `textView` | `PixiText \| undefined` | Current text view |
| `iconView` | `Container \| undefined` | Current icon view |

## Events (Signals)

Signals are the package's own `Signal` class — subscribe with `.connect(handler)`, remove with the returned connection's `.disconnect()`.

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
| `destroy(options?)` | Destroys the component; removes the shared-ticker callback if animations were set |

## State Machine

```
default ←→ hover ←→ pressed
  ↑           ↓         ↓
  └───────────disabled──┘
```

- On `onDown`: transitions to `pressed`
- On `onUp`: transitions to `hover` (desktop) or `default` (mobile)
- On `onUpOut`: transitions to `default`
- On `onOut`: transitions to `default` (only if pointer is not down)
- On `onPress`: transitions to `hover` (desktop) or `default` (mobile)
- On `onHover`: transitions to `hover` (desktop only, if pointer is not down)
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
