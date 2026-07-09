# Movement

## `this.move()`

Basic movement that applies `speed`, `direction`, and `gravity`. No collision checking.

```js
// OnStep
this.hspeed = actions.MoveX.value * 200;
this.vspeed = actions.MoveY.value * 200;
this.move();
```

### With Gravity

```js
// OnCreate
this.gravity = 500;
this.gravityDir = 270; // Downward (270° in ct.js coords)

// OnStep
this.move();
```

### Following Another Copy

```js
var character = templates.list['Character'][0];
if (templates.valid(character)) {
    this.speed = 300;
    this.direction = u.pointDirection(this.x, this.y, character.x, character.y);
} else {
    this.speed = 0;
}
this.move();
```

## `this.moveBullet(cgroup, [precision])`

Continuous collision-checked movement. Prevents tunneling through thin walls. Steps through movement, checking collisions at each step.

```js
// OnStep
this.moveBullet('Solid');
```

### With Precision

```js
// For fast projectiles, set precision between radius and diameter
this.moveBullet('Solid', 8);
```

### Checking Collision Result

```js
var obstacle = this.moveBullet('Solid');
if (obstacle && templates.isCopy(obstacle)) {
    obstacle.kill = true;
    this.kill = true;
}
// obstacle is: false (no contact), true (tile contact), or a copy
```

## `this.moveSmart(cgroup, [precision])`

Axis-separated continuous collision checking. Allows "sliding" along obstacles.

```js
// OnStep — top-down movement
this.hspeed = actions.MoveX.value * 200;
this.vspeed = actions.MoveY.value * 200;
this.moveSmart('Solid');
```

### Platformer Pattern

```js
// OnCreate
this.gravity = 500;
this.gravityDir = 270;

// OnStep
this.hspeed = actions.MoveX.value * 200;

// Check for ground
if (place.occupied(this, this.x, this.y + 1, 'Solid')) {
    if (actions.Jump.pressed) {
        this.vspeed = -600;
    }
}

var collided = this.moveSmart('Solid');

// Reset vertical speed on collision
if (collided && collided.y) {
    this.vspeed = 0;
}
```

### Return Value

Returns `false` (no contact) or an object `{ x, y }` where each property is `false`, `true` (tile), or a copy.

## Grid-Based Movement

### Instant Grid Jump

```js
// OnStep
if (actions.MoveX.pressed) {
    this.x += Math.sign(actions.MoveX.value) * 64;
}
if (actions.MoveY.pressed) {
    this.y += Math.sign(actions.MoveY.value) * 64;
}
```

### Snapped Movement

```js
// OnStep
if (this.x % 64 === 0 && this.y % 64 === 0) {
    this.speed = 0;
    if (actions.MoveX.pressed) {
        this.hspeed = Math.sign(actions.MoveX.value) * 8;
    }
    if (actions.MoveY.pressed) {
        this.vspeed = Math.sign(actions.MoveY.value) * 8;
    }
}
this.x += this.hspeed;
this.y += this.vspeed;
```

### Tween-Based Grid Movement

```js
// OnCreate
this.moving = false;

// OnStep
if (!this.moving) {
    if (actions.MoveX.pressed) {
        this.moving = true;
        tween.add({
            obj: this,
            fields: { x: this.x + Math.sign(actions.MoveX.value) * 64 },
            duration: 650
        }).then(() => { this.moving = false; });
    }
    if (actions.MoveY.pressed) {
        this.moving = true;
        tween.add({
            obj: this,
            fields: { y: this.y + Math.sign(actions.MoveY.value) * 64 },
            duration: 650
        }).then(() => { this.moving = false; });
    }
}
```

## Collision Avoidance Strategies

### Strategy 1: Move then retreat

```js
this.move();
if (place.occupied(this, 'Solid')) {
    this.x = this.xprev;
    this.y = this.yprev;
}
```

### Strategy 2: Repel from obstacle

```js
var obstacle = place.occupied(this, 'Solid');
if (obstacle && templates.isCopy(obstacle)) {
    var repelDir = u.pointDirection(obstacle.x, obstacle.y, this.x, this.y);
    this.x += u.ldx(3, repelDir);
    this.y += u.ldy(3, repelDir);
} else {
    this.move();
}
```

## `this.addSpeed(spd, dir)`

Add a speed vector in a given direction:

```js
this.addSpeed(100, 90); // Add 100 px/s downward
```

## Movement Comparison

| Method | Collision | Sliding | Best For |
|---|---|---|---|
| `this.move()` | No | N/A | Space shooters, bullets without collision |
| `this.moveBullet()` | Yes, continuous | No | Projectiles, precise movement |
| `this.moveSmart()` | Yes, axis-separated | Yes | Characters, platformers, top-down |
| Direct `x/y` manipulation | No | N/A | Grid-based, tween-based, custom |

## Gotchas

- **`this.move()` includes gravity** — gravity is applied before position update.
- **`this.move()` already uses `u.time`** — speed values are pixels per second.
- **`this.moveBullet()` can be expensive** — many bullets with low precision cause many collision checks.
- **`this.moveSmart()` returns object** — check `collided.x` and `collided.y` separately.
- **`this.moveBullet()` doesn't clip** — stops right next to obstacle, doesn't push out.
- **`this.xprev/yprev` updated after OnDraw** — they reflect the position at the start of the frame.
- **Grid movement and `u.delta`** — real-time movement won't snap pixel-perfectly due to lag compensation.
- **`this.moveSmart()` for platformers** — reset `vspeed` on Y collision to prevent smashing into platforms at cosmic speed.
- **`this.moveBullet()` precision** — set between projectile radius and diameter for best results.
- **`this.addSpeed()` is additive** — it adds to existing speed, doesn't replace it.
