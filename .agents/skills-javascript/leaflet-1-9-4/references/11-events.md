# Events

## Evented Mixin

All Leaflet classes that emit events inherit from `L.Evented`.

### Methods

```js
// Subscribe
obj.on(type, fn, context);
obj.on({ click: fn1, mouseover: fn2 }, context);  // Multiple at once

// One-time
obj.once(type, fn, context);

// Unsubscribe
obj.off(type, fn, context);
obj.off({ click: fn1 }, context);
obj.off();  // Remove all listeners

// Fire
obj.fire(type, data, propagate);

// Check
obj.listens(type, propagate);  // → Boolean

// Event propagation
obj.addEventParent(obj);   // Forward events to parent
obj.removeEventParent(obj); // Stop forwarding
```

### Event Data

Leaflet events pass a data object with relevant properties. Map mouse events include:

```js
{
	latlng: LatLng,        // Geographic coordinates
	containerPoint: Point, // Pixel coords relative to container
	layerPoint: Point,     // Pixel coords relative to layer origin
	originalEvent: Event   // Raw DOM event
}
```

## Map Events

### State Change Events

| Event | Data | Description |
|---|---|---|
| `resize` | `{ oldSize, newSize }` | Map container resized |
| `viewprereset` | — | Before view reset |
| `viewreset` | — | View reset (redraw content) |
| `load` | — | Map initialized (center + zoom set) |
| `zoomlevelschange` | — | Min/max zoom changed |
| `unload` | — | Map destroyed |

### Interaction Events

| Event | Data | Description |
|---|---|---|
| `zoomstart` | — | Zoom starting |
| `zoomend` | — | Zoom finished |
| `zoom` | — | During zoom animation |
| `movestart` | — | View starting to change |
| `moveend` | — | View stopped changing |
| `move` | — | During movement |

### Mouse Events

| Event | Data | Description |
|---|---|---|
| `click` | `MouseEvent` | Click/tap |
| `dblclick` | `MouseEvent` | Double-click |
| `mousedown` | `MouseEvent` | Mouse button down |
| `mouseup` | `MouseEvent` | Mouse button up |
| `mouseover` | `MouseEvent` | Mouse enters map |
| `mouseout` | `MouseEvent` | Mouse leaves map |
| `mousemove` | `MouseEvent` | Mouse moving |
| `contextmenu` | `MouseEvent` | Right-click / long-press |
| `preclick` | `MouseEvent` | Before click (for closing popups) |

### Keyboard Events

| Event | Data | Description |
|---|---|---|
| `keypress` | `KeyboardEvent` | Character key pressed |
| `keydown` | `KeyboardEvent` | Any key pressed |
| `keyup` | `KeyboardEvent` | Key released |

### Location Events

| Event | Data | Description |
|---|---|---|
| `locationfound` | `LocationEvent` | Geolocation success |
| `locationerror` | `ErrorEvent` | Geolocation failure |

### Layer Events

| Event | Data | Description |
|---|---|---|
| `layeradd` | `{ layer }` | Layer added to map |
| `layerremove` | `{ layer }` | Layer removed from map |

### Popup Events

| Event | Data | Description |
|---|---|---|
| `popupopen` | `{ popup }` | Popup opened |
| `popupclose` | `{ popup }` | Popup closed |
| `autopanstart` | — | Map autopanning for popup |

### Tooltip Events

| Event | Data | Description |
|---|---|---|
| `tooltipopen` | `{ tooltip }` | Tooltip opened |
| `tooltipclose` | `{ tooltip }` | Tooltip closed |

### Layers Control Events

| Event | Data | Description |
|---|---|---|
| `baselayerchange` | `{ layer, name }` | Base layer changed |
| `overlayadd` | `{ layer, name }` | Overlay added |
| `overlayremove` | `{ layer, name }` | Overlay removed |

## Layer Events

### Lifecycle

| Event | Description |
|---|---|
| `add` | Layer added to a map |
| `remove` | Layer removed from a map |

### Marker Events

| Event | Data | Description |
|---|---|---|
| `dragstart` | — | Drag started |
| `drag` | — | During drag |
| `dragend` | — | Drag finished |
| `move` | `{ oldLatLng, latlng }` | Position changed |

### ImageOverlay Events

| Event | Description |
|---|---|
| `load` | Image loaded |
| `error` | Image failed to load |

### TileLayer Events

| Event | Data | Description |
|---|---|---|
| `tileloadstart` | `{ tile, coords }` | Tile loading started |
| `tileload` | `{ tile, coords }` | Tile loaded |
| `tileunload` | `{ tile, coords }` | Tile unloaded |
| `tileabort` | `{ tile, coords }` | Tile loading aborted |
| `tileerror` | `{ tile, coords, error }` | Tile failed |

## DOM Events

Utility functions for DOM event handling:

```js
// Add/remove listeners
L.DomEvent.on(element, type, fn, context);
L.DomEvent.off(element, type, fn, context);

// Shorthand for multiple events
L.DomEvent.on(element, { click: fn1, mouseover: fn2 }, context);
L.DomEvent.off(element, { click: fn1 }, context);

// Prevent default
L.DomEvent.preventDefault(e);

// Stop propagation
L.DomEvent.stopPropagation(e);

// Both preventDefault + stopPropagation
L.DomEvent.stop(e);

// Disable click propagation on element and children
L.DomEvent.disableClickPropagation(element);

// Disable scroll propagation
L.DomEvent.disableScrollPropagation(element);

// Disable text selection
L.DomEvent.disableTextSelection();
L.DomEvent.enableTextSelection();

// Get mouse position relative to element
L.DomEvent.getMousePosition(e, container);

// Get wheel delta
L.DomEvent.getWheelDelta(e);
```
