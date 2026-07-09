# ct.place — Collision Module

The `place` catmod provides collision checking and advanced movement. Must be enabled in project settings.

## Collision Checks

### `place.occupied(me, [x, y, cgroup])`

Finds a copy or tile colliding with `me`. Returns the colliding object or `false`.

```js
if (place.occupied(this, 'Solid')) {
    this.kill = true;
}

// Check at different coordinates
if (place.occupied(this, this.x + 10, this.y, 'Solid')) {
    // Obstacle 10px to the right
}

// Bullet-enemy collision
var enemy = place.occupied(this, 'Enemies');
if (templates.isCopy(enemy)) {
    this.kill = true;
    enemy.kill = true;
}
```

### `place.free(me, [x, y, cgroup])`

Checks if a position is free. Returns `true` if no obstruction.

```js
if (actions.Click.released && place.free(this)) {
    templates.copy('Tree', this.x, this.y);
}
```

### `place.meet(me, [x, y,] template)`

Checks collision with copies of a specific template. Returns the first colliding copy or `false`.

```js
if (place.meet(this, 'Hero')) {
    rooms.switch('Level_02');
}
```

### `place.collide(c1, c2)`

Direct collision check between two copies. Returns `true` if colliding.

### `place.copies(me, [x, y, cgroup])`

Collision check against copies only (no tiles). Faster in tilemap-heavy rooms.

### `place.tiles(me, [x, y, cgroup])`

Collision check against tiles only.

### Multiple Collision Checks

```js
// Returns array of all colliding objects
var enemies = place.occupiedMultiple(this, 'Enemies');
if (enemies) {
    for (const enemy of enemies) {
        enemy.kill = true;
    }
}
```

Available: `place.occupiedMultiple()`, `place.meetMultiple()`, `place.copiesMultiple()`, `place.tilesMultiple()`.

## Movement Methods

### `place.moveAlong(me, direction, maxLength, [cgroup, stepSize])`

Moves copy step-by-step until `maxLength` is reached or obstacle is hit.

### `place.moveByAxes(me, dx, dy, [cgroup, stepSize])`

Moves by X and Y axes separately. Continues on one axis if blocked on the other.

### `place.go(me, x, y, length, [cgroup])`

Simple obstacle avoidance to reach target point.

```js
place.go(this, targetX, targetY, 100, 'Solid');
```

## Tracing Functions

### `place.traceLine(x1, y1, x2, y2, [cgroup])`

Traces a line between two points. Returns the first colliding copy or `false`.

### `place.traceLineMultiple(x1, y1, x2, y2, [cgroup])`

Returns all colliding objects along the line.

### `place.traceRay(x, y, direction, length, [cgroup])`

Traces a ray from a point in a direction. Returns the first colliding copy or `false`.

## Tilemap Collisions

### `place.enableTilemapCollisions(tilemap, cgroup)`

Enables collision checking for a tilemap. All tiles in the tilemap become part of the collision group.

```js
var tilemap = tilemaps.create(-100);
// ... add tiles ...
tilemap.cache();
place.enableTilemapCollisions(tilemap, 'Solid');
```

## Collision Groups

Set in template editor or tile layer settings. Strings used in collision checks:

```js
// Template editor → Colliding groups field
this.cgroup = 'Solid';

// Runtime change
this.cgroup = 'Enemy'; // Now detected under 'Enemy' group
```

## Gotchas

- **`place` module must be enabled** — `this.moveBullet()`, `this.moveSmart()`, `place.occupied()` all require the place catmod.
- **Collision groups are strings** — set consistently in template/tile editor. Case-sensitive.
- **`place.occupied()` returns first collision** — use `place.occupiedMultiple()` for all collisions.
- **`place.copies()` is faster than `place.occupied()`** — skip tile checks when you know there are no relevant tiles.
- **`place.meet()` checks template name** — not collision group. Use when you need specific template collisions.
- **`this.cgroup` can be changed at runtime** — useful for one-way platforms or toggleable barriers.
- **Tilemap must be cached before enabling collisions** — call `tilemap.cache()` before `place.enableTilemapCollisions()`.
- **`place.traceLine()` returns first hit** — use `traceLineMultiple()` for all hits along the line.
- **`place.go()` doesn't need `this.move()`** — it handles movement internally.
- **`this.myCollidingGroups` is a Set** — configured in template editor. Not used automatically in JS/CS code; must be passed explicitly.
