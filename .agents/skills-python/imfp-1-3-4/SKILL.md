---
name: imfp-1-3-4
description: >
  imfp 1.3.4 — Python package for downloading economic data from the International
  Monetary Fund (IMF) JSON RESTful API (SDMX 3.0). Use when fetching IMF economic
  datasets (exchange rates, balance of payments, commodity prices, government finance,
  trade, IFS, WEO/World Economic Outlook data, etc.), browsing IMF databases, or
  working with IMF parameter codes. Returns pandas DataFrames. No API key required,
  but rate limits apply — set a custom app name to avoid shared throttling.
  Trigger on: IMF, International Monetary Fund, imfp, IMF data, IMF API, SDMX,
  exchange rates IMF, commodity prices IMF, IFS data, WEO data.
metadata:
  tags:
    - python
    - data
    - economics
    - imf
    - sdmx
---

# imfp 1.3.4

## Overview

imfp is a Python package that wraps the [IMF SDMX 3.0 API](https://api.imf.org/external/sdmx/3.0/) for retrieving economic and financial datasets from the International Monetary Fund. It provides four core functions that return `pandas` `DataFrame`s, plus admin helpers for rate-limit management.

### Key Capabilities

- **`imf_databases()`** — list all available IMF database IDs and descriptions (~71 databases)
- **`imf_parameters(database_id)`** — get all filter parameters and their valid input codes for a database
- **`imf_parameter_defs(database_id)`** — get text descriptions of what each parameter means
- **`imf_dataset(database_id, ...)`** — download data series as a DataFrame, with dimension filters, year ranges, and optional raw JSON return

### Admin Functions

- **`set_imf_app_name(name)`** — set a custom application name to avoid shared rate limits
- **`set_imf_wait_time(seconds)`** — adjust minimum wait time between API requests (default 1.5s)

### Dependencies

Install via `pip install imfp`. Runtime dependencies: `pandas`, `requests`, `type-enforced`. Requires Python 3.10+.

### Authentication

No API key required. The IMF API uses application-based rate limiting (50 req/s per app name). Set a unique app name with `set_imf_app_name()` to avoid being throttled alongside other imfp users.

## Usage

### Discovery Workflow

```python
import imfp

# 1. List all available databases
databases = imfp.imf_databases()
databases.head()
#    database_id  description
#  0         AFS  Analytical Financial Statistics
#  1         BOP  Balance of Payments Statistics
#  ...

# 2. Search for a specific database
databases[databases['description'].str.contains("Commodity")]

# 3. Get parameters for a database
params = imfp.imf_parameters("PPI")  # Producer Price Index
params.keys()
# dict_keys(['frequency', 'indicator', 'country', 'type_of_transformation'])

# 4. See valid codes for a parameter
params['frequency']
#   input_code  description
#  0          A      Annual
#  1          M    Monthly
#  2          Q  Quarterly

# 5. Get parameter descriptions
imfp.imf_parameter_defs("PPI")
```

### Fetching Data

```python
# Basic request with keyword filters
df = imfp.imf_dataset(
    database_id="PPI",
    frequency=["A"],           # Annual
    indicator=["PPI"],         # Producer Price Index
    start_year=2000,
    end_year=2015
)

# With multiple values per dimension
df = imfp.imf_dataset(
    database_id="PPI",
    frequency=["A"],
    indicator=["WPI"],
    type_of_transformation=["IX"],
    start_year=2000,
    end_year=2015
)

# Return raw JSON instead of DataFrame
raw = imfp.imf_dataset(
    database_id="PPI",
    frequency=["A"],
    return_raw=True
)
```

### Filtering Parameters Programmatically

```python
# Method 1: filter by description, extract codes
params = imfp.imf_parameters("PPI")
selected_freq = list(
    params['frequency']['input_code'][
        params['frequency']['description'].str.contains("Annual")
    ]
)

df = imfp.imf_dataset(
    database_id="PPI",
    frequency=selected_freq,
    start_year=2000,
    end_year=2015
)

# Method 2: modify parameters dictionary directly
modified_params = params.copy()
modified_params['frequency'] = params['frequency'][
    params['frequency']['description'].str.contains("Annual")
]

df = imfp.imf_dataset(
    database_id="PPI",
    parameters=modified_params,
    start_year=2000,
    end_year=2015
)
```

### Decoding Returned Codes

```python
# Replace input codes with human-readable descriptions
decoded = df.merge(
    params['frequency'][['input_code', 'description']],
    left_on='frequency',
    right_on='input_code',
    how='left'
).drop(columns=['frequency', 'input_code']).rename(
    columns={"description": "frequency"}
)
```

### Rate Limit Management

```python
# Set unique app name (recommended)
imfp.set_imf_app_name("my_analysis_app")

# Increase wait time between requests
imfp.set_imf_wait_time(5)

# Retry more times on failure
df = imfp.imf_dataset("PPI", frequency=["A"], times=5)
```

## Gotchas

- **No API key needed, but rate limits are strict** — the IMF API has both per-application (50 req/s) and global rate limits. At peak times requests may fail regardless. Set a custom app name with `set_imf_app_name()` to avoid sharing limits with other imfp users.
- **Default app name is shared** — using the default `"imfp"` app name means all users share the same rate limit bucket. The function warns about this but does not prevent it.
- **Each database has different parameters** — there is no universal set of filter names. Always call `imf_parameters(database_id)` first to discover valid parameters and codes for a given database.
- **`imf_dataset` with no filters fetches the entire database** — this prints a warning and will fail for large databases. Always supply at least one dimension filter.
- **`parameters` dict and keyword filters are mutually exclusive** — if both are supplied, keyword filters are ignored with a warning. Use one approach or the other.
- **`start_year`/`end_year` accept int or 4-digit string** — e.g., `2020` or `"2020"`. Other formats raise `ValueError`.
- **Year bounds are transformed per-frequency** — for a single frequency, `"2020"` becomes `"2020-Q1"` (start) / `"2020-Q4"` (end) for quarterly data. For multi-frequency or unspecified frequency, bounds use `"2020-A1"` (start) / `"2020-W99"` (end) to avoid excluding periods via lexicographic comparison.
- **Invalid codes are warned and ignored** — if you pass codes not valid for the parameter, imfp warns and drops them. Use `imf_parameters()` to check valid codes.
- **`return_raw=True` returns the raw SDMX JSON dict** — not a DataFrame. Use this when you need the full API response structure or metadata.
- **`include_metadata=True` returns `(metadata_dict, data)`** — the metadata dict is currently sparse (placeholder). The data element is a DataFrame (or raw dict if `return_raw=True`).
- **`times` parameter controls retries** — default is 3. On failure, imfp uses exponential backoff (5^attempt seconds). Increase `times` for unreliable connections.
- **Empty results raise `ValueError`** — if no data matches the filters, `imf_dataset` raises `"No data found for that combination of parameters."` Make the request less restrictive.
- **Returned columns are lowercased** — the DataFrame columns from `imf_dataset` are lowercased (e.g., `time_period`, `obs_value`, `frequency`). Match this casing when merging with parameter descriptions.
- **`set_imf_app_name("")` or `"imfp"` triggers a warning** — use a descriptive unique name. Names >255 chars or containing control characters raise `ValueError`.
- **`set_imf_wait_time(0)` disables inter-request delays** — valid but risky for rate limiting. Default is 1.5 seconds.
- **Alias parameters are auto-mapped** — `freq`/`frequency` and `ref_area`/`refarea`/`ref-area`/`country`/`geo` are recognized as aliases and coerced to the dataset-specific key. Duplicate coercion warns.
- **Caching is not built-in** — imfp has no disk cache. Cache results manually using `pd.to_parquet()` / `pd.read_parquet()` or similar. See the user guide for a caching pattern.

## References

- [01-api-reference](references/01-api-reference.md) — Full API reference for all functions, parameters, and return types
- [02-rate-limits](references/02-rate-limits.md) — Rate limiting, retries, caching strategies, and performance tips
