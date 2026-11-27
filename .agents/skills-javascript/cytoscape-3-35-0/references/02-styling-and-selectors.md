# Styling and selectors

## Style

Style follows CSS conventions as closely as possible — properties usually share names and behaviour with their CSS namesakes, plus Cytoscape-specific extras. **CSS specificity rules are completely ignored: for a given property on a given element, the last matching selector wins.**

### Formats

The `style` init option (or `cy.style()`) accepts three formats:

**Plain JSON** (most common):

```js
style: [
  { selector: 'node', style: { 'background-color': 'red' } }
]
```

**String** (e.g. loaded from a server) — trailing semicolons on every property except the last are **mandatory**; parsing fails without them:

```js
style: 'node { background-color: green; }'
```

**Function** (stylesheet builder):

```js
style: cytoscape.stylesheet()
  .selector('node')
    .style({ 'background-color': 'blue' })
```

`css` can be used in place of `style` (`.selector(...).css(...)` or `{ selector: ..., css: ... }`).

### Function values

A style property value can be a function, evaluated per element:

```js
style: {
  selector: 'node',
  style: {
    'background-color': function( ele ){ return ele.data('bg') }
    // equivalent to: 'background-color': 'data(bg)'
  }
}
```

Caveats: function values may be expensive (memoize them); a stylesheet with function values cannot be serialised to JSON; the function must not read other style values and must not mutate element or graph state — depend only on `ele.data()`, `ele.scratch()`, `cy.data()`, `cy.scratch()`.

### Mappers

String mappers map data onto style values declaratively:

```js
// data() — direct mapping
'label': 'data(name)'
// equivalent to: ele => ele.data('name')

// mapData() — linear mapping between ranges
'background-color': 'mapData(weight, 0, 100, blue, red)'
// weight 0 → blue, weight 100 → red, outside range → extremity
```

### Property types

- **Colours**: named (`red`), hex (`#ff0000`, `#f00`), RGB (`rgb(255,0,0)`), HSL (`hsl(0,100%,50%)`)
- **Lengths**: pixels (`24px`), unitless (`24` = pixels), em (`2em`)
- **Opacity**: `0` to `1`
- **Time**: `250ms`, `0.5s`
- **Angles**: radians (`3.14rad`) or degrees (`180deg`), clockwise
- **Lists**: space-separated string or JS array

### Key style properties

**Node body**

```
width, height
shape: ellipse | triangle | round-triangle | rectangle | round-rectangle
  | bottom-round-rectangle | cut-rectangle | barrel | rhomboid | right-rhomboid
  | diamond | round-diamond | pentagon | round-pentagon | hexagon | round-hexagon
  | concave-hexagon | heptagon | round-heptagon | octagon | round-octagon
  | star | tag | round-tag | vee | polygon
shape-polygon-points: [-1,1, 1,1, 0,-1]   // for polygon shape
corner-radius: 5px                        // for round-* shapes
background-color, background-blacken, background-opacity
background-fill: solid | linear-gradient | radial-gradient
border-width | border-color | border-opacity | border-style | border-cap
  | border-join | border-dash-pattern | border-dash-offset | border-position
outline-width | outline-color | outline-opacity | outline-style | outline-offset
padding: 10px | 50%
padding-relative-to: width | height | average | min | max
compound-sizing-wrt-labels: include | exclude   // compound parents
min-width | min-height (+ bias-* properties)
```

Only `*rectangle` shapes are supported for compound parents.

**Background image and charts**

```
background-image | background-image-opacity | background-image-smoothing
background-image-containment: inside | over
background-width | background-height | background-fit: none | contain | cover
background-repeat | background-position-x | background-position-y
background-clip: node | none
pie-size | pie-start-angle | pie-hole | pie-1-background-color | pie-1-background-size  (up to pie-16)
stripe-size | stripe-direction | stripe-1-background-color | stripe-1-background-size  (up to stripe-16)
```

**Edge line**

```
width: 2
curve-style: haystack | straight | straight-triangle | bezier
  | unbundled-bezier | segments | round-segments | taxi | round-taxi
line-color | line-style: solid | dotted | dashed | line-cap
line-outline-width | line-outline-color | line-opacity
line-fill: solid | linear-gradient | radial-gradient
line-dash-pattern: [6, 3] | line-dash-offset: 24
box-selection: contain | overlap | none

// Bezier edges
control-point-step-size: 50 | control-point-distance: 100 | control-point-weight: 0.5
edge-distances: intersection | node-position | endpoints
source-endpoint | target-endpoint: outside-to-node | outside-to-node-or-label
  | inside-to-node | outside-to-line | outside-to-line-or-label | 50% 50% | 100px 50px | 90deg
source-distance-from-node | target-distance-from-node

// Loop edges: loop-direction: -45deg | loop-sweep: -90deg
// Haystack: haystack-radius: 0 (centre) .. 1 (outside of node)
// Segments: segment-distances | segment-weights | segment-radii (round-segments)
// Taxi: taxi-direction | taxi-turn | taxi-turn-min-distance | taxi-radius (round-taxi)
```

**Edge arrows**

```
source-arrow-color | target-arrow-color | mid-source-arrow-color | mid-target-arrow-color
*-arrow-shape: triangle | triangle-tee | circle-triangle | triangle-cross
  | triangle-backcurve | vee | tee | square | circle | diamond | chevron | none
source-arrow-fill: filled | hollow
source-arrow-width: match-line | 2 | 2px | 50%
arrow-scale: 1
```

Haystack edges only support mid arrows.

**Visibility and z-ordering**

