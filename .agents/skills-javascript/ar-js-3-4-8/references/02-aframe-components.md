# A-Frame components

Full reference for the `arjs` scene system and the marker/NFT anchor components.

## The `arjs` scene system

Attached to `<a-scene>`; initializes AR.js. Schema (verified against `aframe/src/system-arjs-nft.js`, 3.4.8):

| Property | Type | Default | Notes |
|---|---|---|---|
| `trackingMethod` | string | `best` | auto-selects tracking mode |
| `debugUIEnabled` | boolean | `false` | AR.js debug UI |
| `areaLearningButton` | boolean | `true` | |
| `performanceProfile` | string | `default` | |
| `labelingMode` | string | `''` | `black_region` / `white_region` |
| `videoTexture` | boolean | `false` | location-based only; with `sourceType: webcam` replaces the normal video element with a three.js texture (needed for distant content) |
| `debug` | boolean | `false` | legacy |
| `detectionMode` | string | `''` | `color` / `color_and_matrix` / `mono` / `mono_and_matrix` |
| `matrixCodeType` | string | `''` | `3x3`, `3x3_HAMMING63`, `3x3_PARITY65`, `4x4`, `4x4_BCH_13_9_3`, `4x4_BCH_13_5_5` |
| `patternRatio` | number | `-1` (0.5 in context) | custom marker ratio |
| `cameraParametersUrl` | string | `''` | artoolkit camera parameters |
| `maxDetectionRate` | number | `-1` (60 in context) | pose detection rate |
| `sourceType` | string | `''` | `webcam` / `image` / `video` |
| `sourceUrl` | string | `''` | valid for image/video |
| `sourceWidth` / `sourceHeight` | number | `-1` (640/480 in context) | |
| `deviceId` | string | `''` | select a specific camera |
| `displayWidth` / `displayHeight` | number | `-1` | |
| `canvasWidth` / `canvasHeight` | number | `-1` (640/480 in context) | detection resolution |
| `errorPopup` | string | `''` | |

When `videoTexture: true` and `sourceType: webcam`, the system skips normal setup and injects an `arjs-webcam-texture` entity instead.

## `<a-marker/>`

Marker-based anchor.

| Attribute | Description | Component mapping |
|---|---|---|
| `type` | `pattern` / `barcode` / `unknown` | artoolkitmarker.type |
| `size` | marker size in meters | artoolkitmarker.size |
| `url` | url of the pattern (iif `type='pattern'`) | artoolkitmarker.patternUrl |
| `value` | barcode value (iif `type='barcode'`) | artoolkitmarker.barcodeValue |
| `preset` | `hiro` / `kanji` (also `area` in source) | artoolkitmarker.preset |
| `emitevents` | emits `markerFound` / `markerLost` — `true`/`false` | - |
| `smooth` | camera smoothing on/off — default `false` | - |
| `smoothCount` | matrices to smooth over; more = smoother but slower — default `5` | - |
| `smoothTolerance` | distance tolerance for smoothing — default `0.01` | - |
| `smoothThreshold` | keeps still unless enough matrices are over tolerance — default `2` | - |

Barcode example (from the docs' markerFound tutorial):

```html
<a-scene
  arjs="trackingMethod: best; sourceType: webcam; debugUIEnabled: false; detectionMode: mono_and_matrix; matrixCodeType: 3x3;">
  <a-marker type='barcode' value='7'>
    <a-box position='0 0.5 0' color="yellow"></a-box>
  </a-marker>
  <a-entity camera></a-entity>
</a-scene>
```

## `<a-nft/>`

Image tracking (NFT) anchor.

| Attribute | Description | Component mapping |
|---|---|---|
| `type` | `nft` (only valid value) | artoolkitmarker.type |
| `url` | url of the Image Descriptors, without extension | artoolkitmarker.descriptorsUrl |
| `emitevents` | emits `markerFound` / `markerLost` — `true`/`false` | - |
| `smooth` | camera smoothing on/off — default `false` | - |
| `smoothCount` | default `5` | - |
| `smoothTolerance` | default `0.01` | - |
| `smoothThreshold` | default `2` | - |
| `size` | marker size in meters | artoolkitmarker.size |

The `url` must end with the shared prefix of the descriptor files (`trex` for `trex.fset`/`trex.fset3`/`trex.iset`), not a filename.

## Bundled examples (source repo, `aframe/examples/`)

- `marker-based/` — `basic.html`, `minimal.html`, `minimal_ES6.html`, `multiple-independent-markers.html`, `white-region-marker.html`, `marker-camera.html`, `marker-events.html`
- `image-tracking/nft/` — GLTF model over an NFT (trex); `image-tracking/nft-video/` — video content
- `location-based/` — `hello-world`, `multiple-boxes`, `always-face-user`, `click-places`, `basic-js`, `basic-js-modules`, `show-distance`, `poi`, `poi-component`, `osm-ways`, `avoid-shaking`, `classic-components`, `initial-location-as-origin`

The `location-based/README.md` describes each new-location-based example.
