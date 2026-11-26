# Switcher & MaskedFrame

## Switcher

Container-based base component that switches visibility of a list of views on interaction events. `CheckBox` and (conceptually) tabs/segments build on it.

### Constructor

```ts
new Switcher(
    views?: Array<Container | string>,
    triggerEvents?: ButtonEvent | ButtonEvent[],  // default 'onPress'
    activeViewID?: number,                        // initially visible view
    options?: ContainerOptions
);
```

`ButtonEvent` = `'onPress' | 'onDown' | 'onUp' | 'onHover' | 'onOut' | 'onUpOut'`.

### API

| Member | Description |
|--------|-------------|
| `views` | Get/set the switchable views (strings resolved via texture). Setting clears and re-adds them |
| `add(view)` | Append a view (hidden until active); the first added view becomes active automatically |
| `remove(id)` | Remove view by index |
| `active` | Get/set the active view id (set goes through `switch`) |
| `activeView` | The currently visible view |
| `triggerEvents` | Get/set which events trigger a switch (`'onPress'` default; pointer* events are mapped to these) |
| `switch(id?)` | Switch to the next view (or `id`). Emits `onChange` only when the active view actually changed |
| `forceSwitch(id?)` | Switch **without** emitting `onChange`; throws `View with id X does not exist.` for a bad id |
| `onChange` | `Signal<(state: number \| boolean) => void>` |

### `onChange` Payload

- **2 views** — emits a **boolean** (`active === 1`)
- **3+ views** — emits the **active id** (number)

Cycling: with no id, `switch()` advances to the next view and wraps to 0 after the last.

### Example

```ts
// Switch on press (default)
const sw = new Switcher(['switch_off.png', 'switch_on.png']);
sw.onChange.connect((state) => console.log(state)); // boolean

// Switch on hover in/out
const hoverSwitch = new Switcher(
    ['button_default.png', 'button_hover.png'],
    ['onHover', 'onOut']
);
```

## MaskedFrame

Draws a border of any shape around a target container and/or applies an arbitrary mask.

### Options (`MaskedFrameOptions`)

| Option | Type | Description |
|--------|------|-------------|
| `target` | `string \| Container` | Container to mask/border (string = texture name). **Required for `init` to run** — the constructor only initialises when `target` is provided |
| `mask` | `string \| Graphics` | Mask shape applied to the target |
| `borderWidth` | `number` | Border width (0 = none) |
| `borderColor` | `FillStyleInputs` | Border colour (default `0x000000`) |
| + `Omit<ContainerOptions, 'mask'>` | | `mask` is excluded so it doesn't collide with the component's mask option |

### API

| Member | Description |
|--------|-------------|
| `target` | The target container (public) |
| `border` | The `Graphics` that draws the border (public) |
| `init(options)` | (Re)initialise target/mask/border — removes the previous target first |
| `applyMask(mask)` | Set the target's mask (mask stored as `maskData`) |
| `setBorder(borderWidth, borderColor)` | Configure and show the border; when a mask exists, an enlarged copy of the mask clips the border graphics |
| `showBorder()` | Draw the border rect (target size + 2×borderWidth) and offset the target inward by `borderWidth` |
| `hideBorder()` | Clear the border graphics |

### Behaviour

- Border rendering: a filled rectangle in `borderColor` covering `target.size + 2×borderWidth`, with the target shifted by `(borderWidth, borderWidth)` so it sits inside.
- When a mask is set, the border is clipped by an enlarged clone of the mask (sprite for texture strings, `clone(true)` for Graphics), scaled up by `borderWidth` on each side — giving a border that follows the mask shape.

### Example

```ts
const frame = new MaskedFrame({
    target: 'avatar.png',
    mask: 'avatar_mask.png',
    borderWidth: 3,
    borderColor: 0xffffff,
});

frame.showBorder();
frame.hideBorder();
```
