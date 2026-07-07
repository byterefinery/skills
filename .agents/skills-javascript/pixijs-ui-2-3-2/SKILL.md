---
name: pixijs-ui-2-3-2
description: >
  PixiUI v2.3.2 — UI component library for PixiJS v8. Use when building interactive UI with PixiJS:
  buttons (Button, FancyButton), checkboxes, radio groups, sliders (single/double), progress bars
  (linear/circular), text input, dropdown selects, scrollable containers (ScrollBox), modal dialogs,
  masked frames, switchers, and list layouts. Covers component instantiation, event signals (typed-signals),
  state views (default/hover/pressed/disabled), NineSliceSprite scaling, animations via tweedle.js,
  content fitting, and composition patterns. Requires pixi.js ^8.6.2 as peer dependency.
metadata:
  tags:
    - ui
    - components
    - pixi
    - interactive
    - game-dev
    - javascript
---

# pixijs-ui 2.3.2

## Overview

PixiUI is a component library for PixiJS v8 providing ready-made interactive UI elements. It follows a consistent pattern: components accept an options object, use `typed-signals` for events (`.connect()` / `.disconnect()`), and support state views (default, hover, pressed, disabled) with optional `tweedle.js` animations.

### Core Architecture

- **Signal-based events** — all components use `typed-signals`. Subscribe with `.onPress.connect(handler)`, not `.on()` or `.addEventListener()`. Use `.disconnect()` to remove.
- **State views** — interactive components support `defaultView`, `hoverView`, `pressedView`, `disabledView`. Views cascade (pressed falls back to hover, hover to default).
- **View helpers** — pass strings (texture names), `Texture`, `Sprite`, `Graphics`, or `Container` instances where a view is expected. Use `NineSliceSprite` for scalable backgrounds by passing a texture + `nineSliceSprite` option.
- **Animations** — `FancyButton` and `Dialog` use `tweedle.js` tweens. Register `Ticker.shared.add(() => Group.shared.update())` once for tweens to run.
- **Content fitting** — `FancyButton` auto-scales text/icon to fit inside the view. Modes: `default` (scale down to fit), `fill` (scale up to fill), `none` (no constraint).
- **No default export** — import named: `import { FancyButton, ScrollBox } from '@pixi/ui'`.

### Component Hierarchy

```
Switcher          — base: toggle between views on pointer events
├─ CheckBox       — two-state switcher with optional text label
└─ ButtonEvents   — mixin: pointer event processing (down, up, press, hover, out)
   └─ Button      — turns any Container into a button
      ├─ ButtonContainer — Container + Button (exposes signals directly)
      │  └─ FancyButton  — full-featured button: text, icon, animations, state views
      └─ (used by) Select (open/close buttons)

Container
├─ ProgressBar    — linear fill bar with mask
│  └─ SliderBase  — adds draggable sliders on top of ProgressBar
│     ├─ Slider      — single-value slider with step snapping
│     └─ DoubleSlider — range slider (two handles, fill between)
├─ CircularProgressBar — arc-based progress indicator
├─ ScrollBox      — scrollable container with dynamic rendering, drag scroll, wheel
├─ List           — auto-arranging layout (vertical, horizontal, bidirectional)
├─ Select         — dropdown: FancyButton + ScrollBox of FancyButton items
├─ Dialog         — modal: backdrop + inner panel + title + scrollable content + buttons
├─ Input          — text input with hidden HTML input, cursor blink, placeholder
├─ MaskedFrame    — border/mask wrapper for any Container
├─ RadioGroup     — wrapper: makes CheckBox items behave as radio buttons
```

### Quick Start

