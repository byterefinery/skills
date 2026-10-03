---
name: locar-0-2-12
description: LocAR.js 0.2.12 — location-based augmented reality in the browser from the AR.js project. Place three.js objects at real-world lat/lon positions, track GPS and device orientation (compass), and overlay AR content on a live webcam feed. Use when building location-based AR web apps, anchoring 3D content to geographic coordinates, or working with the locar npm package 0.2.x.
metadata:
  tags:
    - javascript
    - ar
    - location-based
    - threejs
    - gps
---

# locar 0.2.12

LocAR.js is a standalone library for location-based augmented reality in the browser, split out from the AR.js monorepo. It renders a three.js scene over a live webcam feed and lets you anchor objects to real-world positions defined by longitude/latitude. It depends on three.js (0.2.12 works with `three` ^0.181.0) and is published to npm as `locar`.

## Overview

- **Package**: `locar@0.2.12`, import as `import * as LocAR from 'locar'` or named `import { App, LocAR } from 'locar'`.
- **Core classes** (exported from `locar`): `App` (orchestrates scene, camera, renderer, webcam, sensors), `LocAR` (engine — GPS, object placement, projection), `Webcam`, `DeviceOrientationControls`, `ClickHandler`, `EventEmitter`, `SphMercProjection`.
- **Exported types**: `LonLat`, `GpsReceivedEvent`, `GpsOptions`, `AppOptions`, `BasicAppOptions`, `ThreeObjects`, `Projection`, `ServerLogger`, `WebcamStartedEvent`, `WebcamErrorEvent`, `DeviceOrientationErrorEvent`, `DeviceOrientationGrantedEvent`, `DeviceOrientationControlsOptions`.
- **0.2 API**: the `App` class abstracts setup. `App.start()` returns a `Promise<LocAR>`. (In 0.1 the class was `LocationBased` and you set up the three.js scene manually.)
- **Browser support**: Chrome on Android and iOS, Safari on iOS. Firefox is unlikely to work — it does not fully implement the Device Orientation API.
- **Projection**: Spherical Mercator (EPSG:3857) by default; the first accepted GPS reading sets the world origin, and coordinates are converted to WebGL with z sign reversed to match OpenGL.

## Usage

### Project setup

Install both packages — three.js is a peer need, not a transitive dependency:

```json
{
  "dependencies": {
    "locar": "^0.2.12",
    "three": "^0.181.0"
  },
  "devDependencies": { "vite": "^8.1.5" }
}
```

The repo's own examples use Vite in dev mode (`npm run dev`); the examples directory pins `locar` to exactly `0.2.12`.

Required HTML (viewport meta tag plus full-screen `html`/`body` so the camera feed occupies the whole screen):

```html
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, user-scalable=no, initial-scale=1, minimum-scale=1, maximum-scale=1" />
<style>
html, body { width: 100%; height: 100%; }
</style>
<script type='module' src='src/main.ts'></script>
</head>
<body>
</body>
</html>
```

### Hello world (fake GPS, works on desktop)

```typescript
import * as THREE from 'three';
import { App } from 'locar';

const app = new App({
    cameraOptions: { hFov: 80, near: 0.001, far: 1000 }
});

try {
    const locar = await app.start();
    const geom = new THREE.BoxGeometry(10, 10, 10);
    const material = new THREE.MeshBasicMaterial({ color: 0xff0000 });
    const mesh = new THREE.Mesh(geom, material);
    locar.add(mesh, -0.72, 51.0505);   // (object, lon, lat)
    locar.fakeGps(-0.72, 51.05);       // place the camera here
} catch (e: any) {
    alert(`Error: ${e.code} ${e.message}`);
}
```

`App` accepts `cameraOptions` (hFov, near, far — these configure an internal `THREE.PerspectiveCamera`; note horizontal, not vertical, fov) or `canvas` to render into an existing `<canvas>`. On a desktop without sensors the scene is locked facing north, so a box placed north of the fake GPS position appears in front of you.

### Real GPS with update events

```typescript
import * as THREE from 'three';
import { App, GpsReceivedEvent } from 'locar';

const app = new App({ cameraOptions: { hFov: 80, near: 0.001, far: 1000 } });

try {
    let firstLocation = true;
    const locar = await app.start();

    locar.on("gpserror", (error: GeolocationPositionError) => {
        alert(`GPS error: ${error.code}`);
    });

    locar.on("gpsupdate", (ev: GpsReceivedEvent) => {
        if (firstLocation) {
            const lon = ev.position.coords.longitude;
            const lat = ev.position.coords.latitude;
            // add AR objects relative to initial position...
            firstLocation = false;
        }
    });

    locar.startGps();
} catch (e: any) {
    alert(`${e.code} ${e.message}`);
}
```

