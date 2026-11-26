# Maths

## Matrix

2D transformation matrix.

```ts
import { Matrix } from 'pixi.js';

// Create
const matrix = new Matrix();

// Identity
const identity = Matrix.IDENTITY;

// Transform operations
matrix.translate(x, y);
matrix.scale(sx, sy);
matrix.rotate(angle); // Radians

// Skip rotation (faster for pure translation + scale)
matrix.skew(sx, sy); // Radians

// Set from components
matrix.set(a, b, c, d, tx, ty);

// Combine
matrix.append(otherMatrix);
matrix.prepend(otherMatrix);

// Invert
matrix.invert();

// Copy
matrix.copyFrom(source);

// Reset to identity
matrix.identity();

// Decompose
matrix.decompose(point); // Extract position

// Apply to point
const result = matrix.apply(inputPoint, outputPoint);

// Determinant
const det = matrix.determinant();

// Properties
matrix.a; // Scale X
matrix.b; // Skew Y
matrix.c; // Skew X
matrix.d; // Scale Y
matrix.tx; // Translate X
matrix.ty; // Translate Y
```

## Point

```ts
import { Point } from 'pixi.js';

// Create
const point = new Point(100, 200);

// Properties
point.x;
point.y;

// Methods
point.set(100, 200);
point.copyFrom(otherPoint);
point.clone();

// Distance
const dist = point.distance(otherPoint);
const distSq = point.distanceSquared(otherPoint);

// Angle
const angle = point.angle(otherPoint); // Radians

// Rotation
point.rotate(otherPoint, angle); // Rotate around another point

// Normalization
point.normalize(); // Unit vector

// Interpolation
point.lerp(otherPoint, alpha); // Linear interpolation

// Equals
point.equals(otherPoint);
```

### ObservablePoint

Point that triggers callbacks on change. Used internally by Container for position, scale, pivot, skew.

```ts
import { ObservablePoint } from 'pixi.js';

const point = new ObservablePoint(
    (point) => { /* callback on change */ },
    0, // initial x
    0  // initial y
);

point.set(100, 200); // Triggers callback
```

### PointData

Lightweight point interface (no methods, just x/y):

```ts
interface PointData {
    x: number;
    y: number;
}

// Any object with x/y works as PointData
const point = { x: 100, y: 200 };
container.position = point;
```

## Shapes

### Rectangle

```ts
import { Rectangle } from 'pixi.js';

// Create
const rect = new Rectangle(0, 0, 100, 100);

// Properties
rect.x; rect.y; rect.width; rect.height;

// Methods
rect.set(x, y, width, height);
rect.copyFrom(source);
rect.clone();

// Containment
rect.contains(x, y);
rect.containsRect(otherRect);

// Intersection
rect.intersection(otherRect, optionalTarget);
rect.intersects(otherRect);

// Padding
rect.pad(padding);
rect.enlarge(width, height);

// Center
rect.centerX;
rect.centerY;

// Conversion
rect.circle; // As Circle
```

### Circle

```ts
import { Circle } from 'pixi.js';

const circle = new Circle(50, 50, 30);

circle.x; circle.y; circle.radius;

circle.contains(x, y);
circle.intersects(rect);
circle.clone();
```

### Ellipse

```ts
import { Ellipse } from 'pixi.js';

const ellipse = new Ellipse(50, 50, 40, 20);

ellipse.x; ellipse.y; ellipse.width; ellipse.height;

ellipse.contains(x, y);
ellipse.clone();
```

### Polygon

```ts
import { Polygon } from 'pixi.js';

// From points
const polygon = new Polygon([
    { x: 0, y: 0 },
    { x: 100, y: 0 },
    { x: 100, y: 100 },
    { x: 0, y: 100 },
]);

// From array
const polygon = new Polygon([0, 0, 100, 0, 100, 100, 0, 100]);

polygon.contains(x, y);
polygon.clone();
polygon.close(); // Close the path
```

### RoundedRectangle

```ts
import { RoundedRectangle } from 'pixi.js';

const rect = new RoundedRectangle(0, 0, 100, 100, 10);

rect.contains(x, y);
```

### Triangle

```ts
import { Triangle } from 'pixi.js';

const triangle = new Triangle(0, 0, 100, 0, 50, 100);

triangle.contains(x, y);
```

## Color

