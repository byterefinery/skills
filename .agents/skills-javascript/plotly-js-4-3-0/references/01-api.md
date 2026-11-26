# plotly.js 4.3.0 — public API

All from `src/plot_api/` in the plotly.js v4.3.0 source. Methods that act on a plot take the graph div (`gd`: element id or DOM element) first and return a Promise.

## Methods

| Method | Signature | Purpose |
|---|---|---|
| `newPlot` | `Plotly.newPlot(gd, data, layout, config)` or `Plotly.newPlot(gd, figure)` | Purge `gd` and plot fresh; `figure` is `{data, layout, config, frames}` |
| `react` | `Plotly.react(gd, data, layout, config)` | Diff-based update of an existing plot |
| `restyle` | `Plotly.restyle(gd, attrs, values, traces)` | Update trace attributes; `traces` restricts which traces |
| `relayout` | `Plotly.relayout(gd, attrs, value)` | Update layout attributes (e.g. `'xaxis.autorange'`) |
| `update` | `Plotly.update(gd, traceUpdate, layoutUpdate, traces)` | Combined restyle + relayout |
| `addTraces` | `Plotly.addTraces(gd, traces, newIndices)` | Append traces at `newIndices` |
| `deleteTraces` | `Plotly.deleteTraces(gd, indices)` | Remove traces by index |
| `moveTraces` | `Plotly.moveTraces(gd, currentIndices, newIndices)` | Reorder traces |
| `extendTraces` | `Plotly.extendTraces(gd, update, indices, maxPoints)` | Append points to existing traces (efficient) |
| `prependTraces` | `Plotly.prependTraces(gd, update, indices, maxPoints)` | Prepend points to existing traces |
| `animate` | `Plotly.animate(gd, frameOrGroupNameOrFrameList, animationOpts)` | Play animation frames |
| `addFrames` | `Plotly.addFrames(gd, frameList, indices)` | Add animation frames |
| `deleteFrames` | `Plotly.deleteFrames(gd, frameList)` | Remove animation frames |
| `redraw` | `Plotly.redraw(gd)` | Force a full redraw |
| `purge` | `Plotly.purge(gd)` | Destroy the plot and free resources |
| `toImage` | `Plotly.toImage(gd, opts)` | Render to an image; resolves with `{url, width, height}`; `opts.format` also accepts `'full-json'` |
| `downloadImage` | `Plotly.downloadImage(gd, opts)` | Trigger an image download |
| `validate` | `Plotly.validate(gd)` | Validate the figure in `gd` |
| `makeTemplate` | `Plotly.makeTemplate(data, layout)` | Create a layout template |
| `validateTemplate` | `Plotly.validateTemplate(template)` | Validate a template |
| `setPlotConfig` | `Plotly.setPlotConfig(obj)` | Set global default config (e.g. `{locale: 'de-CH'}`) |
| `deleteActiveShape` | `Plotly.deleteActiveShape(gd)` | Remove the currently drawn freehand shape |

`restyle`, `relayout`, and `update` also accept attribute-path strings such as `'xaxis.autorange'` (TypeScript types for this were added in 4.2.0).

## Events

User-facing events are emitted on the graph div; subscribe with the EventEmitter methods bound onto it (`gd.on`, `gd.once`, `gd.removeListener`, `gd.removeAllListeners`):

```js
Plotly.newPlot('gd', data, layout).then(function () {
    document.getElementById('gd').on('plotly_click', function (data) {
        console.log(data.points);
    });
});
```

Event names emitted in v4.3.0 source (`src/`):

| Event | Fired |
|---|---|
| `plotly_afterplot` | plot finished (also `plotly_beforeplot`) |
| `plotly_click`, `plotly_doubleclick` | point click / double-click |
| `plotly_hover`, `plotly_unhover` | hover on/off (also `plotly_beforehover`) |
| `plotly_relayout`, `plotly_relayouting` | layout changed (zoom, pan); during drag |
| `plotly_restyle` | restyle applied |
| `plotly_update` | update applied |
| `plotly_select`, `plotly_deselect` | box/lasso selection |
| `plotly_legendclick`, `plotly_legenddoubleclick` | legend item clicked |
| `plotly_frame` | animation frame shown |
| `plotly_animating`, `plotly_animated` | animation start / finish |
| `plotly_sliderstart`, `plotly_sliderchange`, `plotly_sliderend` | slider interaction |
| `plotly_buttonclicked` | modebar/updatemenu button clicked |
| `plotly_clickannotation` | annotation clicked |
| `plotly_treemapclick`, `plotly_sunburstclick`, `plotly_icicleclick` | hierarchical trace node clicked |
| `plotly_webglcontextlost` | WebGL context lost |
| `plotly_beforeexport`, `plotly_afterexport`, `plotly_exportfail` | image export lifecycle |

Internal-only events (framework, autosize, transitions, lifecycle bookkeeping) also exist but are not part of the stable user API.