```ts
import { Application, Graphics, Text } from 'pixi.js';
import { FancyButton, ScrollBox, CheckBox, Slider, ProgressBar } from '@pixi/ui';

const app = new Application();
await app.init({ width: 800, height: 600, backgroundColor: 0x1099bb });
document.body.appendChild(app.canvas);

// Button with state views and animation
const button = new FancyButton({
    defaultView: new Graphics().roundRect(0, 0, 120, 40, 8).fill(0x3366ff),
    hoverView: new Graphics().roundRect(0, 0, 120, 40, 8).fill(0x5588ff),
    pressedView: new Graphics().roundRect(0, 0, 120, 40, 8).fill(0x2244cc),
    text: new Text({ text: 'Click Me', style: { fill: 0xffffff, fontSize: 16 } }),
    padding: 10,
    animations: {
        hover: { props: { scale: { x: 1.05, y: 1.05 } }, duration: 100 },
        pressed: { props: { scale: { x: 0.95, y: 0.95 } }, duration: 100 },
    },
});
button.anchor.set(0.5);
button.position.set(400, 300);
button.onPress.connect(() => console.log('pressed'));
app.stage.addChild(button);

// Checkbox
const checkbox = new CheckBox({
    style: {
        unchecked: new Graphics().rect(0, 0, 20, 20).fill(0x333333),
        checked: new Graphics().rect(0, 0, 20, 20).fill(0x3366ff),
    },
    text: 'Enable feature',
});
checkbox.onCheck.connect((checked) => console.log('checked:', checked));
checkbox.position.set(100, 100);
app.stage.addChild(checkbox);

// Slider
const slider = new Slider({
    bg: new Graphics().rect(0, 0, 200, 10).fill(0x333333),
    fill: new Graphics().rect(0, 0, 200, 10).fill(0x3366ff),
    slider: new Graphics().circle(0, 0, 10).fill(0xffffff),
    min: 0,
    max: 100,
    value: 50,
});
slider.onChange.connect((value) => console.log('slider:', value));
slider.position.set(100, 200);
app.stage.addChild(slider);
```

## Usage

### FancyButton — Full-Featured Button

The most versatile component. Combines state views, text, icon, and animations.

```ts
const button = new FancyButton({
    // State views (all optional, cascade: pressed → hover → default)
    defaultView: 'button_default.png',
    hoverView: 'button_hover.png',
    pressedView: 'button_pressed.png',
    disabledView: 'button_disabled.png',

    // Text — string, Text, BitmapText, or HTMLText
    text: 'Submit',
    // Or with a Text instance for custom styling:
    // text: new Text({ text: 'Submit', style: { fill: 0xffffff, fontSize: 18 } }),

    // Icon (optional) — texture name, Texture, Sprite, or Graphics
    icon: 'icon.png',

    // Layout
    padding: 10,              // Content inset from view edges
    anchor: 0.5,              // Button anchor (ObservablePoint)
    anchorX: 0.5, anchorY: 0.5,
    offset: { x: 0, y: 0 },   // Per-state view offset: { default: {x,y}, hover: {x,y}, ... }
    textOffset: { x: 0, y: 0 },
    iconOffset: { x: 0, y: 0 },

    // Scaling
    scale: 1,
    defaultTextScale: { x: 1, y: 1 },
    defaultIconScale: { x: 1, y: 1 },
    defaultTextAnchor: { x: 0.5, y: 0.5 },
    defaultIconAnchor: { x: 0.5, y: 0.5 },

    // Content fitting
    contentFittingMode: 'default', // 'default' | 'fill' | 'none'

    // NineSliceSprite (pass texture name or Texture instance for views)
    nineSliceSprite: [10, 10, 10, 10],

    // Animations (uses tweedle.js)
    animations: {
        hover: { props: { scale: { x: 1.1, y: 1.1 } }, duration: 100 },
        pressed: { props: { scale: { x: 0.9, y: 0.9 } }, duration: 100 },
        default: { props: { scale: { x: 1, y: 1 } }, duration: 100 },
    },
});

// Events (typed-signals)
button.onPress.connect((btn, e) => { /* clicked */ });
button.onDown.connect(() => {});
button.onUp.connect(() => {});
button.onHover.connect(() => {});
button.onOut.connect(() => {});
button.onUpOut.connect(() => {});

// Runtime updates
button.text = 'New Label';
button.enabled = false; // Switches to disabled state
button.padding = 15;
button.defaultView = newView;
button.removeView('iconView');
button.setState('hover'); // Force state

// Anchor
button.anchor.set(0.5, 0.5);
```

