# Layouts and extensions

## Layouts

A layout positions nodes automatically. Create one with `cy.makeLayout(options)` (analogous `eles.makeLayout()` exists for a subset of the graph) and run it with `layout.run()`; `layout: {...}` in the init options runs it on the initial elements.

Built-in layouts (shipped with the core): `breadthfirst`, `circle`, `concentric`, `cose`, `grid`, `null`, `preset`, `random`.

Layout extensions add more (installed separately, registered with `cytoscape.use()`). Highlights from the curated list:

| extension | notes |
| --- | --- |
| `fcose` | faster CoSE-Bilkent; compound + non-compound; supports fixed/alignment/relative placement constraints. Docs: "If you want to use a force-directed layout, fCoSE should be the first layout you try." |
| `cose-bilkent` | near-perfect end results; more expensive than `cose` and `fcose` |
| `cosep` | force-directed with port constraints on compound graphs |
| `cola` | beautiful, smoothly animated results for relatively small graphs |
| `dagre` | DAGs and trees; hierarchical organisation |
| `elk` | adapter for the ELK layout algorithm family |
| `euler` | fast, small file size, high quality; good for non-compound graphs |
| `klay` | works well for most graph types; strong on DAGs and compound graphs |
| `avsdf` | organises nodes in a circle, minimises edge crossings |
| `cise` | circular clusters with a force-directed layout |
| `d3-force`, `springy`, `ngraph.forcelayout` | other force-directed options |
| `tidytree` | non-layered layout specifically for trees |
| `spread` | tries to use all the viewport space |
| `even-parent`, `cosmos-over-cytoscape` | compound-node and GPU-parallel layouts |

## Extensions

Register any extension on the `cytoscape` namespace:

```js
import ext from 'cy-ext';

cytoscape.use(ext);
```

Extension categories (from the curated list):

- **UI** — `context-menus`, `cxtmenu`, `edgehandles`, `expand-collapse`, `grid-guide`, `html`/`node-html-label`, `navigator`, `panzoom`, `toolbar`, `lasso`, `dom-node`, `html`, `overlays`, `popper` (Tippy.js tooltips), `mapbox-gl`/`leaflet` map backends, and more.
- **Layout** — see the table above.
- **API** — `clipboard`, `dblclick`, `graphml` (import/export), `pdf-export`, `undo-redo`, `view-utilities`, `all-paths`, `layout-utilities`.
- **Utility packages** — `cytosnap` (server-side graph images on Node.js via Puppeteer), `Cytoscape.js Schema` (JSON Schema for the JSON graph format), `RCyjs` (R), `Cyjs.NET` (F#).

First-party extensions are maintained by groups associated with the Cytoscape Consortium; third-party by outside developers.
