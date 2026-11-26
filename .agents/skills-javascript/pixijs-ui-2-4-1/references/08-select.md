# Select — Dropdown

A selection dropdown composed of a `FancyButton` (closed state) plus a `ScrollBox` of `FancyButton` items (open state). Tapping the button toggles the dropdown; tapping an item selects it and closes the dropdown.

## Options (`SelectOptions`)

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `closedBG` | view | — | **Required.** Background of the closed button |
| `openBG` | view | — | **Required.** Background of the open state (behind the item list) |
| `textStyle` | `PixiTextStyle` | — | Text style of button and items |
| `TextClass` | `Text \| BitmapText \| HTMLText` | `Text` | Text class for button and items |
| `selected` | `number` | `0` | Initially selected item id (its text shows on the button) |
| `selectedTextOffset` | `{ x?, y? }` | — | Offset of the button's selected-text label |
| `items` | `SelectItemsOptions` | — | **Required.** Item list config (see below) |
| `visibleItems` | `number` | `5` | Number of item rows visible in the dropdown (height = item height × visibleItems) |
| `scrollBox` | `ScrollBoxOptions & { offset?: {x, y} }` | — | ScrollBox options, spread over the built-in defaults (`type: 'vertical'`, `elementsMargin: 0`, width = button width, height = button height × visibleItems, `radius: 0`, `padding: 0`). `scrollBox.offset` shifts the box below the button. |
| `scrollBoxOffset` / `scrollBoxWidth` / `scrollBoxHeight` / `scrollBoxRadius` | — | — | Present in the type but not applied by `init()` in 2.4.1 — use the `scrollBox` option instead |
| + `ContainerOptions` | | | Passed through to the container |

### `SelectItemsOptions`

| Option | Type | Description |
|--------|------|-------------|
| `items` | `string[]` | Item labels |
| `backgroundColor` | `FillStyleInputs` | Item background |
| `hoverColor` | `FillStyleInputs` | Item hover background (falls back to `backgroundColor`) |
| `width` | `number` | Item width |
| `height` | `number` | Item height |
| `textStyle` | `PixiTextStyle` | Item text style |
| `TextClass` | text class | Item text class |
| `radius` | `number` | Item corner radius |

## API

| Member | Type / Description |
|--------|---------------------|
| `onSelect` | `Signal<(value: number, text: string) => void>` — fires when an item is picked |
| `value` | `number` — selected id; **`-1` until an item is picked** |
| `open()` | Show the dropdown (hides the closed button) |
| `close()` | Hide the dropdown |
| `toggle()` | Toggle; also wired to the closed/open button presses |
| `addItems(items, selected?)` | (Re)build the dropdown from a `SelectItemsOptions` |
| `removeItem(itemID)` | Remove an item by id |
| `init(options)` | (Re)initialise with new options |

## Behaviour & Gotchas

- The closed state is a `FancyButton` whose text shows the selected item; the open state adds a transparent full-size `FancyButton` over the `openBG` (clicking it toggles closed) plus the `ScrollBox` positioned below the button.
- Each dropdown item is a real `FancyButton` with default/hover views built from `items` options (`Graphics.roundRect` fills).
- Dropdown height is derived: `openButton.height * (visibleItems ?? 5)` — not a separate explicit height unless you override via `scrollBox`.
- Methods throw `Select has not been initiated!` if called before the constructor ran `init` (i.e., only when constructed without options).
- Selecting an item updates both the closed and open button labels and emits `onSelect(id, text)`.

## Example

```ts
const select = new Select({
    closedBG: 'select_closed.png',
    openBG: 'select_open.png',
    textStyle: { fill: 0xffffff, fontSize: 20 },
    selected: 0,
    items: {
        items: ['Option A', 'Option B', 'Option C'],
        backgroundColor: 0x000000,
        hoverColor: 0x333333,
        width: 200,
        height: 50,
    },
    scrollBox: {
        width: 200,
        height: 350,
        radius: 30,
    },
});

select.onSelect.connect((id, text) => console.log('selected:', id, text));
select.open();
select.close();
select.toggle();
```