```ts
import { Color } from 'pixi.js';

// Creation from various formats
const color = new Color('red');
const color = new Color(0xff0000);
const color = new Color('#ff0000');
const color = new Color('#f00');
const color = new Color('rgb(255, 0, 0)');
const color = new Color('rgba(255, 0, 0, 0.5)');
const color = new Color([1, 0, 0, 1]);
const color = new Color(new Uint8Array([255, 0, 0, 255]));
const color = new Color({ h: 0, s: 100, l: 50 }); // HSL
const color = new Color({ h: 0, s: 100, v: 100 }); // HSV

// Output
color.toArray();       // [1, 0, 0, 1]
color.toHex();         // '0xff0000'
color.toHexa();        // '0xff0000ff'
color.toHexString();   // '#ff0000'
color.toHexaString();  // '#ff0000ff'
color.toRgba();        // 'rgba(255, 0, 0, 1)'
color.toRgbaString();  // 'rgba(255, 0, 0, 1)'
color.toCssColor();    // 'rgb(255, 0, 0)'
color.toPremultipliedAlpha(); // Premultiplied alpha array

// Components
color.r; // 0-1
color.g;
color.b;
color.a;

// Manipulation
color.clone();
color.lerp(otherColor, alpha);
color.multiply(otherColor);

// Static
Color.shared_set(0xff0000); // Set shared color
Color.shared_copy;          // Get shared color copy
```

### ColorSource

Any valid color input:

```ts
type ColorSource =
    | string           // 'red', '#ff0000', 'rgb(255,0,0)', 'hsl(0,100%,50%)'
    | number           // 0xff0000
    | number[]         // [1, 0, 0, 1]
    | Float32Array     // Float32Array([1, 0, 0, 1])
    | Uint8Array       // Uint8Array([255, 0, 0, 255])
    | Uint8ClampedArray
    | HslColor         // { h, s, l }
    | HslaColor        // { h, s, l, a }
    | HsvColor         // { h, s, v }
    | HsvaColor        // { h, s, v, a }
    | RgbColor         // { r, g, b }
    | RgbaColor        // { r, g, b, a }
    | Color;
```

## Constants

```ts
import { DEG_TO_RAD, RAD_TO_DEG, PI, PI_2, TAU } from 'pixi.js';

DEG_TO_RAD; // Math.PI / 180
RAD_TO_DEG; // 180 / Math.PI
PI;         // Math.PI
PI_2;       // Math.PI / 2
TAU;        // Math.PI * 2
```

## Math Extras

Additional math utilities. Requires `import 'pixi.js/math-extras'`.

```ts
import 'pixi.js/math-extras';
```

### Enhanced Point Methods

| Method | Description |
|---|---|
| `add(other[, out])` | Adds another point |
| `subtract(other[, out])` | Subtracts another point |
| `multiply(other[, out])` | Component-wise multiplication |
| `multiplyScalar(scalar[, out])` | Multiply by scalar |
| `dot(other)` | Dot product |
| `cross(other)` | Scalar z-component of 3D cross product |
| `normalize([out])` | Returns unit-length vector |
| `magnitude()` | Euclidean length |
| `magnitudeSquared()` | Squared length (efficient for comparisons) |
| `project(onto[, out])` | Projects onto another vector |
| `reflect(normal[, out])` | Reflects across a normal |

### Enhanced Rectangle Methods

| Method | Description |
|---|---|
| `containsRect(other)` | Returns true if this rectangle contains the other |
| `equals(other)` | Checks if all properties are equal |
| `intersection(other[, out])` | Returns overlap rectangle |
| `union(other[, out])` | Returns rectangle encompassing both |

## Utility Functions

```ts
import { pointInTriangle } from 'pixi.js';

// Check if point is inside triangle
const inside = pointInTriangle(px, py, x1, y1, x2, y2, x3, y3);
```

## Size

```ts
import { Size } from 'pixi.js';

const size = new Size(800, 600);
size.width;
size.height;
size.set(800, 600);
size.copyFrom(otherSize);
size.clone();
```

## Performance Tips

- **Reuse Matrix/Point objects** — avoid allocation in render loop
- **Use `Matrix.IDENTITY`** instead of creating new identity matrices
- **Use `PointData`** (`{ x, y }`) instead of `Point` when possible — lighter weight
- **Cache computed values** — don't recalculate distances/angles every frame
- **Use `contains()`** on shapes for hit testing instead of manual math
- **Use `Color` class** for color manipulation — handles format conversion
