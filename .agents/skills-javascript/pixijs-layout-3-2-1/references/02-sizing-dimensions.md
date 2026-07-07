# Sizing and Dimensions

Size-related properties accept pixel numbers, percentage strings, `'auto'`, or `'intrinsic'`.

## Width and Height

Define the node's border box size.

```ts
container.layout = {
    width: 300,        // 300 pixels
    height: '50%',     // 50% of parent height
};
```

| Value         | Description                              |
|---------------|------------------------------------------|
| `number`      | Fixed size in pixels                     |
| `'50%'`       | Percentage of parent container           |
| `'auto'`      | Size based on content/children           |
| `'intrinsic'` | Size from PixiJS object bounds           |

## Intrinsic Sizing

Leaf nodes default to `width: 'intrinsic'`, `height: 'intrinsic'`. The layout system checks the PixiJS object's bounds (throttled) and uses those dimensions.

```ts
// These are equivalent for leaf nodes
sprite.layout = true;
sprite.layout = { width: 'intrinsic', height: 'intrinsic' };
```

**Performance note:** Intrinsic sizing triggers periodic bound checks. For many objects, use fixed sizes:

```ts
sprite.layout = {
    width: texture.width,
    height: texture.height,
};
```

## Min/Max Constraints

Strict boundaries that override flex calculations:

```ts
sprite.layout = {
    width: '100%',
    minWidth: 200,
    maxWidth: 500,
    minHeight: 50,
    maxHeight: 400,
};
```

Min/max constraints have **higher priority** than flex grow/shrink and intrinsic sizing.

## Aspect Ratio

Fixed ratio between width and height:

```ts
sprite.layout = {
    width: 200,
    aspectRatio: 16 / 9, // height derived from width
};

// Or derive width from height
sprite.layout = {
    height: 200,
    aspectRatio: 1.5,
};
```

- Has **higher priority** than flex grow/shrink
- Adjusts the cross-axis dimension to maintain the ratio
- Respects min/max constraints

## Default Sizing

| Node Type | Default Width | Default Height |
|-----------|---------------|----------------|
| Leaf (Sprite, Text, Graphics) | `'intrinsic'` | `'intrinsic'` |
| Container | `'auto'` | `'auto'` |
| Shared defaults | `flexShrink: 1`, `flexDirection: 'row'`, `flexWrap: 'nowrap'` |

Customize defaults globally:

```ts
import { Layout } from '@pixi/layout';

Layout.defaultStyle = {
    leaf: { width: 'intrinsic', height: 'intrinsic' },
    container: { width: 'auto', height: 'auto' },
    shared: {
        transformOrigin: '50%',
        objectPosition: 'center',
        flexShrink: 1,
        flexDirection: 'row',
        alignContent: 'stretch',
        flexWrap: 'nowrap',
        overflow: 'visible',
    },
};
```
