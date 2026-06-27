# scipy.cluster Reference

Clustering algorithms: k-means (vector quantization) and hierarchical clustering.

## Table of Contents

- [K-Means / Vector Quantization (scipy.cluster.vq)](#k-means--vector-quantization-sciypyclustervq)
- [Hierarchical Clustering (scipy.cluster.hierarchy)](#hierarchical-clustering-sciypyclusterhierarchy)
  - [Linkage Methods](#linkage-methods)
  - [Tree Statistics](#tree-statistics)
  - [Cutting the Dendrogram](#cutting-the-dendrogram)
  - [Visualization](#visualization)

## K-Means / Vector Quantization (scipy.cluster.vq)

### Data preprocessing

| Function | Description |
|---|---|
| `whiten(obs)` | Normalize observations so each feature has unit variance |

```python
from scipy.cluster.vq import whiten

# Whiten data (important for k-means with different-scale features)
obs_whitened = whiten(observations)
```

### K-Means clustering

| Function | Description |
|---|---|
| `kmeans(obs, k_or_guess, iter=20, ...)` | Classic k-means → `(centroids, distortion)` |
| `kmeans2(obs, k_or_centroids, iter=10, ...)` | K-means with multiple initialization methods |

```python
from scipy.cluster.vq import kmeans, kmeans2, vq
import numpy as np

# Method 1: classic kmeans
centroids, distortion = kmeans(obs_whitened, 3)  # 3 clusters

# Method 2: kmeans2 with initialization options
centroids = kmeans2(obs_whitened, 3, minit='random')    # random init
centroids = kmeans2(obs_whitened, 3, minit='plus')      # k-means++ init
centroids = kmeans2(obs_whitened, 3, minit='points')    # specific points
centroids = kmeans2(obs_whitened, existing_centroids)   # use given centroids

# Assign observations to clusters
cluster_labels, distances = vq(obs_whitened, centroids)
```

**`kmeans2` initialization (`minit`):**
- `'random'` — random observation as initial centroid
- `'++'` / `'plus'` — k-means++ (better spread)
- `'points'` — user-provided points
- (array) — use given array as initial centroids

### Vector quantization

| Function | Description |
|---|---|
| `vq(obs, code_book)` | Assign observations to codebook → `(labels, distances)` |
| `whiten(obs)` | Normalize features to unit variance |

```python
from scipy.cluster.vq import vq

# Given a codebook (centroids), assign each observation
labels, distances = vq(observations, codebook)
# labels[i] = cluster index for observation i
# distances[i] = distance to assigned centroid
```

## Hierarchical Clustering (scipy.cluster.hierarchy)

### Linkage Methods

### `linkage(y, method='single', metric='euclidean', optimal_ordering=False)`

Compute hierarchical clustering. Returns a linkage matrix `Z` of shape `(n-1, 4)`.

**Input `y`:**
- Condensed distance matrix (from `scipy.spatial.distance.pdist`)
- Observation data matrix (distance computed internally)

**Linkage methods:**

| Method | Description |
|---|---|
| `'single'` | Minimum distance between clusters (nearest neighbor) |
| `'complete'` | Maximum distance between clusters (farthest neighbor) |
| `'average'` | UPGMA — average distance between all pairs |
| `'centroid'` | UPGMC — distance between cluster centroids |
| `'median'` | WPGMC — weighted centroid method |
| `'ward'` | Ward's minimum variance (most common, produces compact clusters) |

```python
from scipy.cluster.hierarchy import linkage, dendrogram
from scipy.spatial.distance import pdist
import numpy as np

# From observation data
Z = linkage(data, method='ward')

# From precomputed distances
distances = pdist(data, metric='euclidean')
Z = linkage(distances, method='average')

# Z is (n-1, 4) array:
# Z[i, 0] and Z[i, 1] = cluster indices merged at step i+1
# Z[i, 2] = distance between merged clusters
# Z[i, 3] = number of original observations in the new cluster
```

**Distance metrics:** `'euclidean'`, `'cityblock'`, `'cosine'`, `'braycurtis'`, `'matching'`, `'kulsinski'`, `'mahalanobis'`, `'chebyshev'`, `'canberra'`, `'correlation'`, `'hamming'`, `'jaccard'`, `'minkowski'`, `'seuclidean'`, `'yule'`.

### Tree Statistics

| Function | Description |
|---|---|
| `cophenet(Z, y=None)` | Cophenet distance matrix and correlation coefficient |
| `inconsistent(Z, r=None, depth=None)` | Inconsistency coefficient for each merge |
| `maxinconsistent(Z, max_inconsistency, ...)` | Indices of inconsistent merges |
| `is_leaf(i, Z)` | Check if index i is a leaf in the dendrogram |
| `to_tree(Z, rd=False)` | Convert linkage matrix to tree object |
| `to_column_vector(Z)` | Convert cluster labels to column vector |

```python
from scipy.cluster.hierarchy import cophenet, to_tree

# Cophenet correlation (how well the tree preserves distances)
coph_dist, coph_correlation = cophenet(Z, condensed_distances)
# coph_correlation close to 1.0 = good preservation

# Convert to tree object for traversal
tree = to_tree(Z)
```

### Cutting the Dendrogram

### `fcluster(Z, t, criterion='inconsistent', ...)`

Form flat clusters from hierarchical clustering.

**Criterion options:**

| Criterion | Description | Parameter `t` meaning |
|---|---|---|
| `'inconsistency'` | Inconsistency coefficient | Threshold on inconsistency value |
| `'distance'` / `'maxclust'` | Distance threshold / max clusters | Max distance or max number of clusters |
| `'monocrit'` | User-defined function | Passed to custom criterion function |

```python
from scipy.cluster.hierarchy import fcluster

# Cut by maximum distance
labels = fcluster(Z, t=0.5, criterion='distance')

# Cut to get exactly k clusters
labels = fcluster(Z, t=5, criterion='maxclust')

# Cut by inconsistency coefficient
labels = fcluster(Z, t=1.5, criterion='inconsistency', depth=2)
```

### `fclusterdata(data, t, criterion='maxclust', ...)`

Convenience: linkage + fcluster in one step.

```python
from scipy.cluster.hierarchy import fclusterdata

# Get 5 clusters directly from data
labels = fclusterdata(data, t=5, criterion='maxclust', method='ward')
```

### Visualization

### `dendrogram(Z, p=0, truncate=None, labels=None, ...)`

Plot a dendrogram. Returns a dictionary with plotting info.

```python
from scipy.cluster.hierarchy import dendrogram
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(10, 5))
result = dendrogram(
    Z,
    labels=['sample_1', 'sample_2', ...],
    color_threshold=0.7,       # clusters above this distance are colored
    link_color_func=lambda k: 'red' if k > threshold else 'black',
    orientation='top'           # 'top', 'right', 'left', 'bottom'
)

# result['ivl'] — labels at leaves
# result['leaves'] — leaf indices
# result['color_list'] — colors for each link

ax.axhline(y=threshold, color='r', linestyle='--')
plt.show()
```

### `plot_dendrogram(ax, Z, ...)`

Plot dendrogram on a given matplotlib axes.

### Other visualization helpers

| Function | Description |
|---|---|
| `schur(Z, ...)` | Schur decomposition of cluster data (for ordering) |
| `leaf_order(Z)` | Optimal leaf ordering for dendrogram |

### Distance matrix utilities

| Function | Description |
|---|---|
| `is_valid_y(y, throw=False, name='y')` | Check if valid condensed distance matrix |
| `is_valid_imatrix(im, ...)` | Check inconsistency matrix validity |
| `is_valid_linkage(Z, isra=False, name='Z')` | Check if valid linkage matrix |
| `is_monotonic(Z, name='Z')` | Check if linkage distances are monotonically increasing |
