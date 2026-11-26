# Developers Reference

## Custom Chart Types

Extend `DatasetController` to create new chart types:

```javascript
import { DatasetController } from 'chart.js';

class MyChartController extends DatasetController {
  static id = 'myChart';
  static defaults = {
    datasetElementType: 'line',  // or null
    dataElementType: 'point'     // or null
  };

  update(mode) {
    // Update elements based on new data
    const { dataset } = this.getMeta();
    // ... update logic
  }

  draw() {
    // Draw the dataset
    super.draw();
  }
}

Chart.register(MyChartController);

// Use it
new Chart(ctx, { type: 'myChart', data: { /* ... */ } });
```

## Custom Scales

Extend a built-in scale:

```javascript
import { Scale } from 'chart.js';

class MyScale extends Scale {
  static id = 'myscale';
  static defaults = {
    position: 'bottom'
  };

  determineDataLimits() {
    // Calculate min/max from data
  }

  buildTicks() {
    // Generate tick values
  }

  getLabelForValue(value) {
    // Format value for display
    return value.toString();
  }

  getPixelForValue(value) {
    // Convert data value to pixel
    return this.left + (value / this.max) * this.width;
  }

  getValueForPixel(pixel) {
    // Convert pixel to data value
    return ((pixel - this.left) / this.width) * this.max;
  }
}

Chart.register(MyScale);
```

## Custom Elements

Create custom drawing elements:

```javascript
import { Element } from 'chart.js';

class MyElement extends Element {
  static id = 'myElement';
  static defaults = {
    backgroundColor: 'red',
    borderColor: 'black',
    borderWidth: 1
  };

  draw(ctx) {
    const { x, y, options } = this;
    ctx.save();
    ctx.fillStyle = options.backgroundColor;
    ctx.strokeStyle = options.borderColor;
    ctx.lineWidth = options.borderWidth;
    // Draw custom shape
    ctx.beginPath();
    ctx.arc(x, y, 10, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();
    ctx.restore();
  }

  inRange(mouseX, mouseY) {
    return Math.hypot(mouseX - this.x, mouseY - this.y) <= 10;
  }

  inXRange(mouseX) {
    return Math.abs(mouseX - this.x) <= 10;
  }

  inYRange(mouseY) {
    return Math.abs(mouseY - this.y) <= 10;
  }

  getCenterPoint() {
    return { x: this.x, y: this.y };
  }

  tooltipPosition() {
    return { x: this.x, y: this.y };
  }
}

Chart.register(MyElement);
```

## Extending Built-in Types

Replace a built-in controller:

```javascript
import { BarController } from 'chart.js';

class MyBarController extends BarController {
  update(mode) {
    // Custom update logic
    super.update(mode);
  }

  draw() {
    // Custom draw logic
    super.draw();
  }
}

// Replace bar controller
Chart.register(MyBarController);
```

## Plugin Hooks

Full list of plugin hooks in order:

| Hook | Timing |
|---|---|
| `beforeInit` | Before chart initialization |
| `afterInit` | After chart initialization |
| `beforeUpdate` | Before chart update |
| `afterUpdate` | After chart update |
| `beforeLayout` | Before layout calculation |
| `afterLayout` | After layout calculation |
| `beforeRender` | Before rendering |
| `afterRender` | After rendering |
| `beforeDraw` | Before drawing chart |
| `beforeDatasetsDraw` | Before drawing datasets |
| `beforeDatasetDraw` | Before drawing a dataset |
| `afterDatasetDraw` | After drawing a dataset |
| `afterDatasetsDraw` | After drawing datasets |
| `afterDraw` | After drawing chart |
| `beforeResize` | Before resize |
| `afterResize` | After resize |
| `beforeEvent` | Before processing event |
| `afterEvent` | After processing event |
| `destroy` | When chart is destroyed |

## Tree Shaking

Import only what you need to minimize bundle size:

```javascript
import {
  Chart,
  BarController,
  BarElement,
  CategoryScale,
  LinearScale,
  Legend,
  Tooltip,
  Title
} from 'chart.js';

Chart.register(
  BarController,
  BarElement,
  CategoryScale,
  LinearScale,
  Legend,
  Tooltip,
  Title
);
```

## Helpers

Access `Chart.helpers` for utility functions:

| Helper | Description |
|---|---|
| `helpers.color(value)` | Parse/create color |
| `helpers.clone(source)` | Deep clone object |
| `helpers.merge(target, sources, merger)` | Deep merge objects |
| `helpers.each(loopable, callback, self)` | Iterate array/object |
| `helpers.callback(fn, args, self)` | Safely call callback |
| `helpers.isArray(value)` | Check if array |
| `helpers.isObject(value)` | Check if object |
| `helpers.isNullOrUndef(value)` | Check null/undefined |
| `helpers.valueOrDefault(value, defaultValue)` | Return value or default |
| `helpers.resolveObjectKey(obj, key)` | Resolve nested key |
| `helpers.isArraySorted(array)` | Check if sorted |
| `helpers.toFont(obj)` | Create font spec |
| `helpers.toPadding(obj)` | Create padding object |

## Registration

```javascript
// Register
Chart.register(BarController, BarElement, CategoryScale);

// Unregister
Chart.unregister(BarController);

// Check if registered
Chart.registry.getController('bar');
Chart.registry.getScale('category');
Chart.registry.getPlugin('legend');
```
