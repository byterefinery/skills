# Clustering Reference

## Centroid-Based

### `KMeans(*, n_clusters=8, init="k-means++", n_init="auto", max_iter=300)`
Partition data into k clusters by minimizing within-cluster variance.

| Parameter | Default | Notes |
|-----------|---------|-------|
| `n_clusters` | `8` | Number of clusters |
| `init` | `"k-means++"` | Smart initialization; `"random"` is faster but riskier |
| `n_init` | `"auto"` | Number of random restarts (default 10) |
| `max_iter` | `300` | Max iterations per restart |
| `algorithm` | `"lloyd"` | `"elkan"` is faster for low-dimensional data |

```python
from sklearn.cluster import KMeans
km = KMeans(n_clusters=5, random_state=42)
labels = km.fit_predict(X)
centers = km.cluster_centers_
inertia = km.inertia_  # Within-cluster sum of squares
```

**Choosing k:** Use elbow method (plot inertia vs k) or silhouette score.

### `MiniBatchKMeans(*, n_clusters=8, batch_size=1024)`
Faster variant of KMeans using mini-batches. Good for large datasets.

### `BisectingKMeans(*, n_clusters=3)`
Hierarchical KMeans — recursively splits clusters. More deterministic than standard KMeans.

**1.9:** Fixed bug with custom callable `init` when `n_clusters > 2`.

## Density-Based

### `DBSCAN(*, eps=0.5, min_samples=5)`
Clusters based on density reachability. Finds arbitrary-shaped clusters and noise points.

| Parameter | Default | Notes |
|-----------|---------|-------|
| `eps` | `0.5` | Maximum distance between samples in same neighborhood |
| `min_samples` | `5` | Minimum samples to form a dense region |

**Tip:** Scale features before DBSCAN. Use k-nearest neighbor distance plot to choose `eps`.

### `HDBSCAN(*, min_cluster_size=15, min_samples=None)`
Hierarchical DBSCAN — automatically selects `eps` and handles varying densities. More robust than DBSCAN.

### `OPTICS(*, xi=0.05, min_samples=5)`
Ordering Points to Identify the Clustering Structure. Handles varying densities without fixed `eps`.

## Hierarchical

### `AgglomerativeClustering(*, n_clusters=2, linkage="ward")`
Bottom-up hierarchical clustering.

| Parameter | Default | Notes |
|-----------|---------|-------|
| `n_clusters` | `2` | Number of clusters |
| `linkage` | `"ward"` | `"complete"`, `"average"` — ward minimizes variance |
| `metric` | `None` | With ward, use `"euclidean"` or `"l2"` |

**1.9:** Now accepts `metric="l2"` with `linkage="ward"` (equivalent to `"euclidean"`).

### `FeatureAgglomeration(*, n_clusters=2, linkage="ward")`
Hierarchical clustering used as a feature transformer — merges similar features.

```python
from sklearn.cluster import FeatureAgglomeration
fa = FeatureAgglomeration(n_clusters=10)
X_reduced = fa.fit_transform(X)  # Merges similar columns
```

## Other Methods

### `MeanShift(*, bandwidth=None)`
Automatic cluster detection without specifying k. Computationally expensive.

### `SpectralClustering(*, n_clusters=8, affinity="rbf")`
Uses eigenvectors of similarity matrix. Good for non-convex clusters.

### `AffinityPropagation(damping=0.5)`
Message-passing algorithm. Finds exemplars (representative samples).

### `Birch(n_clusters=3, threshold=0.5)`
Balanced Iterative Reducing and Clustering using Hierarchies. Efficient for large datasets.

### `SpectralBiclustering()` / `SpectralCoclustering()`
Simultaneously cluster rows and columns of a matrix.

## Anomaly Detection (unsupervised)

### `IsolationForest(*, n_estimators=100, contamination="auto")`
(`sklearn.ensemble`) Isolates anomalies by random splitting. Fast O(n log n).

| Parameter | Default | Notes |
|-----------|---------|-------|
| `n_estimators` | `100` | Number of isolation trees |
| `contamination` | `"auto"` | Expected fraction of outliers |

### `LocalOutlierFactor(*, n_neighbors=20, contamination="auto")`
(`sklearn.neighbors`) Detects local density deviations.

## Model Selection for Clustering

```python
from sklearn.metrics import silhouette_score, calinski_harabasz_score

# Internal validation metrics (no ground truth)
silhouette = silhouette_score(X, labels)
ch = calinski_harabasz_score(X, labels)

# With ground truth
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score
ari = adjusted_rand_score(true_labels, predicted_labels)
nmi = normalized_mutual_info_score(true_labels, predicted_labels)
```
