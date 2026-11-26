# Algorithms and performance

## Graph algorithms

Available on collections (see the individual doc pages on the website for options):

- **Search** — `breadthFirstSearch`, `depthFirstSearch`
- **Shortest path / routing** — `aStar`, `bellmanFord`, `dijkstra`, `floydWarshall`
- **Centrality** — `pageRank`, `betweennessCentrality`, `closenessCentrality` (+ `closenessCentralityNormalized`), `degreeCentrality` (+ `degreeCentralityNormalized`)
- **Clustering** — `affinityPropagation`

Use cases from the docs: traversal, connectivity analysis, centrality ranking of nodes, path computation.

## Performance tuning checklist

From the official performance page, in descending order of significance:

1. **Use `cy.getElementById()`** — a lookup-table hit, faster than selector search (`cy.$id('foo')` is the shorthand; the single-ID selector `cy.$('#foo')` is also optimised but pays selector-parse cost).
2. **Batch element modifications** — `cy.batch()` for many changes at once.
3. **Animations** — none is fastest; `eles.flashClass()` is cheaper than smooth animation; limit concurrent animating elements; define `transition-property` only in the states you actually animate.
4. **Function style property values** — expensive; memoize them, or use `data()`/`mapData()` mappings instead.
5. **Labels** — expensive to draw. Drop them or show on tap/mouseover; avoid edge labels; set `min-zoomed-font-size` so tiny labels aren't rendered; label backgrounds and outlines cost more.
6. **Simplify edge style** — `curve-style: haystack` (straight lines) is the default and much cheaper than `bezier`; solid edges beat dotted/dashed; arrows are expensive when semantically meaningless; opaque edges with arrows render more than twice as fast as semitransparent ones.
7. **Simplify node style** — background images are very expensive (prefer non-repeating, non-clipped; preclip or use transparent PNGs); node borders are slightly expensive.
8. **Avoid compound and edge selectors** — e.g. `$node node`, `$node -> node` require traversals.
9. **Lower pixel ratio** — `pixelRatio: 1` on high-density displays (less crisp).
10. **Compound nodes** — make style calculation and rendering more expensive; avoid if unused.
11. **Hide edges during interactivity** — `hideEdgesOnViewport: true` (very large graphs only).
12. **Recycle large instances** — keeps memory lower than repeated `cy.destroy()` (canvas-heavy).
13. **Avoid many node overlays** — overlays can't be cached; limit simultaneous non-zero `overlay-opacity` nodes.
14. **Textured zoom & pan** — `textureOnViewport: true` (absolute cheapest option for very large graphs); `motionBlur`/`motionBlurOpacity` smooth frame transitions.

Renderer init options that affect performance (from the API reference): `styleEnabled` (default true; disable in headless), `hideEdgesOnViewport`, `hideLabelsOnViewport`, `textureOnViewport`, `motionBlur`, `motionBlurOpacity`, `wheelSensitivity`, `pixelRatio` (number or `'auto'`), `webgl` (experimental WebGL mode), `webglDebug`, `webglTexSize`.

Background facts: rendering cost scales with element count, edge count (bezier multigraphs worst), and canvas area (pixel ratio); edges are particularly expensive.
