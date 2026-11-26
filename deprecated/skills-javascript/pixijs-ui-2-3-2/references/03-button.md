# Button / ButtonContainer / ButtonEvents

Lightweight button components for custom implementations.

## Button

Turns any `Container` into a button by adding pointer event handling.

```ts
const button = new Button(view?: Container);
```

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `view` | `Container` | The container that receives button events |
| `enabled` | `boolean` | Enables/disables button interaction |
| `isDown` | `boolean` | Whether pointer is currently down on button |

### Events (Signals)

| Signal | Parameters | Description |
|--------|-----------|-------------|
| `onDown` | `(btn, e)` | Pointer down |
| `onUp` | `(btn, e)` | Pointer up |
| `onUpOut` | `(btn, e)` | Pointer up outside button |
| `onOut` | `(btn, e)` | Pointer out |
| `onPress` | `(btn, e)` | Button pressed (tap/click) |
| `onHover` | `(btn, e)` | Mouse hover (desktop only) |

### Custom Button via Subclassing

Extend `Button` and override the callback methods for full control:

```ts
class CustomButton extends Button {
    constructor(view: Container) {
        super(view);
    }

    override down(e?: FederatedPointerEvent) {
        // Called on pointer down
        this.view?.children[0].tint = 0xcccccc;
    }

    override up(e?: FederatedPointerEvent) {
        // Called on pointer up
        this.view?.children[0].tint = 0xffffff;
    }

    override press(e?: FederatedPointerEvent) {
        // Called on press (tap/click)
        console.log('pressed!');
    }

    override hover(e?: FederatedPointerEvent) {
        // Called on hover (desktop only)
        this.view?.children[0].tint = 0xeeeeee;
    }

    override out(e?: FederatedPointerEvent) {
        // Called on pointer out
        this.view?.children[0].tint = 0xffffff;
    }

    override upOut(e?: FederatedPointerEvent) {
        // Called on pointer up outside
        this.view?.children[0].tint = 0xffffff;
    }
}
```

### Example

```ts
const view = new Graphics().rect(0, 0, 100, 40).fill(0x3366ff);
const button = new Button(view);

button.onPress.connect(() => console.log('pressed'));
button.enabled = true;

app.stage.addChild(view);
```

## ButtonContainer

A `Container` with built-in button events. Signals are exposed directly on the container instance.

```ts
const btn = new ButtonContainer(view?: Container);
```

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `button` | `Button` | Internal Button instance |
| `enabled` | `boolean` | Button enabled state |

### Events (Signals)

Same signals as `Button`, exposed directly on the container:
`onPress`, `onDown`, `onUp`, `onUpOut`, `onOut`, `onHover`.

### Example

```ts
const btn = new ButtonContainer(
    new Graphics().rect(0, 0, 100, 40).fill(0x3366ff)
);

// Can add children freely
const label = new Text({ text: 'OK', style: { fill: 0xffffff } });
label.anchor.set(0.5);
label.position.set(50, 20);
btn.addChild(label);

btn.onPress.connect(() => console.log('pressed'));
app.stage.addChild(btn);
```

## ButtonEvents

Base class providing pointer event processing. Used as a mixin by `Button`.

```ts
class ButtonEvents {
    onDown: Signal<(btn, e) => void>;
    onUp: Signal<(btn, e) => void>;
    onUpOut: Signal<(btn, e) => void>;
    onOut: Signal<(btn, e) => void>;
    onPress: Signal<(btn, e) => void>;
    onHover: Signal<(btn, e) => void>;

    // Override these in subclasses
    down(e?: FederatedPointerEvent) {}
    up(e?: FederatedPointerEvent) {}
    upOut(e?: FederatedPointerEvent) {}
    out(e?: FederatedPointerEvent) {}
    press(e?: FederatedPointerEvent) {}
    hover(e?: FederatedPointerEvent) {}
}
```

### Event Flow

1. `pointerdown` / `mousedown` → `processDown()` → emits `onDown` → calls `down()`
2. `pointerup` / `mouseup` → `processUp()` → emits `onUp` → calls `up()`
3. `pointerupoutside` / `mouseupoutside` → `processUpOut()` → emits `onUp`, `onUpOut` → calls `up()`, `upOut()`
4. `pointerout` / `mouseout` → `processOut()` → emits `onOut` → calls `out()`
5. `pointertap` / `click` → `processPress()` → emits `onPress` → calls `press()`
6. `pointerover` / `mouseover` → `processOver()` → emits `onHover` → calls `hover()`

### Mobile vs Desktop

- **Mobile** — uses `pointer*` events
- **Desktop** — uses `mouse*` events for down/up/out, `click` for press
- `onHover` is never fired on mobile devices
