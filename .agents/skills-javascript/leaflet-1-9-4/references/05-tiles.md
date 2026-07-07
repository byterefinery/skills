# Tile Layers

## TileLayer

Load and display tiled image layers.

```js
L.tileLayer(urlTemplate, options).addTo(map);
```

### URL Template

```
'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
```

| Token | Description |
|---|---|
| `{s}` | Subdomain (`a`, `b`, `c` by default) |
| `{z}` | Zoom level |
| `{x}` | Tile X coordinate |
| `{y}` | Tile Y coordinate |
| `{-y}` | Inverted Y (for TMS) |
| `{r}` | `@2x` on retina displays |

Custom tokens from options are also substituted:

```js
L.tileLayer('https://example.com/{foo}/{z}/{x}/{y}.png', {
	foo: 'bar',
	apiKey: 'abc123'
});
// → https://example.com/bar/5/10/10.png
```

### Options

| Option | Default | Description |
|---|---|---|
| `minZoom` | `0` | Minimum zoom |
| `maxZoom` | `18` | Maximum zoom |
| `subdomains` | `'abc'` | Subdomain letters (string or array) |
| `errorTileUrl` | `''` | Fallback image for failed tiles |
| `zoomOffset` | `0` | Offset zoom in URL |
| `tms` | `false` | Invert Y axis (TMS services) |
| `zoomReverse` | `false` | Use `maxZoom - zoom` in URL |
| `detectRetina` | `false` | Request 4 half-size tiles on retina |
| `crossOrigin` | `false` | CORS attribute |
| `referrerPolicy` | `false` | Referrer policy attribute |
| `attribution` | `''` | Attribution text |
| `tileSize` | `256` | Tile dimensions |
| `opacity` | `1.0` | Layer opacity |
| `zIndex` | `1` | Explicit z-index |
| `bounds` | `null` | Only load tiles within bounds |
| `keepBuffer` | `2` | Number of tile rows/cols to keep loaded |

### Methods

```js
tileLayer.setUrl(url, noRedraw);  // Change URL template
tileLayer.redraw();               // Force reload all tiles
tileLayer.getTileUrl(coords);     // → URL for a tile
```

### Common Providers

```js
// OpenStreetMap
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
	maxZoom: 19,
	attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
});

// CartoDB Positron
L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
	attribution: '&copy; <a href="https://www.carto.com/">CARTO</a>',
	subdomains: 'abcd',
	maxZoom: 20
});

// Esri World Imagery
L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
	attribution: '&copy; Esri',
	maxZoom: 19
});
```

## TileLayer.WMS

Display WMS (Web Map Service) layers.

```js
L.tileLayer.wms(baseUrl, {
	layers: 'topp:states',
	format: 'image/png',
	transparent: true,
	version: '1.1.1',
	attribution: 'GeoServer'
}).addTo(map);
```

### WMS Options

| Option | Default | Description |
|---|---|---|
| `layers` | `''` | **Required**. Comma-separated layer names |
| `styles` | `''` | Comma-separated styles |
| `format` | `'image/jpeg'` | Image format |
| `transparent` | `false` | Return transparent images |
| `version` | `'1.1.1'` | WMS version |
| `crs` | `null` | CRS for requests (defaults to map CRS) |
| `uppercase` | `false` | Uppercase parameter keys |

### Methods

```js
wmsLayer.setParams({ layers: 'new_layer' }, noRedraw);
```

## GridLayer

Base class for tiled grid of HTML elements. Extend to create custom tile layers.

```js
const CanvasLayer = L.GridLayer.extend({
	createTile(coords, done) {
		const tile = document.createElement('canvas');
		const size = this.getTileSize();
		tile.width = size.x;
		tile.height = size.y;

		const ctx = tile.getContext('2d');
		// Draw on canvas using coords.x, coords.y, coords.z

		return tile;
		// Or async:
		// setTimeout(() => done(null, tile), 100);
	}
});
```

### GridLayer Options

| Option | Default | Description |
|---|---|---|
| `tileSize` | `256` | Tile dimensions (Number or Point) |
| `opacity` | `1.0` | Tile opacity |
| `updateWhenIdle` | `Browser.mobile` | Load tiles only after pan ends |
| `updateWhenZooming` | `true` | Update tiles during smooth zoom |
| `updateInterval` | `200` | Min ms between tile updates |
| `zIndex` | `1` | Explicit z-index |
| `bounds` | `null` | Only create tiles within bounds |
| `minZoom` | `0` | Minimum zoom |
| `maxZoom` | `undefined` | Maximum zoom |
| `maxNativeZoom` | `undefined` | Max zoom of source (upscaling) |
| `minNativeZoom` | `undefined` | Min zoom of source (downscaling) |
| `noWrap` | `false` | Don't wrap tiles horizontally |
| `pane` | `'tilePane'` | Map pane |
| `keepBuffer` | `2` | Tile buffer around viewport |

### GridLayer Methods

```js
gridLayer.redraw();            // Reload all tiles
gridLayer.setOpacity(opacity);
gridLayer.setZIndex(zIndex);
gridLayer.isRetina();          // → Boolean
gridLayer.getTileSize();       // → Point
```

### Tile Events

```js
gridLayer.on('tileloadstart', e => { e.tile; e.coords; });
gridLayer.on('tileload', e => { e.tile; e.coords; });
gridLayer.on('tileerror', e => { e.tile; e.coords; e.error; });
gridLayer.on('tileunload', e => { e.tile; e.coords; });
gridLayer.on('tileabort', e => { e.tile; e.coords; });
```
