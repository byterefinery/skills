# Dimensionality Reduction Reference

## Linear Methods

### `PCA(n_components=None, *, svd_solver="auto", random_state=None)`
Principal Component Analysis — finds orthogonal directions of maximum variance.

| Parameter | Default | Notes |
|-----------|---------|-------|
| `n_components` | `None` | int, float (0-1 variance ratio), `"mle"`, `"all"` |
| `svd_solver` | `"auto"` | `"full"` (small data), `"randomized"` (large), `"arpack"` |
| `whiten` | `False` | Scale components to unit variance |

```python
from sklearn.decomposition import PCA
pca = PCA(n_components=0.95)  # Keep 95% of variance
X_pca = pca.fit_transform(X)
pca.explained_variance_ratio_  # Variance per component
pca.components_  # Principal axes
```

**Choosing components:** Plot cumulative explained variance. Use `n_components=0.95` for automatic selection.

### `IncrementalPCA(n_components=None, *, batch_size=None)`
PCA for large datasets that don't fit in memory. Processes data in batches via `partial_fit()`.

### `SparsePCA(n_components=None, alpha=1.0)`
PCA with sparsity constraint on components. Interpretable but slower.

### `MiniBatchSparsePCA(n_components=None, batch_size=256)`
Online variant of SparsePCA.

### `TruncatedSVD(n_components=None)`
SVD for sparse matrices (and dense). Equivalent to PCA without centering. Use for text data (TF-IDF).

```python
from sklearn.decomposition import TruncatedSVD
svd = TruncatedSVD(n_components=50)
X_reduced = svd.fit_transform(tfidf_matrix)
```

### `FactorAnalysis(n_components=None, *, rot=None)`
Probabilistic PCA variant — assumes latent factors with noise.

### `KernelPCA(n_components=None, kernel="rbf")`
Nonlinear PCA using kernel trick. No `inverse_transform()` unless using `"rbf"` kernel with approximation.

## Non-Negative Methods

### `NMF(n_components=None, init=None, solver="cd", random_state=None)`
Non-negative Matrix Factorization. Decomposes data into additive parts. Requires non-negative input.

| Parameter | Default | Notes |
|-----------|---------|-------|
| `solver` | `"cd"` | `"cd"` (coordinate descent), `"mu"` (multiplicative updates) |
| `init` | `None` | `"nndsvda"`, `"nndsvdar"`, `"random"`, `"nndsvd"` |

### `MiniBatchNMF(n_components=None, batch_size=256)`
Online NMF for large datasets.

## Independent Components

### `FastICA(n_components=None, algorithm="parallel", fun="logcosh")`
Independent Component Analysis — finds statistically independent components.

**1.9:** `algorithm='deflation'` with `fun='logcosh'` is now an order of magnitude faster.

## Topic Modeling

### `LatentDirichletAllocation(n_components=10, learning_method="batch")`
Probabilistic topic model for text documents.

```python
from sklearn.decomposition import LatentDirichletAllocation
lda = LatentDirichletAllocation(n_components=10, random_state=42)
doc_topics = lda.fit_transform(doc_term_matrix)
lda.components_  # Topic-word distributions
```

## Dictionary Learning

### `DictionaryLearning(n_components=10, alpha=1, max_iter=100)`
Learn a dictionary of atoms and encode data sparsely.

### `SparseCoder(dictionary, transform_algorithm="lasso_lars")`
Encode data using a pre-learned dictionary.

## Manifold Learning (Nonlinear Embedding)

### `TSNE(n_components=2, perplexity=30.0, learning_rate="auto")`
t-SNE — preserves local structure. Great for visualization (2D/3D).

| Parameter | Default | Notes |
|-----------|---------|-------|
| `perplexity` | `30.0` | Related to number of effective neighbors (5-50) |
| `learning_rate` | `"auto"` | Typically 200; `"auto"` = n_samples / 12 |
| `init` | `"random"` | `"pca"` often gives better results |
| `method` | `"barnes_hut"` | `"exact"` for small data, preserves global structure |

```python
from sklearn.manifold import TSNE
tsne = TSNE(n_components=2, random_state=42, init="pca")
X_2d = tsne.fit_transform(X)
```

**Note:** t-SNE is stochastic — different runs give different layouts. Use `random_state` for reproducibility.

### `LocallyLinearEmbedding(n_components=2, n_neighbors=5)`
LLE — preserves local neighborhood relationships.

### `Isomap(n_components=2, n_neighbors=5)`
Isometric feature mapping — geodesic distances on manifold.

### `MDS(n_components=2, metric=True, normalized_stress="auto")`
Multidimensional scaling — preserves pairwise distances.

### `ClassicalMDS()`
Classic MDS using eigendecomposition of centered dot products.

### `SpectralEmbedding(n_components=2, n_neighbors=5, affinity="nearest_neighbors")`
Laplacian eigenmaps — uses graph structure of nearest neighbors.

**1.9:** ARPACK eigensolver call improved for faster runtimes.

## Random Projection

### `RandomProjection(n_components=None, eps=0.1)`
Fast dimensionality reduction using random matrices (Johnson-Lindenstrauss lemma).

```python
from sklearn.random_projection import GaussianRandomProjection
proj = GaussianRandomProjection(n_components=50)
X_projected = proj.fit_transform(X)
```

## Method Selection Guide

| Goal | Method |
|------|--------|
| Variance preservation, linear | `PCA` |
| Sparse matrices (text) | `TruncatedSVD` |
| Non-negative data, parts-based | `NMF` |
| Signal separation | `FastICA` |
| Large data, out-of-core | `IncrementalPCA`, `MiniBatchSparsePCA` |
| 2D/3D visualization | `TSNE` (local), `UMAP` (external) |
| Global structure preservation | `MDS`, `Isomap` |
| Fast approximate reduction | `RandomProjection` |
| Topic modeling | `LatentDirichletAllocation` |
