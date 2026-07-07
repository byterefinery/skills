# Object Fit and Position

These properties control how leaf node content fits inside its layout box. They only apply to leaf nodes (`Sprite`, `Text`, `Graphics`, `ViewContainer`) or containers with `isLeaf: true`.

## Object Fit

Defines how content is resized to fit the layout box.

| Value        | Description                                                    |
|--------------|----------------------------------------------------------------|
| `fill`       | Stretch to fill exactly (may distort aspect ratio)             |
| `contain`    | Scale to fit entirely, maintaining aspect ratio                |
| `cover`      | Scale to cover entirely, maintaining aspect ratio (may clip)   |
| `none`       | No scaling; original size                                      |
| `scale-down` | Smaller of `none` or `contain`                                 |

```ts
sprite.layout = {
    width: 200,
    height: 200,
    objectFit: 'contain',
};
```

Default for `Text`: `'scale-down'`. Default for other leaf nodes: not set (uses `fill` in the compute logic).

## Object Position

Defines where content is anchored inside the layout box after scaling.

### Keywords

| Value          | Description                          |
|----------------|--------------------------------------|
| `center`       | Center (default)                     |
| `top`          | Top, centered horizontally           |
| `bottom`       | Bottom, centered horizontally        |
| `left`         | Left, centered vertically            |
| `right`        | Right, centered vertically           |
| `top left`     | Top-left corner                      |
| `top right`    | Top-right corner                     |
| `bottom left`  | Bottom-left corner                   |
| `bottom right` | Bottom-right corner                  |

### Edge Offset Syntax

Up to four parts with pixel or percentage offsets:

```ts
sprite.layout = {
    objectPosition: 'bottom 10px right 20px',
};
// Offset 10px up from bottom, 20px left from right
```

```ts
sprite.layout = {
    objectPosition: '50% 100%',
};
// 50% from left, 100% from top
```

## Transform Origin

Defines the pivot point for rotation and scaling, relative to the **layout box** (not the PixiJS element).

```ts
sprite.layout = {
    transformOrigin: 'center',   // default
};

// Corner pivots
sprite.layout = { transformOrigin: 'top left' };

// Edge offset
sprite.layout = { transformOrigin: 'top 0px left 50px' };

// Percentage
sprite.layout = { transformOrigin: '50%' };
```

Conceptually similar to CSS `transform-origin`. When using percentage values, behaves like `anchor`; when using pixel values, behaves like `pivot`.

## Is Leaf

Set `isLeaf: true` on a Container to make it behave like a leaf node:

```ts
const container = new Container();
container.layout = {
    isLeaf: true,
    objectFit: 'contain',
    objectPosition: 'center',
};
```

This ignores children for layout purposes and enables `objectFit`/`objectPosition`. If the container's bounds are negative, content is pushed to the origin (0,0) to stay within the layout box.

## Apply Size Directly

Set `applySizeDirectly: true` to set the PixiJS object's `width`/`height` directly instead of applying a scale offset:

```ts
sprite.layout = {
    applySizeDirectly: true,
};
```

This can be useful when the downstream code depends on the object's actual width/height properties.
