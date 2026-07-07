---
name: leaflet-1-9-4
description: Leaflet 1.9.4 — lightweight JavaScript library for interactive maps. Covers Map initialization and view control, layers (Markers, TileLayer, Polyline, Polygon, Circle, CircleMarker, GeoJSON, ImageOverlay, VideoOverlay), Popups, Tooltips, Controls (Zoom, Layers, Scale, Attribution), CRS projections, LatLng/LatLngBounds geometry, GridLayer for custom tile grids, and the event system. Use when building interactive web maps, overlaying vector data, working with tile providers, or handling map interactions.
metadata:
  tags:
    - javascript
    - maps
    - geospatial
    - gis
---

# leaflet 1.9.4

Leaflet is a modern, lightweight JavaScript library for mobile-friendly interactive maps. It is designed around simplicity, performance, and usability, with an extensible plugin architecture.

## Overview

- **Package**: `leaflet@1.9.4`
- **Namespace**: `L` (global) or ES module imports
- **Default CRS**: `L.CRS.EPSG3857` (Spherical Mercator / Web Mercator)
- **Tile size**: 256×256 pixels (default)
- **Renderers**: `L.SVG` (default) or `L.Canvas` for vector layers
- **Browser support**: All modern browsers, IE11+ (with CSS prefix polyfills)

### Entry Points

| Import | Description |
|---|---|
| `leaflet` (CDN) | Full build via `<script src="leaflet.js">` → global `L` |
| `leaflet/dist/leaflet.js` | UMD bundle (ESM, CommonJS, AMD, global) |
| `leaflet/dist/leaflet.css` | Required stylesheet |

### Quick Start

```js
// Create a map centered on a location
const map = L.map('map', {
	center: [51.505, -0.09],
	zoom: 13
});

// Add a tile layer (OpenStreetMap)
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
	attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);

// Add a marker with a popup
L.marker([51.5, -0.09])
	.bindPopup('A nice place.')
	.addTo(map)
	.openPopup();
```

### Core Architecture

Leaflet follows a layered architecture:

1. **Map** — central controller, manages panes, layers, events, and user interaction
2. **Layers** — visual elements (tiles, markers, vectors, overlays) added to the map
3. **Controls** — UI widgets positioned in map corners (zoom, layers, scale, attribution)
4. **CRS/Projection** — coordinate reference systems for projecting geographic coordinates
5. **Events** — unified event system inherited from `L.Evented`

### Key Design Principles

- **Chaining**: most methods return `this` for fluent API usage
- **Shallow copies**: LatLng/LatLngBounds are lightweight, not deeply cloned
- **Array shorthand**: `[lat, lng]` accepted wherever `LatLng` is expected
- **Pane system**: DOM layers stacked by z-index (tilePane → overlayPane → shadowPane → markerPane → tooltipPane → popupPane)

## Usage

### Map Creation

```js
const map = L.map('container-id', {
	center: [48.8566, 2.3522],   // [lat, lng]
	zoom: 12,
	minZoom: 3,
	maxZoom: 19,
	zoomControl: true,            // default zoom buttons
	attributionControl: true,     // default attribution
	closePopupOnClick: true,      // close popup on map click
	maxBounds: bounds,            // restrict panning area
	renderer: L.canvas(),         // use Canvas instead of SVG
});
```

### Adding Layers

```js
// Tile layer
const tiles = L.tileLayer(url, { maxZoom: 19, attribution: '...' }).addTo(map);

// Marker
L.marker([lat, lng], { draggable: true }).addTo(map);

// Polyline
L.polyline([[lat1, lng1], [lat2, lng2]], { color: 'red', weight: 3 }).addTo(map);

// Polygon (no need to close ring — Leaflet does it)
L.polygon([[lat1, lng1], [lat2, lng2], [lat3, lng3]], { fillColor: '#3388ff' }).addTo(map);

// Circle (radius in meters)
L.circle([lat, lng], { radius: 200, color: 'green' }).addTo(map);

// CircleMarker (radius in pixels, does not scale with zoom)
L.circleMarker([lat, lng], { radius: 10, color: 'blue' }).addTo(map);

// GeoJSON
L.geoJSON(data, {
	pointToLayer: (feature, latlng) => L.circleMarker(latlng, { radius: 5 }),
	style: feature => ({ color: feature.properties.color }),
	onEachFeature: (feature, layer) => {
		layer.bindPopup(`<b>${feature.properties.name}</b>`);
	}
}).addTo(map);

// Image overlay
L.imageOverlay(url, [[swLat, swLng], [neLat, neLng]]).addTo(map);

// Layer groups
L.layerGroup([marker1, marker2]).addTo(map);
L.featureGroup([polyline, polygon]).addTo(map);
```

### Layer Control

```js
const baseLayers = {
	'OpenStreetMap': osmLayer,
	'Satellite': satelliteLayer
};

const overlays = {
	'Markers': markersGroup,
	'Roads': roadsLayer
};

L.control.layers(baseLayers, overlays, { collapsed: true }).addTo(map);
```

### Popups and Tooltips

```js
// Popup — opens on click, closes on map click
marker.bindPopup('<b>Hello</b><br>World').openPopup();

// Standalone popup
L.popup().setLatLng([lat, lng]).setContent('Hello').openOn(map);

// Tooltip — shows on hover
marker.bindTooltip('Hover text', { permanent: false, direction: 'top' });

// Permanent tooltip
marker.bindTooltip('Always visible', { permanent: true });
```

