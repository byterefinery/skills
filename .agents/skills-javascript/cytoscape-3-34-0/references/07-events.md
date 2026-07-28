# Events

Cytoscape.js has a jQuery/React-like event system. Events bubble from elements to compound parents to the core.

## Event Object

```js
{
  cy: cy,                   // core instance
  target: ele,              // originator (element or core)
  type: 'tap',              // event type string
  namespace: 'foo',         // namespace (e.g. 'foo' for 'tap.foo')
  timeStamp: 1234567890,    // Unix epoch ms

  // User input events only:
  position: { x: 100, y: 100 },       // model position
  renderedPosition: { x: 200, y: 150 }, // rendered position
  originalEvent: MouseEvent              // native event

  // Layout events only:
  layout: layoutInstance
}
```

## Event Bubbling

Events bubble: element → compound parent → core. On the core, check `event.target` to distinguish background events from element events:

```js
cy.on('tap', (e) => {
  if (e.target === cy) {
    // tapped on background
  } else {
    // tapped on element e.target
  }
});
```

## Binding Events

```js
// On core
cy.on('tap', (e) => { /* ... */ });
cy.on('tap zoom pan', (e) => { /* ... */ }); // multiple types
cy.on('tap.namespace', (e) => { /* ... */ }); // namespaced

// On collections
cy.nodes().on('tap', (e) => { /* ... */ });
cy.$('#a').on('grab drag free', (e) => { /* ... */ });

// One-time
cy.one('ready', (e) => { /* ... */ });

// Promise-based
cy.promiseOn('ready').then(() => { /* ... */ });
cy.promiseOn('layoutstop').then(() => { /* ... */ });

// Unbind
cy.off();                    // all listeners
cy.off('tap');               // specific type
cy.off('tap.namespace');     // namespaced
cy.removeListener(fn);       // specific function
```

## User Input Device Events

### Raw Browser Events

```
mousedown, mouseup, click
mouseover, mouseout, mousemove
touchstart, touchmove, touchend
```

### Normalised Events (unified mouse/touch)

```
tapstart (vmousedown)   — tap start
tapdrag (vmousemove)    — drag/move
tapdragover             — over element during drag
tapdragout              — off element during drag
tapend (vmouseup)       — tap end
tap (vclick)            — tap/click
onetap (oneclick)       — single tap (debounced to distinguish from dbltap)
dbltap (dblclick)       — double tap
taphold                 — long press
```

### Right-Click / Context

```
cxttapstart  — right-click mousedown or two-finger tapstart
cxttapend    — right-click mouseup or two-finger tapend
cxttap       — right-click or two-finger tap
cxtdrag      — mousemove or two-finger drag after cxttapstart
cxtdragover  — over node via cxtdrag
cxtdragout   — off node via cxtdrag
```

### Box Selection

```
boxstart   — box selection started
boxend     — box selection ended
boxselect  — triggered on elements selected by box
box        — triggered on elements inside box on boxend
```

## Collection Events

```
add         — element added to graph
remove      — element removed from graph
move        — topology change (parent/source/target changed)
select      — element selected
unselect    — element unselected
tapselect   — selected by tap gesture
tapunselect — unselected by tap elsewhere
boxselect   — selected by box selection
box         — inside box on boxend
lock        — element locked
unlock      — element unlocked
grabon      — grabbed directly (one node under cursor)
grab        — grabbed (including all dragged elements)
drag        — grabbed and moved
free        — let go (freed)
freeon      — freed directly
dragfree    — freed after being dragged
dragfreeon  — freed directly after being dragged
position    — position changed
data        — data changed
scratch     — scratchpad data changed
style       — style changed
background  — background image loaded
```

## Graph Events (on core)

```
layoutstart   — layout started
layoutready   — layout set initial positions
layoutstop    — layout finished
ready         — instance ready for interaction
destroy       — instance destroyed
render        — viewport rendered
pan           — viewport panned
dragpan       — panned via dragging
zoom          — viewport zoomed
pinchzoom     — zoomed via pinch gesture
scrollzoom    — zoomed via scroll wheel
viewport      — viewport changed (pan, zoom, or both)
resize        — viewport resized
```

## Emitting Custom Events

```js
// Emit from core
cy.emit('myevent', [arg1, arg2]);

// Emit from collection
cy.nodes().emit('myevent', [arg1, arg2]);

// Listen
cy.on('myevent', (e, arg1, arg2) => {
  console.log(arg1, arg2);
});
```

## Common Patterns

### Click on specific element

```js
cy.on('tap', 'node', (e) => {
  const node = e.target;
  console.log('tapped node:', node.id());
});

// Or on collection
cy.nodes().on('tap', (e) => {
  console.log('tapped:', e.target.id());
});
```

### Drag and drop

```js
cy.on('grab', 'node', (e) => {
  console.log('grabbed:', e.target.id());
});

cy.on('drag', 'node', (e) => {
  console.log('dragging:', e.target.id(), e.target.position());
});

cy.on('free', 'node', (e) => {
  console.log('dropped:', e.target.id(), e.target.position());
});
```

### Layout completion

```js
cy.layout({ name: 'cose' })
  .on('layoutstop', () => {
    cy.fit();
  })
  .run();
```

### Debounced viewport change

```js
let timeout;
cy.on('viewport', () => {
  clearTimeout(timeout);
  timeout = setTimeout(() => {
    console.log('viewport settled', cy.zoom(), cy.pan());
  }, 100);
});
```

## Render Events

```js
// Before render (for extensions)
cy.onRender((e) => { /* ... */ });

// After render
cy.on('render', (e) => { /* ... */ });

// Remove render listener
cy.offRender(fn);
```