### Button / ButtonContainer — Lightweight Button

For custom button implementations where you control the view directly.

```ts
// Button — wraps any Container with button events
const button = new Button(new Graphics().rect(0, 0, 100, 40).fill(0x3366ff));
button.onPress.connect(() => console.log('pressed'));
button.enabled = true;

// ButtonContainer — Container with built-in button events
const btn = new ButtonContainer(new Graphics().rect(0, 0, 100, 40).fill(0x3366ff));
btn.onPress.connect(() => console.log('pressed'));
btn.addChild(new Text({ text: 'OK', style: { fill: 0xffffff } }));
```

### CheckBox — Two-State Toggle

```ts
const checkbox = new CheckBox({
    style: {
        unchecked: 'unchecked.png',
        checked: 'checked.png',
        text: { fill: 0xffffff, fontSize: 16 },
    },
    text: 'Accept terms',
    checked: false,
});

checkbox.onCheck.connect((checked) => console.log(checked));
checkbox.checked = true;
checkbox.forceCheck(true); // Without emitting signal
```

### RadioGroup — Mutually Exclusive Selection

```ts
const radioGroup = new RadioGroup({
    items: [
        new CheckBox({ style: { unchecked: 'off.png', checked: 'on.png' }, text: 'A' }),
        new CheckBox({ style: { unchecked: 'off.png', checked: 'on.png' }, text: 'B' }),
        new CheckBox({ style: { unchecked: 'off.png', checked: 'on.png' }, text: 'C' }),
    ],
    type: 'vertical',
    elementsMargin: 10,
    selectedItem: 0,
});

radioGroup.onChange.connect((id, text) => console.log('selected:', id, text));
radioGroup.selectItem(2);
```

### Slider — Single Value

```ts
const slider = new Slider({
    bg: new Graphics().rect(0, 0, 200, 10).fill(0x333333),
    fill: new Graphics().rect(0, 0, 200, 10).fill(0x3366ff),
    slider: new Graphics().circle(0, 0, 10).fill(0xffffff),
    min: 0, max: 100, value: 50, step: 5,
});

slider.onUpdate.connect((v) => {}); // During drag
slider.onChange.connect((v) => {});  // On release
slider.value = 75;
```

### DoubleSlider — Range Selection

```ts
const rangeSlider = new DoubleSlider({
    bg: 'slider_bg.png', fill: 'slider_fill.png',
    slider1: 'handle.png', slider2: 'handle.png',
    min: 0, max: 100, value1: 20, value2: 80,
});

rangeSlider.onChange.connect((v1, v2) => console.log(v1, '—', v2));
```

### ProgressBar / CircularProgressBar

```ts
const bar = new ProgressBar({
    bg: 'bar_bg.png', fill: 'bar_fill.png',
    fillPaddings: { top: 2, right: 2, bottom: 2, left: 2 },
});
bar.progress = 65; // 0–100

const circular = new CircularProgressBar({
    fillColor: 0x3366ff, lineWidth: 8, radius: 50, cap: 'round',
});
circular.progress = 75;
```

### Input — Text Entry

```ts
const input = new Input({
    bg: 'input_bg.png',
    textStyle: { fill: 0xffffff, fontSize: 16 },
    placeholder: 'Enter text...',
    maxLength: 50, secure: false, align: 'left',
    padding: { top: 8, right: 8, bottom: 8, left: 8 },
});

input.onChange.connect((text) => {});  // On every keystroke
input.onEnter.connect((text) => {});   // On blur
input.value = 'Hello';
input.secure = true; // Password mode
```

