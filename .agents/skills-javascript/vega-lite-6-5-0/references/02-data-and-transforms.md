# Data and transforms

## Data sources

The `data` property describes the visualization's tabular data source. A data source is one of:

| form | property | notes |
| --- | --- | --- |
| Inline data | `values` | Array of objects (row-oriented), or a string parsed per `format`. A bare array of primitives maps each value to a `data` field (`[5,3]` → `[{data:5},{data:3}]`) |
| URL | `url` | Format inferred from the file extension; override with `format` |
| Named source | `name` | Empty source bound at runtime via the Vega View API (`view.insert('myData', data).run()`), or populated from top-level `datasets` |
| Generator | `sequence`, `graticule`, `sphere` | Data generators — see below |

### Format

`format` describes parsing. Types: `json` (default; row-oriented; optional `property` to extract a sub-object), `csv`, `tsv`, `dsv` (custom `delimiter`), `topojson` (converts to GeoJSON via mutually exclusive `feature` or `mesh`). `format.parse` can force types on individual fields.

### Generators

- **`sequence`** — numeric series with `start`, `stop`, optional `step`; field name defaults to `data` (change with `as`).
- **`graticule`** — lat/lon grid as GeoJSON (boolean `true` for defaults, or object with `extent`, `extentMajor`, `extentMinor`, `precision`, `step`, `stepMajor`, `stepMinor`).
- **`sphere`** — `[{"type": "Sphere"}]` GeoJSON, a map background layer (boolean `true` or empty object).

### Datasets

Top-level `datasets` maps names to inline tables so the same data can be referenced by several named sources:

```json
{
  "datasets": { "somedata": [1, 2, 3] },
  "data": { "name": "somedata" }
}
```

## Transforms

Transforms are described either as **view-level** `transform` (an array in the spec) or as **inline field transforms** inside `encoding` (`bin`, `timeUnit`, `aggregate`, `sort`, `stack`). Execution order: view-level transforms first, in array order, then inline transforms in the fixed order `bin` → `timeUnit` → `aggregate` → `sort` → `stack`.

View-level transform types:

| transform | purpose |
| --- | --- |
| `aggregate` | SQL-style aggregation; unaggregated encoded fields become group-by |
| `bin` | Bin a field into ranges |
| `calculate` | Compute new fields with expression strings |
| `density` | Kernel density estimation |
| `extent` | Compute data extent |
| `filter` | Keep rows matching a predicate |
| `flatten` | Unnest arrays into multiple rows |
| `fold` | Pivot multiple fields into two (key/value) fields |
| `impute` | Fill missing values |
| `joinaggregate` | Cross-join aggregated values (e.g., totals) back onto each row |
| `lookup` | Join another dataset by key |
| `pivot` | Reshape rows into columns |
| `quantile` | Quantile sampling |
| `regression` / `loess` | Regression fits |
| `sample` | Random sampling |
| `stack` | Stacking for layered area/bar |
| `timeunit` | Time-unit conversion |
| `window` | Windowed calculations over sorted groups — ranking, lead/lag, running aggregates; written back into the stream (`op`, `field`, `as`, `param`; options `sort`, `groupby`, `frame`, `ignorePeers`) |

### 6.5.0 aggregate ops

The `exponential` and `exponentialb` aggregate ops (exponential moving average) are parameterized — they take an object with the parameter value instead of a bare string:

```json
{ "exponential": 0.5 }
```

The arg-taking ops work the same way: `{"argmax": "field"}`, `{"argmin": "field"}`.
