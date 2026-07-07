# Input

Text entry component using a hidden HTML `<input>` element for keyboard input, with a PixiJS-rendered cursor and text display.

## Constructor

```ts
const input = new Input(options: InputOptions);
```

## Options (`InputOptions`)

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `bg` | `ViewType` | required | Background (texture name, Texture, Sprite, Graphics) |
| `textStyle` | `PixiTextStyle` | `{fill: 0x000000, align: 'center'}` | Text style |
| `TextClass` | `PixiTextClass` | `Text` | Text class: `Text`, `BitmapText`, `HTMLText` |
| `placeholder` | `string` | `''` | Placeholder text (shown when empty and not editing) |
| `value` | `string` | `''` | Initial text value |
| `maxLength` | `number` | `undefined` | Maximum character count |
| `secure` | `boolean` | `false` | Password mode (displays `*` characters) |
| `align` | `InputAlign` | `'left'` | Text alignment: `'left'`, `'center'`, `'right'` |
| `padding` | `Padding` | `0` | Text padding from bg edges |
| `cleanOnFocus` | `boolean` | `false` | Clear value when focus gained |
| `nineSliceSprite` | `[number, number, number, number]` | — | Nine-slice for bg |
| `addMask` | `boolean` | `false` | Mask text to bg bounds |

## Padding Type

```ts
type Padding =
    | number                          // Uniform padding
    | [number, number]                // [vertical, horizontal]
    | [number, number, number, number] // [top, right, bottom, left]
    | { top?: number; right?: number; bottom?: number; left?: number };
```

## Properties

| Property | Type | Description |
|----------|------|-------------|
| `value` | `string` | Current text value |
| `secure` | `boolean` | Password mode |
| `padding` | `[number, number, number, number]` | Current padding `[top, right, bottom, left]` |
| `bg` | `Container \| NineSliceSprite \| Graphics` | Background element |

## Events (Signals)

| Signal | Parameters | Description |
|--------|-----------|-------------|
| `onChange` | `(text: string)` | Fires on every character change |
| `onEnter` | `(text: string)` | Fires when input loses focus (blur) |

## Methods

| Method | Description |
|--------|-------------|
| `destroy(options?)` | Cleanup — removes window event listeners |

## Example

```ts
const input = new Input({
    bg: new Graphics().roundRect(0, 0, 200, 36, 6).fill(0x222222),
    textStyle: { fill: 0xffffff, fontSize: 16, fontFamily: 'Arial' },
    placeholder: 'Enter username...',
    padding: { top: 8, right: 12, bottom: 8, left: 12 },
    align: 'left',
    maxLength: 20,
});

input.onChange.connect((text) => {
    console.log('typing:', text);
});

input.onEnter.connect((text) => {
    console.log('submitted:', text);
});

// Set value
input.value = 'Hello';

// Toggle password mode
input.secure = true;  // Shows ***
input.secure = false; // Shows Hello
```

## How It Works

1. **Activation** — On `pointertap` on the input, a hidden `<input>` element is created and appended to `document.body`
2. **Hidden input** — Positioned at the input's global position, with near-zero opacity (`0.0000001`), matching size
3. **Keyboard capture** — All keystrokes go to the hidden input. Key events are intercepted via `onKeyUp`
4. **Text display** — The visible text is a PixiJS `Text` (or `BitmapText`/`HTMLText`) that mirrors the input value
5. **Cursor** — A white sprite (tinted to match text color) blinks via the shared ticker
6. **Deactivation** — On blur (clicking outside), the hidden input is removed, cursor stops blinking

### Key Handling

- **Single characters** — Appended to value (respecting `maxLength`)
- **Backspace** — Removes last character
- **Escape / Enter** — Stops editing, fires `onEnter`
- **Paste** — Full text paste supported via clipboard event
- **Modifier keys** — Shift, Ctrl, Alt, Meta, arrows, function keys are skipped

### Mobile Considerations

- On Android, focus/click on the hidden input uses a 100ms delay to prevent instant keyboard dismissal
- Touch events use `touchstart` instead of `click` for activation

### Auto-Align Behavior

When text overflows the input width:
- While editing: text aligns right (to show newest characters)
- While not editing: text aligns left (to show beginning)

This overrides the `align` option when overflow occurs.

### Cleanup

Always call `destroy()` when removing an Input:

```ts
input.destroy();
```

This removes:
- `window` event listener for activation
- `pointertap` listener
- Hidden `<input>` element (if active)
