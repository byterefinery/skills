# Datasets and Utilities

## load_dataset

Load built-in example datasets.

```python
df = sns.load_dataset("tips")
df = sns.load_dataset("penguins")
df = sns.load_dataset("iris")
```

**Parameters:**
- `name` — dataset name (required)
- `cache` — `True` (default, cache downloaded files), `False`
- `data_home` — directory to cache data (default `~/.seaborn`)

**Available datasets:**
| Dataset | Description |
|---------|-------------|
| `"tips"` | Restaurant bills, tips, day, time, size |
| `"penguins"` | Penguin measurements (species, island, bill, flipper, sex) |
| `"iris"` | Iris flower measurements (species, sepal/petal dimensions) |
| `"titanic"` | Titanic passenger data (survival, class, age, sex, fare) |
| `"mpg"` | Car mileage data (manufacturer, model, cylinders, hp, weight) |
| `"fmri"` | fMRI scan data (subject, event, region, timepoint, signal) |
| `"fmri_subset"` | Subset of fmri |
| `"exercise"` | Exercise heart rate data (id, day, subject, kind, time, pulse) |
| `"dots"` | Dot pattern perception data |
| `"brain"` | Brain region data |
| `"cars"` | Car performance data |
| `"anscombe"` | Anscombe's quartet |
| `"attention"` | Span of attention experiment |
| `"births"` | Monthly births by day of week |
| `"geyser"` | Old Faithful geyser eruption data |
| `"planets"` | Exoplanet discovery data |
| `"seaice"` | Arctic sea ice extent |
| `"diamonds"` | Diamond prices and characteristics |
| `"flights"` | Monthly airline passengers |
| `"groceries"` | Grocery store spending |
| `"baseball"` | Baseball player statistics |
| `"species_richness"` | Species richness data |
| `"sixteen"` | 16-person personality data |
| `"dalmatian"` | Dalmatian image pixel data |
| `"synthetic"` | Synthetic regression data |

## move_legend

Move legend on an existing Axes.

```python
ax = sns.scatterplot(data=df, x="x", y="y", hue="group")
sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))
```

**Parameters:**
- `ax` — matplotlib Axes with a legend
- `location` — position string or `(x, y)` tuple
- `**kwargs` — passed to `ax.legend()`

## descriptive_stat

Compute descriptive statistics (internal utility).

## get_dataset_names

List all available built-in dataset names.

```python
from seaborn.utils import get_dataset_names
names = get_dataset_names()
# ['anscombe', 'attention', 'brain', 'cars', 'dots', 'exercise', 'flights',
#  'fmri', 'fmri_subset', 'geyser', 'gluebridge', 'groceries', 'iris',
#  'mpg', 'penguins', 'planets', 'seaice', 'titanic', 'tips']
```

## Loading External Data

For data not in the built-in set, use pandas:

```python
import pandas as pd

df = pd.read_csv("data.csv")
df = pd.read_parquet("data.parquet")
df = pd.read_excel("data.xlsx")
df = pd.read_json("data.json")
df = pd.read_sql("SELECT * FROM table", connection)
```

## Common Data Patterns

```python
# Wide-form to long-form (melt)
df_long = pd.melt(df, id_vars=["id"], var_name="variable", value_name="value")

# Pivot for heatmap
pivot = df.pivot_table(index="row_col", columns="col_col", values="value", aggfunc="mean")

# Correlation matrix for heatmap
corr = df.corr()

# Grouped data for categorical plots
grouped = df.groupby("category").agg({"value": ["mean", "std", "count"]})
```
