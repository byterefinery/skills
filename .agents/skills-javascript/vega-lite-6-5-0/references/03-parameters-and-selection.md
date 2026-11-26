# Parameters and selections

`params` is an array of named parameters — Vega-Lite's grammar of interaction. Parameters can be simple variables or complex selections that map user input (clicks, drags) to data queries, and can be used throughout the spec to determine encoding rules, filter data, set data extents, or appear in expression strings. They can also be bound to input widgets (sliders, dropdowns).

## Variable parameters

```js
{
  "params": [
    { "name": "cornerRadius", "value": 5, "bind": { "input": "range", ... } }
  ]
}
```

Properties: `name`, `value`, `bind`. Values can be changed dynamically by binding to a widget or by setting the underlying signal via the Vega View API.

**Expressions** — a parameter can be defined with `expr` instead of a static `value`. **Built-in parameters**: the spec's `width`, `height`, `padding`, `autosize`, and `background` are auto-defined (spec-level definitions merge with top-level values, winning). Reserved names you may not define: `datum`, `item`, `event`, `parent`. A parameter named `cursor` automatically drives the CSS mouse cursor.

## Selection parameters

A parameter becomes a selection when it has a `select` property — a data query driven by direct-manipulation input.

```js
{
  "params": [
    {
      "name": "pts",
      "select": {
        "type": "point",        // or "interval"
        "encodings": ["x", "y"] // projection — optional
      }
    }
  ]
}
```

- **`type: "point"`** — only directly interacted values (e.g. clicked marks) are considered selected.
- **`type: "interval"`** — values within _both_ the horizontal (`x`) and vertical (`y`) extents are considered selected (brushing).

The type determines the default trigger events and the resulting data query; override both with a full selection definition.
- `select` can also be a full selection definition to override defaults: `on` (event stream), `clear`, `resolve` (union/overwrite across multiple marks), `encodings`/`fields` (projection of the query onto fields or encodings).

## Using parameters

- **In expression strings** — the parameter name references its value; for selections, an object with properties for each projected field (e.g. `sel.Miles_per_Gallon > 75`).
- **As predicates** — pass the parameter where a predicate is expected (e.g. in `transform: [{filter: {param: "brush"}}]` or `condition`). Variable values are coerced to booleans per JS conventions; a selection predicate is true when the datum lies within the selection. **Empty selections contain all data by default** — set the optional `empty` property on the predicate to flip this.
- **As data extents** — a selection can drive a bin's extent or a scale's `domain` (overview+detail patterns). Extents are more performant than filtering data out. If the selection is projected over multiple fields/encodings, name which one the extent uses: `{"scale": {"domain": {"param": "brush", "encoding": "x"}}}`.

## Selection configuration

`config.selection` sets defaults for the `point` and `interval` selection types.