Key points from the tutorial and source:

- The `gpsupdate` event fires on each accepted GPS reading with a `GpsReceivedEvent` containing `position` (the standard Geolocation API object) and `distMoved` (metres moved since the last update). The `LocAR` object automatically moves the camera to the new location — nothing else to do.
- GPS readings are filtered: only positions with accuracy ≤ `gpsMinAccuracy` (default 100 m) count, and only if the device moved at least `gpsMinDistance` (default 0 m). Configure via `gpsOptions: { gpsMinDistance, gpsMinAccuracy }` in the `App` options or `locar.setGpsOptions()`.
- `startGps()` uses `navigator.geolocation.watchPosition` with `enableHighAccuracy: true`; it returns `false` if GPS was already started. `stopGps()` returns `true` if it was stopped, `false` if it was never started.
- `fakeGps(lon, lat, elev?, acc?)` injects a synthetic reading for desktop testing; the first accepted position (real or fake) becomes the world origin.

### Placing AR objects

- `locar.add(object, lon, lat, elev?, properties?)` — places a three.js `Object3D` at a geographic location (elevation default 0), stores `properties` on the object, and adds it to the scene. This is instead of setting `mesh.position` manually.
- `locar.addGeoLine(points, material, lineWidth?)` — triangle-strip polyline from `[lon, lat, alt?]` tuples; returns the `THREE.Mesh` and uses double-sided rendering. `locar.createGeoLine(points, lineWidth?)` builds only the geometry (no mesh), useful when you construct the mesh yourself (e.g. in react-three-fiber).
- `locar.lonLatToWorldCoords(lon, lat)` → `[x, z]` WebGL world coordinates; `locar.eastNorthToWorldCoords(projectedPos)` converts projected easting/northing to `[x, z]`. Both throw if no initial position has been determined yet.
- `LocAR.haversineDist(src, dest)` — static; distance in metres between two `LonLat` objects (`{ longitude, latitude }`).
- `locar.setElevation(elev)` — sets the camera y coordinate.
- `locar.getLastKnownLocation()` — `{ latitude, longitude }` or `null`.
- `locar.setProjection(proj)` — custom projection; a `Projection` implements `project(lon, lat): [easting, northing]` and `unproject(...)`.

### App options

```typescript
const app = new App({
    cameraOptions: { hFov: 80, near: 0.001, far: 1000 },  // or threeObjects, not both
    canvas: document.getElementById('glscene'),           // optional existing canvas
    gpsOptions: { gpsMinDistance: 1, gpsMinAccuracy: 100 },
    videoConstraints: { video: { facingMode: 'environment' } },
    deviceOrientationOptions: { enabled: true, smoothingFactor: 0.2,
        enablePermissionDialog: true, enableStyling: true,
        preferConfirmDialog: false, orientationChangeThreshold: 0 },
    threeObjects: { camera, renderer, scene },             // e.g. from react-three-fiber
    dimensionsProvider: () => ({ width, height }),         // default window.innerWidth/Height
    serverLogger: logger,                                  // optional; consent/GDPR required
    projection: new SphMercProjection()
});
```

- Specifying both `cameraOptions` and `threeObjects` throws — `cameraOptions` configures a new camera, `threeObjects` supplies existing ones.
- With `threeObjects` (e.g. R3F/RDK apps), App skips creating renderer/scene and does not run the render loop itself; call `app.syncFovWithWebcam(aspect?)` on each frame (or on orientation change) to keep the fov/aspect matched to the visible webcam portion. Pure LocAR apps do not need this.
- `app.start()` resolves with the `LocAR` once the webcam has started and (on iOS) the user has granted sensor permission; it rejects with `{ code, message }` on webcam or device-orientation errors.
- `app.on("webcamstarted", ev)` fires with `{ videoWidth, videoHeight, landVideoWidth, landVideoHeight }` (landscape-mode dimensions added in 0.2.12).

### Object picking

