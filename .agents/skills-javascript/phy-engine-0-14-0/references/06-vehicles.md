# Vehicles

## Overview

Vehicle simulation is available on **PhysX** and **Ammo** backends only. Havok, Jolt, Rapier, and Oimo do not support vehicles.

phy provides three vehicle creation methods:

1. **`phy.add({ type: 'vehicle' })`** — full car with chassis + wheels (PhysX and Ammo)
2. **`phy.vehicle({ type: 'raycar' })`** — RayCar vehicle (raycast-based, PhysX and Ammo)
3. **`phy.vehicle({ type: 'kart' })`** — Kart vehicle (arcade-style)
4. **`phy.vehicle({ type: 'helico' })`** — Helicopter vehicle

## Car (Full Vehicle)

```js
const car = phy.add({
    type: 'vehicle',
    name: 'myCar',
    mass: 2000,                    // total mass
    size: [1.7, 1.0, 5.0],        // chassis size [x, y, z]
    massCenter: [0, 0.55, 1.594], // center of mass offset
    chassisPos: [0, 0.83, 0],     // chassis visual offset
    numWheel: 4,                   // number of wheels
    radius: 0.35,                  // front wheel radius
    radiusBack: 0.35,              // rear wheel radius
    deep: 0.3,                     // front wheel depth (width)
    deepBack: 0.3,                 // rear wheel depth
    wPos: [0.8, 0.1, 1.4],        // wheel positions [x, y, z]
    maxSteering: 24,               // max steering angle
    incSteering: 2,                // steering increment
    s_travel: 0.4,                 // suspension travel
    chassisMesh: carModel,         // THREE.Object3D chassis visual
    wheelMesh: wheelModel,         // THREE.Object3D wheel visual
    suspensionMesh: suspModel,     // THREE.Object3D suspension visual
});
```

### Wheel Positions

`wPos` defines wheel placement. Format: `[x, y, z]` or `[x, y, [z_front, z_rear]]`.

- `x`: half-track width (distance from center)
- `y`: ride height (0 = auto from radius)
- `z`: distance from center along Z axis

For 4 wheels, phy places them at ±x, ±z automatically.

### Chassis Shape

By default, the chassis uses a box collider. For custom shapes:

```js
phy.add({
    type: 'vehicle',
    chassisShape: customGeometry,  // BufferGeometry for convex hull
    chassisMesh: visualModel,      // visual mesh
    // ...
});
```

### Car Properties After Creation

```js
car.position          // THREE.Vector3
car.quaternion        // THREE.Quaternion
car.velocity          // linear velocity
car.angular           // angular velocity
car.steering          // current steering value (-1 to 1)
car.suspension        // array of suspension compression values
car.rolling           // array of wheel rotation angles
```

### Driving Controls

```js
// Apply driving input
phy.change({
    name: 'myCar',
    engineForce: 5000,     // engine torque
    brake: 0,              // brake force
    steering: 0.5,         // steering (-1 to 1)
});
```

### Respawn

```js
car.respawn({
    pos: [0, 2, 0],
    rot: [0, 0, 0],
    keepVelocity: false,
    keepRotation: true,
});
```

## RayCar

Raycast-based vehicle (lighter than full vehicle):

```js
const raycar = phy.vehicle({
    type: 'raycar',
    name: 'myRayCar',
    // similar parameters to car
});
```

## Kart

Arcade-style kart vehicle:

```js
const kart = phy.vehicle({
    type: 'kart',
    name: 'myKart',
    // simplified parameters
});
```

## Helicopter

```js
const heli = phy.vehicle({
    type: 'helico',
    name: 'myHeli',
    // helicopter-specific parameters
});
```

## Vehicle in Animation Loop

Vehicles are updated automatically during `phy.step()`. Their `position`, `quaternion`, wheel transforms, and suspension morphs are synced each frame.

## Gotchas

- **PhysX and Ammo only** — vehicles are not supported on Havok, Jolt, Rapier, or Oimo.
- **Wheel count** — supports 2 or 4 wheels. `numWheel` determines placement.
- **Suspension morphs** — if `suspensionMesh` is provided, morph targets `low` and `top` are used for compression visualization.
- **Brake visuals** — if `brakeMesh` is provided, brake disc visuals follow wheel rotation.
- **`s_travel`** — suspension travel distance. Affects suspension ratio calculation.
- **PhysX-specific** — uses `decaly = s_travel * 0.5` for suspension offset.
- **Mass center** — critical for realistic behavior. Default `[0, 0.55, 1.594]` works for typical car proportions.
- **Chassis shape** — when using `chassisShape`, the box size is auto-computed from the geometry bounding box.
- **Max 50 vehicles** — configurable in `Config.js Max.vehicle`.
