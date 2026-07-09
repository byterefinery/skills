# Inputs and Actions

## Actions Overview

Actions are an abstraction layer over input methods. One action can listen to keyboard, gamepad, pointer, and virtual keys simultaneously. Code references actions by name, not specific keys.

Actions are defined in ct.js IDE: **Project → Actions and input methods**. Each action maps to `actions.ActionName`.

### Action Properties

| Property | Type | Description |
|---|---|---|
| `value` | `number` | Scalar value between -1 and 1. 0 = no input. |
| `pressed` | `boolean` | `true` only on the frame the action became active |
| `down` | `boolean` | `true` while the action is active (held) |
| `released` | `boolean` | `true` only on the frame the action became inactive |

### Action Methods

```js
actions.Move.methodExists(code);           // Check if method is bound
actions.Move.addMethod(code, multiplier);  // Add input method
actions.Move.removeMethod(code);           // Remove input method
actions.Move.setMultiplier(code, value);   // Change multiplier
actions.Move.update();                     // Recalculate value
actions.Move.reset();                      // Reset state (value=0, pressed/down/released=false)
```

## Creating Actions Programmatically

```js
inputs.addAction('Move', [
    { code: 'keyboard.ArrowLeft', multiplier: -1 },
    { code: 'keyboard.ArrowRight', multiplier: 1 },
    { code: 'keyboard.KeyA', multiplier: -1 },
    { code: 'keyboard.KeyD', multiplier: 1 }
]);

inputs.removeAction('Move');
```

## Input Method Codes

Input methods use dot-notation codes:

| Provider | Code Format | Examples |
|---|---|---|
| `keyboard` | `keyboard.KeyName` | `keyboard.Space`, `keyboard.KeyA`, `keyboard.ArrowLeft` |
| `pointer` | `pointer.Property` | `pointer.primary`, `pointer.secondary`, `pointer.x`, `pointer.y` |
| `gamepad` | `gamepad.Property` | `gamepad.button0`, `gamepad.leftStickX` |
| `vkeys` | `vkeys.KeyName` | Virtual key codes for on-screen controls |

## Multipliers

Multipliers flip or scale the action value:

- `1` — positive direction (default)
- `-1` — negative direction (left, up)
- `0.5` — half strength

For directional actions (e.g., horizontal movement), use `-1` for left/up and `1` for right/down.

## Typical Action Setup

### Platformer (horizontal movement)

```
MoveX: ArrowLeft(-1), ArrowRight(1), KeyA(-1), KeyD(1)
MoveY: ArrowUp(-1), ArrowDown(1), KeyW(-1), KeyS(1)
Jump: Space, pointer.primary
```

### Top-down shooter

```
MoveX: ArrowLeft(-1), ArrowRight(1), KeyA(-1), KeyD(1)
MoveY: ArrowUp(-1), ArrowDown(1), KeyW(-1), KeyS(1)
Shoot: Space, pointer.primary
```

## Usage Patterns

### Scalar movement

```js
this.hspeed = actions.MoveX.value * 300;
this.vspeed = actions.MoveY.value * 300;
this.move();
```

### Single press

```js
if (actions.Jump.pressed) {
    this.vspeed = -400;
}
```

### Continuous while held

```js
if (actions.Shoot.down) {
    this.fireRate -= u.time;
    if (this.fireRate <= 0) {
        templates.copy('Bullet', this.x, this.y);
        this.fireRate = 0.2;
    }
}
```

### Release detection

```js
if (actions.Pause.released) {
    // Handle pause toggle
}
```

## Pointer Object

The `pointer` global object tracks mouse/touch position:

```js
pointer.x;  // Pointer X in UI coordinates
pointer.y;  // Pointer Y in UI coordinates
```

Convert to game coordinates for gameplay interactions:

```js
var gamePos = u.uiToGameCoord(pointer.x, pointer.y);
templates.copy('Fruit', gamePos.x, gamePos.y);
```

## Gotchas

- **Actions must be defined in IDE** — `actions.ActionName` only works if the action exists in project settings.
- **`pressed` is frame-accurate** — `true` only on the exact frame the action became active.
- **`value` is -1 to 1** — keyboard/pointer give discrete values; gamepad sticks give analog values.
- **Multipliers matter for directional actions** — without `-1` for left/up, both directions push positive.
- **`pointer.x/y` are UI coordinates** — convert with `u.uiToGameCoord()` before using for gameplay.
- **`inputs.addAction()` creates at runtime** — actions created this way persist until `inputs.removeAction()`.
- **`gamepad` module must be enabled** — gamepad input requires the gamepad catmod.
- **`vkeys` are on-screen controls** — virtual keys are touch/pointer controls drawn on screen.
- **`pointer.polyfill` for older browsers** — enables pointer events on browsers without native support.
- **`keyboard.polyfill` for mobile** — enables keyboard events on mobile browsers.
