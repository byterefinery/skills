# Solvers and Articulations

## Overview

Articulation solvers are **PhysX-only**. They provide hierarchical joint chains for robotics, procedural animation, and complex mechanical systems.

## Creating a Solver

```js
const solver = phy.add({
    type: 'solver',
    name: 'myRobot',
    needData: true,    // enable data feedback from physics
});
```

## Adding Bones

Bodies are added to the solver by setting the `solver` property:

```js
phy.add({
    type: 'box',
    name: 'bone1',
    size: [1, 1, 1],
    pos: [0, 5, 0],
    mass: 1,
    solver: 'myRobot',    // associate with solver
});

phy.add({
    type: 'box',
    name: 'bone2',
    size: [1, 1, 1],
    pos: [0, 7, 0],
    mass: 1,
    solver: 'myRobot',
});
```

## Adding Joints to Solver

```js
solver.addJoint({
    name: 'joint1',
    type: 'hinge',         // joint type
    b1: 'bone1',
    b2: 'bone2',
    pos1: [0, 0.5, 0],
    pos2: [0, -0.5, 0],
    axis1: [0, 0, 1],
    axis2: [0, 0, 1],
    limits: [
        ['z', -90, 90],   // [axis, min, max]
    ],
    target: [
        ['z', 0],          // [axis, value] — initial target
    ],
});
```

### Joint Drive Types

```js
solver.addJoint({
    name: 'joint1',
    type: 'hinge',
    b1: 'bone1',
    b2: 'bone2',
    // stiffness, damping, forceLimit, acceleration drive flag
    drives: [['z', 100000, 0, Infinity, true]],
});
```

## Solver Methods

```js
// Start articulation simulation
solver.start();

// Stop articulation simulation
solver.stop();

// Common initialization
solver.commonInit();

// Drive joints with delta time
solver.driveJoints(dt);

// Set angles with animation
const promise = solver.setAngles(angles, time);
await promise;  // resolves when animation completes

// Dispose — removes all bones
solver.dispose();
```

## Angle Animation

```js
// Animate multiple joints to target angles
const angles = [45, -30, 60];  // one angle per joint
const time = 1.0;               // animation speed

await solver.setAngles(angles, time);
```

### Individual Joint Pose

```js
const joint = solver.joints[0];
joint.pose(targetAngle, speed);

// targetAngle: clamped to joint limits
// speed: animation speed (higher = faster)
```

## Joint Data Feedback

When `needData: true`, the solver reads back joint state each frame:

```js
solver.joints.forEach(j => {
    console.log(j.data.target);
    // {
    //     x: 0, y: 0, z: 0,    // linear target
    //     rx: 0, ry: 0, rz: 0, // rotational target
    //     count: 0,             // update counter
    // }
});
```

## Solver Joint Properties

```js
joint.name          // joint name
joint.solver        // parent solver reference
joint.current       // current angle value
joint.target        // target angle value
joint.start         // animation start value
joint.time          // animation speed
joint.isDrive       // whether joint is currently being driven
joint.min           // minimum limit
joint.max           // maximum limit
joint.driveType     // drive axis ('x', 'y', or 'z')
joint.nup           // next update payload (null when idle)
```

## Gotchas

- **PhysX only** — articulation solvers are not available on any other backend.
- **`needData: true`** — must be set to enable joint data feedback. Without it, `solver.joints[k].data.target` won't update.
- **`type: 'fixe'` joints** are added to the solver but not tracked in `solver.joints` array (they don't have drives).
- **`setAngles()` returns a Promise** — resolves when all joint animations complete.
- **Angle clamping** — target angles are automatically clamped to `[min, max]` limits.
- **`driveJoints(dt)`** — must be called each frame with delta time to update animations.
- **Bone names are tracked** — `solver.bones` array stores all bone names for cleanup via `solver.dispose()`.
- **Max 20 solvers** — configurable in `Config.js Max.solver`.
- **Solver joints use 7 floats each** — `[x, y, z, rx, ry, rz, count]` in the physics array.
