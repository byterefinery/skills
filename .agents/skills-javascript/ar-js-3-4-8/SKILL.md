---
name: ar-js-3-4-8
description: AR.js 3.4.8 — lightweight Augmented Reality for the Web built on A-Frame and three.js with jsartoolkit5 tracking. Covers marker-based tracking (hiro, kanji, barcode, custom patterns), image tracking (NFT with .fset/.fset3/.iset descriptors), location-based GPS AR (gps-new-camera, gps-new-entity-place), the arjs scene system, custom events (markerFound, gps-camera-update-position), and CORS/HTTPS deployment. Use when building Web AR experiences, scanning markers or images with a phone camera, or placing AR content at GPS coordinates.
license: MIT
compatibility: Requires a server (HTTPS or localhost) and a phone with WebGL, WebRTC, camera; location-based also needs GPS, accelerometer and magnetometer. A-Frame 1.6.0
metadata:
  tags:
    - javascript
    - augmented-reality
    - ar
    - aframe
    - threejs
---

# ar-js 3.4.8

AR.js is a lightweight library for Augmented Reality on the Web. It tracks using jsartoolkit5 and renders with either A-Frame (declarative HTML components) or three.js (programmatic classes). Three feature families: **marker-based** (printed markers), **image tracking** (NFT — natural feature tracking of images), and **location-based** (GPS-anchored content).

## Overview

- **Package**: `@ar-js-org/ar.js@3.4.8` (MIT; bundled jsartoolkit5 is LGPLv3)
- **A-Frame version required**: 1.6.0 (AR.js ≤ 3.4.4 required A-Frame 1.0.4)
- **Requirements**: WebGL + WebRTC; camera access only works under HTTPS or localhost; all examples must run on a server
- **Tracking backend**: jsartoolkit5; A-Frame build is a thin wrapper over the three.js core

### Choosing a build

Builds are **exclusive** — import the one that matches your features and renderer, never both:

| Build | Features |
|---|---|
| `aframe/build/aframe-ar-nft.js` | Image Tracking + Location Based (A-Frame) |
| `aframe/build/aframe-ar.js` | Marker Tracking + Location Based (A-Frame) |
| `aframe/build/aframe-ar-location-only.js` | Location Based only (A-Frame) |
| `three.js/build/ar-threex.js` | Image + Marker (three.js, no `ARjs` namespace) |
| `three.js/build/ar.js` | same, plus global `ARjs` namespace |
| `three.js/build/ar-threex-location-only.js` | Location Based only (three.js) |

