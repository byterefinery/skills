# Positioning

Positioning determines how a node is placed within its container.

## Position Types

| Value      | Description                                                                 |
|------------|-----------------------------------------------------------------------------|
| `relative` | Normal flex flow. Insets offset from computed position. (default)           |
| `absolute` | Removed from flex flow. Does not affect siblings. Positioned via insets.    |
| `static`   | Like `relative` but ignores all insets.                                     |

```ts
// Absolute positioning — removed from flex flow
sprite.layout = {
    position: 'absolute',
    left: 0,
    top: 0,
};

// Relative with offset
sprite.layout = {
    position: 'relative',
    left: 20,
    top: 10,
};
```

## Insets

| Property | Description                                           |
|----------|-------------------------------------------------------|
| `left`   | Distance from left edge                               |
| `top`    | Distance from top edge                                |
| `right`  | Distance from right edge                              |
| `bottom` | Distance from bottom edge                             |
| `start`  | Start edge (left in LTR, right in RTL)                |
| `end`    | End edge (right in LTR, left in RTL)                  |

Insets accept pixel numbers or percentage strings.

```ts
sprite.layout = {
    position: 'absolute',
    left: '10%',
    top: '10%',
    right: '10%',
    bottom: '10%',
};
```

## Shorthand Insets

| Property     | Description                      |
|--------------|----------------------------------|
| `inset`      | All four edges                   |
| `insetInline` | left and right (or start/end)   |
| `insetBlock`  | top and bottom                   |

## Opposing Insets

When both opposing insets are set (e.g., `left` and `right`):

- The **start inset has priority** (`left` over `right`, `top` over `bottom`) for positioning
- If the node has a **fixed width**, the opposing inset defines alignment relative to the container
- If width/height are flexible, layout may stretch or shrink the node

## Direction

| Value | Description |
|-------|-------------|
| `ltr` | Left to right (default) |
| `rtl` | Right to left |

Affects `start`/`end` inset mapping and `marginStart`/`marginEnd`, `paddingStart`/`paddingEnd`.

```ts
container.layout = { direction: 'rtl' };
```

## Display

| Value      | Description                                          |
|------------|------------------------------------------------------|
| `flex`     | Normal flex container (default)                      |
| `none`     | Hidden from layout and rendering                     |
| `contents` | Container not rendered; only children participate    |

```ts
// Hide from layout
container.layout = { display: 'none' };
```

## Margins

All margin properties accept pixel numbers, percentage strings, or `'auto'`.

| Property       | Description                          |
|----------------|--------------------------------------|
| `margin`       | All edges                            |
| `marginTop`    | Top margin                           |
| `marginBottom` | Bottom margin                        |
| `marginLeft`   | Left margin                          |
| `marginRight`  | Right margin                         |
| `marginStart`  | Start edge margin                    |
| `marginEnd`    | End edge margin                      |
| `marginInline` | Left and right margins               |
| `marginBlock`  | Top and bottom margins               |

Auto margins center the element:

```ts
child.layout = {
    marginLeft: 'auto',
    marginRight: 'auto',
};
```

## Padding

| Property         | Description                    |
|------------------|--------------------------------|
| `padding`        | All edges                      |
| `paddingTop`     | Top padding                    |
| `paddingBottom`  | Bottom padding                 |
| `paddingLeft`    | Left padding                   |
| `paddingRight`   | Right padding                  |
| `paddingStart`   | Start edge padding             |
| `paddingEnd`     | End edge padding               |
| `paddingInline`  | Left and right padding         |
| `paddingBlock`   | Top and bottom padding         |
