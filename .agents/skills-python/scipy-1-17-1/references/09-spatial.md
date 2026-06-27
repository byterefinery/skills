# scipy.spatial Reference

Spatial algorithms, distance metrics, geometry, and transforms.

## Table of Contents

- [Nearest-Neighbor Queries](#nearest-neighbor-queries)
- [Distance Metrics (scipy.spatial.distance)](#distance-metrics-sciypyspatialdistance)
- [Delaunay Triangulation](#delaunay-triangulation)
- [Convex Hulls](#convex-hulls)
- [Voronoi Diagrams](#voronoi-diagrams)
- [Halfspace Intersection](#halfspace-intersection)
- [Plotting Helpers](#plotting-helpers)
- [Spatial Transforms (scipy.spatial.transform)](#spatial-transforms-sciypyspatialtransform)

## Nearest-Neighbor Queries

### `KDTree(data, leafsize=10)`

k-d tree for efficient nearest-neighbor queries. Good for low-dimensional data (d ≤ 20).

```python
from scipy.spatial import KDTree
import numpy as np

points = np.random.rand(1000, 3)
tree = KDTree(points, leafsize=10)

# Query: find k nearest neighbors
distances, indices = tree.query(query_point, k=5)

# Query multiple points at once
distances, indices = tree.query(query_points, k=5)  # query_points: (M, d)

# Find all neighbors within radius r
indices = tree.query_ball_point(query_point, r=0.1)

# Find all pairs within distance r
pairs = tree.query_pairs(r=0.1)
```

### `cKDTree(data, leafsize=10)`

Cython-implemented k-d tree. Faster than `KDTree` but with slightly less flexible API. Same methods as `KDTree`.

### `Rectangle(vertices)`

Axis-aligned rectangle for spatial queries.

## Distance Metrics (scipy.spatial.distance)

### Pairwise distance computation

| Function | Description |
|---|---|
| `pdist(X, metric='euclidean')` | Pairwise distances between observations in X → condensed form |
| `cdist(XA, XB, metric='euclidean')` | Distances between two collections of observations |
| `squareform(y)` | Convert condensed ↔ redundant (square) distance matrix |
| `directed_hausdorff(u, v)` | Directed Hausdorff distance between arrays |

```python
from scipy.spatial.distance import pdist, squareform

X = np.random.rand(10, 3)
condensed = pdist(X, metric='euclidean')  # condensed form: n*(n-1)/2 values
square = squareform(condensed)             # full n×n matrix
```

### Distance predicates

| Function | Description |
|---|---|
| `is_valid_dm(dm)` | Check if valid distance matrix |
| `is_valid_y(y)` | Check if valid condensed distance matrix |
| `num_obs_dm(dm)` | Number of observations in distance matrix |
| `num_obs_y(y)` | Number of observations in condensed matrix |

### Numeric vector distances

| Metric | Function | Description |
|---|---|---|
| Euclidean | `euclidean(u, v)` | Standard L2 distance |
| Squared Euclidean | `sqeuclidean(u, v)` | Squared L2 (avoids sqrt) |
| Manhattan | `cityblock(u, v)` | L1 distance |
| Minkowski | `minkowski(u, v, p=2)` | Generalized Lp |
| Chebyshev | `chebyshev(u, v)` | L∞ distance |
| Cosine | `cosine(u, v)` | 1 - cosine similarity |
| Correlation | `correlation(u, v)` | 1 - Pearson correlation |
| Mahalanobis | `mahalanobis(u, v, VI=None)` | With optional inverse covariance |
| Bray-Curtis | `braycurtis(u, v)` | Ecological dissimilarity |
| Canberra | `canberra(u, v)` | Canberra distance |
| Jensen-Shannon | `jensenshannon(u, v)` | Symmetric KL divergence variant |
| Standardized Euclidean | `seuclidean(u, v, V=None)` | With optional variance vector |

### Boolean (set) distances

| Metric | Function | Description |
|---|---|---|
| Jaccard | `jaccard(u, v)` | Proportion of differing elements |
| Dice | `dice(u, v)` | Dice dissimilarity |
| Russell-Rao | `russellrao(u, v)` | Proportion where both are 0 |
| Sokal-Michener | `sokalmichener(u, v)` | (discordant) / (concordant + discordant) |
| Sokal-Sneath | `sokalsneath(u, v)` | 2×discordant / (concordant + 2×discordant) |
| Matching | `matching(u, v)` | Fraction of mismatched bits |
| Kulsinski | `kulsinski(u, v)` | Kulsinski dissimilarity |

### Information-theoretic distances

| Metric | Function | Description |
|---|---|---|
| KL divergence | `kl_divergence(u, v)` | Kullback-Leibler (asymmetric) |
| Hellinger | `hellinger(u, v)` | Hellinger distance between distributions |
| Wasserstein | `wasserstein_distance(u, v)` | 1-D Earth Mover's Distance |

### Statistic distances

| Function | Description |
|---|---|
| `energy_distance(u, v, ...)` | Energy distance between samples |
| `maha` | Alias for mahalanobis |

## Delaunay Triangulation

### `Delaunay(points, qhull_options=None)`

Compute Delaunay triangulation of points in any dimension.

```python
from scipy.spatial import Delaunay
import numpy as np

points = np.random.rand(20, 2)
tri = Delaunay(points)

# tri.simplices — array of simplex indices
# tri.vertices — same as simplices
# tri.find_point(x) — find simplex containing point x
# tri.coplanar(x, extra_radius=0) — find coplanar points
in_simplex = tri.find_simplex(query_points)  # simplex index for each query point
```

### Finding if points are inside the convex hull

```python
# Points with in_simplex >= 0 are inside the triangulation
inside = tri.find_simplex(query_points) >= 0
```

## Convex Hulls

### `ConvexHull(points, qhull_options=None)`

Compute the convex hull of a set of points.

```python
from scipy.spatial import ConvexHull

points = np.random.rand(20, 3)
hull = ConvexHull(points)

print(hull.volume)       # volume of the hull
print(hull.area)         # surface area
print(hull.simplices)    # indices of points forming each facet
print(hull.vertices)     # indices of points on the hull
```

## Voronoi Diagrams

### `Voronoi(points, qhull_options=None)`

Compute the Voronoi diagram from input points.

```python
from scipy.spatial import Voronoi

points = np.random.rand(20, 2)
vor = Voronoi(points)

# vor.regions — list of vertex indices for each region (-1 = infinite)
# vor.ridge_vertices — vertex pairs for each ridge
# vor.ridge_points — input point pairs for each ridge
# vor.vertices — coordinates of Voronoi vertices
```

### `SphericalVoronoi(points, radius=1.0, center=[0, 0, 0])`

Voronoi diagram on the surface of a sphere.

## Halfspace Intersection

### `HalfspaceIntersection(halfspaces, constraint_halfspace)`

Compute the intersection of input halfspaces.

```python
from scipy.spatial import HalfspaceIntersection

# halfspaces: (N, d+1) array where each row defines a hyperplane
# constraint_halfspace: a bounding box (d+1 values)
intersection = HalfspaceIntersection(halfspaces, constraint_halfspace)
print(intersection.intersecting_points)  # vertices of the intersection
```

## Plotting Helpers

| Function | Description |
|---|---|
| `delaunay_plot_2d(tri, show_points=True, show_vertices=True)` | Plot 2-D Delaunay triangulation |
| `convex_hull_plot_2d(hull, show_indices=False)` | Plot 2-D convex hull |
| `voronoi_plot_2d(vor, show_points=True, show_vertices=True)` | Plot 2-D Voronoi diagram |

```python
from scipy.spatial import Delaunay, delaunay_plot_2d
import matplotlib.pyplot as plt

tri = Delaunay(points)
delaunay_plot_2d(tri)
plt.show()
```

## Spatial Transforms (scipy.spatial.transform)

### Rotations in 3D

#### `Rotation`

Represents 3D rotations. Can be constructed from multiple representations.

```python
from scipy.spatial.transform import Rotation as R
import numpy as np

# From Euler angles (default: 'xyz' extrinsic)
r = R.from_euler('xyz', [90, 45, 0], degrees=True)

# From quaternion (x, y, z, w)
r = R.from_quat([0, 0, 0, 1])

# From rotation matrix (3×3)
r = R.from_matrix([[0, -1, 0], [1, 0, 0], [0, 0, 1]])

# From axis-angle
r = R.from_rotvec([0, 0, np.pi/2])  # 90° around z-axis

# Apply rotation to vectors
vectors = np.array([[1, 0, 0], [0, 1, 0]])
rotated = r.apply(vectors)

# Convert between representations
print(r.as_matrix())     # 3×3 rotation matrix
print(r.as_euler('xyz')) # Euler angles
print(r.as_quat())       # Quaternion (x, y, z, w)
print(r.as_rotvec())     # Rotation vector (axis × angle)
```

#### `RigidTransform`

Combination of rotation and translation.

```python
from scipy.spatial.transform import RigidTransform

# From rotation + translation
rot = R.from_euler('z', 90, degrees=True)
transform = RigidTransform(rotation=rot, translation=[1, 2, 3])

# Apply to points
points = np.array([[0, 0, 0], [1, 0, 0]])
transformed = transform(points)
```

#### `Slerp`

Spherical linear interpolation between rotations.

```python
from scipy.spatial.transform import Rotation as R, Slerp

# Define keyframe rotations at times t
key_rots = R.from_euler('xyz', [[0, 0, 0], [90, 0, 0], [90, 90, 0]], degrees=True)
times = [0, 0.5, 1.0]

slerp = Slerp(times, key_rots)
interpolated = slerp([0.25, 0.75])  # rotations at intermediate times
```

#### `RotationSpline`

Spline interpolation of rotation sequences (Akima spline on SO(3)).
