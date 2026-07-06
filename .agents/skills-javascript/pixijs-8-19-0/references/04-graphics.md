# Graphics

## Graphics Class

Vector drawing with fluent API. Build shapes first, then apply fill/stroke.

### Creation

```ts
import { Graphics } from 'pixi.js';

// Default (creates own GraphicsContext)
const graphics = new Graphics();

// With options
const graphics = new Graphics({
    roundPixels: true,
    position: { x: 100, y: 100 },
});

// Shared context (multiple Graphics share same drawing)
const context = new GraphicsContext();
const graphics1 = new Graphics({ context });
const graphics2 = new Graphics({ context });
```

### Fluent Drawing API

```ts
// Build shape → fill/stroke
graphics
    .rect(0, 0, 100, 100)
    .fill({ color: 0xff0000, alpha: 0.8 })
    .stroke({ width: 2, color: 0xffffff });

// Multiple shapes
graphics
    .circle(50, 50, 30)
    .fill(0x00ff00)
    .stroke({ width: 1, color: 0x000000 });

graphics
    .rect(120, 0, 80, 100)
    .fill(0x0000ff);
```

### Shape Methods

| Method | Parameters | Description |
|---|---|---|
| `rect(x, y, w, h)` | Rectangle | Draw rectangle |
| `roundRect(x, y, w, h, radius)` | Rounded rect | Rounded rectangle |
| `chamferRect(x, y, w, h, radius)` | Chamfered rect | Cut corners |
| `filletRect(x, y, w, h, radius)` | Filleted rect | Rounded with tangent arcs |
| `circle(x, y, radius)` | Circle | Circle at center |
| `ellipse(x, y, w, h)` | Ellipse | Ellipse at center |
| `poly(points)` | Polygon | Custom polygon |
| `regularPoly(x, y, radius, sides)` | Regular polygon | Regular n-sided polygon |
| `roundPoly(x, y, radius, sides)` | Rounded polygon | Rounded n-sided polygon |
| `star(x, y, points, radius, innerRadius)` | Star | Star shape |

### Path Methods (for complex shapes)

```ts
// Freeform paths
graphics
    .moveTo(0, 0)
    .lineTo(100, 0)
    .lineTo(100, 100)
    .lineTo(0, 100)
    .closePath()
    .fill(0xff0000);

// Arcs
graphics
    .arc(50, 50, 40, 0, Math.PI)
    .closePath()
    .fill(0x00ff00);

// ArcTo
graphics
    .moveTo(0, 0)
    .arcTo(100, 0, 100, 100, 50)
    .stroke({ width: 2, color: 0xff0000 });

// Quadratic bezier
graphics
    .moveTo(0, 0)
    .quadraticCurveTo(50, 100, 100, 0)
    .stroke({ width: 2, color: 0x00ff00 });

// Cubic bezier
graphics
    .moveTo(0, 0)
    .bezierCurveTo(25, 0, 75, 100, 100, 100)
    .stroke({ width: 2, color: 0x0000ff });

// SVG path string
graphics.svgPath('M 0 0 L 100 0 L 100 100 L 0 100 Z');
```

### Fill Styles

```ts
// Color fill
graphics.rect(0, 0, 100, 100).fill(0xff0000);
graphics.rect(0, 0, 100, 100).fill('red');
graphics.rect(0, 0, 100, 100).fill('#ff0000');

// Fill with options
graphics.rect(0, 0, 100, 100).fill({
    color: 0xff0000,
    alpha: 0.5,
});

// Gradient fill
const gradient = new FillGradient({
    start: { x: 0, y: 0 },
    end: { x: 100, y: 100 },
    stops: [
        { color: 0xff0000, offset: 0 },
        { color: 0x0000ff, offset: 1 },
    ]
});
graphics.rect(0, 0, 100, 100).fill(gradient);

// Texture fill
graphics.rect(0, 0, 100, 100).fill({
    texture: patternTexture,
    alpha: 0.5,
});

// Pattern fill
const pattern = new FillPattern(texture);
graphics.rect(0, 0, 100, 100).fill(pattern);
```

### Stroke Styles

