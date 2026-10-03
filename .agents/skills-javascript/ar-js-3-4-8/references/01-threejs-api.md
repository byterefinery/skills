# three.js API

Programmatic API for AR.js without A-Frame. The A-Frame build wraps these classes. Builds: `three.js/build/ar-threex.js` (no `ARjs` namespace), `ar.js` (with `ARjs` namespace), `ar-threex-location-only.js` (location-based only). Since 3.4.6 the `.mjs` variants are ES modules imported via an import map (mapping `three` and the module path).

## Marker / Image Tracking

`threex-artoolkit` is composed of three classes:

- `THREEx.ArToolkitSource` — the image analyzed for position tracking. Webcam, video, or image.
- `THREEx.ArToolkitContext` — the main engine; finds marker position in the image source.
- `THREEx.ArMarkerControls` — controls the marker position using the classical three.js controls API; positions your content on top of the marker.

### ArToolkitSource parameters

```javascript
var parameters = {
  // type of source - ['webcam', 'image', 'video']
  sourceType: "webcam",
  // url of the source - valid if sourceType = image|video
  sourceUrl: null,
  // resolution at which the source image is initialized
  sourceWidth: 640,
  sourceHeight: 480,
  // resolution displayed for the source
  displayWidth: 640,
  displayHeight: 480
};
```

### ArToolkitContext parameters

```javascript
var parameters = {
  // debug - true displays the artoolkit debug canvas
  debug: false,
  // detection mode - ['color', 'color_and_matrix', 'mono', 'mono_and_matrix']
  detectionMode: 'color_and_matrix',
  // matrix code type - valid iif detectionMode ends with 'matrix'
  // [3x3, 3x3_HAMMING63, 3x3_PARITY65, 4x4, 4x4_BCH_13_9_3, 4x4_BCH_13_5_5]
  matrixCodeType: '3x3',
  // Pattern ratio for custom markers
  patternRatio: 0.5,
  // labeling mode - ['black_region', 'white_region']
  // black_region: black-bordered markers on white background
  // white_region: white-bordered markers on black background
  labelingMode: 'black_region',
  // url of the camera parameters
  cameraParametersUrl: THREEx.ArToolkitContext.baseURL + '../data/data/camera_para.dat',
  // maximum rate of pose detection in the source image
  maxDetectionRate: 60,
  // resolution at which pose is detected in the source image
  canvasWidth: 640,
  canvasHeight: 480,
  // image smoothing for canvas copy
  imageSmoothingEnabled: true
};
```

### ArMarkerControls parameters

```javascript
var parameters = {
  // size of the marker in meter
  size: 1,
  // type of marker - ['pattern', 'barcode', 'unknown']
  type: "unknown",
  // url of the pattern - IIF type='pattern'
  patternUrl: null,
  // value of the barcode - IIF type='barcode'
  barcodeValue: null,
  // change matrix mode - [modelViewMatrix, cameraTransformMatrix]
  changeMatrixMode: "modelViewMatrix",
  // turn on/off camera smoothing
  smooth: true,
  // number of matrices to smooth tracking over; more = smoother but slower follow
  smoothCount: 5,
  // distance tolerance for smoothing
  smoothTolerance: 0.01,
  // threshold for smoothing; keeps still unless enough matrices are over tolerance
  smoothThreshold: 2
};
```

## Location-based classes

- `THREEx.LocationBased` — general manager for the three.js location-based API.
- `THREEx.WebcamRenderer` — renders the webcam feed as a WebGL texture.
- `THREEx.DeviceOrientationControls` — detects device orientation changes (accelerometer + magnetometer).

### LocationBased

- `constructor(scene, camera, options={})` — initialises with a `THREE.Scene`, a `THREE.Camera`, and GPS options (see `setGpsOptions`).
- `setProjection(proj)` — sets the projection; default is Spherical Mercator. `proj` must provide `project(longitude, latitude)` returning a 2-member `[easting, northing]` array.
- `setGpsOptions(options={})` — sets `gpsMinDistance` and `gpsMinAccuracy` (as documented for the A-Frame camera components).
- `startGps()` — starts GPS; takes an optional `maximumAge` as used by the Geolocation API.
- `stopGps()` — stops GPS.
- `fakeGps(lon, lat, elev=null, acc=0)` — fakes a GPS position (elevation, accuracy optional).
- `lonLatToWorldCoords(lon, lat)` — projects lon/lat into world coordinates; northing sign reversed to match the OpenGL coordinate system.
- `add(object, lon, lat, elev)` — adds a three.js object at the given lon/lat and elevation.
- `setWorldPosition(object, lon, lat, elev)` — repositions an existing object without adding it.
- `setElevation(elev)` — sets the current elevation in metres; sets the camera `y` coordinate.
- `on(eventname, eventhandler)` — supports `gpsupdate` (new GPS position) and `gpserror` (Geolocation API errors).

### WebcamRenderer

- `constructor(renderer, videoElementSelector)` — takes a `THREE.WebGLRenderer` plus a selector for an HTML `<video>` element to stream the feed to.
- `update()` — update the camera feed each render frame.

### DeviceOrientationControls

- `constructor(cameraObject)` — takes a three.js camera.
- `update()` — update each render frame.

## Using three.js location-based in an application

Recommended setup: npm install + bundler.

```json
{
    "dependencies": {
        "@ar-js-org/ar.js": "3.4.7"
    },
    "devDependencies": {
        "webpack": "^5.75.0",
        "webpack-cli": "^5.0.0"
    },
    "scripts": { "build": "npx webpack" }
}
```

```javascript
import * as THREEx from './node_modules/@ar-js-org/ar.js/three.js/build/ar-threex-location-only.js'
```

A sample `webpack.config.js` (mode development, entry `./index.js`, output `dist/bundle.js`, `optimization.minimize: false`) is in the docs; the bundled `aframe/examples/location-based/basic-js-modules` example ships one.

For new three.js location-based projects the docs recommend LocAR.js (Vite-based, more frequent updates, API almost identical).
