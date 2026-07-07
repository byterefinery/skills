# List

Auto-arranging layout container that positions children based on their sizes and layout type.

## Constructor

```ts
const list = new List<C extends ContainerChild = ContainerChild>(options?: { type?: ListType } & ListOptions<C>);
```

## Options (`ListOptions`)

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `type` | `ListType` | `'bidirectional'` | `'vertical'`, `'horizontal'`, `'bidirectional'` |
| `elementsMargin` | `number` | `0` | Margin between elements |
| `padding` | `number` | `0` | Padding (all sides) |
| `vertPadding` | `number` | `0` | Vertical padding |
| `horPadding` | `number` | `0` | Horizontal padding |
| `topPadding` | `number` | `0` | Top padding |
| `bottomPadding` | `number` | `0` | Bottom padding |
| `leftPadding` | `number` | `0` | Left padding |
| `rightPadding` | `number` | `0` | Right padding |
| `maxWidth` | `number` | `0` | Max width for bidirectional wrapping |
| `maxHeight` | `number` | `0` | Max height (reserved) |
| `children` | `C[]` | — | Initial children |
| `items` | `C[]` | — | Alias for children |

## Properties

| Property | Type | Description |
|----------|------|-------------|
| `type` | `ListType` | Current layout type |
| `elementsMargin` | `number` | Current margin between elements |
| `padding` | `number` | Current uniform padding |
| `vertPadding` | `number` | Current vertical padding |
| `horPadding` | `number` | Current horizontal padding |
| `topPadding` | `number` | Current top padding |
| `bottomPadding` | `number` | Current bottom padding |
| `leftPadding` | `number` | Current left padding |
| `rightPadding` | `number` | Current right padding |
| `maxWidth` | `number` | Current max width for wrapping |
| `children` | `C[]` | Child containers |

## Methods

| Method | Description |
|--------|-------------|
| `init(options)` | Initialize/reinitialize with options |
| `arrangeChildren()` | Manually recalculate positions |
| `removeItem(itemID)` | Remove child by index (does not destroy) |

## Layout Types

### Vertical

Items stack top to bottom. All items get full available width.

```
┌─────────────┐
│  Item 0     │  ← y = topPadding
│  Item 1     │  ← y = topPadding + h0 + margin
│  Item 2     │
└─────────────┘
```

### Horizontal

Items flow left to right. All items get full available height.

```
┌──────────────────────────┐
│ Item 0 │ Item 1 │ Item 2 │
└──────────────────────────┘
```

### Bidirectional (default)

Items flow left to right, wrapping to new line when exceeding `maxWidth`. Similar to CSS `inline-block`.

```
┌──────────────────────────────┐
│ Item 0 │ Item 1 │ Item 2    │
│ Item 3 │ Item 4 │           │
└──────────────────────────────┘
```

When `maxWidth` is 0 (default), parent width is used.

## Example

```ts
// Vertical list
const list = new List({
    type: 'vertical',
    elementsMargin: 10,
    padding: 10,
});

for (let i = 0; i < 5; i++) {
    const item = new Graphics()
        .roundRect(0, 0, 200, 50, 5)
        .fill(0x333333);
    list.addChild(item);
    // arrangeChildren() called automatically
}

// Horizontal list
const hList = new List({
    type: 'horizontal',
    elementsMargin: 5,
    leftPadding: 10,
    rightPadding: 10,
});

// Bidirectional grid
const grid = new List({
    type: 'bidirectional',
    elementsMargin: 8,
    padding: 10,
    maxWidth: 400,
});
```

## Auto-Arrange

`arrangeChildren()` is called automatically on:
- `childAdded` event
- `added` event (when list is added to a parent)
- Setting any layout property (`type`, `elementsMargin`, padding setters, `maxWidth`)

Call manually only after bulk operations:

```ts
// Bulk add without intermediate arrangements
list.removeChildren();
items.forEach(item => list.addChild(item));
list.arrangeChildren(); // Single layout pass
```

## Padding Hierarchy

Setters override related values:

- `padding` → sets `vertPadding`, `horPadding`, and all individual paddings
- `vertPadding` → sets `topPadding`, `bottomPadding`
- `horPadding` → sets `leftPadding`, `rightPadding`
- Individual setters (`topPadding`, etc.) only affect that side

Getters resolve from most specific to least:

- `topPadding` → falls back to `vertPadding` → falls back to `padding` → 0
