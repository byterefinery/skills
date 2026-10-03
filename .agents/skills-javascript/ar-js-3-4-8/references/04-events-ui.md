# UI and events

## Custom events

| Event | Description | Payload | Feature |
|---|---|---|---|
| `arjs-video-loaded` | camera video stream appended to DOM | `{ detail: { component: <HTMLElement> } }` | all |
| `camera-error` | camera stream could not be retrieved | `{ error: <Error> }` | all |
| `camera-init` | camera stream retrieved correctly | `{ stream: <MediaStream> }` | all |
| `markerFound` | a marker (marker-based) or image (NFT) was found | - | marker + NFT |
| `markerLost` | marker/image lost | - | marker + NFT |
| `arjs-nft-loaded` | all NFT descriptors fully loaded | - | NFT |
| `gps-camera-update-positon` | `gps-camera` updated its position (sic — note the docs' spelling) | `{ detail: { position: <GeolocationCoordinates>, origin: <GeolocationCoordinates> } }` | location-based |
| `gps-entity-place-update-positon` | `gps-entity-place` updated its position | `{ detail: { distance: <Number> } }` | classic + projected only |
| `gps-entity-place-added` | entity was added | `{ detail: { component: <HTMLElement> } }` | classic + projected only |
| `gps-camera-origin-coord-set` | origin coordinates set | - | classic + projected only |
| `gps-entity-place-loaded` | entity loaded (A-Frame `loaded` semantics) | `{ detail: { component: <HTMLElement> } }` | classic + projected only |

Note: the location-based event names contain the typo `update-positon` in the official docs — verify against the actual source if binding programmatically; the bundled `basic-js` example listens to `gps-camera-update-position` (with the final `i`), which is what the new-location-based component fires.

### Built-in loader removal

Both NFT and location-based apps automatically remove any DOM element with class `.arjs-loader` once descriptors are loaded / the origin GPS position is set. Style it however you like; the removal is free:

```html
<div class="arjs-loader"><div>Loading, please wait...</div></div>
```

## Trigger actions on marker/image found

Use a tiny A-Frame component listening on the scene. Redirect-on-scan example:

```html
<script>
  AFRAME.registerComponent('markerhandler', {
    init: function () {
      this.el.sceneEl.addEventListener('markerFound', () => {
        window.location = 'https://github.com/AR-js-org/AR.js';
      });
    }
  });
</script>
...
<a-nft markerhandler type="nft" url="/descriptors/trex"></a-nft>
```

The same works on `a-marker` (e.g., `detectionMode: mono_and_matrix; matrixCodeType: 3x3` with `type='barcode' value='7'`).

### Getting distance from a marker

```javascript
window.addEventListener('load', () => {
  const camera = document.querySelector('[camera]');
  const marker = document.querySelector('a-marker');
  let check;

  marker.addEventListener('markerFound', () => {
    let cameraPosition = camera.object3D.position;
    let markerPosition = marker.object3D.position;
    let distance = cameraPosition.distanceTo(markerPosition);

    check = setInterval(() => {
      cameraPosition = camera.object3D.position;
      markerPosition = marker.object3D.position;
      distance = cameraPosition.distanceTo(markerPosition);
      console.log(distance);
    }, 100);
  });

  marker.addEventListener('markerLost', () => {
    clearInterval(check);
  });
});
```

## Overlayed DOM UI

Normal HTML on the body, outside the `a-scene`, behaves like any website — buttons, HUDs, modals. Position with CSS, wire with normal DOM events:

```html
<div class="buttons"><button class="say-hi-button">SAY HI!</button></div>
<style>
  .buttons { position: absolute; bottom: 0; left: 0; width: 100%; height: 5em;
             display: flex; justify-content: center; align-items: center; z-index: 10; }
  .say-hi-button { padding: 0.25em; border-radius: 4px; border: none;
                   background: white; color: black; width: 4em; height: 2em; }
</style>
<script>
  window.onload = () => {
    document.querySelector(".say-hi-button")
      .addEventListener("click", () => { /* change a-scene/entities, open links, ... */ });
  };
</script>
```

## Clicking AR content

Taps on AR entities use standard A-Frame raycasting (`raycaster`/`cursor` components) — not AR.js. Gesture zoom/rotate of the 3D content is also A-Frame-based and applies to the whole `a-scene`, so it suits single-marker/image scenes. See the A-Frame docs for event and DOM APIs, and the `click-places` location-based example.
