# Mark properties

Mark-specific properties go in the mark definition object — `"mark": {"type": "bar", "cornerRadius": 5}` — and are overridden by the same-named encoding channels (`color` in encoding beats `color` in the mark definition). All marks accept the common properties first; per-mark properties follow.

## Common mark properties

| Property | Type | Notes |
|---|---|---|
| `color` / `fill` / `stroke` | string | default colour, fill, stroke |
| `opacity` / `fillOpacity` / `strokeOpacity` | number 0–1 | |
| `tooltip` | boolean | show a tooltip on hover |
| `aria` | boolean | generate ARIA labels for accessibility |
| `cursor` | string | CSS cursor value |

## bar

- `orient`: `auto` (default) | `vertical` | `horizontal`
- `baseline`: `start` | `center` (default) | `center-clip` | `end`
- `cornerRadius`: number, or per-corner object `{topLeft, topRight, bottomLeft, bottomRight}`
- `filled`: boolean (default true)

## line

- `point`: boolean — draw point marks at the line vertices (`{"type": "line", "point": true}`)
- `orient`: `auto` | `vertical` | `horizontal`
- `interpolate`: `linear` (default) | `step-before` | `step-after` | `step-middle` | `linear-closed` | `monotone` | `monotone-x` | `monotone-y` | `natural` | `basis` | `basis-open` | `bundle` | `cardinal` | `cardinal-open`
- `connectNulls`: boolean — connect across missing/null values
- `defined`: expression — predicate over the datum to exclude points
- `strokeWidth`, `strokeDash` — e.g. dashed lines `{"type": "line", "strokeDash": [6, 4], "strokeWidth": 2}`

## area

- `orient`, `interpolate`, `connectNulls`, `defined` — same options as `line`
- `line`: boolean — draw the outline line over the filled area
- Stacking (mark or channel level): `stack` = `zero` | `normal` | `expand` | `center` | `null` (disable)

## point / circle

- `size`: number (pixel area; `circle`/`point` accept the `size` encoding channel for bubble charts)
- `filled`: boolean (default false)
- `shape`: constant shape value (see Shape values) — usually set via the `shape` encoding channel
- `disc` (`circle` only): boolean — anti-aliased disc rendering

## square

- `size`: number (side length)
- `filled`: boolean (default false)

## rect

- `orient`: `auto` | `vertical` | `horizontal`
- `cornerRadius`: number, or per-corner object
- `filled`: boolean (default true)

## rule

- `orient`: `auto` | `vertical` | `horizontal`
- `strokeWidth`, `strokeDash` — dashed reference lines
- Vertical reference lines: encode `x` to an aggregated value, leave `y` unset

## arc

- Requires `theta` encoding for the angle span; `radius` / `radius2` channels for ring thickness
- `innerRadius`: number (px) — donut hole, e.g. `{"type": "arc", "innerRadius": 50}`
- `outerRadius`: number (px)
- `startAngle`, `endAngle`: number (radians)
- `cornerRadius`: number, or per-corner object

## text

- `text`: template string with `{field}` placeholders (usually via the `text` encoding channel)
- `textFormat`: number format for formatted values (e.g. `,.2f`)
- `lineHeight`: number
- `radius`: number — radial offset for polar labels (e.g. `1.1` places text just outside a pie arc)
- `dx`, `dy`: number — pixel offsets from the mark position
- `limit`: number — maximum text length before truncation
- `ellipsis`: string (default `…`)
- `angle`: number (radians) — text rotation
- `baseline`: `alphabetic` | `middle` | `central` | `text-after` | `text-before` | `top` | `bottom` | `auto`

## tick

- `orient`: `auto` | `vertical` | `horizontal` (horizontal = strip plot along x)
- `size`: number (px) — tick length
- `bandPosition`: number 0–1 — position of the tick within its band
- `color`

## trail

- Like `line`, but the stroke width is driven by a **quantitative `size` encoding** (variable width)
- `length`: number 0–1 — fraction of the data trail each point covers
- `thickness`: number 0–1 — relative stroke thickness
- `orient`, `interpolate` — line-style options
- Typical uses: comet charts (trend + volume width)

## geoshape

- Data must be `geojson` or `topojson` (format inferred from the URL extension, or set explicitly)
- Top-level `projection` property for map projections, e.g. `{"type": "geoMercator"}`
- `points`: boolean — render GeoJSON as points instead of shapes
- `line`: boolean — outline (stroke) the shapes
- Layer with `circle` marks to annotate specific locations on maps

## image

- Position with `x`/`y` encodings; image source via the `url` encoding channel
- `width`, `height`: number (px) — mark size
- `resize`: `fit` | `contain` | `cover`
- `aspect`: boolean — keep the image's aspect ratio
- Supports inline data URLs and external image sources

## Composite marks

### boxplot

- `extent`: `iqr` (default) | `min-max` | `sd` | number (multiplier) | `[lo, hi]` pair
- `span`: number (default 1.5) — whisker span as a fraction of the IQR
- `size`: number (px) — box width
- `filled`: boolean
- `orient`: `vertical` (default) | `horizontal` (swap x/y)
- Requires a quantitative channel to plot against; the other channel is the group

### errorbar

- `extent`: `ci` (default, 95% confidence interval) | `iqr` | `stdev` | number (sd multiplier) | `[lo, hi]` pair
- `size`: number (px) — cap size
- `orient`: `vertical` (default) | `horizontal`
- `borders`: boolean — stroke outline on the bars
- `strokeWidth`, `strokeDash`, `color`

### errorband

- `extent`: same options as `errorbar`
- `line`: boolean — draw the central line through the band
- `borders`: boolean — outline the band
- `orient`, `color`, `opacity`
- Layer a `line` mark over an `errorband` to show the mean trend through the uncertainty region

## Shape values

For the `shape` encoding channel / mark property: `circle` | `square` | `symbol` | `cross` | `diamond` | `triangle-up` | `triangle-down` | `triangle-right` | `triangle-left` | `wedge` | `stroke` | `none`

## Notes

- Composite marks compile to layered primitive specs — their special properties are `extent`, `span`, `borders`, `line` (in addition to the common ones).
- `"mark": "bar"` is shorthand; use the object form when customizing mark properties: `"mark": {"type": "bar", "tooltip": true}`.
- Every spec must still pass `vega-lite.sh validate` — property names/positions are enforced by the bundled v6.5.0 schema.
