---
name: faostat-2-0-1
description: Python wrapper for the FAOSTAT API (FAO statistical database). Install via `pip install faostat` or `conda install -c noemicazzaniga faostat`. Use when the user needs to query FAO agricultural, food, production, trade, or commodity statistics programmatically — listing datasets, inspecting parameters, and downloading data as lists of tuples or pandas DataFrames. Requires a FAOSTAT Developer Portal account (JWT Bearer token or username/password).
---

# faostat 2.0.1

## Overview

Python package to read data and metadata from the FAOSTAT API. Every API call requires a JWT Bearer token (obtained manually from the [FAOSTAT Developer Portal](https://www.fao.org/faostat/en/#developer-portal) or programmatically via username/password). Tokens expire after 60 minutes and are not auto-refreshed.

The package exposes two families of functions: raw list-of-tuples (`list_datasets`, `list_pars`, `get_par`, `get_data`) and pandas DataFrame equivalents (`*_df`).

## Usage

### Install

```python
pip install faostat
```

Or via conda:

```python
conda install -c noemicazzaniga faostat
```

### Authenticate

Call `set_requests_args` before any other function. Provide either a token or username/password:

```python
import faostat

# Option A: manual token (from Developer Portal)
faostat.set_requests_args(token='my-jwt-token')

# Option B: programmatic login
faostat.set_requests_args(username='myuser', password='mypass')
```

Optional arguments:

| Argument | Default | Description |
|---|---|---|
| `lang` | `'en'` | Download language: `en`, `fr`, `es`, `ar`, `zh`, `ru` |
| `timeout` | `120.` | Seconds before raising a timeout error |
| `proxies` | `None` | Dict, e.g. `{'https': 'http://proxy:8080'}` |
| `verify` | `None` | TLS certificate verification |
| `cert` | `None` | Client SSL certificate |

Check current settings with `faostat.get_requests_args()` (returns token and lang; never returns username/password).

### Browse Datasets

```python
# List all available datasets
datasets = faostat.list_datasets()        # list of tuples
datasets_df = faostat.list_datasets_df()  # pandas DataFrame

# Columns: code, label, date_update, note_update, release_current,
#          state_current, year_current, release_next, state_next, year_next
```

Common dataset codes: `QCL` (Crops & livestock products), `QI` (Production Indices), `QV` (Value of Agricultural Production), `SCL` (Supply Utilization Accounts), `FS` (Food Security Indicators).

### Inspect Parameters

```python
# Available parameters for a dataset
pars = faostat.list_pars('QCL')        # list of tuples
pars_df = faostat.list_pars_df('QCL')  # DataFrame

# Columns: parameter code, coding_systems, subdimensions {code: meaning}
```

For `QCL`, parameters are: `area`, `element`, `item`, `year`.

### Get Parameter Values

```python
# As dict {label: code}
areas = faostat.get_par('QCL', 'area')

# As DataFrame with label, code, aggregate_type
areas_df = faostat.get_par_df('QCL', 'area')

# Subdimensions differ from parameter names — use subdimension codes
special_groups = faostat.get_par_df('QCL', 'specialgroups')
```

### Download Data

```python
mypars = {'area': '5815', 'element': [2312, 2313], 'item': '221', 'year': [2020, 2021]}

# List of tuples (values as strings by default)
data = faostat.get_data('QCL', pars=mypars)

# DataFrame with numeric values
df = faostat.get_data_df('QCL', pars=mypars, strval=False)
```

Optional arguments for `get_data` / `get_data_df`:

| Argument | Default | Description |
|---|---|---|
| `pars` | `{}` | Filter: `{parameter: code_or_list}` — **recommended** to avoid timeouts |
| `coding` | `{}` | Coding system override, e.g. `{'area': 'ISO3'}` (default is `FAO`) |
| `show_flags` | `False` | Include data quality flags |
| `null_values` | `False` | Include null data points |
| `show_notes` | `False` | Include data notes |
| `strval` | `True` | `True` = keep all values as strings; `False` = convert codes/values to numbers |
| `limit` | `-1` | Pagination row count per page; `-1` = no pagination (single request) |

#### Pagination for large datasets

```python
# Download in pages of 500 rows
df = faostat.get_data_df('QCL', pars={'item': '221'}, limit=500)
```

#### Coding system override

```python
# Use ISO3 country codes instead of FAO numeric codes
df = faostat.get_data_df('QCL', pars={'item': '221'}, coding={'area': 'ISO3'})
```

## Gotchas

- **Token expiry** — JWT tokens expire after 60 minutes. Re-authenticate by calling `set_requests_args` again. There is no auto-refresh.
- **`pars` is optional but strongly recommended** — omitting it requests the entire dataset, which often triggers a `TimeoutError` (HTTP 524). Always filter by at least one parameter.
- **Subdimension codes differ from parameter codes** — `list_pars` returns subdimensions (e.g., `countries`, `regions`, `specialgroups`) which are distinct from the parameter name (`area`). Use subdimension codes with `get_par` / `get_par_df`.
- **Default coding system is `FAO`** — area codes are FAO numeric codes by default. Use `coding={'area': 'ISO3'}` or `coding={'area': 'M49'}` to get ISO or M49 codes.
- **`strval=False` uses `eval()` internally** — it converts codes and values to numbers via `eval()`. Strings that cannot be evaluated remain as strings. Prefer `strval=True` (default) and convert types explicitly in pandas if needed.
- **`get_requests_args` never returns credentials** — username and password are not stored. It returns the derived token and language instead.
- **`assert` failures on bad arguments** — passing unexpected kwargs to `set_requests_args` or `get_data` raises `AssertionError` (not a custom exception). Validate argument names before calling.
- **Pagination adds a 1-second sleep between pages** — `limit=n` introduces `time.sleep(1)` between batches. Factor this into expected download time.
- **500 "Index: 0, Size: 0" means empty result** — the package prints a warning and returns `[]`. This is not a server error; it means no data matches the query.

## References

- [FAOSTAT Developer Portal](https://www.fao.org/faostat/en/#developer-portal) — register account, obtain token, browse API docs
- [FAOSTAT Data Catalog](https://www.fao.org/faostat/en/#data) — browse available datasets
- [Source code](https://bitbucket.org/noemicazzaniga/faostat/src/v2.0.1/) — full package on Bitbucket
- [PyPI](https://pypi.org/project/faostat/) — package page
- [Conda](https://anaconda.org/noemicazzaniga/faostat) — conda channel
- [Issues](https://bitbucket.org/noemicazzaniga/faostat/issues) — bug reports and feature requests
