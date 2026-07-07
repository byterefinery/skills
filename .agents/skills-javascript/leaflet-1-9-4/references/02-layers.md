# Layers

## Layer Base Class

All layers inherit from `L.Layer` (which inherits from `L.Evented`).

### Options

| Option | Default | Description |
|---|---|---|
| `pane` | `'overlayPane'` | Map pane to render in |
| `attribution` | `null` | Text for attribution control |
| `bubblingMouseEvents` | `true` | Propagate mouse events to map |

### Methods

```js
layer.addTo(map);           // Add to map or layer group
layer.remove();             // Remove from current map
layer.removeFrom(map);      // Remove from specific map
layer.getPane(name);        // Get HTMLElement of named pane
layer.getAttribution();     // → attribution string
```

### Extension Methods

When creating custom layers, implement:

```js
const CustomLayer = L.Layer.extend({
	onAdd(map) {
		// Create DOM elements, add to panes, bind events
	},
	onRemove(map) {
		// Clean up DOM, remove event listeners
	},
	getEvents() {
		// Return { event: handler } — auto-bound/unbound
		return { zoom: this._reset, viewreset: this._reset };
	},
	getAttribution() {
		return 'Custom layer';
	},
	beforeAdd(map) {
		// Called before layer is added, before events init
	}
});
```

## Interactive Layer

Abstract base for layers that respond to mouse/touch events.

### Options

| Option | Default | Description |
|---|---|---|
| `interactive` | `true` | Enable mouse/touch interaction |
| `bubblingMouseEvents` | `true` | Bubble events to map |

### Mouse Events

| Event | Data |
|---|---|
| `click` | `MouseEvent` with `latlng`, `containerPoint`, `layerPoint` |
| `dblclick` | Same |
| `mousedown` | Same |
| `mouseup` | Same |
| `mouseover` | Same |
| `mouseout` | Same |
| `mousemove` | Same |
| `contextmenu` | Same (right-click / long-press) |
| `keypress` | `KeyboardEvent` |
| `keydown` | `KeyboardEvent` |
| `keyup` | `KeyboardEvent` |

```js
layer.on('click', e => {
	e.latlng;           // LatLng of click
	e.containerPoint;   // Point relative to container
	e.layerPoint;       // Point relative to layer origin
	e.originalEvent;    // Raw DOM MouseEvent
});
```

## LayerGroup

Groups multiple layers, managing them as one unit.

```js
const group = L.layerGroup([layer1, layer2], options);
```

### Methods

```js
group.addLayer(layer);
group.removeLayer(layer);
group.hasLayer(layer);          // or by internal ID
group.clearLayers();
group.eachLayer(fn, context);
group.getLayer(id);             // → Layer (by internal ID)
group.getLayers();              // → Layer[]
group.setZIndex(zIndex);
group.getLayerId(layer);        // → Number
group.invoke(methodName, ...args); // Call method on all children
```

## FeatureGroup

Extended LayerGroup with event propagation and convenience methods.

```js
const fg = L.featureGroup([layer1, layer2]);
```

### Methods

```js
fg.setStyle(style);            // Apply style to all Path layers
fg.bringToFront();             // Bring all layers to top
fg.bringToBack();              // Send all layers to bottom
fg.getBounds();                // → LatLngBounds of all children
```

### Events

```js
// Events from child layers propagate to FeatureGroup
fg.on('click', e => {
	e.target;    // The actual child layer that was clicked
	e.latlng;
});

// Child add/remove events
fg.on('layeradd', e => console.log(e.layer));
fg.on('layerremove', e => console.log(e.layer));
```

### Popup/Tooltip Binding

Binding popup or tooltip to a FeatureGroup applies it to all children:

```js
L.featureGroup([marker1, marker2, polygon])
	.bindPopup('Hello from group')
	.bindTooltip('Hover any layer')
	.addTo(map);
```

## Popup Methods (on all Layers)

```js
layer.bindPopup(content, options);
layer.unbindPopup();
layer.openPopup(latlng);
layer.closePopup();
layer.togglePopup();
layer.isPopupOpen();           // → Boolean
layer.setPopupContent(content);
layer.getPopup();              // → Popup
```

## Tooltip Methods (on all Layers)

```js
layer.bindTooltip(content, options);
layer.unbindTooltip();
layer.openTooltip(latlng);
layer.closeTooltip();
layer.toggleTooltip();
layer.isTooltipOpen();         // → Boolean
layer.setTooltipContent(content);
layer.getTooltip();            // → Tooltip
```
