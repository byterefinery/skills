# TabFM 1.0.0 — Data Preparation

## Input Formats

TabFM accepts pandas DataFrames or numpy arrays. DataFrames are preferred as they handle mixed column types naturally.

### DataFrame (Recommended)

```python
import pandas as pd

df = pd.read_csv("data.csv")
X = df.drop(columns=["target"])
y = df["target"]
```

Columns can be any mix of:
- Numerical (int, float)
- Categorical (string, object, categorical dtype)
- Boolean

TabFM handles encoding internally.

### Numpy Array

```python
import numpy as np

X = np.array([[1.0, 2.5], [3.0, 4.5]])
y = np.array([0, 1])
```

All columns must be numerical. Categorical columns need manual encoding (e.g., one-hot or label encoding) before conversion.

## Categorical Columns

- **In DataFrames**: Pass as-is (strings, objects, or pandas Categorical). TabFM applies Fourier feature embedding and per-group linear projection internally.
- **In numpy arrays**: Encode manually first. One-hot encoding works but can widen the feature matrix. Label encoding preserves column count but loses cardinality information.

## Handling Missing Values

TabFM does not explicitly document missing value handling. Best practices:

1. **Numerical columns**: Fill with median or mean, or add a binary indicator column for missingness
2. **Categorical columns**: Fill with a sentinel value like `"missing"` or the mode
3. **Drop rows** with excessive missingness if the dataset is large enough

```python
# Fill numerical with median, categorical with "missing"
for col in X.select_dtypes(include=["number"]).columns:
    X[col] = X[col].fillna(X[col].median())
for col in X.select_dtypes(exclude=["number"]).columns:
    X[col] = X[col].fillna("missing")
```

## Train/Test Split

TabFM uses in-context learning — training rows are the context, test rows are predicted. The split determines how much context the model sees:

```python
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
```

- More training rows = richer context but higher memory usage
- For small datasets, use all available data as context
- For very large datasets, consider subsetting training context

## Feature Count

TabFM is optimized for tables up to 500 features. For wider tables:

- Consider dimensionality reduction (PCA, feature selection) before passing to TabFM
- Remove near-zero variance columns
- Drop highly correlated features

## Loading from Different Sources

### CSV

```python
df = pd.read_csv("data.csv")
```

### Excel

```python
df = pd.read_excel("data.xlsx")
```

### Parquet

```python
df = pd.read_parquet("data.parquet")
```

### Database

```python
import sqlalchemy as sa

engine = sa.create_engine("sqlite:///data.db")
df = pd.read_sql("SELECT * FROM table", engine)
```