### View Control

```js
map.setView([lat, lng], zoom);           // Jump to location
map.flyTo([lat, lng], zoom, { duration: 1.5 }); // Smooth animated transition
map.fitBounds([[swLat, swLng], [neLat, neLng]], { padding: [50, 50] });
map.fitWorld();
map.panTo([lat, lng]);
map.zoomIn(); map.zoomOut();
```

### Events

```js
// Map events
map.on('click', e => console.log(e.latlng));
map.on('zoomend', () => console.log(map.getZoom()));
map.on('moveend', () => console.log(map.getCenter()));

// Layer events
marker.on('click', e => { /* ... */ });
marker.on('dragend', e => console.log(e.target.getLatLng()));

// One-time event
map.once('load', () => console.log('Map loaded'));

// Remove listener
map.off('click', handler);
```

## Gotchas

- **Container must have a height** — the map container needs explicit CSS height (e.g., `height: 400px` or `height: 100%` on a sized parent). A zero-height container produces an invisible map with no error.
- **Call `invalidateSize()` after container resize** — if the map container is hidden then shown, or its size changes dynamically, call `map.invalidateSize()` to recalculate tile positions.
- **LatLng order is `[lat, lng]`** — not `[lng, lat]`. GeoJSON coordinates use `[lng, lat]`, so `L.GeoJSON` handles the conversion internally. Mixing the order causes maps to appear in the Atlantic Ocean.
- **Polygon rings should not be closed** — do not repeat the first point as the last point. Leaflet closes rings automatically; duplicating the point creates a zero-length segment.
- **Tile layer attribution is mandatory** — most tile providers require attribution. Set the `attribution` option or it will be missing from the control.
- **`L.CRS.EPSG3857` is the default** — if using WMS or non-Mercator tiles, set the CRS explicitly (e.g., `L.CRS.EPSG4326` for lat/lng tiles).
- **`maxBounds` bounces the view** — setting `maxBounds` restricts panning but does not prevent zooming out beyond the bounds. Use `minZoom`/`maxZoom` together.
- **`fitBounds` respects layer zoom limits** — if a tile layer has `maxZoom: 18`, `fitBounds` will not zoom beyond 18 even if the map allows it.
- **SVG vs Canvas rendering** — SVG is default and supports interactivity (hover, click) on vector paths. Canvas is faster for large datasets but lacks per-segment interactivity. Set via `map.options.renderer` or `L.polyline(latlngs, { renderer: L.canvas() })`.
- **Popup `autoClose`** — by default only one popup is open at a time. Set `autoClose: false` on a popup to allow multiple simultaneous popups, or use `map.addLayer(popup)` instead of `map.openPopup(popup)`.
- **GridLayer `updateWhenIdle`** — on mobile, tiles only load after panning stops. On desktop, they load during panning. Override with the `updateWhenIdle` option.
- **`L.Icon.Default.imagePath`** — when loading Leaflet from a non-standard path, the default marker icons may 404. Set `L.Icon.Default.imagePath = '/path/to/leaflet/images/'` before creating markers.
- **Event data `e.latlng` vs `e.originalEvent`** — Leaflet events wrap the original DOM event. Use `e.latlng` for geographic coordinates; `e.originalEvent` for raw mouse/keyboard data.
- **`remove()` destroys the map** — calling `map.remove()` clears all layers and event listeners. To reuse the container, create a new map instance. There is no `map.destroy()` — `remove()` is the method.
- **GeoJSON `pointToLayer` receives the feature** — the first argument is the full GeoJSON feature object (with `properties`), not just coordinates. Use it for styling decisions.
- **WMS `setParams` redraws tiles** — calling `tileLayerWms.setParams({ layers: 'new_layer' })` triggers a full redraw. Pass `true` as second argument to skip redraw.

## References

- [01-map](references/01-map.md) — Map class, options, view methods, panes, geolocation
- [02-layers](references/02-layers.md) — Layer base class, LayerGroup, FeatureGroup, interactive layers
- [03-markers](references/03-markers.md) — Marker, Icon, DivIcon, draggable markers
- [04-vectors](references/04-vectors.md) — Polyline, Polygon, Circle, CircleMarker, Path styling, SVG/Canvas renderers
- [05-tiles](references/05-tiles.md) — TileLayer, TileLayer.WMS, GridLayer, URL templates
- [06-overlays](references/06-overlays.md) — ImageOverlay, VideoOverlay, SVGOverlay
- [07-popup-tooltip](references/07-popup-tooltip.md) — Popup, Tooltip, DivOverlay base
- [08-controls](references/08-controls.md) — Control base, Layers, Zoom, Scale, Attribution
- [09-geojson](references/09-geojson.md) — GeoJSON parsing, pointToLayer, style, toGeoJSON serialization
- [10-geo-types](references/10-geo-types.md) — LatLng, LatLngBounds, Point, Bounds, CRS, Projections
- [11-events](references/11-events.md) — Evented mixin, map events, layer events, DOM events
- [12-utilities](references/12-utilities.md) — Util helpers, DomEvent, DomUtil, Browser detection
