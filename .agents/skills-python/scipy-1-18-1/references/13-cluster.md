# scipy.cluster Reference (1.18.1)

Clustering algorithms: k-means (vector quantization) and hierarchical clustering.

## Table of Contents

- [K-Means / Vector Quantization (scipy.cluster.vq)](#k-means--vector-quantization-sciypyclustervq)
- [Hierarchical Clustering (scipy.cluster.hierarchy)](#hierarchical-clustering-sciypyclusterhierarchy)

## K-Means / Vector Quantization (scipy.cluster.vq)

| Function/Class | Description |
|---|---|
| `whiten(obs)` | Normalize observations so each feature has unit variance |
| `kmeans(obs, k_or_guess, iter=20, ...)` | Classic k-means → `(centroids, distortion)` |
| `kmeans2(obs, k_or_centroids, iter=10, minit='random', ...)` | K-means with multiple initialization methods |
| `vq(obs, code_book)` | Assign observations to a codebook → `(labels, distances)` |
| `ClusterError` | Error class |

```python
from scipy.cluster.vq import whiten, kmeans2, vq
import numpy as np

obs_whitened = whiten(observations)           # important for different-scale features
centroids = kmeans2(obs_whitened, 3, minit='++')   # k-means++ init
labels, distances = vq(obs_whitened, centroids)
```

**`kmeans2` initialization (`minit`):** `'random'`, `'++'`/`'plus'` (k-means++), `'points'` (user-provided points), or an array of existing centroids.

**1.18.0 note:** `scipy.cluster.vq.py_vq` is deprecated (it was unintentionally public).

## Hierarchical Clustering (scipy.cluster.hierarchy)

### `linkage(y, method='single', metric='euclidean', optimal_ordering=False)`

Compute hierarchical clustering. Input `y` is either an observation data matrix (distance computed internally) or a condensed distance matrix (from `scipy.spatial.distance.pdist`). Returns a linkage matrix `Z` of shape `(n-1, 4)`:
- `Z[i, 0]` and `Z[i, 1]` = cluster indices merged at step i+1
- `Z[i, 2]` = distance between merged clusters
- `Z[i, 3]` = number of original observations in the new cluster

**Linkage methods:** `'single'` (nearest), `'complete'` (farthest), `'average'` (UPGMA), `'centroid'` (UPGMC), `'median'` (WPGMC), `'ward'` (Ward's minimum variance — most common, compact clusters). The seven linkage methods are also available as functions (`single`, `complete`, `average`, `weighted`, `centroid`, `median`, `ward`).

**Distance metrics:** `'euclidean'`, `'cityblock'`, `'cosine'`, `'braycurtis'`, `'matching'`, `'chebyshev'`, `'canberra'`, `'correlation'`, `'hamming'`, `'jaccard'`, `'minkowski'`, `'seuclidean'`, `'yule'`, ... (see `scipy.spatial.distance` for the full metric list).

```python
from scipy.cluster.hierarchy import linkage, dendrogram
from scipy.spatial.distance import pdist

Z = linkage(data, method='ward')                 # from observations
Z = linkage(pdist(data, metric='euclidean'), method='average')  # from distances
```

### Tree statistics and validation

| Function | Description |
|---|---|
| `cophenet(Z, y=None)` | Cophenet distance matrix and correlation coefficient |
| `inconsistent(Z, r=None, depth=None)` | Inconsistency coefficient for each merge |
| `maxinconsts(Z, max_inconsistency, ...)` | Indices of inconsistent merges |
| `maxdists(Z)` / `maxRstat(Z)` | Max distance / R-statistic per cluster |
| `leaders(Z)` | Leaders of clusters |
| `to_tree(Z, rd=False)` | Convert linkage matrix to a `ClusterNode` tree |
| `cut_tree(Z, ...)` | Cut the tree at a given depth |
| `optimal_leaf_ordering(Z, ...)` | Optimal leaf ordering for the dendrogram |
| `leaves_list(Z)` | Leaves of the tree in order |
| `from_mlab_linkage(Z)` / `to_mlab_linkage(Z)` | MATLAB linkage-format conversion |
| `is_valid_linkage(Z, ...)` / `is_valid_imatrix(im, ...)` | Linkage / inconsistency-matrix validation |
| `is_isomorphic(Z1, Z2)` / `is_monotonic(Z, ...)` | Tree comparison / monotonicity check |
| `correspond(Z1, Z2)` | Correspondence between two trees |
| `num_obs_linkage(Z)` | Number of observations in the linkage |
| `set_link_color_palette(...)` / `ClusterWarning` | Dendrogram colors / warning |

### Cutting the dendrogram

### `fcluster(Z, t, criterion='inconsistent', depth=..., ...)`

Form flat clusters from a hierarchical clustering. `criterion`:
- `'inconsistency'` — threshold on the inconsistency coefficient (uses `depth`)
- `'distance'` / `'maxclust'` — max distance or max number of clusters

```python
from scipy.cluster.hierarchy import fcluster

labels = fcluster(Z, t=0.5, criterion='distance')   # cut by distance
labels = fcluster(Z, t=5, criterion='maxclust')     # exactly k clusters
```

### `fclusterdata(data, t, criterion='maxclust', ...)`

Convenience: linkage + fcluster in one step.

```python
labels = fclusterdata(data, t=5, criterion='maxclust', method='ward')
```

### Visualization

### `dendrogram(Z, p=0, truncate=None, labels=None, ...)`

Plot a dendrogram (returns a dict with `ivl`, `leaves`, `color_list`, ...).

```python
from scipy.cluster.hierarchy import dendrogram
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(10, 5))
dendrogram(Z, labels=['s1', 's2', ...], color_threshold=0.7, orientation='top')
plt.show()
```
