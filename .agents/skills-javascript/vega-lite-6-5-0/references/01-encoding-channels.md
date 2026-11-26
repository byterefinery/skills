# Encoding channels

`encoding` is the mapping between channels and data fields, constant visual values, or constant data values (datum). Every channel definition is one of:

- **Field definition** — `{field, type, ...}`: encodes a data field. Supports inline field transforms (`aggregate`, `bin`, `sort`, `stack`, `timeUnit`) plus `band`, `title`, `tooltip`.
- **Value definition** — `{value}`: a constant *visual* value (e.g. a fixed color, a fixed x position).
- **Datum definition** — `{datum}`: a constant *data* value passed through the scale. Supports `band`, `scale`, `axis`, `legend`, `format`, `condition` — but no data transforms.

Channel-specific additions by group:

| Channel group | Channels | Extra definition properties |
| --- | --- | --- |
| Position | `x`, `y`, `x2`, `y2`, `xError`, `yError`, `xError2`, `yError2` | `scale`, `axis`, `sort`, `impute`, `stack` (`x2`/`y2` share the base channel's) |
| Position offset | `xOffset`, `yOffset` | `scale`, `sort` |
| Polar | `theta`, `theta2`, `radius`, `radius2` | `scale`, `stack`, `sort` |
| Geographic | `longitude`, `latitude`, `longitude2`, `latitude2` | (projection-based; see the spec's `projection` property) |
| Mark property | `angle`, `color` (and `fill`/`stroke`), `opacity`, `fillOpacity`, `strokeOpacity`, `shape`, `size`, `strokeDash`, `strokeWidth` | `scale`, `legend`, `condition` |
| Text and tooltip | `text`, `tooltip` | `format`, `formatType`, `condition` |
| Hyperlink | `href` | `condition` — the mark becomes a clickable link; `cursor` defaults to `pointer` |
| Description | `description` | `format`, `formatType`, `condition` — ARIA `aria-label` for SVG output; auto-generated from encoding unless `config.aria` is false or `mark.aria` is false |
| Level of detail | `detail` | grouping field with no visual mapping |
| Key | `key` | object constancy for transitions over dynamic data — matches data elements to existing mark instances on updates |
| Order | `order` | `sort` — stacking order, line point order (connected scatterplots), zorder |
| Facet | `facet`, `row`, `column` | small-multiple partitioning |

## Position channels

`x`/`y` determine mark position (or width/height of horizontal/vertical `area` and `bar`). `x2`/`y2` specify the span of ranged `area`, `bar`, `rect`, and `rule`. Vega-Lite auto-generates a scale and axis for each mapped field; customize via the field definition's `scale` and `axis` properties.

`xOffset`/`yOffset` add an offset to the `x`/`y` position (grouped bars, jittering). With a discrete base channel, a quantitative offset drives ranged geometry — e.g. a nominal `y` lane plus quantitative `yOffset` makes each bar span from the lane baseline to the offset value. Path marks (`line`, `area`, `trail`) draw one connected path, so multi-lane charts need a grouping channel like `detail` (or `color`) to split paths per lane.

## Mark property channels

Each mapped field auto-generates a scale and legend; customize with `scale`, `legend`, and `condition`. Mark property value definitions also accept `condition`.

## Text and tooltip

Text/tooltip directly encode text values; Vega-Lite picks sensible formats for quantitative and temporal values — override with `format` (`formatType` selects the pattern type).

Tooltips accept an **array of field definitions** for multi-field tooltips (Vega tooltip renders a name/value table). Since 6.5.0, field definitions in the array may include a **`filter` predicate** to omit individual fields at runtime.

## Level of detail

Mapping an unaggregated field to any non-position channel groups `line`/`area` marks by it. In aggregated plots, all encoded unaggregated fields act as `GROUP BY` fields. `detail` adds grouping fields without mapping them to visual properties.

## Condition

`condition` (on mark property, text, and several other channels) specifies conditional encoding rules — the standard mechanism for highlighting selection results or emphasizing subsets of the data.
