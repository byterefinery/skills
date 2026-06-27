# Data I/O Reference

## Built-In Datasets (Ship with scikit-learn)

### Classification

| Function | Samples | Features | Description |
|----------|---------|----------|-------------|
| `load_iris()` | 150 | 4 | Flower species classification |
| `load_breast_cancer()` | 569 | 30 | Breast cancer diagnosis (binary) |
| `load_wine()` | 178 | 13 | Wine quality classification |
| `load_digits()` | 1797 | 64 | Handwritten digits (0-9) |

```python
from sklearn.datasets import load_iris
data = load_iris()
X, y = data.data, data.target
data.feature_names
data.target_names
```

**Return type:** `Bunch` object (dict-like with attributes). Use `return_X_y=True` for tuple.

### Regression

| Function | Samples | Features | Description |
|----------|---------|----------|-------------|
| `load_diabetes()` | 442 | 10 | Disease progression |
| `load_linnerud()` | 20 | 3/3 | Multivariate (exercise dataset) |

### Image

| Function | Description |
|----------|-------------|
| `load_sample_image("asteroid")` | Single color image (numpy array) |
| `load_sample_images()` | Multiple small images |

## Remote Datasets (Downloaded on First Use)

### `fetch_california_housing(*, as_frame=False)`
California housing prices. 20,640 samples, 8 features.

### `fetch_openml(name, version=None, parser="auto", *, as_frame=False)`
Fetch any dataset from OpenML.

```python
from sklearn.datasets import fetch_openml

# MNIST
mnist = fetch_openml("mnist_784", version=1, as_frame=False, parser="auto")

# Titanic
titanic = fetch_openml("titanic", version=1, as_frame=True)

# Search by task type
housing = fetch_openml(name="house_prices", as_frame=True)
```

**1.9:** Fixed to use `https://www.openml.org/api/v1/` endpoint.

### Other Remote Datasets

| Function | Description |
|----------|-------------|
| `fetch_20newsgroups(subset="train")` | Text classification (20 topics) |
| `fetch_20newsgroups_vectorized()` | Pre-vectorized newsgroups |
| `fetch_covtype()` | Forest cover type (500K samples) |
| `fetch_kddcup99()` | Network intrusion detection |
| `fetch_lfw_people(min_face_size=0.4)` | Face recognition |
| `fetch_lfw_pairs()` | Face pairs for similarity |
| `fetch_olivetti_faces()` | 400 faces (10 images per person) |
| `fetch_rcv1()` | Multi-label text classification |
| `fetch_species_distributions()` | Species distribution modeling |

## Synthetic Data Generators

### Classification

| Function | Parameters | Description |
|----------|------------|-------------|
| `make_classification(n_samples=100, n_features=20, n_classes=2)` | `n_informative`, `n_redundant`, `n_clusters_per_class` | Random classification dataset |
| `make_blobs(n_samples=100, centers=3, n_features=2)` | `cluster_std` | Isotropic Gaussian blobs |
| `make_circles(n_samples=100, noise=None)` | `factor` (inner/outer radius ratio) | Concentric circles |
| `make_moons(n_samples=100, noise=None)` | — | Interleaving half-moons |
| `make_hastie_10_2(n_samples=1200)` | — | Hastie's binary classification |
| `make_gaussian_quantiles()` | — | Gaussian blobs with quantile labels |
| `make_multilabel_classification()` | `n_classes`, `n_labels` | Multi-label classification |

```python
from sklearn.datasets import make_classification
X, y = make_classification(
    n_samples=1000, n_features=20, n_informative=10,
    n_redundant=5, n_classes=3, random_state=42
)
```

### Regression

| Function | Description |
|----------|-------------|
| `make_regression(n_samples=100, n_features=10)` | Linear regression with noise |
| `make_friedman1(n_samples=100)` | Nonlinear regression (Friedman #1) |
| `make_friedman2(n_samples=100)` | Nonlinear regression (Friedman #2) |
| `make_friedman3(n_samples=100)` | Nonlinear regression (Friedman #3) |

```python
from sklearn.datasets import make_regression
X, y = make_regression(
    n_samples=500, n_features=10, n_informative=5,
    noise=0.1, random_state=42
)
```

### Matrix Generators

| Function | Description |
|----------|-------------|
| `make_low_rank_matrix()` | Low rank matrix |
| `make_spd_matrix()` | Symmetric positive-definite matrix |
| `make_sparse_spd_matrix()` | Sparse SPD matrix |
| `make_sparse_uncorrelated()` | Sparse uncorrelated matrix |
| `make_sparse_coded_signal()` | Sparse coding signal |

### Biclustering

| Function | Description |
|----------|-------------|
| `make_biclusters()` | Data with strong bicluster structure |
| `make_checkerboard()` | Checkerboard pattern |

### Manifold

| Function | Description |
|----------|-------------|
| `make_s_curve(n_samples=100)` | S-curve manifold |
| `make_swiss_roll(n_samples=100)` | Swiss roll manifold |

## File I/O

### LIBSVM Format

```python
from sklearn.datasets import load_svmlight_file, dump_svmlight_file

# Load
X, y = load_svmlight_file("data.svm")

# Save
dump_svmlight_file(X, y, "data.svm")
```

### Text Files

```python
from sklearn.datasets import load_files
categories_data = load_files(
    "./text_data",
    categories=["positive", "negative"],
    encoding="utf-8"
)
```

## Utility Functions

| Function | Purpose |
|----------|---------|
| `get_data_home()` | Return path to data directory |
| `clear_data_home()` | Remove cached data |
| `fetch_file(url, *, dirname=None)` | Download and cache a file |

## Data Format Notes

- `as_frame=True` returns pandas DataFrames with proper column names
- Default return is `Bunch` object with `.data` (numpy array) and `.target` (numpy array)
- Use `return_X_y=True` for `(X, y)` tuple instead of `Bunch`
- For large datasets, consider `parser="liar"` (faster) or `parser="auto"` in `fetch_openml`
