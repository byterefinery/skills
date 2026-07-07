# Controls

## Control (Base Class)

Base class for map UI widgets positioned in corners.

### Options

| Option | Default | Description |
|---|---|---|
| `position` | `'topright'` | `'topleft'`, `'topright'`, `'bottomleft'`, `'bottomright'` |

### Extension API

```js
const MyControl = L.Control.extend({
	options: { position: 'topleft' },

	onAdd(map) {
		// Create and return container HTMLElement
		const container = L.DomUtil.create('div', 'my-control');
		container.innerHTML = 'Hello';
		return container;
	},

	onRemove(map) {
		// Cleanup
	}
});

L.control.myControl = options => new MyControl(options);
```

### Methods

```js
control.getPosition();          // → String
control.setPosition(position);
control.getContainer();         // → HTMLElement
control.addTo(map);
control.remove();
```

### Map Methods

```js
map.addControl(control);
map.removeControl(control);
```

## Control.Layers

Switch between base layers and toggle overlays.

```js
L.control.layers(baseLayers, overlays, options).addTo(map);
```

### Arguments

```js
const baseLayers = {
	'OpenStreetMap': osmLayer,
	'Satellite': satelliteLayer
};

const overlays = {
	'Markers': markersGroup,
	'Roads': roadsLayer
};
```

Only one base layer should be on the map at initialization. The control handles switching.

### Options

| Option | Default | Description |
|---|---|---|
| `collapsed` | `true` | Collapsed into icon, expands on hover |
| `position` | `'topright'` | Corner position |
| `autoZIndex` | `true` | Manage z-index for layer ordering |
| `hideSingleBase` | `false` | Hide radio button if only one base layer |
| `sortLayers` | `false` | Sort layers alphabetically |
| `sortFunction` | `*` | Custom compare function |

### Methods

```js
control.addBaseLayer(layer, name);
control.addOverlay(layer, name);
control.removeLayer(layer);
control.expand();
control.collapse();
```

### Events

```js
map.on('baselayerchange', e => { e.layer; e.name; });
map.on('overlayadd', e => { e.layer; e.name; });
map.on('overlayremove', e => { e.layer; e.name; });
```

## Control.Zoom

Zoom in/out buttons. Added by default.

```js
L.control.zoom({ position: 'topleft' }).addTo(map);
```

### Options

| Option | Default | Description |
|---|---|---|
| `position` | `'topleft'` | Corner position |
| `zoomInText` | `'+` | Zoom in button text |
| `zoomInTitle` | `'Zoom in'` | Zoom in button title |
| `zoomOutText` | `'−'` | Zoom out button text |
| `zoomOutTitle` | `'Zoom out'` | Zoom out button title |

### Methods

```js
control.disable();
control.enable();
```

Disable via map options: `L.map('map', { zoomControl: false })`.

## Control.Scale

Shows scale bar in metric and/or imperial units.

```js
L.control.scale({ position: 'bottomleft', maxWidth: 200 }).addTo(map);
```

### Options

| Option | Default | Description |
|---|---|---|
| `position` | `'bottomleft'` | Corner position |
| `maxWidth` | `100` | Max width in pixels |
| `metric` | `true` | Show metric (m/km) |
| `imperial` | `true` | Show imperial (mi/ft) |
| `updateWhenIdle` | `false` | Update on `moveend` instead of `move` |

## Control.Attribution

Displays attribution text. Added by default.

```js
L.control.attribution({ position: 'bottomright' }).addTo(map);
```

### Options

| Option | Default | Description |
|---|---|---|
| `position` | `'bottomright'` | Corner position |
| `prefix` | `'Leaflet'` | HTML text before attributions (false to disable) |

### Methods

```js
control.setPrefix(html);
control.addAttribution(text);
control.removeAttribution(text);
```

### Layer Attribution

Layers with `attribution` option automatically register with the control:

```js
L.tileLayer(url, {
	attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);
// Attribution appears automatically
```

Disable via map options: `L.map('map', { attributionControl: false })`.
