# Animation

Cytoscape.js supports animating element positions, styles, and the viewport.

## Element Animation

### Animate Method

```js
ele.animate({
  style: {
    'background-color': 'red',
    'width': 100,
    'height': 100
  },
  position: { x: 200, y: 300 },
  renderPosition: { x: 100, y: 100 }, // animate in rendered coords

  // Options
  duration: 500,              // ms
  easing: 'ease-in-out',      // easing function
  queue: true,                // queue if another animation is running
  complete: () => {},         // callback on completion
  progress: (ele, progress, remainingDuration) => {}, // per-step callback
  step: (ele, progress, remainingDuration) => {}       // alias
});
```

### Animation Object

```js
const ani = ele.animation({
  style: { 'background-color': 'red' },
  position: { x: 200, y: 300 },
  duration: 500,
  easing: 'ease-in-out'
});

ani.start();   // start
ani.stop();    // stop
ani.pause();   // pause
ani.resume();  // resume
ani.reverse(); // reverse direction
ani.completed; // boolean: is complete?
```

### Core Animation

```js
// Animate viewport
cy.animate({
  zoom: 2,
  pan: { x: 100, y: 50 },
  duration: 500,
  easing: 'ease-in-out',
  complete: () => {}
});
```

## Easing Functions

### Built-in Easings

```
linear
ease, ease-in, ease-out, ease-in-out
ease-in-sine, ease-out-sine, ease-in-out-sine
ease-in-quad, ease-out-quad, ease-in-out-quad
ease-in-cubic, ease-out-cubic, ease-in-out-cubic
ease-in-quart, ease-out-quart, ease-in-out-quart
ease-in-quint, ease-out-quint, ease-in-out-quint
ease-in-expo, ease-out-expo, ease-in-out-expo
ease-in-circ, ease-out-circ, ease-in-out-circ
```

### Custom Easings

```js
// Spring
'spring( tension, friction )'
// e.g. 'spring( 250, 20 )'

// Cubic bezier
'cubic-bezier( x1, y1, x2, y2 )'
// e.g. 'cubic-bezier( 0.42, 0, 0.58, 1 )'
```

## Queues

```js
// Queue animations
ele.animate({ style: { 'background-color': 'red' }, queue: true });
ele.animate({ style: { 'width': 100 }, queue: true });
// Second runs after first completes

// Clear queue
ele.clearQueue();
cy.clearQueue();
```

## Delay

```js
// Delay before next animation
ele.delay(500);
ele.animate({ style: { 'background-color': 'red' } });
// Animation starts 500ms later

// Delay as animation
const delayAni = ele.delayAnimation(500);
delayAni.start();
delayAni.stop();
```

## Stop

```js
// Stop all animations
ele.stop();
cy.stop();

// Stop and jump to end
ele.stop(true);
```

## Check Animation State

```js
ele.animated();  // true if currently animating
```

## Style Transitions

Stylesheets can define automatic transitions:

```js
{
  selector: 'node',
  style: {
    'transition-property': 'background-color width height',
    'transition-duration': '0.5s',
    'transition-delay': '250ms',
    'transition-timing-function': 'ease-in-out'
  }
}
```

When a node's style changes (via class change or stylesheet update), the specified properties animate automatically.

## Common Patterns

### Smooth zoom to element

```js
cy.animate({
  spell: [
    { zoom: ele.renderedPosition() },
    { pan: ele.renderedPosition() }
  ],
  duration: 500,
  easing: 'ease-in-out'
});

// Or simpler:
cy.fit(ele, 30);
cy.center(ele);
```

### Pulse effect

```js
function pulse(ele) {
  ele.animate({
    style: { 'width': ele.width() * 1.2, 'height': ele.height() * 1.2 },
    duration: 200,
    easing: 'ease-in-out',
    complete: () => {
      ele.animate({
        style: { 'width': ele.width() * 0.8 / 1.2, 'height': ele.height() * 0.8 / 1.2 },
        duration: 200,
        easing: 'ease-in-out',
        complete: () => pulse(ele) // repeat
      });
    }
  });
}
```

### Sequential highlight

```js
const nodes = cy.nodes();
nodes.forEach((node, i) => {
  node.delay(i * 100).animate({
    style: { 'background-color': 'yellow' },
    duration: 200,
    complete: () => {
      node.animate({
        style: { 'background-color': '#666' },
        duration: 200
      });
    }
  });
});
```

### Animate along path

```js
const positions = [
  { x: 0, y: 0 },
  { x: 100, y: 50 },
  { x: 200, y: 0 }
];

let i = 0;
function nextPos() {
  if (i >= positions.length) return;
  node.animate({
    position: positions[i],
    duration: 300,
    easing: 'ease-in-out',
    complete: () => { i++; nextPos(); }
  });
}
nextPos();
```

## Performance Notes

- Animating many elements simultaneously can impact performance
- Use `cy.notifications(false)` during bulk animation setup
- `textureOnViewport: true` in init options improves rendering during viewport gestures
- For layout animations, use `animate: 'end'` to avoid continuous animation overhead
