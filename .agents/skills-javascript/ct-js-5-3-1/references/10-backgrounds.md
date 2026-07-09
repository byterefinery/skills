# Backgrounds

## Creating Backgrounds

```js
// Add a background
var bg = backgrounds.add('TextureName', [frame], [depth], [container]);

// Properties
bg.alpha = 0.5;        // Opacity
bg.tint = 0x999999;    // Color tint
bg.movementX = 1;      // Horizontal parallax movement
bg.movementY = 0.5;    // Vertical parallax movement
```

### Parameters

| Parameter | Type | Description |
|---|---|---|
| `texName` | `string` | Texture name |
| `frame` | `number` | Frame index (default 0) |
| `depth` | `number` | Depth (default 0, negative for behind) |
| `container` | `PIXI.Container` | Where to place (default `ct.room`) |

## Background Properties

| Property | Type | Description |
|---|---|---|
| `alpha` | `number` | Opacity (0-1) |
| `tint` | `number` | Color tint (hex) |
| `movementX` | `number` | Parallax horizontal movement |
| `movementY` | `number` | Parallax vertical movement |
| `x`, `y` | `number` | Position |
| `scale` | `object` | Scale |
| `visible` | `boolean` | Visibility |

## Accessing Backgrounds

```js
// Get backgrounds by texture name
if (backgrounds.list['BG_Sand']) {
    var bg = backgrounds.list['BG_Sand'][0];
    bg.tint = 0x999999;
}

// Backgrounds without a texture name go into backgrounds.list.OTHER
```

## Parallax Movement

```js
// Horizontal scrolling background
var bg = backgrounds.add('BG_SkyClouds', 0, -1000);
bg.alpha = 0.5;
bg.movementX = 1;
bg.movementY = 0;
```

`movementX` and `movementY` control how much the background moves relative to the camera. Values of `1` follow the camera fully; `0` stays fixed.

## Gotchas

- **`backgrounds.list` keyed by texture name** — check if the array exists before accessing elements.
- **Backgrounds without texture name → `backgrounds.list.OTHER`** — unnamed backgrounds go here.
- **Depth ordering** — use negative depth (e.g., `-1000`) for backgrounds behind gameplay.
- **`movementX/Y` are parallax factors** — not speed values. `1` = follows camera fully, `0` = fixed.
- **Backgrounds are always drawn before copies at same depth** — set depth lower than gameplay copies.
- **`Background` class docs** — see the Background class reference for full property list.
