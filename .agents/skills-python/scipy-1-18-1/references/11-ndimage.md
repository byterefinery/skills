# scipy.ndimage Reference (1.18.1)

N-dimensional image processing: filters, interpolation, morphology, labeling, and measurements.

## Table of Contents

- [Filters](#filters)
- [Fourier Filters](#fourier-filters)
- [Interpolation](#interpolation)
- [Morphology](#morphology)
- [Segmentation and Labeling](#segmentation-and-labeling)
- [Object Measurements](#object-measurements)

All functions share common parameters: `input`, `output`, `mode` (`'reflect'`, `'constant'`, `'nearest'`, `'mirror'`, `'wrap'`), `cval` (fill value for constant mode), and `origin`/`mode` handling per the module docstring.

## Filters

### Convolution and correlation

| Function | Description |
|---|---|
| `convolve(input, footprint, output=None, mode='reflect')` | N-D convolution |
| `convolve1d(input, size, axis=-1, mode='reflect')` | 1-D convolution along axis |
| `correlate(input, footprint, ...)` | N-D correlation |
| `correlate1d(input, size, axis=-1, ...)` | 1-D correlation along axis |

### Gaussian filters

| Function | Description |
|---|---|
| `gaussian_filter(input, sigma, order=0, mode='reflect')` | N-D Gaussian filter |
| `gaussian_filter1d(input, sigma, axis=-1, order=0)` | 1-D Gaussian filter |
| `gaussian_gradient_magnitude(input, sigma)` | Gradient magnitude via Gaussian smoothing |
| `gaussian_laplace(input, sigma)` | Laplacian via Gaussian smoothing |

```python
from scipy.ndimage import gaussian_filter, gaussian_gradient_magnitude

smoothed = gaussian_filter(image, sigma=2.0)
edges = gaussian_gradient_magnitude(image, sigma=1.0)
```

### Edge detection filters

| Function | Description |
|---|---|
| `sobel(input, axis=-1)` | Sobel filter (gradient approximation) |
| `prewitt(input, axis=-1)` | Prewitt filter |
| `generic_gradient_magnitude(input, footprint)` | Gradient magnitude with custom kernel |
| `laplace(input, ...)` | Laplacian (approximate second derivatives) |
| `generic_laplace(input, delta2)` | Laplacian with custom second-derivative kernel |

### Order-statistic filters

| Function | Description |
|---|---|
| `minimum_filter(input, size=None, footprint=None)` | N-D minimum filter |
| `maximum_filter(input, size=None, footprint=None)` | N-D maximum filter |
| `median_filter(input, size=None, footprint=None)` | N-D median filter (removes salt-and-pepper noise) |
| `percentile_filter(input, percentile, size=None)` | N-D percentile filter |
| `rank_filter(input, rank, size=None)` | N-D rank filter |

### Uniform and generic filters

| Function | Description |
|---|---|
| `uniform_filter(input, size=None, ...)` | N-D uniform (box) filter |
| `uniform_filter1d(input, size, axis=-1)` | 1-D uniform filter |
| `generic_filter(input, function, size=None, footprint=None)` | Apply an arbitrary function to local neighborhoods |
| `generic_filter1d(input, function, size, axis=-1)` | 1-D generic filter |
| `vectorized_filter(input, function, ...)` | Vectorized generic filter (faster for simple functions) |

```python
from scipy.ndimage import generic_filter
import numpy as np

def local_std(filter_inputs):
    return np.std(filter_inputs)

result = generic_filter(image, local_std, size=5)
```

## Fourier Filters

| Function | Description |
|---|---|
| `fourier_ellipsoid(input, sloblim, ...)` | Ellipsoidal low-pass filter in Fourier domain |
| `fourier_gaussian(input, sigma, ...)` | Gaussian filter in Fourier domain |
| `fourier_shift(input, shift, ...)` | Shift image via Fourier-domain multiplication |
| `fourier_uniform(input, size, ...)` | Uniform (box) filter in Fourier domain |

## Interpolation

Geometric transformations and resampling. Interpolation `order`: 0 (nearest), 1 (bilinear), 2 (quadratic), 3 (bicubic), 4–5 (higher-order spline).

| Function | Description |
|---|---|
| `zoom(input, zoom, order=3, mode='constant')` | Zoom image by factor(s) |
| `shift(input, shift, order=3, mode='constant')` | Shift image by offset(s) |
| `rotate(input, angle, reshape=True, order=3)` | Rotate image by angle (degrees) |
| `affine_transform(input, matrix, offset=0, ...)` | General affine transformation |
| `map_coordinates(input, coordinates, order=3, mode='constant')` | Map coordinates to values (arbitrary transform) |
| `geometric_transform(input, function, ...)` | Arbitrary geometric transform |
| `spline_filter(input, order=3, axis=-1)` | Spline pre-filter for interpolation |

```python
from scipy.ndimage import rotate, zoom, shift

rotated = rotate(image, 45, reshape=True, order=1)  # bilinear
zoomed = zoom(image, 2.0, order=3)                  # cubic, 2× zoom
shifted = shift(image, shift=(5, -3))
```

## Morphology

### Binary morphology

| Function | Description |
|---|---|
| `binary_erosion(input, structure=None, iterations=1)` | Erode (shrink) binary objects |
| `binary_dilation(input, structure=None, iterations=1)` | Dilate (grow) binary objects |
| `binary_opening(input, structure=None, iterations=1)` | Erosion then dilation (removes small objects) |
| `binary_closing(input, structure=None, iterations=1)` | Dilation then erosion (fills small holes) |
| `binary_fill_holes(input, structure=None)` | Fill holes in binary objects |
| `binary_hit_or_miss(input, footprint)` | Pattern matching |
| `binary_propagation(input, structure, mask)` | Propagate seeds through mask |

### Gray-level morphology

| Function | Description |
|---|---|
| `grey_erosion(input, size=None, footprint=None)` / `grey_dilation(...)` | Gray-level erosion / dilation |
| `grey_opening(...)` / `grey_closing(...)` | Gray-level opening / closing |
| `white_tophat(input, ...)` | Input minus opening (high-frequency details) |
| `black_tophat(input, ...)` | Closing minus input (dark details) |
| `morphological_gradient(input, ...)` | Dilation minus erosion (edge detection) |
| `morphological_laplace(input, ...)` | Dilation + erosion − 2×input |

### Distance transforms

| Function | Description |
|---|---|
| `distance_transform_edt(input, sampling=None)` | Euclidean distance transform (fast) |
| `distance_transform_cdt(input, metric='taxicab')` | Chamfer distance transform |
| `distance_transform_bf(input, masking_value=0)` | Boolean forest distance transform |

```python
from scipy.ndimage import binary_opening, distance_transform_edt
import numpy as np

cleaned = binary_opening(noisy_binary, structure=np.ones((3, 3)))
dist = distance_transform_edt(binary_objects)  # distance to nearest background pixel
```

### Structure generation

| Function | Description |
|---|---|
| `generate_binary_structure(rank, connectivity=1)` | Generate a structuring element |
| `iterate_structure(structure, iterations)` | Iterate a structure for multi-iteration morphology |

## Segmentation and Labeling

| Function | Description |
|---|---|
| `label(input, structure=None)` | Label connected features → `(labeled_array, num_features)` |
| `find_objects(label)` | Find bounding boxes of labeled objects |
| `watershed_ift(ift, markers, mask=None)` | Watershed segmentation via inverse forest transform |

```python
from scipy.ndimage import label, find_objects

labeled, num_features = label(binary_image)
print(f"Found {num_features} objects")
slices = find_objects(labeled)  # bounding boxes
```

## Object Measurements

All take `input` (values) and `label` (region labels), with optional `index` to select specific regions (regions are numbered from 1).

| Function | Description |
|---|---|
| `minimum(input, label, index=None)` / `maximum(...)` | Min / max value per region |
| `minimum_position(...)` / `maximum_position(...)` | Position of min / max |
| `sum_labels(input, label, index=None)` | Sum of values per region |
| `mean(...)` / `median(...)` | Mean / median per region |
| `variance(...)` / `standard_deviation(...)` | Variance / standard deviation per region |
| `center_of_mass(input, label, index=None)` | Center of mass per region |
| `extrema(input, label, index=None)` | Min/max values and positions |
| `histogram(input, min, max, label, index=None)` | Histogram per region |
| `value_indices(label, max_label=None)` | Indices for each distinct label value |
| `labeled_comprehension(input, condition, output, ...)` | Per-region custom computation |

```python
from scipy.ndimage import label, center_of_mass, mean

labeled, num = label(binary_image)
com = center_of_mass(image, labeled, range(1, num + 1))
avg = mean(image, labeled, range(1, num + 1))
```