Register `app.on("objectsIntersected", ...)` and a `ClickHandler` is created automatically; it raycasts from the camera through the last click/touch point and emits the event with `{ intersections }` (a `THREE.Intersection[]`), every frame in which a click produced hits. Objects carry whatever `properties` you passed to `locar.add()`.

### Connecting to a web API (POI pattern)

The tutorial's Part 3 pattern — fetch GeoJSON around the current location, deduplicate by ID, throttle by distance:

```typescript
locar.on("gpsupdate", async (ev: GpsReceivedEvent) => {
    const lonLat: LonLat = {
        longitude: ev.position.coords.longitude,
        latitude: ev.position.coords.latitude
    };
    if (lastLonLat !== null) distSinceUpdate = LocAR.haversineDist(lonLat, lastLonLat);

    if (firstPosition || distSinceUpdate > 500) {
        firstPosition = false;
        lastLonLat = lonLat;
        const response = await fetch(`<geojson-api>?bbox=${lon-0.02},${lat-0.02},${lon+0.02},${lat+0.02}`);
        const pois = await response.json();
        pois.features.forEach((poi: any) => {
            if (!indexedObjects.get(poi.properties.osm_id)) {
                const mesh = new THREE.Mesh(cube, new THREE.MeshBasicMaterial({ color: 0xff0000 }));
                locar.add(mesh, poi.geometry.coordinates[0], poi.geometry.coordinates[1], 0, poi.properties);
                indexedObjects.set(poi.properties.osm_id, mesh);
            }
        });
    }
});
```

Use a `Map` keyed by a stable feature ID so overlapping fetches never add the same object twice; the distance gate (500 m in the example) minimises server requests.

## Gotchas

- **`three` is a separate dependency** — install `three` (0.181.x for this version) alongside `locar`; do not import the built bundle files directly, which causes duplicate three.js imports.
- **Desktop has no sensors** — with `fakeGps()` the view is fixed facing north; the box must be placed north of the fake position to be visible. Real testing needs Android Chrome or iOS Safari (not Firefox, not iOS Chrome per the project's own recommendations).
- **`gpsupdate` fires repeatedly** — it runs on every accepted GPS reading, so guard one-time setup (adding objects around the initial position) with a `firstLocation`/`firstPosition` flag, as in the official examples.
- **First position sets the world origin** — `lonLatToWorldCoords`/`eastNorthToWorldCoords` throw ("No initial position determined") before the first GPS/fakeGps fix.
- **`cameraOptions.hFov` is horizontal** — three.js `PerspectiveCamera.fov` is vertical; LocAR converts internally via `LocAR.htov()`/`LocAR.vtoh()`. The 0.2.12 release specifically fixed incorrect h/v fov conversion — do not replicate that math yourself.
- **Sensor miscalibration on some Android devices** — North can be wrong (e.g. consistently rotated), producing misaligned AR. The repo's `02-gps-and-sensors` example (four boxes N/S/E/W) exists precisely to check calibration; a calibration tool is on the roadmap but not shipped.
- **iOS permission flow** — device orientation requires a user gesture to grant permission; `App.start()` handles this via `enablePermissionDialog` (default true). `start()` can reject with an orientation error code if denied.
- **`serverLogger` has legal implications** — it streams GPS positions and added objects to a server; the source notes you must comply with privacy law (GDPR or equivalent) and gain user consent.
- **`stopGps()` before `fakeGps()`** — to switch from real GPS to a fake location at runtime (as the example 2 UI does), call `locar.stopGps()` first, then `locar.fakeGps(...)`.
- **`add()` takes longitude before latitude** — the signature is `add(object, lon, lat, elev?, properties?)`, but `LonLat` objects and GeoJSON `coordinates` use `[lon, lat]` order consistently; the tutorial's Part 3 has a known bug swapping the two when building `lonLat` — use `longitude: coords.longitude`.

## References

- [Official API documentation (typedoc)](https://ar-js-org.github.io/locar.js/api) — full class and event reference for 0.2.x
- [Official tutorial](https://github.com/AR-js-org/locar.js/blob/master/docs/tutorial/index.md) — Parts 1–3 (hello world, GPS/sensors, web API)
- [Examples in the repo](https://github.com/AR-js-org/locar.js/tree/v0.2.12/examples) — `01-helloworld`, `02-gps-and-sensors`, `03-api-communication`, `devorient`, runnable locally with Vite
- [AR.js main repository](https://github.com/AR-js-org/AR.js) — origin of the location-based components and known open issues (#278, #590, #607)
