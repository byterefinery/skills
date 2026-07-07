# GeoJSON

## L.GeoJSON

Parse and display GeoJSON data on the map.

```js
L.geoJSON(data, options).addTo(map);
```

### Options

| Option | Default | Description |
|---|---|---|
| `pointToLayer` | `*` | Function(geoJsonPoint, latlng) → Layer |
| `style` | `*` | Function(geoJsonFeature) → Path options |
| `onEachFeature` | `*` | Function(feature, layer) — attach events/popups |
| `filter` | `*` | Function(geoJsonFeature) → Boolean |
| `coordsToLatLng` | `*` | Custom coordinate converter |
| `markersInheritOptions` | `false` | Default markers inherit group options |

### Default `pointToLayer`

```js
function(geoJsonPoint, latlng) {
	return L.marker(latlng);
}
```

### Default `style`

```js
function(geoJsonFeature) {
	return {};  // No overrides
}
```

### Usage

```js
const geojsonLayer = L.geoJSON(data, {
	// Render points as circle markers
	pointToLayer: (feature, latlng) =>
		L.circleMarker(latlng, { radius: 5, color: '#3388ff' }),

	// Style based on properties
	style: feature => ({
		color: feature.properties.color || '#3388ff',
		weight: feature.properties.weight || 2,
		fillOpacity: 0.3
	}),

	// Attach popup to each feature
	onEachFeature: (feature, layer) => {
		if (feature.properties && feature.properties.name) {
			layer.bindPopup(`<b>${feature.properties.name}</b>`);
		}
		layer.on('mouseover', e => {
			e.target.setStyle({ weight: 4, fillOpacity: 0.5 });
		});
		layer.on('mouseout', e => {
			geojsonLayer.resetStyle(e.target);
		});
		layer.on('click', () => map.fitBounds(e.target.getBounds()));
	},

	// Filter out features
	filter: feature =>
		!feature.properties || feature.properties.visible !== false
}).addTo(map);
```

### Methods

```js
geojsonLayer.addData(geojson);    // Add more GeoJSON data
geojsonLayer.resetStyle(layer);   // Reset style to original (or all if no arg)
geojsonLayer.setStyle(style);     // Apply new style function to all layers
```

### Static Functions

```js
// Convert GeoJSON feature to a Leaflet layer
L.GeoJSON.geometryToLayer(featureData, options);

// Convert GeoJSON coords [lng, lat] to LatLng
L.GeoJSON.coordsToLatLng(coords);  // → LatLng

// Convert coords array to LatLng array
L.GeoJSON.coordsToLatLngs(coords, levelsDeep, coordsToLatLng);

// Reverse: LatLng to GeoJSON coords
L.GeoJSON.latLngToCoords(latlng, precision);

// Reverse: LatLng array to coords array
L.GeoJSON.latLngsToCoords(latlngs, levelsDeep, closed, precision);

// Normalize to Feature
L.GeoJSON.asFeature(geojson);

// Get Feature from layer
L.GeoJSON.getFeature(layer, newGeometry);
```

## toGeoJSON Serialization

Most Leaflet layers can export to GeoJSON:

```js
marker.toGeoJSON();       // → { type: 'Feature', geometry: { type: 'Point', ... } }
polyline.toGeoJSON();     // → LineString or MultiLineString
polygon.toGeoJSON();      // → Polygon or MultiPolygon
circle.toGeoJSON();       // → Point
circleMarker.toGeoJSON(); // → Point
layerGroup.toGeoJSON();   // → FeatureCollection or GeometryCollection
```

Optional precision parameter rounds coordinate values:

```js
layer.toGeoJSON(6);  // 6 decimal places
layer.toGeoJSON(false);  // No rounding
```

## Supported GeoJSON Types

| GeoJSON Type | Leaflet Layer |
|---|---|
| `Point` | `L.Marker` (or custom via `pointToLayer`) |
| `MultiPoint` | `L.FeatureGroup` of markers |
| `LineString` | `L.Polyline` |
| `MultiLineString` | `L.Polyline` |
| `Polygon` | `L.Polygon` |
| `MultiPolygon` | `L.Polygon` |
| `GeometryCollection` | `L.FeatureGroup` |
| `Feature` | Wrapped geometry type |
| `FeatureCollection` | `L.FeatureGroup` |
