# Geometry Reference

## Points

```python
from sympy import Point, Point2D, Point3D, symbols

# 2D points
p1 = Point(1, 2)
p2 = Point2D(3, 4)
p3 = Point(0, 0)

# 3D points
p4 = Point3D(1, 2, 3)
p5 = Point(1, 2, 3)   # auto-detects dimension

# Symbolic points
x, y = symbols('x y')
ps = Point(x, y)

# Operations
p1.distance(p2)         # Euclidean distance
p1.midpoint(p2)         # midpoint
p1.reflect(Point(0, 0)) # reflection through point
```

## Lines, Rays, Segments

```python
from sympy import Line, Ray, Segment, Point

# Line through two points
line = Line(Point(0, 0), Point(1, 1))
line.equation()          # -x + y = 0
line.slope               # 1

# Ray (starts at p1, goes through p2)
ray = Ray(Point(0, 0), Point(1, 0))

# Segment
seg = Segment(Point(0, 0), Point(3, 4))
seg.length               # 5

# Parallel/perpendicular
line.parallel(Line(Point(0, 1), Point(1, 2)))   # True
line.perpendicular(Line(Point(0, 1), Point(-1, 0)))  # True

# Projection of point onto line
line.projection(Point(2, 0))
```

## Circles and Ellipses

```python
from sympy import Circle, Ellipse, Point, pi

# Circle from center and radius
c = Circle(Point(0, 0), 5)
c.radius                 # 5
c.center                 # Point2D(0, 0)
c.area                   # 25*pi
c.circumference          # 10*pi

# Circle from three points
c3 = Circle(Point(0, 0), Point(2, 0), Point(1, 1))

# Ellipse
e = Ellipse(Point(0, 0), 3, 2)   # center, rx, ry
e.area                          # 6*pi
```

## Polygons

```python
from sympy import Polygon, RegularPolygon, Triangle, Point

# General polygon
poly = Polygon(Point(0, 0), Point(4, 0), Point(4, 3), Point(0, 3))
poly.area                    # 12
poly.perimeter               # 14
poly.centroid                # Point2D(2, 3/2)

# Regular polygon
reg = RegularPolygon(Point(0, 0), 5, 6)   # center, radius, n sides
reg.area

# Triangle
tri = Triangle(Point(0, 0), Point(4, 0), Point(2, 3))
tri.area
tri.is_right                 # check if right triangle
tri.is_isosceles
```

## Planes (3D)

```python
from sympy import Plane, Point3D

# From point and normal vector
plane = Plane(Point3D(0, 0, 0), (1, 1, 1))
plane.equation()

# From three points
plane2 = Plane(Point3D(1, 0, 0), Point3D(0, 1, 0), Point3D(0, 0, 1))
```

## Intersections and Relations

```python
from sympy import Line, Circle, Point, intersection

# Line-circle intersection
line = Line(Point(-5, 0), Point(5, 0))
circle = Circle(Point(0, 0), 3)
intersection(line, circle)   # [Point2D(-3, 0), Point2D(3, 0)]

# Line-line intersection
l1 = Line(Point(0, 0), Point(1, 1))
l2 = Line(Point(0, 1), Point(1, 0))
l1.intersection(l2)          # [Point2D(1/2, 1/2)]

# Distance between objects
line.distance(Point(1, 2))
circle.distance(Point(10, 10))

# Closest/farthest points
from sympy import closest_points, farthest_points
closest_points(poly1, poly2)
```

## Convex Hull and Centroid

```python
from sympy import convex_hull, centroid, Point

points = [Point(0, 0), Point(1, 0), Point(1, 1), Point(0, 1), Point(0.5, 0.5)]
convex_hull(points)          # Polygon of outer points

# Centroid of polygon
poly = Polygon(Point(0, 0), Point(4, 0), Point(2, 3))
centroid(poly)
```

## Parabolas and Curves

```python
from sympy import Parabola, Curve, symbols
t = symbols('t')

# Parabola from focus and directrix
p = Parabola(Point(0, 1), Line(Point(-1, -1), Point(1, -1)))
p.focus
p.vertex
p.directrix

# Parametric curve
curve = Curve((t, t**2), (t, 0, 1))
```

## Similarity Checks

```python
from sympy import are_similar, Triangle, Point

t1 = Triangle(Point(0, 0), Point(3, 0), Point(0, 4))
t2 = Triangle(Point(0, 0), Point(6, 0), Point(0, 8))
are_similar(t1, t2)          # True
```

## Gotchas

- **`Point()` auto-detects dimension** — `Point(1, 2)` is 2D, `Point(1, 2, 3)` is 3D. Mixing dimensions in operations raises errors.
- **`Line()` through two identical points fails** — ensure distinct points or use point + slope.
- **Intersection returns a list** — may be empty (no intersection), single element (tangent), or multiple points.
- **`Circle()` from three collinear points fails** — the points must not be collinear.
- **Geometry objects are immutable** — `.translate()`, `.rotate()` return new objects.
- **Symbolic geometry can be slow** — intersection and distance with symbolic coordinates may produce complex expressions.
