---
title: Embedding Vega-Lite in Web Apps
---

# Embedding Vega-Lite in Web Apps

Vega-Lite specs are compiled to Vega by the `vega-lite` library, then rendered by `vega`.

## Basic Embedding

```html
<div id="vis"></div>
<script src="https://cdn.jsdelivr.net/npm/vega@5"></script>
<script src="https://cdn.jsdelivr.net/npm/vega-lite@6.4.3"></script>
<script src="https://cdn.jsdelivr.net/npm/vega-embed@6"></script>
<script>
  vegaEmbed("#vis", spec, {actions: false});
</script>
```

## Options

`vegaEmbed` accepts a third options object:

- `actions: false` — hide the default action bar (source, editor, download buttons)
- `renderer: "svg"` or `"canvas"` — choose the rendering backend
- `defaultStyle: true` — apply default CSS styling to the container
- `bind: undefined` — prevent binding selections to DOM elements

## Programmatic Access

`vegaEmbed` returns a promise resolving to a `View` object:

```js
vegaEmbed("#vis", spec).then(result => {
  result.view.run();           // re-render
  result.view.change("data", vegalite.data(spec.data.values)); // update data
  result.view.change("spec", vegalite.spec(newSpec));           // update spec
  result.view.run();
});
```
