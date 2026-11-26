# API and Updating Charts

## Instance Methods

| Method | Notes |
|---|---|
| `chart.destroy()` | Clean up references and event listeners. **Must** be called before the canvas is reused for a new chart. |
| `chart.update(mode?)` | Update scales, legend, and re-render after data/options changes. Mode: a string transition — 'active', 'hide', 'reset', 'resize', 'show', or `'none'` to skip animations; or a function receiving `{datasetIndex}` returning a mode string. |
| `chart.reset()` | Reset to the state before the initial animation; a new animation can be triggered with update. |
| `chart.render()` | Redraw all elements; does not recompute for new data (use update). |
| `chart.stop()` | Stop the current animation loop; call render to re-animate. Returns this. |
| `chart.resize(width?, height?)` | No args = fit container; explicit dims for e.g. printing. Returns this. |
| `chart.clear()` | Clear the canvas. Returns this. |
| `chart.toBase64Image(type?, quality?)` | Data URL of current canvas; png by default, e.g. `'image/jpeg', 1` for max quality jpeg. |
| `chart.getElementsAtEventForMode(e, mode, options, useFinalPosition)` | Elements hit by event under mode; options/useFinalPosition passed through to handlers. |
| `chart.getSortedVisibleDatasetMetas()` | Visible dataset metas in draw order. |
| `chart.getDatasetMeta(index)` | Dataset metadata; `meta.data` holds point/bar/etc. info. |
| `chart.getVisibleDatasetCount()` | Count of non-hidden datasets. |
| `chart.isDatasetVisible(i)` | Boolean; checks metadata hidden flag first, then `dataset.hidden`. |
| `chart.setDatasetVisibility(i, v)` | Set dataset visibility (then call update); handy for HTML legends. |
| `chart.toggleDataVisibility(index)` | Toggle one item in all datasets; supported by doughnut/pie, polarArea, bar (then call update). |
| `chart.getDataVisibility(index)` | Visibility state set by toggleDataVisibility. |
| `chart.hide(datasetIndex, dataIndex?)` | Hide dataset (animated 'hide') or one data element (then update). |
| `chart.show(datasetIndex, dataIndex?)` | Show dataset (animated 'show') or one data element (then update). |
| `chart.setActiveElements(elements)` | Programmatic hover, e.g. `[{datasetIndex: 0, index: 1}]`. |
| `chart.isPluginEnabled(id)` | Plugin registered for this instance? |

## Static Methods

- `Chart.getChart(key)` — find instance by canvas id (string), context, or DOM element; undefined if not found.
- `Chart.register(...components)` — register controllers, elements, scales, plugins (and inline plugin objects).

## Clicking Points

```js
function clickHandler(evt) {
  const points = myChart.getElementsAtEventForMode(evt, 'nearest', { intersect: true }, true);
  if (points.length) {
    const firstPoint = points[0];
    const label = myChart.data.labels[firstPoint.index];
    const value = myChart.data.datasets[firstPoint.datasetIndex].data[firstPoint.index];
  }
}
```

## Updating Data

```js
function addData(chart, label, newData) {
  chart.data.labels.push(label);
  chart.data.datasets.forEach((dataset) => { dataset.data.push(newData); });
  chart.update();
}

function removeData(chart) {
  chart.data.labels.pop();
  chart.data.datasets.forEach((dataset) => { dataset.data.pop(); });
  chart.update();
}
```

## Updating Options

Mutating `chart.options` in place preserves other (including internally calculated) properties; assigning a **new** options object replaces everything, like creating a new chart.

```js
// in place
chart.options.plugins.title.text = 'new title';
chart.update();

// replacement
chart.options = { responsive: true, /* full options */ };
chart.update();
```

Scales can be updated separately — pass an object containing **all** customization including unchanged ones. Variables referencing entries of `chart.scales` are lost after updating scales with a new id or changed type; re-read references.

## Preventing Animations

`chart.update('none')` skips animation for that update.
