# Map

## Construction

```js
const map = L.map('container-id', options);
// or
const map = L.map(containerElement, options);
```

### Map Options

| Option | Default | Description |
|---|---|---|
| `crs` | `L.CRS.EPSG3857` | Coordinate Reference System |
| `center` | `undefined` | Initial `[lat, lng]` |
| `zoom` | `undefined` | Initial zoom level |
| `minZoom` | `*` | Minimum zoom (inferred from layers if omitted) |
| `maxZoom` | `*` | Maximum zoom (inferred from layers if omitted) |
| `layers` | `[]` | Array of layers to add initially |
| `maxBounds` | `null` | Restrict view to bounds (bounces back on pan) |
| `renderer` | `*` | Default vector renderer (`L.SVG` or `L.Canvas`) |
| `zoomAnimation` | `true` | Enable zoom animation |
| `zoomAnimationThreshold` | `4` | Skip animation if zoom diff exceeds this |
| `fadeAnimation` | `true` | Enable tile fade animation |
| `markerZoomAnimation` | `true` | Animate markers during zoom |
| `zoomSnap` | `1` | Snap zoom to multiples (0 = no snap) |
| `zoomDelta` | `1` | Zoom change per button/scroll |
| `trackResize` | `true` | Auto-update on window resize |
| `zoomControl` | `true` | Add zoom buttons by default |
| `attributionControl` | `true` | Add attribution control by default |
| `closePopupOnClick` | `true` | Close popup when clicking map |

## View Methods

```js
// Set view
map.setView([lat, lng], zoom, { animate: true, duration: 1 });
map.setZoom(zoom, { animate: true });
map.zoomIn(delta);
map.zoomOut(delta);
map.setZoomAround(latlng, zoom);  // Zoom keeping a point stationary

// Smooth fly-to animation
map.flyTo([lat, lng], zoom, { duration: 1.5, easeLinearity: 0.25 });
map.flyToBounds(bounds, { padding: [50, 50], maxZoom: 18 });

// Fit bounds
map.fitBounds([[swLat, swLng], [neLat, neLng]], {
	padding: [50, 50],              // Padding from edges
	paddingTopLeft: [0, 0],
	paddingBottomRight: [0, 0],
	maxZoom: 18,
	animate: true
});
map.fitWorld();

// Pan
map.panTo([lat, lng], { animate: true, duration: 0.5 });
map.panBy([x, y]);                 // Pan by pixel offset
map.panInsideBounds(bounds);       // Pan to keep view inside bounds
map.panInside(latlng, { padding: [50, 50] }); // Pan minimally to show point
```

## State Methods

```js
map.getCenter();        // → LatLng
map.getZoom();          // → Number
map.getBounds();        // → LatLngBounds (visible area)
map.getMinZoom();       // → Number
map.getMaxZoom();       // → Number
map.getSize();          // → Point (container size in pixels)
map.getBoundsZoom(bounds, inside, padding); // → best zoom for bounds
map.getPixelBounds();   // → Bounds (projected pixel coords)
map.getPixelOrigin();   // → Point (top-left of map layer)
map.distance(latlng1, latlng2); // → meters
```

## Bounds Methods

```js
map.setMaxBounds([[swLat, swLng], [neLat, neLng]]);
// Remove bounds restriction
map.setMaxBounds(null);
// or
map.setMaxBounds(new L.LatLngBounds([[0, 0], [0, 0]])); // invalid bounds
```

## Coordinate Conversion

```js
// Geographic ↔ Layer pixel (relative to origin)
map.latLngToLayerPoint([lat, lng]);  // → Point
map.layerPointToLatLng([x, y]);      // → LatLng

// Geographic ↔ Container pixel (relative to container)
map.latLngToContainerPoint([lat, lng]);  // → Point
map.containerPointToLatLng([x, y]);      // → LatLng

// Layer ↔ Container
map.containerPointToLayerPoint([x, y]);
map.layerPointToContainerPoint([x, y]);

// Mouse event → coordinates
map.mouseEventToLatLng(e);
map.mouseEventToContainerPoint(e);
map.mouseEventToLayerPoint(e);

// Projection
map.project(latlng, zoom);    // → Point (CRS projected)
map.unproject(point, zoom);   // → LatLng

// Wrapping
map.wrapLatLng(latlng);
map.wrapLatLngBounds(bounds);

// Scale
map.getZoomScale(toZoom, fromZoom);  // → scale factor
map.getScaleZoom(scale, fromZoom);   // → zoom level
```

## Layer Management

```js
map.addLayer(layer);
map.removeLayer(layer);
map.hasLayer(layer);
map.eachLayer(fn, context);
```

## Geolocation

```js
map.locate({
	timeout: 10000,
	watch: false,
	setView: true,        // Auto-center on user location
	maxZoom: 18,
	enableHighAccuracy: false,
	maximumAge: 0
});

map.stopLocate();

// Events
map.on('locationfound', e => {
	console.log(e.latlng);      // User's LatLng
	console.log(e.accuracy);    // Accuracy in meters
	console.log(e.bounds);      // Accuracy circle as LatLngBounds
});
map.on('locationerror', e => {
	console.log(e.code);    // 0=not supported, 1=permission, 2=unavailable, 3=timeout
	console.log(e.message);
});
```

## Panes

Default panes (z-index order):

| Pane | z-index | Content |
|---|---|---|
| `tilePane` | 200 | GridLayer / TileLayer |
| `overlayPane` | 400 | Paths, ImageOverlay, VideoOverlay |
| `shadowPane` | 500 | Marker shadows |
| `markerPane` | 600 | Marker icons |
| `tooltipPane` | 650 | Tooltips |
| `popupPane` | 700 | Popups |

```js
map.getPane('tilePane');       // → HTMLElement
map.getPanes();                // → { tilePane: ..., ... }
map.createPane('customPane', container); // → HTMLElement
```

## Lifecycle

```js
map.whenReady(callback, context);
// or
map.on('load', callback);

// Destroy map
map.remove();  // Clears all layers, events, DOM
// Fires 'unload' event
```

## Size Invalidations

Call `invalidateSize()` when the container changes size externally:

```js
map.invalidateSize({
	animate: true,    // Pan animation
	pan: true,        // Reposition center
	debounceMoveend: true  // Delay moveend event
});
```

## Interaction Handlers

Built-in handlers (enabled by default):

| Handler | Option | Description |
|---|---|---|
| Drag | `dragging` | Pan by dragging |
| Scroll zoom | `scrollWheelZoom` | Zoom by scroll |
| Double-click zoom | `doubleClickZoom` | Zoom on double-click |
| Touch zoom | `touchZoom` | Pinch-to-zoom |
| Box zoom | `boxZoom` | Drag rectangle to zoom |
| Keyboard | `keyboard` | Arrow keys, +/- |

```js
map.dragging.disable();
map.dragging.enable();
map.scrollWheelZoom.disable();
```
