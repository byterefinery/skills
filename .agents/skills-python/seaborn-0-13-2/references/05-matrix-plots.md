# Matrix Plots

Plots for visualizing matrix/array data.

## heatmap

Color-encoded matrix.

```python
sns.heatmap(
    data=corr_matrix,
    annot=True, fmt=".2f", cmap="coolwarm", center=0,
    linewidths=0.5, linecolor="white",
    cbar=True, cbar_kws={"shrink": 0.8},
    xticklabels="auto", yticklabels="auto",
    mask=mask, square=False
)
```

**Parameters:**
- `data` — 2D array or DataFrame (required)
- `vmin`, `vmax` — color scale limits
- `cmap` — colormap name or `matplotlib.colors.Colormap`
- `center` — center value for diverging colormaps (e.g., 0 for correlation matrices)
- `robust` — `True` to set vmin/vmax to 5th/95th percentile (outlier-resistant)
- `annot` — `True` to write cell values, or array of same shape as data
- `fmt` — string format for annotations (default `".2g"`)
- `annot_kws` — dict passed to `ax.text()` for annotations (e.g., `{"fontsize": 8}`)
- `linewidths` — width of lines between cells (default 0)
- `linecolor` — color of lines between cells (default `"white"`)
- `cbar` — `True` (default, show colorbar), `False`
- `cbar_kws` — dict passed to colorbar creation (e.g., `{"shrink": 0.8, "label": "Correlation"}`)
- `cbar_ax` — Axes to draw colorbar on
- `square` — `True` to make cells square
- `xticklabels`, `yticklabels` — `"auto"` (default, use DataFrame columns/index), `True`, `False`, or list of labels
- `mask` — boolean array of same shape; `True` values are hidden (useful for triangular masks)
- `ax` — target Axes

**Common patterns:**

```python
# Correlation matrix
corr = df.corr()
sns.heatmap(corr, annot=True, cmap="coolwarm", center=0, vmin=-1, vmax=1)

# Upper triangle only
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(corr, mask=mask, annot=True, cmap="coolwarm", center=0)

# With custom labels
sns.heatmap(corr, xticklabels=short_names, yticklabels=short_names, annot=True)

# Annotated with different format
sns.heatmap(data, annot=True, fmt=".1f", annot_kws={"fontsize": 10, "weight": "bold"})
```

## clustermap

Hierarchically clustered heatmap with dendrograms.

```python
g = sns.clustermap(
    data=matrix,
    method="average", metric="euclidean",
    z_score=0,  # 0=rows, 1=cols, None=neither
    standard_scale=None,
    row_cluster=True, col_cluster=True,
    row_colors=color_palette, col_colors=color_palette,
    figsize=(10, 10),
    cmap="coolwarm", center=0,
    dendrogram_ratio=0.2, colors_ratio=0.03,
    cbar_pos=(0.02, 0.8, 0.05, 0.18)
)
```

**Parameters:**
- `data` — 2D array or DataFrame (required)
- `pivot_kws` — dict for `pd.pivot_table()` if data is long-form (keys: `index`, `columns`, `values`)
- `method` — linkage method: `"average"` (default), `"single"`, `"complete"`, `"weighted"`, `"centroid"`, `"median"`, `"ward"`
- `metric` — distance metric: `"euclidean"` (default), or any `scipy.spatial.distance` metric
- `z_score` — `0` (normalize rows), `1` (normalize columns), `None` (no normalization)
- `standard_scale` — `0` (standardize rows), `1` (standardize columns), `None`
- `figsize` — `(width, height)` tuple
- `cbar_kws` — dict passed to colorbar creation
- `row_cluster`, `col_cluster` — `True` (default) to perform clustering, `False` to skip
- `row_linkage`, `col_linkage` — precomputed linkage matrices (skip clustering if provided)
- `row_colors`, `col_colors` — ColorList or DataFrame for annotating rows/columns with colors
- `mask` — boolean array; `True` values are hidden
- `dendrogram_ratio` — fraction of axis dedicated to dendrogram (default 0.2)
- `colors_ratio` — fraction of axis for color annotations (default 0.03)
- `cbar_pos` — `(left, bottom, width, height)` for colorbar position
- `tree_kws` — dict passed to dendrogram drawing
- `**kwargs` — passed to `heatmap()`

**Return value:** `ClusterGrid` object.

```python
# Save clustermap
g.figure.savefig("cluster.png", dpi=150, bbox_inches="tight")

# Access heatmap axes
g.ax_heatmap  # the heatmap Axes
g.ax_row_dendrogram  # row dendrogram Axes
g.ax_col_dendrogram  # column dendrogram Axes
g.ax_cbar  # colorbar Axes
```

**Note:** `clustermap` requires `scipy` for hierarchical clustering.