### Select — Dropdown

```ts
const select = new Select({
    closedBG: 'select_closed.png', openBG: 'select_open.png',
    textStyle: { fill: 0xffffff, fontSize: 16 },
    selected: 0,
    items: {
        items: ['Option A', 'Option B', 'Option C'],
        backgroundColor: 0x222222, hoverColor: 0x444444,
        width: 200, height: 40, radius: 5,
    },
    scrollBox: { width: 200, height: 200, radius: 10 },
});

select.onSelect.connect((id, text) => console.log('selected:', id, text));
select.open(); select.close(); select.toggle();
```

### ScrollBox — Scrollable Container

```ts
const scrollBox = new ScrollBox({
    background: 0x111111, width: 400, height: 300, radius: 10,
    type: 'vertical', elementsMargin: 10, padding: 10,
});

scrollBox.addItem(container);
scrollBox.addItems([c1, c2]);
scrollBox.removeItem(0); scrollBox.removeItems();
scrollBox.scrollTop(); scrollBox.scrollBottom(); scrollBox.scrollTo(5);
scrollBox.onScroll.connect((value) => {}); // number or {x, y}
```

### List — Auto-Layout Container

```ts
const list = new List({
    type: 'vertical', elementsMargin: 10, padding: 10,
    maxWidth: 400, // For bidirectional: wrap width
});
list.addChild(container);
list.removeItem(0);
list.arrangeChildren(); // Manual re-layout
```

### Dialog — Modal

```ts
const dialog = new Dialog({
    background: new Graphics().roundRect(0, 0, 400, 200, 15).fill(0x222222),
    backdropColor: 0x000000, backdropAlpha: 0.6,
    title: new Text({ text: 'Confirm', style: { fill: 0xffffff, fontSize: 20 } }),
    content: 'Are you sure?',
    width: 400, height: 200, padding: 20,
    buttons: [
        { text: 'Cancel', defaultView: new Graphics().roundRect(0, 0, 80, 30, 5).fill(0x444444) },
        { text: 'OK', defaultView: new Graphics().roundRect(0, 0, 80, 30, 5).fill(0x3366ff) },
    ],
    closeOnBackdropClick: true,
});

dialog.onSelect.connect((index, text) => {});
dialog.open(); dialog.close(); dialog.isOpen;
```

### MaskedFrame / Switcher

```ts
// MaskedFrame — border/mask wrapper
const frame = new MaskedFrame({
    target: 'avatar.png', mask: 'avatar_mask.png',
    borderWidth: 3, borderColor: 0xffffff,
});
frame.showBorder(); frame.hideBorder();

// Switcher — base toggle component
const switcher = new Switcher(['off.png', 'on.png'], 'onPress', 0);
switcher.onChange.connect((state) => {});
switcher.switch(); switcher.switch(1);
```

## Gotchas

