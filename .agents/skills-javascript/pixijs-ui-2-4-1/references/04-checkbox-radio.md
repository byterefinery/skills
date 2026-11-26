# CheckBox / RadioGroup

## CheckBox

Two-state toggle built on `Switcher` with an optional text label.

### Options (`CheckBoxOptions`)

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `style` | `CheckBoxStyle` | — | **Required.** Views for both states (see below) |
| `text` | `string` | `''` | Label text (rendered right of the box) |
| `TextClass` | `Text \| BitmapText \| HTMLText` | `Text` | Class used to render the label |
| `checked` | `boolean` | `false` | Initial state |
| + `ContainerOptions` | | | Passed through to the container |

```ts
type CheckBoxStyle = {
    checked: GetViewSettings;    // view shown when checked
    unchecked: GetViewSettings;  // view shown when unchecked
    text?: PixiTextStyle;        // label style
    textOffset?: { x?: number; y?: number }; // label position offset
};
```

### Signals

| Signal | Parameters | Description |
|--------|-----------|-------------|
| `onCheck` | `(checked: boolean)` | Emitted whenever the checked state changes |
| `onChange` | `(state: boolean)` | Inherited from `Switcher`; `CheckBox` mirrors it into `onCheck` |

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `checked` | `boolean` | Checked state (setter switches without force) |
| `text` | `string \| ''` | Label text (setting `''` removes the label) |
| `style` | `CheckBoxStyle` | Style settings (rebuilds both views, preserves checked state) |
| `labelText` | `PixiText \| undefined` | The label text instance |

### Methods

| Method | Description |
|--------|-------------|
| `forceCheck(checked: boolean)` | Set state **without** emitting `onCheck` |

### Label behaviour

- The label is placed to the right of the unchecked view (10px gap) and vertically centrelined, with `style.textOffset` applied.
- **The label itself is clickable** — tapping it toggles the checkbox.
- The whole component gets a `pointer` cursor.

### Example

```ts
const checkbox = new CheckBox({
    style: {
        unchecked: 'switch_off.png',
        checked: 'switch_on.png',
        text: { fill: 0xffffff, fontSize: 16 },
    },
    text: 'Enable feature',
    checked: false,
});

checkbox.onCheck.connect((checked) => console.log(checked));
checkbox.checked = true;
checkbox.forceCheck(false); // no signal
```

## RadioGroup

Wrapper that makes an array of `CheckBox` instances behave as radio buttons — only one can be selected at a time. Items are laid out with an internal `List`.

### Options (`RadioBoxOptions`)

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `items` | `CheckBox[]` | `[]` | Checkbox instances to manage |
| `type` | `ListType` | `'vertical'` | Layout: `vertical` \| `horizontal` \| `bidirectional` |
| `elementsMargin` | `number` | `0` | Margin between items |
| `selectedItem` | `number` | `0` | Initially selected item id |
| + `ContainerOptions` | | | Passed through to the container |

### Signals

| Signal | Parameters | Description |
|--------|-----------|-------------|
| `onChange` | `(selectedItemID: number, selectedVal: string)` | Emitted when a different item is selected |

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `items` | `CheckBox[]` | Managed checkboxes (protected; use methods) |
| `innerView` | `List \| undefined` | The internal List holding the checkboxes |
| `selected` | `number` | Id of the selected item |
| `value` | `string` | Label text of the selected item |

### Methods

| Method | Description |
|--------|-------------|
| `addItems(items: CheckBox[])` | Append checkboxes to the group (wires their `onChange`) |
| `removeItems(ids: number[])` | Remove items by id array (descending order internally) |
| `selectItem(id: number)` | Select by id; forces all items via `forceCheck` and emits `onChange` only when the selection changed |
| `init(options)` | Re-initialise (detaches previous item subscriptions first) |

### Example

```ts
const radioGroup = new RadioGroup({
    items: [
        new CheckBox({ style: { unchecked: 'off.png', checked: 'on.png' }, text: 'A' }),
        new CheckBox({ style: { unchecked: 'off.png', checked: 'on.png' }, text: 'B' }),
        new CheckBox({ style: { unchecked: 'off.png', checked: 'on.png' }, text: 'C' }),
    ],
    type: 'vertical',
    elementsMargin: 10,
    selectedItem: 0,
});

radioGroup.onChange.connect((id, text) => console.log('selected:', id, text));
radioGroup.selectItem(2);
```