CDN (pin the version tag — the docs' `master` links drift):

```html
<script src="https://cdn.jsdelivr.net/gh/aframevr/aframe@1.6.0/dist/aframe.min.js"></script>
<script src="https://raw.githack.com/AR-js-org/AR.js/3.4.8/aframe/build/aframe-ar-nft.js"></script>
```

npm: `npm install @ar-js-org/ar.js`. Since 3.4.6 the `.mjs` builds (`ar-threex.mjs`, `ar.mjs`, `ar-threex-location-only.mjs`) are imported via an import map that maps `three` and the module, e.g.:

```html
<script type="importmap">
{
  "imports": {
    "three": "https://cdn.jsdelivr.net/npm/three@0.164.0/build/three.module.js",
    "threex": "./path/to/ar-threex.mjs"
  }
}
</script>
<script type="module">
import * as THREE from 'three';
import { ArToolkitSource, ArToolkitContext, ArMarkerControls } from 'threex';
</script>
```

### Feature selection

- **Marker-based** — very lightweight, very stable; markers are limited in shape/color/size. Good when many different markers must carry different content (augmented books, flyers, advertising).
- **Image tracking (NFT)** — tracks any image with interesting features; more CPU-consuming; content stabilization is weaker, so enable `smooth` on the anchor.
- **Location-based** — GPS-anchored content (POIs, treasure hunts, situated art). Indoor precision is low; outdoor use recommended. The docs recommend the separate [LocAR.js](https://github.com/AR-js-org/locar.js) project for new location-based work (better iOS support, more frequent updates); AR.js 3.4.x location-based is maintained but in maintenance mode.

### The `arjs` scene system (A-Frame)

AR.js is initialized on `<a-scene>` via the `arjs` attribute. Full schema with defaults in [02-aframe-components](references/02-aframe-components.md); common values:

```html
<a-scene
  vr-mode-ui="enabled: false;"
  renderer="logarithmicDepthBuffer: true; precision: medium;"
  embedded
  arjs="trackingMethod: best; sourceType: webcam; debugUIEnabled: false;"
>
```

Key properties: `trackingMethod` (`best` default), `sourceType` (`webcam`), `sourceUrl`, `sourceWidth`/`sourceHeight`, `displayWidth`/`displayHeight`, `canvasWidth`/`canvasHeight`, `maxDetectionRate` (60), `detectionMode` (`color_and_matrix`), `matrixCodeType` (`3x3`), `patternRatio` (0.5), `labelingMode` (`black_region`/`white_region`), `cameraParametersUrl`, `debugUIEnabled`, and `videoTexture` (location-based only — see below). `trackingMethod: best` auto-selects between marker and NFT builds.

## Usage

### Marker-based (A-Frame)

Markers come in three types: `preset` (`hiro`, `kanji`, `area`), `barcode`, and custom `pattern` (a `.patt` file from the [pattern generator](https://ar-js-org.github.io/AR.js/three.js/examples/marker-training/examples/generator.html), which outputs the scannable image + `.patt`).

```html
<a-scene embedded arjs>
  <a-marker preset="hiro" emitevents>
    <a-entity position="0 0 0" scale="0.05 0.05 0.05"
              gltf-model="scene.gltf"></a-entity>
  </a-marker>
  <a-entity camera></a-entity>
</a-scene>
```

`<a-marker/>` attributes (full table in [02-aframe-components](references/02-aframe-components.md)): `type` (`pattern`|`barcode`|`unknown`), `preset`, `url` (pattern file), `value` (barcode value), `size` (meters), `emitevents` (fires `markerFound`/`markerLost`), `smooth`, `smoothCount` (5), `smoothTolerance` (0.01), `smoothThreshold` (2).

For barcode markers set `arjs="detectionMode: mono_and_matrix; matrixCodeType: 3x3"` on the scene.

### Image tracking / NFT (A-Frame)

1. Choose a good image — high-contrast shapes, no large blank areas; a source image at 300+ DPI tracks more stably than 72 DPI (low DPI makes users stand close and still).
2. Generate Image Descriptors with the [NFT Marker Creator](https://carnaux.github.io/NFT-Marker-Creator/) (web, recommended) or the node version (`node app.js -i image.jpg`). Output: three files `name.fset`, `name.fset3`, `name.iset` served from your app's server; the shared prefix is the descriptor name.
3. Anchor with `<a-nft/>`:

```html
<div class="arjs-loader"><div>Loading, please wait...</div></div>
<a-scene
  vr-mode-ui="enabled: false;"
  renderer="logarithmicDepthBuffer: true;"
  embedded
  arjs="trackingMethod: best; sourceType: webcam; debugUIEnabled: false;"
>
  <a-nft
    type="nft"
    url="/path/to/descriptors/trex"   <!-- prefix, no extension -->
    smooth="true" smoothCount="10" smoothTolerance=".01" smoothThreshold="5"
  >
    <a-entity gltf-model="scene.gltf" scale="5 5 5" position="50 150 0"></a-entity>
  </a-nft>
  <a-entity camera></a-entity>
</a-scene>
```

`<a-nft/>` attributes: `type="nft"` (only valid value), `url` (descriptor prefix without extension), `emitevents`, `smooth`/`smoothCount`/`smoothTolerance`/`smoothThreshold` (same defaults as `a-marker`), `size`. Use `smooth` for NFT — raw tracking jitters without it.

The `arjs-nft-loaded` window event fires when all descriptors finish loading (use it to hide your loader):

```js
window.addEventListener("arjs-nft-loaded", () => { /* hide .arjs-loader */ });
```

Any element with class `.arjs-loader` is **automatically removed from the DOM** once descriptors load (or, in location-based, once the origin GPS position is set) — a free built-in loading overlay.

### Location-based (A-Frame)

Three component variants (recommended first):

| Variant | Camera | Entity-place |
|---|---|---|
| **new-location-based (recommended)** | `gps-new-camera` | `gps-new-entity-place` |
| projected | `gps-projected-camera` | `gps-projected-entity-place` |
| classic | `gps-camera` | `gps-entity-place` |

Minimal example — a box ~100 m north of the user:

```html
<a-scene vr-mode-ui='enabled: false'
  arjs='sourceType: webcam; videoTexture: true; debugUIEnabled: false'
  renderer='antialias: true; alpha: true'>
  <a-camera gps-new-camera='gpsMinDistance: 5'></a-camera>
  <a-box color="red" depth="10" height="10" width="10"
    gps-new-entity-place="latitude: <your-lat>; longitude: <your-lon>"/>
</a-scene>
```

- `gps-new-camera` — one per scene, required; properties `gpsMinDistance` (5 m, prevents jumping), `positionMinAccuracy` (100 m), `gpsMinAccuracy`, `simulateLatitude`/`simulateLongitude`/`simulateAltitude` (testing), `gpsTimeInterval`.
- `gps-new-entity-place` — any number; requires `latitude`/`longitude`; a `distance` property exposes metres from the camera (this component only — classic/projected use events). The A-Frame `position` `y` value is metres above/below camera height.
- Text/models should face the user — use the third-party `look-at` component (`aframe-look-at-component`) pointed at the camera.
- **Distant content (~1 km+)**: set `videoTexture: true` on the `arjs` system with `sourceType: webcam` — the camera feed becomes a three.js texture so far content renders correctly.
- **Shaking**: add the AR.js smoothing `look-controls` to the camera and disable A-Frame's default: `look-controls-enabled='false' arjs-device-orientation-controls='smoothingFactor: 0.1'` (new-location-based; `arjs-look-controls` for classic/projected). Smaller `smoothingFactor` = more smoothing.
- **Projection**: new-location-based and projected components use Spherical Mercator (EPSG:3857); world units ≈ metres away from the poles. `latLonToWorld(lat, lon)` on the camera component returns `[x, z]` world coordinates — the way to overlay geodata (e.g., OpenStreetMap polylines). Note `gps-projected-camera` keeps the original GPS position as world origin; `gps-new-camera` does not (as of 3.4.4 the initial GPS location is the origin).
- **Loading POIs dynamically**: listen for `gps-camera-update-position` on the camera element, then create entities with `gps-new-entity-place` (full tutorial with GeoJSON fetch in [03-location-based](references/03-location-based.md)).

### three.js API

Programmatic API (used by the A-Frame build internally):

- **Marker/image**: `THREEx.ArToolkitSource` (webcam/video/image source), `THREEx.ArToolkitContext` (tracking engine), `THREEx.ArMarkerControls` (positions content on the marker). Parameter objects in [01-threejs-api](references/01-threejs-api.md).
- **Location-based**: `THREEx.LocationBased` (GPS manager: `startGps`, `fakeGps`, `add(object, lon, lat, elev)`, `lonLatToWorldCoords`, `latLonToWorld`), `THREEx.WebcamRenderer` (camera feed as texture), `THREEx.DeviceOrientationControls`. Details in [03-location-based](references/03-location-based.md).

### UI and events

- **markerFound / markerLost** — fire on `a-marker`/`a-nft` (enable `emitevents`), and can be listened on the scene. Typical use: trigger an action when an image is found without linking 3D content.
- **Full custom event table** (`arjs-video-loaded`, `camera-error`, `camera-init`, `arjs-nft-loaded`, `gps-camera-update-positon`, `gps-entity-place-*`, ...) with payloads in [04-events-ui](references/04-events-ui.md).
- **Overlayed DOM UI** — normal HTML/CSS on the body outside the `a-scene` works (buttons, HUDs); position with CSS, listen with normal DOM events.
- **Clicking AR content** — A-Frame raycasting (`raycaster`/`cursor`) handles taps on AR entities; gesture zoom/rotate of content is A-Frame-side, not AR.js.

## Gotchas

- **HTTPS + server is mandatory** — camera and GPS access fail on `file://` or plain-HTTP origins. Run a local server (e.g. `npx http-server`) or deploy under HTTPS (GitHub Pages works).
- **The old `arjs-cors-proxy.herokuapp.com` is dead** (Heroku killed free plans in Nov 2022) — it still appears in doc examples. The correct fix is to serve descriptors, models, and other external resources from the same server as your app; only self-host a CORS proxy ([Rob--W/cors-anywhere](https://github.com/Rob--W/cors-anywhere)) as a fallback, and check your host's policy on running one.
- **Pin matching versions** — AR.js 3.4.8 pairs with A-Frame 1.6.0; 3.4.4 and below need 1.0.4. Mixing them breaks the build.
- **Import exactly one build** — `aframe-ar.js` and `aframe-ar-nft.js` are exclusive; loading both double-registers components. Choose by feature (marker vs NFT) and by renderer (A-Frame vs three.js).
- **Pin `3.4.8` in script URLs, not `master`** — `raw.githack.com/.../master/...` silently pulls future breaking changes; docs snippets use `master` but production pages should use the tag.
- **`a-nft` url is the descriptor prefix without extension** — for `trex.fset`/`trex.fset3`/`trex.iset` the url ends in `.../trex`, not `trex.fset`. All three files must be reachable (CORS-safe).
- **Location-based does not work on Firefox** — absolute device orientation (compass bearing) cannot be obtained there. Android/Chrome is the reference target.
- **Compass inaccuracy is a hardware issue** — Android/Chrome may report wrong north due to sensor miscalibration; there is nothing in AR.js to fix it. Also enable high-accuracy location on Android — it is sometimes off by default.
- **Location-based needs all three sensors** (GPS + accelerometer + magnetometer); without any of them the feature cannot work. On iOS, heed the browser/AR.js alerts — iOS requires explicit user actions to activate geolocation.
- **Known location-based camera-feed bug** — the video feed can appear stretched away from screen center, reducing placement accuracy for off-center objects (open issue, being pursued in LocAR).
- **Multi-camera phones** — Chrome may pick the wrong camera; use Firefox if AR.js opens on the wrong one.
- **New-location-based components lack some classic events** — `gps-entity-place-update-positon` and friends fire only on classic/projected; use the `distance` property or the new components' own event set. Classic components also handle embedded AR scenes where the others do not.
- **`minDistance`/`maxDistance` on new-location-based** — in `gps-new-camera` these do not cull content; set the perspective camera's near/far clipping planes instead.
- **`smooth` defaults to false on both `a-marker` and `a-nft`** — enable it (especially for NFT) or content jitters visibly.
- **Pattern markers want high contrast** — simple, high-contrast images with a black border (classic `black_region` labeling) track best; white-bordered markers on black background work but less reliably.
- **A-Frame `position` y ≠ world y in location-based** — with `gps-new-entity-place`, `position="0 30 0"` means 30 m above/below the *camera's* current height, not absolute altitude.
- **Altitude support is new in 3.4.8** — the location-based code gained altitude support in this release (e.g., `simulateAltitude` on the camera, `elev` in `fakeGps`/`add`).

## References

- [01-threejs-api](references/01-threejs-api.md) — three.js classes and full parameter objects (ArToolkitSource/Context/ArMarkerControls)
- [02-aframe-components](references/02-aframe-components.md) — full `arjs` scene system schema plus `a-marker`/`a-nft` attribute tables
- [03-location-based](references/03-location-based.md) — GPS components, Spherical Mercator, three.js LocationBased API, POI tutorial
- [04-events-ui](references/04-events-ui.md) — complete custom event table, markerFound handlers, DOM overlay UI, click handling
- [Official documentation](https://ar-js-org.github.io/AR.js-Docs/) — AR.js org docs (mkdocs)
- [AR.js repository 3.4.8](https://github.com/AR-js-org/AR.js/tree/3.4.8) — source and all bundled examples
- [LocAR.js](https://github.com/AR-js-org/locar.js) — maintained successor for location-based AR
