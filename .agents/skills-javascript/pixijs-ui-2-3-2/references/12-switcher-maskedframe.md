# Switcher / MaskedFrame

## Switcher

Base toggle component that switches visibility between views on pointer events.

### Constructor

```ts
const switcher = new Switcher(
    views?: Array<Container | string>,
    triggerEvents?: ButtonEvent | ButtonEvent[],
    activeViewID?: number
);
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `views` | `Array<Container \| string>` | Views to cycle through |
| `triggerEvents` | `ButtonEvent \| ButtonEvent[]` | Events that trigger switching |
| `activeViewID` | `number` | Initially active view index |

### ButtonEvent Type

```ts
type ButtonEvent = 'onDown' | 'onUp' | 'onUpOut' | 'onOut' | 'onPress' | 'onHover';
```

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `innerView` | `Container` | Container holding all views |
| `active` | `number \| undefined` | Index of currently visible view |
| `activeView` | `Container \| undefined` | Currently visible view |
| `views` | `Container[]` | All switchable views |
| `triggerEvents` | `ButtonEvent[]` | Events that trigger switching |
| `onChange` | `Signal<(state: number \| boolean) => void>` | Fires when active view changes |

### Methods

| Method | Description |
|--------|-------------|
| `switch(id?)` | Switch to next view, or to specific `id`. Emits `onChange` |
| `forceSwitch(id?)` | Switch without emitting `onChange` |
| `add(view)` | Add a view to the switching list |
| `remove(id)` | Remove view by index |

### Events (Signals)

| Signal | Parameters | Description |
|--------|-----------|-------------|
| `onChange` | `(state: number \| boolean)` | Fires when active view changes. For 2 views: `boolean` (true = view 1). For 3+ views: `number` (active index) |

### Examples

```ts
// Two-state toggle (like a checkbox without label)
const toggle = new Switcher(
    ['off.png', 'on.png'],
    'onPress',
    0
);
toggle.onChange.connect((state) => {
    // state is boolean: false = view 0, true = view 1
});

// Three-state cycle
const cycle = new Switcher(
    ['state1.png', 'state2.png', 'state3.png'],
    'onPress'
);
cycle.onChange.connect((state) => {
    // state is number: 0, 1, or 2
});

// Hover-triggered switch (like a button with hover state)
const hoverSwitch = new Switcher(
    ['default.png', 'hover.png'],
    ['onHover', 'onOut']
);

// Programmatic control
switcher.switch();      // Next view
switcher.switch(2);     // Jump to view 2
switcher.active;         // Current index
switcher.add('new.png'); // Add view
switcher.remove(1);      // Remove view at index 1
```

### How It Works

1. All views are added to `innerView` with `visible = false`
2. The active view is set to `visible = true`
3. On trigger events, `switch()` cycles to the next view (or jumps to specified index)
4. The previous active view is hidden, the new one is shown
5. `onChange` emits with `boolean` (2 views) or `number` (3+ views)

### Event Binding

Pointer events are bound on `innerView`:

```
pointerdown     → handleEvents('onDown')
pointerup       → handleEvents('onUp')
pointerupoutside → handleEvents('onUpOut')
pointerout      → handleEvents('onOut')
pointertap      → handleEvents('onPress')
pointerover     → handleEvents('onHover')
```

If the event is in `triggerEvents` set, `switch()` is called.

## MaskedFrame

Applies a mask and/or border to a target container.

### Constructor

```ts
const frame = new MaskedFrame(options?: MaskedFrameOptions);
```

### Options (`MaskedFrameOptions`)

| Option | Type | Description |
|--------|------|-------------|
| `target` | `string \| Container` | Container to apply mask/border to |
| `mask` | `string \| Graphics` | Mask shape |
| `borderWidth` | `number` | Border width in pixels |
| `borderColor` | `FillStyleInputs` | Border color |

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `target` | `Container \| undefined` | Target container |
| `border` | `Graphics` | Border graphics element |

### Methods

| Method | Description |
|--------|-------------|
| `init(options)` | Initialize/reinitialize with options |
| `applyMask(mask)` | Apply a mask to the target |
| `setBorder(borderWidth, borderColor)` | Show border around target |
| `showBorder()` | Show the border |
| `hideBorder()` | Hide the border |

### Example

```ts
// Circular avatar with border
const frame = new MaskedFrame({
    target: 'avatar.png',
    mask: 'circle_mask.png',
    borderWidth: 3,
    borderColor: 0xffffff,
});

// Apply mask only (no border)
const masked = new MaskedFrame({
    target: 'image.png',
    mask: new Graphics().circle(0, 0, 50).fill(0xffffff),
});

// Border only
const bordered = new MaskedFrame({
    target: 'panel.png',
    borderWidth: 2,
    borderColor: 0x3366ff,
});
bordered.showBorder();

// Toggle border
bordered.hideBorder();
bordered.showBorder();
```

### How Border Works

1. A `Graphics` rect is drawn matching the target size + border width
2. The target is offset by `borderWidth` to center within the border
3. If a mask is provided, a border mask is created from the mask (expanded by border width) and applied
4. The border uses the mask shape, so a circular mask produces a circular border