```
display: element | none          // none = not drawn, not interactive, no space
visibility: visible | hidden     // hidden = drawn but not interactive, takes space
opacity: 0..1                    // 0 = invisible but interactive, takes space
z-index: 0                      // floating point, higher = drawn on top
z-compound-depth: bottom | orphan | auto | top
z-index-compare: auto | manual   // auto = edges under nodes
```

**Labels**

```
label: data(name)
source-label | target-label      // edge labels
color | text-opacity | font-family | font-size | font-style | font-weight
  | text-transform: none | uppercase | lowercase
text-wrap: none | wrap | ellipsis | text-max-width: 200px
text-justification: left | center | right | auto | line-height: 1.5
text-halign: left | left-inside | center | right | right-inside    // nodes
text-valign: top | top-inside | center | bottom | bottom-inside   // nodes
source-text-offset | target-text-offset                            // edges
text-margin-x | text-margin-y | text-rotation: 0deg | autorotate
text-outline-color | text-outline-opacity | text-outline-width
text-background-color | text-background-opacity (0 = disabled)
text-background-shape: rectangle | round-rectangle | circle
text-background-padding | text-border-opacity | text-border-width | text-border-style
min-zoomed-font-size: 12         // hide label if it would render smaller
```

**Overlay, underlay, ghost, transitions**

```
overlay-color | overlay-padding | overlay-opacity | overlay-shape: round-rectangle | ellipse
underlay-color | underlay-padding | underlay-opacity | underlay-shape
ghost: yes | no | ghost-offset-x | ghost-offset-y | ghost-opacity
transition-property: background-color width
transition-duration: 0.5s | transition-delay: 250ms
transition-timing-function: linear | ease | ease-in | ease-out | ease-in-out
  | ease-in-sine | ease-out-quad | spring(tension, friction) | cubic-bezier(x1, y1, x2, y2)
```

**Core styles** (apply to `selector: 'core'`)

```
active-bg-color | active-bg-opacity | active-bg-size
selection-box-color | selection-box-border-color | selection-box-border-width | selection-box-opacity
outside-texture-bg-color | outside-texture-bg-opacity
```

## Selectors

Selectors work like CSS selectors on DOM elements, but over graph element collections. Wherever a selector is accepted, a filter function may be used instead.

- **Group** — `node`, `edge`, `*`
- **Class** — `.foo`
- **ID** — `#foo` (same as `[id = 'foo']`)
- **Data** — `[foo]` (defined, i.e. not `undefined`; `null` counts as defined), `[^foo]` (not defined), `[?foo]` (truthy), `[!foo]` (falsey), `[foo = 'bar']`, `[foo != 2]`, `[num > 2]`, `[num >= 2]`, `[num < 2]`, `[num <= 2]`
- **Comma** joins selectors (logical OR): `cy.elements('node#j, edge[source = "j"]')`
- **Compound** (adjacency): e.g. `$node -> node` edge selectors, `$node node` compound selectors — powerful but expensive (traversals required)
- **Dot-notation** into nested data: `node[name.first = "Jerry"]`, `node[labels.0 = "Person"]`

### Data operators

```
[name *= value]   — contains substring
[name ^= value]   — starts with
[name $= value]   — ends with

Operators combine with @ (case insensitive, e.g. [name @$= "ry"])
and ! (negate, e.g. [name !$= "ry"])
```

### Metadata brackets

```
[[degree > 2]]       — matches by degree
[[indegree > 1]]     — matches by in-degree
[[outdegree > 1]]    — matches by out-degree
```

### Compound node selectors

```
parent > child    — direct children (child selector)
parent child      — all descendants (descendant selector, space-separated)
$parent > child   — selects parent nodes instead of children (subject selector)
```

### State pseudo-classes

```
:animated | :unanimated
:selected | :unselected | :selectable | :unselectable
:locked | :unlocked
:visible | :hidden | :transparent
:backgrounding | :nonbackgrounding
:grabbed | :free | :grabbable | :ungrabbable | :active | :inactive | :touch
:removed | :inside
:parent | :childless | :child | :orphan | :compound
:loop | :simple
```

### Selector examples

```js
cy.$('node');                           // all nodes
cy.$('node#foo');                       // node with id 'foo'
cy.$('.active');                        // elements with class 'active'
cy.$('[weight > 50]');                  // high-weight elements
cy.$('[name = "Alice"]');               // string match
cy.$('[labels.0 = "Person"]');          // array element
cy.$('[name.first = "John"]');          // nested object
cy.$(':selected');                      // selected elements
cy.$(':visible');                       // visible elements
cy.$('node > node');                    // direct children
cy.$('node node');                      // all descendants
cy.$('$node > node');                   // parent nodes
cy.$('#a, #b, #c');                    // multiple IDs
cy.$('node[weight > 50]:visible');      // combined conditions
cy.$('[[degree > 2]]');                // metadata
```

### Selector performance

- ID selectors (`#id`) are O(1) — use them when you know the ID; `cy.getElementById('id')` is still fastest by-ID access.
- Data attribute selectors scan all elements — consider caching results.
- State pseudo-classes are fast (check internal flags).
- Nested/compound selectors traverse the hierarchy — avoid them in hot paths.
- For repeated queries, cache the resulting collection rather than re-querying.

Rules and traps:

- String values must be quoted: `node[name = "Jerry"]` works, `node[name = Jerry]` does not.
- Special characters in IDs/field names need escaping: `#some\$funky\@id`. Characters that need escaping include `( ^ $ \ / ( ) | ? + * [ ] { } , . )`. Prefer alphanumeric IDs, or a data selector (`[id = "some$funky@id"]`) when you must use special characters.
- `cy.$('#id')` (single ID selector) is optimised to use the ID lookup table; `cy.getElementById('id')` is still the fastest by-ID access.
