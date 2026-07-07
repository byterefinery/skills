# Overlays

## ImageOverlay

Display a single image over a defined geographic area.

```js
L.imageOverlay(url, bounds, options).addTo(map);
```

### Options

| Option | Default | Description |
|---|---|---|
| `opacity` | `1.0` | Image opacity |
| `alt` | `''` | Alt text for accessibility |
| `interactive` | `false` | Enable mouse events |
| `crossOrigin` | `false` | CORS attribute |
| `errorOverlayUrl` | `''` | Fallback image on error |
| `zIndex` | `1` | Explicit z-index |
| `className` | `''` | Custom CSS class |

### Methods

```js
overlay.setUrl(url);
overlay.setBounds([[swLat, swLng], [neLat, neLng]]);
overlay.getBounds();            // → LatLngBounds
overlay.setOpacity(opacity);
overlay.setStyle({ opacity: 0.5 });
overlay.setZIndex(value);
overlay.bringToFront();
overlay.bringToBack();
overlay.getElement();           // → HTMLImageElement
overlay.getCenter();            // → LatLng
```

### Events

```js
overlay.on('load', e => {});
overlay.on('error', e => {});
```

## VideoOverlay

Display a video element over a geographic area.

```js
// From a URL
L.videoOverlay(videoUrl, bounds, options).addTo(map);

// From an existing element
L.videoOverlay(videoElement, bounds, options).addTo(map);

// Multiple sources (browser picks format)
L.videoOverlay([
	'source1.mp4',
	'source2.webm'
], bounds, options).addTo(map);
```

### Options

| Option | Default | Description |
|---|---|---|
| `autoplay` | `true` | Autoplay video |
| `loop` | `true` | Loop video |
| `keepAspectRatio` | `true` | Maintain video aspect ratio |
| `opacity` | `1.0` | Video opacity |
| `interactive` | `false` | Enable mouse events |
| `zIndex` | `1` | Explicit z-index |
| `className` | `''` | Custom CSS class |

### Methods

```js
videoOverlay.setUrl(url);
videoOverlay.setBounds(bounds);
videoOverlay.getBounds();       // → LatLngBounds
videoOverlay.setOpacity(opacity);
videoOverlay.setZIndex(value);
videoOverlay.bringToFront();
videoOverlay.bringToBack();
videoOverlay.getElement();      // → HTMLVideoElement
videoOverlay.getCenter();       // → LatLng
```

## SVGOverlay

Overlay a pre-existing SVG element onto the map.

```js
const svgElement = document.getElementById('my-svg');

L.svgOverlay(svgElement, [[swLat, swLng], [neLat, neLng]], {
	interactive: true,
	opacity: 1.0
}).addTo(map);
```

### Options

| Option | Default | Description |
|---|---|---|
| `interactive` | `false` | Enable mouse events |
| `opacity` | `1.0` | SVG opacity |

### Methods

```js
svgOverlay.setBounds(bounds);
svgOverlay.setOpacity(opacity);
svgOverlay.bringToFront();
svgOverlay.bringToBack();
svgOverlay.getElement();        // → SVGSVGElement
```