```ts
// Simple stroke
graphics.rect(0, 0, 100, 100).stroke({ color: 0xffffff, width: 2 });

// Full stroke options
graphics.rect(0, 0, 100, 100).stroke({
    width: 3,
    color: 0xffffff,
    alpha: 0.8,
    alignment: 0.5,       // 0 = inside, 0.5 = center, 1 = outside
    miterLimit: 10,
    cap: 'butt',          // 'butt', 'round', 'square'
    join: 'miter',        // 'miter', 'round', 'bevel'
    pixelLine: false,     // Pixel-perfect lines
});

// Texture stroke
graphics.rect(0, 0, 100, 100).stroke({
    texture: lineTexture,
    width: 10,
    color: 0xff0000,
});

// Gradient stroke
graphics.rect(0, 0, 100, 100).stroke(gradient);
```

### Cut (Holes)

```ts
// Create a shape with a hole
graphics
    .rect(0, 0, 100, 100)
    .fill(0x00ff00)
    .circle(50, 50, 20)
    .cut(); // Cut out the circle
```

### Clear and Reset

```ts
graphics.clear(); // Remove all drawing instructions
```

## GraphicsContext

Lightweight drawable context that can be shared between Graphics objects.

### Creation and Sharing

```ts
import { GraphicsContext } from 'pixi.js';

// Create context
const context = new GraphicsContext();

// Draw on context
context
    .rect(0, 0, 100, 100)
    .fill(0xff0000)
    .stroke({ width: 2, color: 0xffffff });

// Share between multiple Graphics
const g1 = new Graphics({ context });
const g2 = new Graphics({ context });
// Both show the same drawing!

// Modify context (affects all Graphics using it)
context.circle(50, 50, 20).fill(0x00ff00);
```

### Context Methods

```ts
// State management
context.save();
context.restore();

// Transform
context.transform(matrix);
context.translate(x, y);
context.scale(x, y);
context.rotate(angle);

// Batch mode
context.batchMode = 'auto';   // Automatic batching
context.batchMode = 'batch';  // Force batching
context.batchMode = 'no-batch'; // No batching

// Custom shader
context.customShader = shader;

// Clone
const clone = context.clone();

// Destroy
context.destroy();
```

### Default Styles

```ts
// Change defaults (affects all new contexts)
GraphicsContext.defaultFillStyle = {
    color: 0xffffff,
    alpha: 1,
    texture: Texture.WHITE,
    matrix: null,
    fill: null,
    textureSpace: 'local',
};

GraphicsContext.defaultStrokeStyle = {
    width: 1,
    color: 0xffffff,
    alpha: 1,
    alignment: 0.5,
    miterLimit: 10,
    cap: 'butt',
    join: 'miter',
    texture: Texture.WHITE,
    matrix: null,
    fill: null,
    textureSpace: 'local',
    pixelLine: false,
};
```

## SVG Import

Parse SVG strings into Graphics:

```ts
import { SVGParser } from 'pixi.js';

const svgString = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
    <rect x="10" y="10" width="80" height="80" fill="red" stroke="black" stroke-width="2"/>
</svg>`;

const graphicsData = await SVGParser.parseSVG(svgString);

// Use the parsed data
const graphics = new Graphics(graphicsData.context);
```

## GraphicsPath

Low-level path building (used internally by Graphics):

```ts
import { GraphicsPath } from 'pixi.js';

const path = new GraphicsPath();
path.moveTo(0, 0);
path.lineTo(100, 0);
path.lineTo(100, 100);
path.closePath();

// Use with context
context.rectPath(path).fill(0xff0000);
```

## Performance Tips

- **Use GraphicsContext sharing** — one context shared by many Graphics avoids redundant geometry builds
- **Set `batchMode: 'batch'`** for simple graphics that benefit from batching
- **Use `boundsArea`** on parent containers with many graphics to skip bounds calculation
- **Avoid complex paths** — simple shapes (rect, circle) are much faster than freeform paths
- **Reuse styles** — don't create new FillGradient/FillPattern objects every frame
- **Clear and redraw** instead of destroying/recreating Graphics objects
- **Use `roundPixels: true`** for crisp rendering of vector shapes
