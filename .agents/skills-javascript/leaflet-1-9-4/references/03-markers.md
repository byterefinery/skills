# Markers

## Marker

Display clickable/draggable icons on the map.

```js
const marker = L.marker([lat, lng], options).addTo(map);
```

### Options

| Option | Default | Description |
|---|---|---|
| `icon` | `L.Icon.Default` | Icon instance |
| `keyboard` | `true` | Tab-focusable, enter-clickable |
| `title` | `''` | Browser tooltip text on hover |
| `alt` | `'Marker'` | Alt text for accessibility |
| `zIndexOffset` | `0` | Override auto z-index (use 1000 for top) |
| `opacity` | `1.0` | Marker opacity |
| `riseOnHover` | `false` | Bring to front on hover |
| `riseOffset` | `250` | Z-index boost for riseOnHover |
| `pane` | `'markerPane'` | Pane for icon |
| `shadowPane` | `'shadowPane'` | Pane for shadow |
| `bubblingMouseEvents` | `false` | Bubble mouse events to map |
| `autoPanOnFocus` | `true` | Pan to show marker on keyboard focus |
| `draggable` | `false` | Enable drag |
| `autoPan` | `false` | Auto-pan map when dragging near edge |
| `autoPanPadding` | `[50, 50]` | Edge padding for auto-pan |
| `autoPanSpeed` | `10` | Pixels per auto-pan step |

### Methods

```js
marker.getLatLng();            // → LatLng
marker.setLatLng([lat, lng]);  // Fires 'move' event
marker.setZIndexOffset(n);
marker.getIcon();              // → Icon
marker.setIcon(icon);
marker.setOpacity(opacity);
marker.getElement();           // → HTMLElement (the icon DOM element)
```

### Events

```js
marker.on('move', e => {
	e.oldLatLng;   // Previous position
	e.latlng;      // New position
});

// Drag events (when draggable: true)
marker.on('dragstart', e => {});
marker.on('drag', e => {});
marker.on('dragend', e => {
	console.log(marker.getLatLng());
});
```

## Icon

Defines the appearance of a marker icon.

```js
const icon = L.icon({
	iconUrl: 'my-icon.png',
	iconRetinaUrl: 'my-icon@2x.png',
	iconSize: [38, 95],
	iconAnchor: [22, 94],
	popupAnchor: [-3, -76],
	tooltipAnchor: [0, -76],
	shadowUrl: 'shadow.png',
	shadowSize: [68, 95],
	shadowAnchor: [22, 94],
	className: '',
	crossOrigin: false
});
```

### Options

| Option | Default | Description |
|---|---|---|
| `iconUrl` | `null` | **Required**. URL to icon image |
| `iconRetinaUrl` | `null` | Retina (2x) version |
| `iconSize` | `null` | `[width, height]` in pixels |
| `iconAnchor` | `null` | Tip position relative to top-left (auto-centered if omitted) |
| `popupAnchor` | `[0, 0]` | Popup offset from icon anchor |
| `tooltipAnchor` | `[0, 0]` | Tooltip offset from icon anchor |
| `shadowUrl` | `null` | URL to shadow image |
| `shadowRetinaUrl` | `null` | Retina shadow |
| `shadowSize` | `null` | Shadow `[width, height]` |
| `shadowAnchor` | `null` | Shadow tip position |
| `className` | `''` | CSS class on both icon and shadow |
| `crossOrigin` | `false` | CORS attribute |

### Default Icon

`L.Icon.Default` is the blue marker. Set `imagePath` if Leaflet images are at a non-default path:

```js
L.Icon.Default.imagePath = '/path/to/leaflet/images/';
```

## DivIcon

Lightweight icon using a `<div>` instead of `<img>`. Useful for text markers or HTML content.

```js
const divIcon = L.divIcon({
	html: '<div class="custom-marker">A</div>',
	iconSize: [24, 24],       // Optional — auto-size if omitted
	iconAnchor: [12, 12],     // Optional — centered if omitted
	popupAnchor: [0, -12],
	className: '',            // CSS class on the div
	htmlAnchor: null          // Deprecated
});

L.marker([lat, lng], { icon: divIcon }).addTo(map);
```

### Options

| Option | Default | Description |
|---|---|---|
| `html` | `''` | HTML content or HTMLElement |
| `iconSize` | `null` | Fixed size (omit for auto-size) |
| `iconAnchor` | `null` | Anchor point |
| `popupAnchor` | `null` | Popup offset |
| `tooltipAnchor` | `null` | Tooltip offset |
| `className` | `'` | CSS class |
