# scipy.spatial Reference (1.18.1)

Spatial algorithms, distance metrics, geometry, and 3-D transforms.

## Table of Contents

- [Nearest-Neighbor Queries](#nearest-neighbor-queries)
- [Distance Metrics (scipy.spatial.distance)](#distance-metrics-sciypyspatialdistance)
- [Delaunay Triangulation](#delaunay-triangulation)
- [Convex Hulls](#convex-hulls)
- [Voronoi Diagrams](#voronoi-diagrams)
- [Halfspace Intersection](#halfspace-intersection)
- [Plotting Helpers](#plotting-helpers)
- [Other Functions](#other-functions)
- [Spatial Transforms (scipy.spatial.transform)](#spatial-transforms-sciypyspatialtransform)
- [Version Notes (1.18)](#version-notes-118)

## Nearest-Neighbor Queries

### `KDTree(data, leafsize=10)`

k-d tree for efficient nearest-neighbor queries. Thread-safe (no mutation interface after construction).

```python
from scipy.spatial import KDTree
import numpy as np

points = np.random.rand(1000, 3)
tree = KDTree(points, leafsize=10)

distances, indices = tree.query(query_points, k=5)   # k nearest neighbors
indices = tree.query_ball_point(query_point, r=0.1)  # all within radius r
pairs = tree.query_pairs(r=0.1)                      # all pairs within distance r
```

### `cKDTree(data, leafsize=10)`

Cython-implemented k-d tree — faster implementation with the same query API.

### `Rectangle(vertices)`

Axis-aligned bounding rectangle for spatial queries.

## Distance Metrics (scipy.spatial.distance)

### Pairwise distance computation

| Function | Description |
|---|---|
| `pdist(X, metric='euclidean')` | Pairwise distances between observations in X → condensed form |
| `cdist(XA, XB, metric='euclidean')` | Distances between two collections of observations |
| `squareform(y)` | Convert condensed ↔ redundant (square) distance matrix |
| `is_valid_dm(dm)` / `is_valid_y(y)` | Check distance-matrix validity |
| `num_obs_dm(dm)` / `num_obs_y(y)` | Number of observations in dm / condensed matrix |
| `directed_hausdorff(u, v, ...)` | Directed Hausdorff distance between arrays |

```python
from scipy.spatial.distance import pdist, squareform
import numpy as np

condensed = pdist(X, metric='euclidean')  # condensed: n*(n-1)/2 values
square = squareform(condensed)            # full n×n matrix
```

### Numeric vector distances (available `metric` names)

`euclidean`, `sqeuclidean`, `cityblock` (Manhattan), `minkowski` (with `p`), `chebyshev`, `cosine`, `correlation`, `mahalanobis` (with `VI`), `braycurtis`, `canberra`, `jensenshannon`, `seuclidean` (with `V`).

### Boolean (set) distances

`jaccard`, `dice`, `russellrao`, `sokalsneath`, `hamming`, `yule`.

## Delaunay Triangulation

### `Delaunay(points, qhull_options=None)`

Delaunay triangulation of points in any dimension.

```python
from scipy.spatial import Delaunay
import numpy as np

tri = Delaunay(points)
# tri.simplices — simplex index array
# tri.find_point(x) — simplex containing point x
# tri.find_simplex(query_points) — simplex index per query point (-1 = outside)
# tri.coplanar(x, extra_radius=0) — coplanar points
inside = tri.find_simplex(query_points) >= 0  # inside the triangulation
```

`Delaunay` also serves the role of the deprecated `tsearch` — use it directly.

## Convex Hulls

### `ConvexHull(points, qhull_options=None)`

```python
from scipy.spatial import ConvexHull
hull = ConvexHull(points)
print(hull.volume, hull.area)     # volume / surface area
print(hull.simplices)             # facet simplices
print(hull.vertices)              # indices of hull points
```

## Voronoi Diagrams

### `Voronoi(points, qhull_options=None)`

```python
from scipy.spatial import Voronoi
vor = Voronoi(points)
# vor.regions — vertex-index lists per region (-1 = unbounded)
# vor.ridge_vertices — vertex pairs per ridge
# vor.ridge_points — input point pairs per ridge
# vor.vertices — Voronoi vertex coordinates
```

### `SphericalVoronoi(points, radius=1.0, center=[0, 0, 0])`

Voronoi diagram on the surface of a sphere.

## Halfspace Intersection

### `HalfspaceIntersection(halfspaces, constraint_halfspace)`

Intersection of input halfspaces; `halfspaces` is `(N, d+1)` and `constraint_halfspace` bounds the search. `.intersecting_points` holds the resulting vertices.

## Plotting Helpers

| Function | Description |
|---|---|
| `delaunay_plot_2d(tri, ...)` | Plot a 2-D Delaunay triangulation |
| `convex_hull_plot_2d(hull, ...)` | Plot a 2-D convex hull |
| `voronoi_plot_2d(vor, ...)` | Plot a 2-D Voronoi diagram |

## Other Functions

| Function | Description |
|---|---|
| `procrustes(A, B, scaling=True)` | Orthogonal Procrustes analysis |
| `geometric_slerp(a, b, t)` | Spherical linear interpolation of unit vectors |
| `QhullError` | Error from Qhull |

## Spatial Transforms (scipy.spatial.transform)

### `Rotation`

Represents 3-D rotations. Construct from any representation and convert between them.

```python
from scipy.spatial.transform import Rotation as R
import numpy as np

r = R.from_euler('xyz', [90, 45, 0], degrees=True)   # Euler angles
r = R.from_quat([0, 0, 0, 1])                        # quaternion (x, y, z, w)
r = R.from_matrix([[0, -1, 0], [1, 0, 0], [0, 0, 1]])
r = R.from_rotvec([0, 0, np.pi/2])                   # axis-angle vector

rotated = r.apply(vectors)                            # apply to vectors
r.as_matrix(); r.as_euler('xyz'); r.as_quat(); r.as_rotvec()
```

### `RigidTransform`

Rotation + translation combined; call with points to transform them.

### `Slerp`

Spherical linear interpolation between keyframe rotations.

```python
from scipy.spatial.transform import Rotation as R, Slerp

key_rots = R.from_euler('xyz', [[0, 0, 0], [90, 0, 0], [90, 90, 0]], degrees=True)
slerp = Slerp([0, 0.5, 1.0], key_rots)
interpolated = slerp([0.25, 0.75])
```

### `RotationSpline`

Spline interpolation of rotation sequences.

## Version Notes (1.18)

**Deprecated in 1.18.0** (use the alternatives):
- `scipy.spatial.tsearch` — duplicates functionality in the `Delaunay` class proper
- `scipy.spatial.minkowski_distance` / `minkowski_distance_p` — superseded by other functions
- `scipy.spatial.distance_matrix` — superseded by other functions
