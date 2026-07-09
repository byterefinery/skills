# Tilemaps

## Creating Tilemaps

```js
// Create a tilemap at a specific depth
var tilemap = tilemaps.create(-100);

// Add tiles
tilemaps.addTile(tilemap, 'TextureName', x, y, [frame]);

// Or use the tilemap's own method
tilemap.addTile('TextureName', x, y, [frame]);
```

### Tilemap Methods

| Method | Description |
|---|---|
| `tilemaps.create(depth)` | Create new tilemap, returns `Tilemap` instance |
| `tilemaps.addTile(tilemap, textureName, x, y, [frame])` | Place a tile, returns `PIXI.Sprite` |
| `tilemaps.cache(tilemap, [chunkSize])` | Cache for performance (no further editing) |
| `tilemaps.cacheDiamond(tilemap, [chunkSize])` | Cache with diamond chunks (for isometric) |

### Tilemap Instance Methods

| Method | Description |
|---|---|
| `tilemap.addTile(textureName, x, y, [frame])` | Place a tile |
| `tilemap.cache([chunkSize])` | Cache tilemap |
| `tilemap.cacheDiamond([chunkSize])` | Diamond cache (isometric) |

Tilemaps derive from `PIXI.Container` — they can be tinted, transformed, and moved.

## Caching

Caching groups tiles into large chunks and turns them into bitmaps. **Once cached, a tilemap cannot be edited.**

```js
tilemap.cache();           // Default chunk size: 1024
tilemap.cache(512);        // Smaller chunks
tilemap.cacheDiamond();    // For isometric games
```

### Diamond Caching

Packs tiles into rhombus-shaped chunks, sorted top to bottom. Fixes seam issues for isometric games.

```js
// Tiles should be on a flat plane
// For elevation effects, shift with tile.pivot.y
tilemap.cacheDiamond();
```

## Examples

### Row of tiles with different frames

```js
this.tilemap = tilemaps.create(-100);
for (let i = 0; i < 10; i++) {
    tilemaps.addTile(this.tilemap, 'Tiles', i * 64, 0, i);
}
this.tilemap.cache();
```

### Procedural map with noise

```js
var tilemap = tilemaps.create(-100);
noise.setSeed(); // Randomize seed

for (var x = 0; x < camera.width / 64; x++) {
    for (var y = 0; y < camera.height / 64; y++) {
        var value = noise.simplex2d(x / 7, y / 7);
        if (value > 0) {
            var tile = tilemap.addTile('RockTile', x * 64, y * 64);
            tile.alpha = value * 0.5 + 0.5;
        }
    }
}

tilemap.cache();
place.enableTilemapCollisions(tilemap, 'Solid');
```

## Tilemap Collisions

```js
// Enable collision checking for a tilemap
place.enableTilemapCollisions(tilemap, 'Solid');
```

Tiles become part of the specified collision group. `place.occupied()` and movement methods will detect them.

## Gotchas

- **Cache before enabling collisions** — call `tilemap.cache()` before `place.enableTilemapCollisions()`.
- **Cannot edit after caching** — cached tilemaps are frozen. Add all tiles before caching.
- **`addTile` returns `PIXI.Sprite`** — tweak `alpha`, `tint`, etc. before caching.
- **Diamond caching needs flat plane** — tiles should be on the same plane. Use `tile.pivot.y` for elevation effects.
- **`chunkSize` default is 1024** — larger chunks = better performance but larger memory usage.
- **Tilemaps are `PIXI.Container`** — can be tinted, rotated, scaled, moved.
- **Depth positioning** — use negative depth (e.g., `-100`) for background tilemaps.
- **`noise` module required for procedural generation** — must be enabled in project settings.
- **`noise.setSeed()` randomizes** — call for different patterns each game start.
