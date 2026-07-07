# Flexbox Styles

Flexbox controls how child elements are arranged inside a layout-enabled container. PixiJS Layout uses Yoga, which implements the CSS Flexbox specification.

## Flex Direction

`flexDirection` defines the **main axis** — the direction children are laid out. The cross axis is perpendicular (used for alignment and wrapping).

| Value            | Description                                       |
|------------------|---------------------------------------------------|
| `row`            | Horizontal, left to right (default)               |
| `row-reverse`    | Horizontal, right to left                         |
| `column`         | Vertical, top to bottom                           |
| `column-reverse` | Vertical, bottom to top                           |

```ts
container.layout = { flexDirection: 'column' };
```

## Flex Grow, Shrink, and Basis

Each child controls how it grows and shrinks relative to siblings.

| Property     | Description                                                      |
|--------------|------------------------------------------------------------------|
| `flexGrow`   | How much the item expands to fill remaining positive space       |
| `flexShrink` | How much the item shrinks when there is negative overflow        |
| `flexBasis`  | Starting size along the main axis before grow/shrink adjustments |

```ts
// child1 grows, child2 grows twice as much
child1.layout = { flexGrow: 1 };
child2.layout = { flexGrow: 2 };

// Don't shrink
child.layout = { flexShrink: 0 };

// Starting size
child.layout = { flexBasis: 100 }; // 100px
```

- `flexGrow` defaults to `0` (no growth)
- `flexShrink` defaults to `1` (can shrink)
- `flexBasis` defaults to `'auto'` (content or width/height)
- In `row` direction, flexBasis behaves like `width`; in `column`, like `height`

## Flex Wrapping

| Value          | Description                                      |
|----------------|--------------------------------------------------|
| `nowrap`       | Single line, items may shrink (default)          |
| `wrap`         | Multiple lines, top to bottom                    |
| `wrap-reverse` | Multiple lines, bottom to top                    |

```ts
container.layout = { flexWrap: 'wrap' };
```

With `row` direction: wrapped lines stack vertically. With `column` direction: wrapped lines stack horizontally.

## Gap

Spacing between adjacent children (not at start or end):

| Property     | Description                                        |
|--------------|----------------------------------------------------|
| `gap`        | Both row and column spacing                        |
| `rowGap`     | Vertical spacing between rows (when wrapping)      |
| `columnGap`  | Horizontal spacing between columns or items        |

```ts
container.layout = {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 20,
};

// Or individual axes
container.layout = { rowGap: 10, columnGap: 30 };
```

## Alignment

### Justify Content (main axis)

| Value           | Description                         |
|-----------------|-------------------------------------|
| `flex-start`    | Pack at start                       |
| `center`        | Center items                        |
| `flex-end`      | Pack at end                         |
| `space-between` | Even spacing, first/last at edges   |
| `space-around`  | Equal margins around items          |
| `space-evenly`  | Equal spacing everywhere            |

```ts
container.layout = { justifyContent: 'center' };
```

### Align Items (cross axis)

| Value        | Description                              |
|--------------|------------------------------------------|
| `flex-start` | Align to start of cross axis             |
| `center`     | Center along cross axis                  |
| `flex-end`   | Align to end of cross axis               |
| `stretch`    | Stretch to fill cross axis (default)     |
| `baseline`   | Align by baseline                        |

```ts
container.layout = { alignItems: 'center' };
```

### Align Self (per-child override)

Same values as `alignItems`, applied to individual children:

```ts
child.layout = { alignSelf: 'flex-end' };
```

### Align Content (multi-line spacing)

Controls how wrapped lines are spaced along the cross axis. Only applies when `flexWrap` is enabled.

| Value           | Description                              |
|-----------------|------------------------------------------|
| `flex-start`    | Pack lines at start                      |
| `center`        | Center lines                             |
| `flex-end`      | Pack lines at end                        |
| `space-between` | Even spacing between lines               |
| `space-around`  | Even spacing around lines                |
| `stretch`       | Stretch lines (default)                  |
| `space-evenly`  | Equal spacing everywhere                 |

```ts
container.layout = {
    flexWrap: 'wrap',
    alignContent: 'space-around',
};
```

## Box Sizing

| Value         | Description                                      |
|---------------|--------------------------------------------------|
| `content-box` | Width/height excludes padding and border         |
| `border-box`  | Width/height includes padding and border         |

```ts
container.layout = { boxSizing: 'border-box' };
```
