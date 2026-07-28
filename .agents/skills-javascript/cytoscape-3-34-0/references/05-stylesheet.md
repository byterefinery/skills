# Stylesheet

Cytoscape.js stylesheets follow CSS conventions. Specificity rules are ignored — the last matching selector wins.

## Format

### JSON Array (most common)

```js
style: [
  {
    selector: 'node',
    style: {
      'background-color': '#666',
      'label': 'data(id)',
      'width': 40,
      'height': 40
    }
  },
  {
    selector: 'edge',
    style: {
      'width': 2,
      'line-color': '#ccc',
      'target-arrow-color': '#ccc',
      'target-arrow-shape': 'triangle'
    }
  }
]
```

### Function Builder

```js
style: cytoscape.stylesheet()
  .selector('node')
    .style({ 'background-color': 'blue' })
  .selector('edge')
    .style({ 'width': 2 })
```

### String Format

```js
style: 'node { background-color: green; } edge { width: 2; }'
```

Trailing semicolons are mandatory between properties (except the last).

## Mappers

### data() — Direct Mapping

```js
'label': 'data(name)'
// equivalent to: ele => ele.data('name')
```

### mapData() — Linear Mapping

```js
'background-color': 'mapData(weight, 0, 100, blue, red)'
// weight 0 → blue, weight 100 → red, outside range → extremity
```

### Function Mapper

```js
'background-color': function(ele) {
  return ele.data('active') ? 'green' : 'red';
}
```

Function mappers should be pure — depend only on `ele.data()`, `ele.scratch()`, or state representable via selectors. Do not call `ele.style()` or mutate state.

## Property Types

- **Colours**: named (`red`), hex (`#ff0000`, `#f00`), RGB (`rgb(255,0,0)`), HSL (`hsl(0,100%,50%)`)
- **Lengths**: pixels (`24px`), unitless (`24` = pixels), em (`2em`)
- **Opacity**: `0` to `1`
- **Time**: `250ms`, `0.5s`
- **Angles**: radians (`3.14rad`) or degrees (`180deg`), clockwise
- **Lists**: space-separated string or JS array

## Node Body

### Shape and Size

```
width, height
shape: ellipse | triangle | round-triangle | rectangle | round-rectangle
  | bottom-round-rectangle | cut-rectangle | barrel | rhomboid | right-rhomboid
  | diamond | round-diamond | pentagon | round-pentagon | hexagon | round-hexagon
  | concave-hexagon | heptagon | round-heptagon | octagon | round-octagon
  | star | tag | round-tag | vee | polygon
shape-polygon-points: [-1,1, 1,1, 0,-1]  // for polygon shape
corner-radius: 5px                        // for round-* shapes
```

Only `*rectangle` shapes are supported for compound parents.

### Background

```
background-color: #666
background-blacken: 0.2        // 0-1 darkens, 0 to -1 whitens
background-opacity: 1
background-fill: solid | linear-gradient | radial-gradient
```

### Gradients

```
background-gradient-stop-colors: cyan magenta yellow
background-gradient-stop-positions: 0% 50% 100%
background-gradient-direction: to-bottom | to-top | to-left | to-right
  | to-bottom-right | to-bottom-left | to-top-right | to-top-left
```

### Border

```
border-width: 2px
border-color: #333
border-opacity: 1
border-style: solid | dotted | dashed | double
border-cap: butt | round | square
border-join: miter | bevel | round
border-dash-pattern: [6, 3]
border-dash-offset: 24
border-position: center | inside | outside
```

### Outline

```
outline-width: 2px
outline-color: #333
outline-opacity: 1
outline-style: solid | dotted | dashed | double
outline-offset: 5px
```

### Padding

```
padding: 10px | 50%
padding-relative-to: width | height | average | min | max
```

### Compound Parent Sizing

```
compound-sizing-wrt-labels: include | exclude
min-width: 400px
min-width-bias-left: 50%
min-width-bias-right: 50%
min-height: 300px
min-height-bias-top: 50%
min-height-bias-bottom: 50%
```

## Background Image

```
background-image: url | data URI
background-image-crossorigin: anonymous | use-credentials | null
background-image-opacity: 1
background-image-smoothing: yes | no
background-image-containment: inside | over
background-width: auto | 50% | 100px
background-height: auto | 50% | 100px
background-fit: none | contain | cover
background-repeat: no-repeat | repeat-x | repeat-y | repeat
background-position-x: 50% | 10px
background-position-y: 50% | 10px
background-offset-x: 0px
background-offset-y: 0px
background-clip: node | none
bounds-expansion: 20px              // expand bounding box for overflow
```

Multiple images: `['url1', 'url2']` with paired properties like `'contain cover'`.

## Pie Chart Background

```
pie-size: 100% | 25px
pie-start-angle: 0deg
pie-hole: 0%                        // 0 = pie, >0 = ring chart
pie-1-background-color: red
pie-1-background-size: 25%
pie-1-background-opacity: 1
// ... up to pie-16
```

## Stripe Chart Background

```
stripe-size: 100%
stripe-direction: vertical | horizontal
stripe-1-background-color: red
stripe-1-background-size: 25%
// ... up to stripe-16
```

## Edge Line

```
width: 2
curve-style: haystack | straight | straight-triangle | bezier
  | unbundled-bezier | segments | round-segments | taxi | round-taxi
line-color: #ccc
line-style: solid | dotted | dashed
line-cap: butt | round | square
line-outline-width: 1px
line-outline-color: #999
line-opacity: 1
line-fill: solid | linear-gradient | radial-gradient
line-dash-pattern: [6, 3]
line-dash-offset: 24
box-selection: contain | overlap | none
```