- **Signals, not events** — PixiUI uses `typed-signals`, not PixiJS events. Use `.onPress.connect(handler)`, not `.on('press')`. Disconnect with `.disconnect(handler)`.
- **Ticker required for animations** — `FancyButton` animations and `Dialog` open/close tweens need `Ticker.shared.add(() => Group.shared.update())`. Register once at app startup.
- **NineSliceSprite needs textures** — `nineSliceSprite` option only works when views are passed as texture names (strings) or `Texture` instances, not `Graphics` or `Container`.
- **Content fitting auto-scales** — `FancyButton` with `contentFittingMode: 'default'` shrinks text/icon to fit. Use `'none'` to disable auto-scaling or `'fill'` to scale up.
- **Input uses hidden HTML element** — `Input` creates a transparent `<input>` overlay for keyboard input. On Android, it uses a 100ms delay for focus to prevent keyboard dismissal.
- **Input cursor blinks via Ticker** — The blinking cursor is updated in the shared ticker. Without a running ticker, the cursor won't blink.
- **ScrollBox dynamic rendering** — Hidden items have `renderable = false` by default. They re-render during scroll and hide after 2 seconds. Set `disableDynamicRendering: true` to always render (performance cost).
- **ScrollBox wheel event is global** — `ScrollBox` listens to `document` wheel events. Call `scrollBox.destroy()` to clean up the listener.
- **Slider step snaps to nearest** — `step` rounds the value to the nearest multiple. Default step is 1.
- **DoubleSlider prevents crossing** — `value1` cannot exceed `value2` and vice versa. The component clamps automatically.
- **Dialog buttons emit index + text** — `onSelect` fires with `(buttonIndex, buttonText)`. For `Button`/`FancyButton` instances passed directly, text may be empty string.
- **RadioGroup wraps CheckBoxes** — Pass `CheckBox` instances, not plain data. The group manages mutual exclusivity via `forceCheck()`.
- **CheckBox label is clickable** — The text label next to a CheckBox triggers toggle on tap.
- **Select composes FancyButton + ScrollBox** — Each dropdown item is a `FancyButton`. Customize via `items` options (backgroundColor, hoverColor, textStyle, radius).
- **List auto-arranges on childAdded** — Adding children triggers `arrangeChildren()` automatically. Call it manually only after bulk changes.
- **Switcher cascades to next** — `switcher.switch()` cycles forward. With 2 views it toggles; with 3+ it rotates.
- **Button event cascade** — `FancyButton` state machine: default → hover → pressed → default/disabled. On mobile, hover state is skipped.
- **`enabled = false` on FancyButton** — Switches to `disabled` state view automatically, not just disabling events.
- **View cascade** — If `pressedView` is not set, `hoverView` is used. If `hoverView` is not set, `defaultView` is used. Same for `disabledView`.
- **Peer dependency** — Requires `pixi.js ^8.6.2`. PixiUI v2.x is for PixiJS v8.x; v1.x was for PixiJS v7.x.
- **No default export** — Always use named imports: `import { FancyButton } from '@pixi/ui'`.
- **`destroy()` cleanup** — `ScrollBox` and `Input` attach global listeners. Always call `destroy()` when removing.
- **Progress is 0–100** — Both `ProgressBar` and `CircularProgressBar` use percentage values, not 0–1.
- **SliderBase is internal** — `SliderBase` and `ButtonEvents` are base classes. Use `Slider`, `DoubleSlider`, `Button`, or `FancyButton` directly.

## References

- [01-installation-setup](references/01-installation-setup.md) — Installation, peer dependencies, import patterns, ticker setup, compatibility matrix
- [02-fancybutton](references/02-fancybutton.md) — FancyButton API, state views, text/icon, content fitting, animations, offsets, nine-slice, runtime updates
- [03-button](references/03-button.md) — Button, ButtonContainer, ButtonEvents — lightweight button with custom views
- [04-checkbox-radio](references/04-checkbox-radio.md) — CheckBox, RadioGroup — toggle states, labels, mutual exclusion
- [05-sliders](references/05-sliders.md) — Slider, DoubleSlider, SliderBase — single/range selection, step, fill, value display
- [06-progress](references/06-progress.md) — ProgressBar, CircularProgressBar — linear and arc progress indicators
- [07-input](references/07-input.md) — Input — text entry, hidden HTML input, cursor, placeholder, secure mode, padding
- [08-select](references/08-select.md) — Select — dropdown composition, items, scroll box, open/close/toggle
- [09-scrollbox](references/09-scrollbox.md) — ScrollBox — scrollable container, dynamic rendering, drag/wheel scroll, proximity, scroll control
- [10-list](references/10-list.md) — List — auto-layout, vertical/horizontal/bidirectional arrangement, padding, margins
- [11-dialog](references/11-dialog.md) — Dialog — modal overlay, backdrop, title/content/buttons, animations, open/close
- [12-switcher-maskedframe](references/12-switcher-maskedframe.md) — Switcher base class, MaskedFrame border/mask wrapper
