# Characters

## Hero Character Controller

phy includes a built-in character controller (`Hero`) that uses impulse-based physics rather than native engine character controllers. This approach works across all backends.

### Creating a Character

```js
const hero = phy.add({
    type: 'character',
    name: 'player',
    radius: 0.3,           // character collision radius
    height: 1.81,          // character height
    floating: false,       // enable floating ray mode
    useImpulse: false,     // use impulse-based movement
    isPlayer: true,        // mark as player (for camera follow)
    autoLOD: false,        // automatic LOD
});
```

### Character Options

The Hero has extensive tunable parameters:

```js
hero.option = {
    // Speed
    maxVelLimit: 1,            // max movement velocity
    turnVelMultiplier: 0.2,    // velocity reduction when turning
    turnSpeed: 15,             // rotation speed
    sprintMult: 2.94,          // sprint speed multiplier
    crouchMult: 0.442,         // crouch speed multiplier
    crawlMult: 0.506,          // crawl speed multiplier

    // Jump
    jumpVel: 5,                // jump velocity
    jumpForceToGroundMult: 5,  // force applied to ground on jump
    slopJumpMult: 0.25,        // slope jump reduction
    sprintJumpMult: 1.2,       // sprint jump boost
    airDragMultiplier: 0.2,    // air drag

    // Movement
    slowDown: 0.9,             // drag damping
    accDeltaTime: 8,           // acceleration delta time
    rejectVelMult: 4,          // velocity rejection multiplier
    moveImpulsePointY: 0.5,    // impulse application height
    camFollowMult: 11,         // camera follow speed

    // Gravity
    initialGravityScale: 1,    // normal gravity multiplier
    fallingGravityScale: 2.5,  // increased gravity when falling
    fallingMaxVel: -20,        // max falling velocity

    // Floating Ray
    floatHeight: 0.3,          // floating height above ground
    rayHitForgiveness: 0.1,    // ray hit tolerance
    Spring: 4,                 // spring force
    Damping: 0.5,              // spring damping
    forceMultiply: 5,          // force multiplier

    // Slope
    slopeMaxAngle: 1,          // max walkable slope (radians)
    slopeRayLength: radius + 3,// slope detection ray length
    slopeUpExtraForce: 0.1,    // extra force going uphill
    slopeDownExtraForce: 0.2,  // extra force going downhill

    // Auto Balance
    autoBalance: false,        // enable auto-balance
    autoBalanceSpring: 0.3,    // balance spring
    autoBalanceDamping: 0.03,  // balance damping
};
```

### Character Methods

```js
// Movement
hero.move();              // apply current movement input
hero.jump();              // jump
hero.crouch();            // crouch
hero.crawl();             // crawl
hero.sprint();            // sprint toggle

// State
hero.isGrounded();        // check if on ground
hero.getVelocity();       // current velocity
```

### Character with Model

```js
const hero = phy.add({
    type: 'character',
    name: 'player',
    radius: 0.3,
    height: 1.81,
    mesh: characterModel,   // THREE.Object3D character model
    isPlayer: true,
});
```

### Camera Follow

```js
// Set up camera controls
phy.setControl(controls);

// Follow the character
phy.follow('player', {
    // follow options
});

// Or follow by Object3D
phy.follow(hero);

// Stop following
phy.follow('');
```

### Key Input

phy manages keyboard input through its User system:

```js
// Set key state
phy.setKey('w', true);
phy.setKey('s', true);
phy.setKey('a', true);
phy.setKey('d', true);
phy.setKey('space', true);  // jump

// Get key state
const keys = phy.getKey();
```

## Auto Ragdoll

Create an automatic ragdoll from a skeleton:

```js
const ragdoll = phy.autoRagdoll({
    name: 'ragdoll',
    skeleton: skeleton,      // THREE.Skeleton or Object3D with bones
    // ragdoll options
});

// ragdoll.model is the THREE.Object3D to add to scene
```

## Gotchas

- **Not native character controller** — phy's Hero uses impulse-based physics, not the engine's built-in character controller. This works on all backends but has different behavior.
- **`floating: true`** — enables spring-based floating above ground using a downward ray. Adjust `Spring`, `Damping`, and `floatHeight` for desired feel.
- **`useImpulse: true`** — uses direct impulse application instead of velocity setting. Better for interaction with other bodies.
- **Character takes control** — call `phy.control('player')` to give input to the character. Call `phy.control(null)` to release.
- **Characters don't respond to `phy.control()`** — the character system has its own input handling. `phy.control()` is for vehicles.
- **Slope detection** — uses a separate ray from the character center. Adjust `slopeMaxAngle` (in radians) for walkable slopes.
- **Auto-balance** — when enabled, applies corrective torque to keep the character upright. Tune `autoBalanceSpring` and `autoBalanceDamping`.
- **`isPlayer: true`** — marks the character for camera follow and input priority.
- **Height includes capsule caps** — `height` is the total character height including the hemispherical caps.
- **Ragdoll vs Character** — `autoRagdoll` creates a physics-driven skeleton. `type: 'character'` creates a capsule-based controller. They are different systems.