### Gradient

```
line-gradient-stop-colors: cyan magenta yellow
line-gradient-stop-positions: 0% 50% 100%
```

### Bezier Edges

```
control-point-step-size: 50
control-point-distance: 100
control-point-weight: 0.5
edge-distances: intersection | node-position | endpoints
source-endpoint: outside-to-node | 20 10 | 90deg
target-endpoint: outside-to-node | 20 10 | 90deg
```

### Loop Edges

```
loop-direction: -45deg
loop-sweep: -90deg
```

### Haystack Edges

```
haystack-radius: 0  // 0 = centre, 1 = outside of node
```

### Segments / Round-Segments

```
segment-distances: -20 20 -20
segment-weights: 0.25 0.5 0.75
segment-radii: 15 0 5             // round-segments only
radius-type: arc-radius | influence-radius
```

### Taxi / Round-Taxi

```
taxi-direction: auto | vertical | downward | upward | horizontal | rightward | leftward
taxi-turn: 50% | 20px
taxi-turn-min-distance: 5px
taxi-radius: 5px                  // round-taxi only
radius-type: arc-radius | influence-radius
edge-distances: intersection | node-position
```

### Edge Arrows

```
source-arrow-color: #ccc
source-arrow-shape: triangle | triangle-tee | circle-triangle | triangle-cross
  | triangle-backcurve | vee | tee | square | circle | diamond | chevron | none
source-arrow-fill: filled | hollow
source-arrow-width: match-line | 2 | 2px | 50%
arrow-scale: 1

// Positions: source, mid-source, target, mid-target
// E.g.: target-arrow-shape, mid-source-arrow-color
```

Haystack edges only support mid arrows.

### Edge Endpoints

```
source-endpoint: outside-to-node | outside-to-node-or-label | inside-to-node
  | outside-to-line | outside-to-line-or-label | 50% 50% | 100px 50px | 90deg
target-endpoint: outside-to-node
source-distance-from-node: 0px
target-distance-from-node: 0px
```

## Visibility

```
display: element | none           // none = not drawn, not interactive, no space
visibility: visible | hidden      // hidden = drawn but not interactive, takes space
opacity: 0 to 1                   // 0 = invisible but interactive and takes space
```

## Z-Ordering

```
z-index: 0                        // floating point, higher = drawn on top
z-compound-depth: bottom | orphan | auto | top
z-index-compare: auto | manual    // auto = edges under nodes; manual = z-index only
```

## Labels

### Text

```
label: data(name)
source-label: data(sourceLabel)   // edge source label
target-label: data(targetLabel)   // edge target label
```

### Font

```
color: #333
text-opacity: 1
font-family: Arial, sans-serif
font-size: 14px
font-style: normal | italic
font-weight: normal | bold
text-transform: none | uppercase | lowercase
```

### Wrapping

```
text-wrap: none | wrap | ellipsis
text-max-width: 200px
text-overflow-wrap: whitespace | anywhere
text-justification: left | center | right | auto
line-height: 1.5
```

### Alignment

```
text-halign: left | left-inside | center | right | right-inside  // nodes
text-valign: top | top-inside | center | bottom | bottom-inside  // nodes
source-text-offset: 10                                           // edges
target-text-offset: 10                                           // edges
```

### Margins and Rotation

```
text-margin-x: 0px
text-margin-y: 0px
text-rotation: 0deg | autorotate  // autorotate for edges
```

### Outline and Background

```
text-outline-color: #fff
text-outline-opacity: 1
text-outline-width: 2px
text-background-color: #fff
text-background-opacity: 0       // 0 = disabled
text-background-shape: rectangle | round-rectangle | circle
text-background-padding: 5px
text-border-opacity: 0           // 0 = disabled
text-border-width: 1px
text-border-style: solid | dotted | dashed | double
text-border-color: #333
```

### Interactivity

```
min-zoomed-font-size: 12         // hide label if smaller
text-events: yes | no
box-selection: contain | overlap | none
```

## Overlay and Underlay

```
overlay-color: red
overlay-padding: 10px
overlay-opacity: 0.25
overlay-shape: round-rectangle | ellipse

underlay-color: yellow
underlay-padding: 10px
underlay-opacity: 0.25
underlay-shape: round-rectangle | ellipse
```

## Ghost Effect

```
ghost: yes | no
ghost-offset-x: 2px
ghost-offset-y: 2px
ghost-opacity: 0.5
```

## Transitions

```
transition-property: background-color width
transition-duration: 0.5s
transition-delay: 250ms
transition-timing-function: linear | ease | ease-in | ease-out | ease-in-out
  | ease-in-sine | ease-out-sine | ease-in-quad | ease-out-cubic
  | spring(tension, friction)
  | cubic-bezier(x1, y1, x2, y2)
```

## Core Styles

Apply to `core` selector:

```js
{
  selector: 'core',
  style: {
    'active-bg-color': '#ccc',
    'active-bg-opacity': 0.33,
    'active-bg-size': 150,
    'selection-box-color': '#9999ff',
    'selection-box-border-color': '#9999ff',
    'selection-box-border-width': 3px,
    'selection-box-opacity': 0.33,
    'outside-texture-bg-color': '#000',
    'outside-texture-bg-opacity': 0.25
  }
}
```

## Events Style

```
events: yes | no          // whether element receives events
text-events: yes | no     // whether label receives events
box-selection: contain | overlap | none
```
