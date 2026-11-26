# Extensions

Cytoscape.js is fully extensible. Extensions register via `cytoscape.use()` or `cytoscape(type, name, impl)`.

## Registration

### Using cytoscape.use()

```js
import cytoscape from 'cytoscape';
import extension from 'cytoscape-extension';

cytoscape.use(extension);
cytoscape.use(extension, arg1, arg2); // with arguments
```

The extension's default export is a function receiving `(cytoscape, ...args)`.

### Direct Registration

```js
// Core function
cytoscape('core', 'myFn', function() { /* ... */ });
cy.myFn();

// Collection function
cytoscape('collection', 'myFn', function() { /* ... */ });
cy.nodes().myFn();

// Layout
cytoscape('layout', 'myLayout', MyLayoutClass);
cy.layout({ name: 'myLayout' }).run();
```

## Extension Template

```js
// my-extension.js
export default function register(cytoscape) {
  cytoscape('collection', 'myExtensionFn', function() {
    return 'result';
  });
}

// Auto-register for script tag usage
if (typeof window !== 'undefined' && window.cytoscape) {
  register(window.cytoscape);
}
```

## Layout Prototype

Layout extensions implement a constructor and `run()` method:

```js
function MyLayout(options) {
  this.options = Object.assign({}, defaults, options);
}

MyLayout.prototype.run = function() {
  const { eles } = this.options;

  // Calculate positions
  const positions = {};
  eles.nodes().forEach((node, i) => {
    positions[node.id()] = { x: i * 50, y: 0 };
  });

  // Apply positions
  eles.layoutPositions((ele, i, oldPosition) => {
    return positions[ele.id()];
  });

  return this; // chaining
};

export default MyLayout;
```

### Continuous Layouts

Force-directed layouts run over multiple iterations:

```js
MyLayout.prototype.run = function() {
  const { eles, ready, stop } = this.options;

  ready && ready.call(this);

  let iteration = 0;
  const maxIter = 1000;

  function step() {
    if (iteration >= maxIter) {
      stop && stop.call(this);
      return;
    }

    // Calculate new positions
    // ...

    // Apply to nodes each visible iteration
    eles.nodes().positions((node) => ({ x: /* ... */, y: /* ... */ }));

    iteration++;
    requestAnimationFrame(step);
  }

  step();
  return this;
};
```

## Extension Ecosystem

### Layout Extensions

| Extension | Description |
|---|---|
| `cytoscape-cola` | Cola.js physics, beautiful results for small graphs |
| `cytoscape-fcose` | Fast CoSE — best force-directed, supports compounds |
| `cytoscape-cose-bilkent` | Enhanced CoSE, near-perfect results |
| `cytoscape-dagre` | DAG/tree hierarchical layout |
| `cytoscape-euler` | Fast, small, high-quality force-directed |
| `cytoscape-klay` | General-purpose, handles DAGs and compounds |
| `cytoscape-elk` | ELK adapter, multiple algorithms |
| `cytoscape-spread` | Uses all viewport space |
| `cytoscape-avsdf` | Circular, minimises edge crossings |
| `cytoscape-cise` | Circular clusters with physics |
| `cytoscape-springy` | Basic force-directed |
| `cytoscape-d3-force` | D3 force layout |

### UI Extensions

| Extension | Description |
|---|---|
| `cytoscape-panzoom` | Pan/zoom control widget |
| `cytoscape-navigator` | Bird's eye view minimap |
| `cytoscape-edgehandles` | UI for connecting nodes with edges |
| `cytoscape-context-menus` | Right-click context menus |
| `cytoscape-cxtmenu` | Circular context menu |
| `cytoscape-popover` | Popper.js wrapper for tooltips |
| `cytoscape-qtip` | qTip wrapper for tooltips |
| `cytoscape-node-resize` | Node resizing UI |
| `cytoscape-expand-collapse` | Expand/collapse compound nodes |
| `cytoscape-autopan-on-drag` | Auto-pan when dragging nodes out of viewport |
| `cytoscape-automove` | Constrain/sync node movements |
| `cytoscape-grid-guide` | Grid and snapping |
| `cytoscape-compound-drag-and-drop` | Compound node drag-and-drop |
| `cytoscape-edge-editing` | Edit edge bends |
| `cytoscape-leaflet` | Leaflet map underneath |
| `cytoscape-toolbar` | Custom toolbar widget |
| `cytoscape-dom-node` | HTML elements as node bodies |
| `cytoscape-lasso` | Lasso selection |

### API Extensions

| Extension | Description |
|---|---|
| `cytoscape-graphml` | GraphML import/export |
| `cytoscape-clipboard` | Copy/paste utilities |
| `cytoscape-undo-redo` | Undo/redo API |
| `cytoscape-pdf-export` | PDF export |
| `cytoscape-view-utilities` | Search and highlight APIs |
| `cytoscape-layout-utilities` | Layout placement utilities |
| `cytoscape-all-paths` | All longest directed paths |

### Framework Integrations

| Extension | Framework |
|---|---|
| `react-cytoscapejs` | React |
| `vue-cytoscape` | Vue |
| `ngx-cytoscape` | Angular |

### Utility Packages

| Extension | Description |
|---|---|
| `cytosnap` | Server-side rendering (Puppeteer) |
| `cytoscape-sbgn-stylesheet` | SBGN stylesheet preset |
| `cytoscape-sbgnml-to-cytoscape` | SBGNML → Cytoscape JSON |
| `cytoscape-pptx` | Export to PowerPoint |

## Installing Extensions

```bash
npm install cytoscape-fcose
```

```js
import cytoscape from 'cytoscape';
import fcose from 'cytoscape-fcose';

cytoscape.use(fcose);

// Now available
cy.layout({ name: 'fcose' }).run();
```

## CDN Usage

```html
<script src="cytoscape.min.js"></script>
<script src="cytoscape-fcose.min.js"></script>
<!-- Auto-registers if window.cytoscape exists -->
```
