# Timers

## Creating Timers

```js
// Game timer (affected by pause/slow-mo)
var myTimer = timer.add(2500, 'invincibility');

// UI timer (unaffected by pause/slow-mo)
var uiTimer = timer.addUi(1000, 'ui-tick');

// Constructor form
var timer = new CtTimer(1000, 'test');
```

## Promise-Based Usage

```js
var myTimer = timer.add(2500, 'test');

myTimer.then(() => {
    this.invincible = false;
    console.log('Done!');
});

myTimer.catch((e) => {
    console.log('Timer removed', e);
    // Clean up on room switch
    this.invincible = false;
});
```

## Timer Properties

| Property | Type | Description |
|---|---|---|
| `time` | `number` | Time elapsed (milliseconds) |
| `timeLeft` | `number` | Time remaining (milliseconds) |
| `name` | `string\|false` | Timer name, or `false` if unnamed |
| `uiDelta` | `boolean` | Uses `u.timeUi` if `true`, `u.time` if `false` |
| `promise` | `Promise` | Internal promise |
| `done` | `boolean` | `true` if resolved |
| `rejected` | `boolean` | `true` if rejected |
| `settled` | `boolean` | `true` if resolved or rejected |

## Timer Methods

```js
myTimer.then(callback);     // On completion
myTimer.catch(callback);    // On rejection/interruption
myTimer.resolve();          // Trigger immediately
myTimer.reject();           // Stop (won't trigger then)
```

## Timer Patterns

### Repeating Timer

```js
function repeat() {
    timer.add(1000, 'repeat').then(() => {
        if (!this.kill) {
            // Do something
            repeat.call(this);
        }
    });
}
repeat.call(this);
```

### Conditional Timer

```js
timer.add(2000, 'check').then(() => {
    if (templates.valid(this) && !this.kill) {
        // Action
    }
});
```

### Chaining Timers

```js
timer.add(500, 'fade-start').then(() => {
    return timer.add(1000, 'fade-end');
}).then(() => {
    rooms.switch('NextLevel');
});
```

## Built-in Copy Timers

Each copy has six built-in timers (`timer1` through `timer6`), measured in seconds:

```js
// OnCreate
this.timer1 = 2; // 2 seconds

// OnStep
this.timer1 -= u.time;
if (this.timer1 <= 0) {
    // Timer expired
    this.timer1 = 2; // Reset
}
```

## Gotchas

- **`timer.add()` uses game time** — affected by pause (`pixiApp.ticker.speed = 0`). Use `timer.addUi()` for pause-independent timers.
- **Timers reject on room switch** — always use `.catch()` or check validity in `.then()`.
- **`timer.reject()` won't trigger `.then()`** — use `.catch()` for cleanup on rejection.
- **`timer.resolve()` triggers `.then()` immediately** — useful for manual triggering.
- **Built-in timers (`timer1`-`timer6`) are in seconds** — subtract `u.time`, not `u.delta`.
- **Built-in timers don't auto-reset** — manually reset after expiration.
- **`CtTimer.time` is elapsed time** — not remaining time. Use `timeLeft` for remaining.
- **`timer.add()` returns a `CtTimer`** — it's both a timer and a Promise-like object.
- **Timer names are optional** — useful for debugging but not required.
- **`uiDelta` property** — `true` for UI timers, `false` for game timers.
