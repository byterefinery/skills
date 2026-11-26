# Usage — embedding, compiling, CLI

## Embedding in a web page

Vega-Embed is the painless path. Load Vega, Vega-Lite, and Vega-Embed (CDN via jsDelivr, or npm), create a container, embed:

```sh
npm install vega
npm install vega-lite
npm install vega-embed
```

```html
<div id="vis"></div>
```

```js
vegaEmbed('#vis', yourVlSpec);
```

Vega-Embed automatically adds links to export an image, view the source, and open the spec in the online editor — each can be disabled individually. A full minimal page:

```html
<!doctype html>
<html>
  <head>
    <title>Embedding Vega-Lite</title>
    <script src="https://cdn.jsdelivr.net/npm/vega"></script>
    <script src="https://cdn.jsdelivr.net/npm/vega-lite"></script>
    <script src="https://cdn.jsdelivr.net/npm/vega-embed"></script>
  </head>
  <body>
    <div id="vis"></div>
    <script type="text/javascript">
      var yourVlSpec = {
        $schema: 'https://vega.github.io/schema/vega-lite/v6.json',
        description: 'A simple bar chart with embedded data.',
        data: {
          values: [
            {a: 'A', b: 28}, {a: 'B', b: 55}, {a: 'C', b: 43},
            {a: 'D', b: 91}, {a: 'E', b: 81}, {a: 'F', b: 53},
            {a: 'G', b: 19}, {a: 'H', b: 87}, {a: 'I', b: 52},
          ],
        },
        mark: 'bar',
        encoding: {
          x: {field: 'a', type: 'ordinal'},
          y: {field: 'b', type: 'quantitative'},
        },
      };
      vegaEmbed('#vis', yourVlSpec);
    </script>
  </body>
</html>
```

## Compiling in JavaScript

`vegaLite.compile(vlSpec, options)` returns the compiled result; `.spec` is the Vega spec:

```js
var vgSpec = vegaLite.compile(vlSpec, options).spec;
```

`options`:

- `config` — a default config object. The spec's own `config` property **overrides** it.
- `logger` — custom logger implementing `level(_)`, `warn(...)`, `info(...)`, `debug(...)`; by default messages go to the JS console.
- `fieldTitle` — a `function (fieldDef, config)` formatter for generated axis/legend titles.

## Command line

The package ships `vl2vg`, `vl2png`, `vl2svg`, `vl2pdf` (Vega-Lite → Vega / PNG / SVG / PDF). Each takes the spec as its first argument, or reads it from stdin:

```sh
vl2svg spec.vl.json
cat spec.vl.json | vl2svg
vl2vg spec.vl.json -p   # -p formats the generated Vega spec
```

Easiest via `npx` (no pre-install needed):

```sh
npx -p vega -p vega-lite vl2png --help
```

In a project, prefix calls with `node_modules/.bin/`. If you get `Error: CanvasRenderer is missing a valid canvas or context`, install the [`canvas`](https://github.com/Automattic/node-canvas) package (or vega-cli).
