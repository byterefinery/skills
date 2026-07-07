# Vector Layers

## Path (Base Class)

Abstract base for Polyline, Polygon, Circle, CircleMarker. Defines shared styling options.

### Path Options

| Option | Default | Description |
|---|---|---|
| `stroke` | `true` | Draw stroke |
| `color` | `'#3388ff'` | Stroke color |
| `weight` | `3` | Stroke width in pixels |
| `opacity` | `1.0` | Stroke opacity |
| `lineCap` | `'round'` | Stroke line cap (`round`, `butt`, `square`) |
| `lineJoin` | `'round'` | Stroke line join (`round`, `bevel`, `miter`) |
| `dashArray` | `null` | Dash pattern, e.g. `'5, 10'` |
| `dashOffset` | `null` | Dash offset |
| `fill` | `false` | Fill with color (depends on subclass) |
| `fillColor` | `*` | Fill color (defaults to `color`) |
| `fillOpacity` | `0.2` | Fill opacity |
| `fillRule` | `'evenodd'` | Fill rule (`evenodd`, `nonzero`) |
| `interactive` | `true` | Enable mouse events |
| `bubblingMouseEvents` | `true` | Bubble events to map |

### Path Methods

```js
path.setStyle({ color: 'red', weight: 5, fillColor: 'blue', fillOpacity: 0.4 });
path.redraw();
path.bringToFront();
path.bringToBack();
path.getElement();             // → SVG element or canvas
path.getLatLngs();             // → LatLng[] (Polyline/Polygon only)
path.getBounds();              // → LatLngBounds
```

## Polyline

Draw lines from an array of LatLng points.

```js
const polyline = L.polyline([
	[45.51, -122.68],
	[37.77, -122.43],
	[34.04, -118.2]
], { color: 'red', weight: 3, dashArray: '5, 10' }).addTo(map);
```

### Options

| Option | Default | Description |
|---|---|---|
| `smoothFactor` | `1.0` | Smoothing (higher = smoother, better performance) |
| `noClip` | `false` | Disable clipping for very long lines |

### Methods

```js
polyline.getLatLngs();         // → LatLng[]
polyline.setLatLngs(latlngs);
polyline.isEmpty();            // → Boolean
polyline.addLatLng(latlng);    // Append a point
polyline.getBounds();          // → LatLngBounds
polyline.getCenter();          // → LatLng (centroid, requires map)
polyline.closestLayerPoint(p); // → Point with .distance
polyline.toGeoJSON();          // → GeoJSON Feature
```

### MultiPolyline

Pass an array of arrays for multiple separate lines:

```js
L.polyline([
	[[45.51, -122.68], [37.77, -122.43]],
	[[40.78, -73.91], [32.76, -96.72]]
]).addTo(map);
```

## Polygon

Closed shape from LatLng points. Do not repeat the first point — Leaflet closes the ring.

```js
const polygon = L.polygon([
	[37, -109.05],
	[41, -109.03],
	[41, -102.05],
	[37, -102.04]
], { color: 'red', fillColor: '#f03', fillOpacity: 0.5 }).addTo(map);
```

### Polygon with Holes

```js
L.polygon([
	[[37, -109.05], [41, -109.03], [41, -102.05], [37, -102.04]],  // outer
	[[37.29, -108.58], [40.71, -108.58], [40.71, -102.50], [37.29, -102.50]]  // hole
]).addTo(map);
```

### MultiPolygon

```js
L.polygon([
	[ // First polygon
		[[37, -109.05], [41, -109.03], [41, -102.05], [37, -102.04]]
	],
	[ // Second polygon
		[[41, -111.03], [45, -111.04], [45, -104.05], [41, -104.05]]
	]
]).addTo(map);
```

### Methods

```js
polygon.getLatLngs();          // → LatLng[][] (rings)
polygon.setLatLngs(latlngs);
polygon.addLatLng(latlng);     // Add to first ring
polygon.getBounds();
polygon.toGeoJSON();
```

## Circle

Circle with radius in meters. Approximation — distorts near poles.

```js
const circle = L.circle([50.5, 30.5], {
	radius: 200,               // Meters
	color: 'green',
	fillColor: 'white',
	fillOpacity: 0.5
}).addTo(map);
```

### Methods

```js
circle.getLatLng();            // → LatLng (center)
circle.setLatLng([lat, lng]);
circle.getRadius();            // → Number (meters)
circle.setRadius(meters);
circle.getBounds();            // → LatLngBounds
circle.toGeoJSON();
```

## CircleMarker

Circle with fixed radius in pixels. Does not scale with zoom.

```js
const cm = L.circleMarker([50.5, 30.5], {
	radius: 10,                // Pixels
	color: 'blue',
	fillColor: 'blue',
	fillOpacity: 0.6
}).addTo(map);
```

### Methods

```js
cm.getLatLng();                // → LatLng
cm.setLatLng([lat, lng]);
cm.getRadius();                // → Number (pixels)
cm.setRadius(px);
cm.toGeoJSON();
```

## Rectangle

Convenience for axis-aligned rectangles.

```js
L.rectangle([[40.712, -74.227], [40.774, -74.125]], {
	color: 'red',
	fillColor: 'blue',
	fillOpacity: 0.3
}).addTo(map);
```

## Renderers

### SVG (Default)

Supports per-path interactivity (hover, click). Better for small-to-medium datasets.

```js
L.polyline(latlngs, { renderer: L.svg() });
// or set as map default
const map = L.map('map', { renderer: L.svg() });
```

### Canvas

Faster rendering for large datasets. No per-segment hover/click — events fire on the whole path.

```js
L.polyline(latlngs, { renderer: L.canvas() });
// or set as map default
const map = L.map('map', { renderer: L.canvas() });
```

### Switching Renderers

```js
// Per-layer
const polyline = L.polyline(latlngs, { renderer: L.canvas() });

// Per-map default
const map = L.map('map', { renderer: L.canvas() });

// Check current renderer
map.getRenderer(layer);
```

## SVGOverlay

Overlay an existing SVG element onto the map.

```js
L.svgOverlay(svgElement, [[swLat, swLng], [neLat, neLng]], {
	interactive: true,
	opacity: 1.0
}).addTo(map);
```
