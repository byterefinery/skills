# CheckBox / RadioGroup

## CheckBox

Two-state toggle component extending `Switcher`.

### Constructor

```ts
const checkbox = new CheckBox(options: CheckBoxOptions);
```

### Options (`CheckBoxOptions`)

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `style` | `CheckBoxStyle` | required | Checked/unchecked views + optional text style |
| `text` | `string` | `''` | Label text |
| `TextClass` | `PixiTextClass` | `Text` | Text class: `Text`, `BitmapText`, or `HTMLText` |
| `checked` | `boolean` | `false` | Initial checked state |

### CheckBoxStyle

```ts
type CheckBoxStyle = {
    checked: GetViewSettings;      // View when checked
    unchecked: GetViewSettings;    // View when unchecked
    text?: PixiTextStyle;          // Text style (applied when set via style setter)
    textOffset?: { x?: number; y?: number }; // Text position offset
};
```

`GetViewSettings` accepts: `string` (texture name), `Texture`, `Sprite`, `Graphics`, or `Container`.

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `checked` | `boolean` | Current checked state |
| `text` | `string` | Label text |
| `style` | `CheckBoxStyle` | Style configuration |
| `labelText` | `PixiText \| undefined` | Text label element |

### Events (Signals)

| Signal | Parameters | Description |
|--------|-----------|-------------|
| `onCheck` | `(state: boolean)` | Fires when checked state changes |
| `onChange` | `(state: boolean)` | Inherited from Switcher |

### Methods

| Method | Description |
|--------|-------------|
| `forceCheck(checked)` | Set state without emitting `onCheck` signal |

### Examples

```ts
// Graphics-based checkbox
const checkbox = new CheckBox({
    style: {
        unchecked: new Graphics().rect(0, 0, 20, 20).fill(0x333333),
        checked: new Graphics().rect(0, 0, 20, 20).fill(0x3366ff),
        text: { fill: 0xffffff, fontSize: 16 },
    },
    text: 'Enable feature',
});

checkbox.onCheck.connect((checked) => {
    console.log('checkbox:', checked);
});

// Texture-based
const checkbox = new CheckBox({
    style: {
        unchecked: 'checkbox_off.png',
        checked: 'checkbox_on.png',
    },
    text: 'Accept terms',
    checked: true,
});

// Toggle programmatically
checkbox.checked = !checkbox.checked;

// Toggle without signal
checkbox.forceCheck(true);
```

### Label Behavior

- The text label is clickable — tapping it toggles the checkbox
- Label position is calculated from the unchecked view dimensions + `textOffset`
- Default horizontal gap: 10px from checkbox to label
- Label is vertically centered relative to the checkbox

## RadioGroup

Wrapper that makes `CheckBox` items behave as radio buttons (mutually exclusive selection).

### Constructor

```ts
const radioGroup = new RadioGroup(options?: RadioBoxOptions);
```

### Options (`RadioBoxOptions`)

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `items` | `CheckBox[]` | `[]` | Array of CheckBox instances |
| `type` | `ListType` | `'vertical'` | Layout: `'vertical'`, `'horizontal'`, `'bidirectional'` |
| `elementsMargin` | `number` | `0` | Margin between items |
| `selectedItem` | `number` | `0` | Initially selected item index |

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `selected` | `number` | Index of currently selected item |
| `value` | `string` | Text label of selected item |
| `items` | `CheckBox[]` | Array of CheckBox instances |
| `innerView` | `List` | Internal List layout container |

### Events (Signals)

| Signal | Parameters | Description |
|--------|-----------|-------------|
| `onChange` | `(selectedItemID: number, selectedVal: string)` | Fires when selection changes |

### Methods

| Method | Description |
|--------|-------------|
| `selectItem(id)` | Select item by index |
| `addItems(items)` | Add CheckBox instances |
| `removeItems(ids)` | Remove items by index array |

### Example

```ts
const radioGroup = new RadioGroup({
    items: [
        new CheckBox({
            style: {
                unchecked: new Graphics().circle(0, 0, 8).fill(0x333333),
                checked: new Graphics().circle(0, 0, 8).fill(0x3366ff),
            },
            text: 'Option A',
        }),
        new CheckBox({
            style: {
                unchecked: new Graphics().circle(0, 0, 8).fill(0x333333),
                checked: new Graphics().circle(0, 0, 8).fill(0x3366ff),
            },
            text: 'Option B',
        }),
        new CheckBox({
            style: {
                unchecked: new Graphics().circle(0, 0, 8).fill(0x333333),
                checked: new Graphics().circle(0, 0, 8).fill(0x3366ff),
            },
            text: 'Option C',
        }),
    ],
    type: 'vertical',
    elementsMargin: 10,
    selectedItem: 1,
});

radioGroup.onChange.connect((id, text) => {
    console.log('selected:', id, text);
});

// Change selection
radioGroup.selectItem(2);
console.log(radioGroup.selected); // 2
console.log(radioGroup.value);    // 'Option C'
```

### How It Works

- Each CheckBox's `onChange` signal is connected to `selectItem(id)`
- `selectItem()` calls `forceCheck()` on all items, setting only the selected one to `true`
- This prevents multiple checkboxes from being checked simultaneously
- The `onChange` signal on RadioGroup fires with the new selection index and text
