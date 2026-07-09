# Resources (res)

## Getting Textures

```js
// Get all frames as array
var frames = res.getTexture('PlayerShip');

// Get specific frame
var frame0 = res.getTexture('PlayerShip', 0);

// Empty texture
var empty = res.getTexture(-1);
```

## Asset Tree

Enable in project settings (Export tab). Adds `res.tree` with browsable project structure.

```js
// Top-level assets and folders
res.tree; // Array of { name, type, entries? }

// Types: 'template', 'room', 'sound', 'style', 'texture', 'tandem', 'font', 'behavior', 'folder'

// Get children of a folder
res.getChildren('/Core/Player');

// Get by type
res.getOfType('texture', 'Enemies/Ships');

// Get all (recursive)
res.getAll('/Enemies');
res.getAllOfType('texture', '/Enemies');
```

### Path Format

```js
// All equivalent
res.getChildren('/Player/Core');
res.getChildren('Player/Core/');
res.getChildren('Player/Core');
```

Omit path or use `/` for project root.

## Loading Resources

### Load Script

```js
res.loadScript('path/to/script.js'); // Returns Promise<void>
```

### Load Texture

```js
res.loadTexture('path/to/image.png', 'TextureName', {
    anchor: { x: 0, y: 0 }
}).then(() => {
    ct.backgrounds.add('TextureName', 0, -100);
});
```

### Load Atlas

```js
// Load Texture Packer compatible .json + image
res.loadAtlas('path/to/atlas.json').then(textureNames => {
    // textureNames: array of loaded texture names
});

// Unload
res.unloadAtlas('path/to/atlas.json');
```

### Load Bitmap Font

```js
res.loadBitmapFont('path/to/font.xml').then(fontName => {
    // Use the font
});

res.unloadBitmapFont('path/to/font.xml');
```

## Gotchas

- **`res.getTexture()` returns an array** — use `[0]` for single frame or specify frame index.
- **`-1` returns empty texture** — `res.getTexture(-1)` gives a blank texture.
- **`res.tree` is opt-in** — enable in project Export settings. Adds to build size.
- **`res.tree` may expose asset names** — consider privacy for shipped games.
- **`loadTexture` anchor** — `{ x: 0, y: 0 }` = top-left; `{ x: 0.5, y: 0.5 }` = center.
- **Atlas must be Texture Packer compatible** — standard .json + .png format.
- **`loadScript` executes immediately** — the script runs in global scope.
- **Bitmap font returns font name** — use the resolved name with `PIXI.BitmapText`.
- **`res.getOfType()` filters by type** — type strings: `'texture'`, `'template'`, `'sound'`, etc.
- **Paths are case-sensitive** — match the folder structure in ct.js IDE exactly.
