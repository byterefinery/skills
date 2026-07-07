# Select

Dropdown selection component composed of a `FancyButton` (closed state) and a `ScrollBox` of `FancyButton` items (open state).

## Constructor

```ts
const select = new Select(options?: SelectOptions);
```

## Options (`SelectOptions`)

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `closedBG` | `GetViewSettings` | required | Background when dropdown is closed |
| `openBG` | `GetViewSettings` | required | Background when dropdown is open |
| `textStyle` | `PixiTextStyle` | — | Text style for buttons |
| `TextClass` | `PixiTextClass` | `Text` | Text class for buttons |
| `selected` | `number` | `0` | Initially selected item index |
| `selectedTextOffset` | `{x?: number, y?: number}` | — | Text offset on the closed button |
| `items` | `SelectItemsOptions` | required | Dropdown item configuration |
| `scrollBox` | `ScrollBoxOptions & {offset?}` | — | ScrollBox configuration |
| `visibleItems` | `number` | `5` | Number of visible items in dropdown |

## SelectItemsOptions

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `items` | `string[]` | required | Array of label strings |
| `backgroundColor` | `FillStyleInputs` | required | Background color of each item |
| `hoverColor` | `FillStyleInputs` | — | Hover color (defaults to backgroundColor) |
| `width` | `number` | required | Width of each item button |
| `height` | `number` | required | Height of each item button |
| `textStyle` | `PixiTextStyle` | — | Text style for item labels |
| `TextClass` | `PixiTextClass` | `Text` | Text class for items |
| `radius` | `number` | — | Corner radius of item buttons |

## Properties

| Property | Type | Description |
|----------|------|-------------|
| `value` | `number` | Currently selected item index (-1 if none) |

## Events (Signals)

| Signal | Parameters | Description |
|--------|-----------|-------------|
| `onSelect` | `(value: number, text: string)` | Fires when an item is selected |

## Methods

| Method | Description |
|--------|-------------|
| `init(options)` | Re-initialize with new options |
| `addItems(items, selected?)` | Add dropdown items |
| `removeItem(itemID)` | Remove item by index |
| `open()` | Show dropdown |
| `close()` | Hide dropdown |
| `toggle()` | Toggle open/closed state |

## Example

```ts
const select = new Select({
    closedBG: new Graphics().roundRect(0, 0, 200, 40, 8).fill(0x222222),
    openBG: new Graphics().roundRect(0, 0, 200, 40, 8).fill(0x333333),
    textStyle: { fill: 0xffffff, fontSize: 16 },
    selected: 0,
    items: {
        items: ['Select...', 'Option A', 'Option B', 'Option C', 'Option D'],
        backgroundColor: 0x222222,
        hoverColor: 0x444444,
        width: 200,
        height: 40,
        textStyle: { fill: 0xffffff, fontSize: 14 },
        radius: 5,
    },
    scrollBox: {
        width: 200,
        height: 200,
        radius: 10,
        background: 0x111111,
    },
    visibleItems: 5,
});

select.onSelect.connect((id, text) => {
    console.log('selected:', id, text);
});

// Programmatic control
select.open();
select.close();
select.toggle();
```

## Internal Structure

```
Select (Container)
├─ openButton: FancyButton     — Visible when closed, shows selected item
├─ view: Container             — Visible when open
   ├─ openView: Container      — Background when open
   ├─ closeButton: FancyButton — Click to close, shows selected item
   └─ scrollBox: ScrollBox     — Scrollable list of item buttons
      └─ FancyButton[]         — One per item string
```

- Clicking `openButton` calls `toggle()` → shows dropdown
- Clicking `closeButton` calls `toggle()` → hides dropdown
- Clicking an item button → fires `onSelect`, updates both button texts, calls `close()`
