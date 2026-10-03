# Location-based AR

GPS-anchored AR content. Docs target: Android/Chrome (Firefox cannot obtain absolute device orientation). LocAR.js is the maintained successor for new location-based work; this reference covers the AR.js 3.4.8 main-repository API.

## Component variants

| Variant | Camera | Entity-place | Notes |
|---|---|---|---|
| new-location-based (recommended) | `gps-new-camera` | `gps-new-entity-place` | since 3.4.0; bug fixes, simple code, thin wrapper over the three.js API; does not fire the classic `gps-entity-place-*` events |
| projected | `gps-projected-camera` | `gps-projected-entity-place` | since 3.3.1; same internals as classic plus Spherical Mercator projection; not recommended unless `new-location-based` misbehaves |
| classic | `gps-camera` | `gps-entity-place` | pre-3.3.1; no lat/lon projection facility; needed for some embedded-AR-scene uses |

## Camera component properties

One per scene, required, attached to the `a-camera` entity.

| Property | Description | Default | Availability |
|---|---|---|---|
| `positionMinAccuracy` | minimum accuracy allowed for the position signal (m) | 100 | all |
| `gpsMinDistance` | meters the camera must move before a GPS update event; prevents content jumping | 5 | all |
| `simulateLatitude` | simulated latitude for testing | 0 (disabled) | all (GPS-update event only in new-location-based) |
| `simulateLongitude` | simulated longitude for testing | 0 (disabled) | all (as above) |
| `simulateAltitude` | simulated altitude (meters above sea level) | 0 (disabled) | all |
| `alert` | show a message when GPS signal is under `positionMinAccuracy` | false | projected, classic |
| `minDistance` | hide places closer than this (m); in new-location-based use the near clipping plane instead | 0 (disabled) | projected, classic |
| `maxDistance` | hide places farther than this (m); in new-location-based use the far clipping plane instead | 0 (disabled) | projected, classic |
| `gpsTimeInterval` | geolocation `maximumAge` in ms; cached position reused if younger than this | 0 (always new) | all |

`gps-new-entity-place` exposes a `distance` property (meters from camera, dynamically updated) — available only on this component; classic/projected use events instead. The A-Frame `position` `y` value is meters above/below the current camera height (3.4.8 enables real altitude in the location-based code).

## Spherical Mercator projection

`new-location-based` and `projected` store camera and POI positions in Spherical Mercator (EPSG:3857), same as Google Maps — units approximate (not equal to) metres away from the poles. Rationale: geodata (roads, paths) can be projected and used directly as WebGL/A-Frame world coordinates.

- Key method: `latLonToWorld(lat, lon)` on `gps-new-camera` / `gps-projected-camera` — returns `[x, z]` world coordinates (northing sign reversed for OpenGL); specify `y` (altitude) independently.
- `gps-projected-camera` sets the **original GPS position** as world origin; `gps-new-camera` does not (as of 3.4.4 the initial GPS location is the origin).

## Reducing shaking and jumping

Add AR.js's smoothing look-controls to the camera and disable A-Frame's default:

```html
<a-camera id='camera1' look-controls-enabled='false'
  arjs-device-orientation-controls='smoothingFactor: 0.1'
  gps-new-camera='gpsMinDistance: 5'></a-camera>
```

`arjs-device-orientation-controls` for new-location-based; `arjs-look-controls` for classic/projected (which can show occasional display artefacts when moving quickly — test before enabling there). Exponential smoothing: `smoothedAngle = k * newValue + (1 - k) * previousSmoothedAngle`; smaller `k` (`smoothingFactor`) = more smoothing; 0.1 is the tested sweet spot. `gpsMinDistance` separately suppresses content jumping from GPS noise.

## Distant content

For content ~1 km or more away, use `videoTexture: true` on the `arjs` system with `sourceType: webcam` (component `arjs-webcam-texture`, since 3.2.0) — the camera feed streams as a three.js texture, so distant content renders without the stretched-feed distortion.

## Face-the-user content

Use the third-party `aframe-look-at-component` pointed at the camera:

```html
<script src="https://unpkg.com/aframe-look-at-component@0.8.0/dist/aframe-look-at-component.min.js"></script>
...
<a-text value="..." look-at="[gps-new-camera]" scale="120 120 120"
  gps-entity-place="latitude: <lat>; longitude: <lon>"></a-text>
```

(Bundled example: `aframe/examples/location-based/always-face-user`.)

## Loading POIs dynamically (tutorial pattern)

Listen for `gps-camera-update-position` on the camera element; `e.detail.position` has `latitude`/`longitude` (and `altitude` in 3.4.8). Create entities on the first update:

```javascript
window.onload = () => {
  let downloaded = false;
  const el = document.querySelector("[gps-new-camera]");
  el.addEventListener("gps-camera-update-position", async (e) => {
    if (downloaded) return;
    downloaded = true;
    const { latitude, longitude } = e.detail.position;
    const west = longitude - 0.05, east = longitude + 0.05;
    const south = latitude - 0.05, north = latitude + 0.05;
    const response = await fetch(
      `https://hikar.org/webapp/map?bbox=${west},${south},${east},${north}&layers=poi&outProj=4326`
    );
    const pois = await response.json(); // GeoJSON
    pois.features.forEach((feature) => {
      const compound = document.createElement("a-entity");
      compound.setAttribute('gps-new-entity-place', {
        latitude: feature.geometry.coordinates[1],
        longitude: feature.geometry.coordinates[0]
      });
      const box = document.createElement("a-box");
      box.setAttribute("scale", { x: 20, y: 20, z: 20 });
      box.setAttribute('material', { color: 'red' });
      box.setAttribute("position", { x: 0, y: 20, z: 0 }); // 20 m above the POI point
      const text = document.createElement("a-text");
      text.setAttribute("look-at", "[gps-new-camera]");
      text.setAttribute("scale", { x: 100, y: 100, z: 100 });
      text.setAttribute("value", feature.properties.name);
      text.setAttribute("align", "center");
      compound.appendChild(box);
      compound.appendChild(text);
      document.querySelector("a-scene").appendChild(compound);
    });
  });
};
```

GeoJSON notes: `features[].geometry.coordinates` is `[lon, lat]`; `properties.name` and `properties.amenity` (restaurant, cafe, ...) describe the POI; `properties.osm_id` is a stable OpenStreetMap ID for deduplication. The Hikar server (`hikar.org/webapp/map`) covers Europe and Turkey only — use your own GeoJSON/OSM endpoint elsewhere.

## three.js location-based API

Classes `THREEx.LocationBased`, `THREEx.WebcamRenderer`, `THREEx.DeviceOrientationControls` — full method lists (`startGps`, `fakeGps`, `add`, `lonLatToWorldCoords`, `setElevation`, `on('gpsupdate' | 'gpserror')`, ...) in [01-threejs-api](01-threejs-api.md). Import via npm + bundler:

```javascript
import * as THREEx from '@ar-js-org/ar.js/three.js/build/ar-threex-location-only.js'
```

## Limitations

- Device needs GPS + accelerometer + magnetometer.
- Sensor miscalibration can give wrong north (device hardware issue; three.js issue #22654).
- Camera feed can appear stretched away from screen center — reduced placement accuracy off-center (open issue; LocAR is tracking this).
- Indoor use works but with low precision.
- iOS requires user actions to enable geolocation — heed browser/AR.js alerts.
