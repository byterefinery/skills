---
name: pixijs-ui-2-4-1
description: >
  PixiUI v2.4.1 — UI component library for PixiJS v8. Use when building interactive UI with PixiJS —
  buttons (Button, FancyButton), checkboxes, radio groups, sliders (single/double), progress bars
  (linear/circular), text input, dropdown selects, scrollable containers (ScrollBox), modal dialogs,
  edge drawers (Drawer), masked frames, switchers, and list layouts. Covers component instantiation,
  signals (package-exported Signal class), state views (default/hover/pressed/disabled),
  NineSliceSprite scaling, tweedle.js animations, content fitting, and composition patterns.
  Requires pixi.js ^8.6.2 as peer dependency.
license: MIT
compatibility: Requires pixi.js ^8.6.2 (PixiJS v8.x); tweedle.js ^2.1.0 ships as a package dependency
metadata:
  tags:
    - ui
    - components
    - pixi
    - interactive
    - game-dev
    - javascript
---

# pixijs-ui 2.4.1

## Overview

PixiUI is a component library for PixiJS v8 providing ready-made interactive UI elements. Components accept an options object, use the package's own `Signal` class for events, and support state views (default, hover, pressed, disabled) with optional `tweedle.js` animations.

### Core Architecture

- **Signal-based events** — `@pixi/ui` exports its own `Signal` class (not `typed-signals`, not PixiJS events). Subscribe with `const conn = button.onPress.connect(handler)`; remove with `conn.disconnect()`.
- **State views** — `defaultView`, `hoverView`, `pressedView`, `disabledView`. Views cascade (pressed → hover → default; disabled → default).
- **View helpers** — pass texture names (strings), `Texture`, `Sprite`, `Graphics`, or `Container` where a view is expected. `NineSliceSprite` scaling only works with texture names or `Texture` instances.
- **Animations** — `FancyButton` (with `animations` set), `Dialog`, and `Drawer` tween via `tweedle.js` and register their own `Ticker.shared` callback in the constructor (removed in `destroy()`) — no manual ticker registration needed.
- **Content fitting** — `FancyButton` auto-scales text/icon: `default` (scale down to fit), `fill` (scale to fill), `none` (no constraint).
- **No default export** — import named: `import { FancyButton, Drawer } from '@pixi/ui'`.

### Component Hierarchy

```
Switcher          — base: toggle between views on pointer events
├─ CheckBox       — two-state switcher with optional text label
└─ ButtonEvents   — mixin: pointer event processing (down, up, press, hover, out)
   └─ Button      — turns any Container into a button
      └─ ButtonContainer — Container + Button (exposes signals directly)
         └─ FancyButton  — full-featured button: text, icon, animations, state views

Container
├─ ProgressBar    — linear fill bar with mask
│  └─ SliderBase  — adds draggable sliders on top of ProgressBar
│     ├─ Slider      — single-value slider with step snapping
│     └─ DoubleSlider — range slider (two handles, fill between)
├─ CircularProgressBar — arc-based progress indicator
├─ ScrollBox      — scrollable container with dynamic rendering, drag/wheel scroll, proximity
├─ List           — auto-arranging layout (vertical, horizontal, bidirectional)
├─ Select         — dropdown: FancyButton + ScrollBox of FancyButton items
├─ Dialog         — modal: backdrop + panel + title + scrollable content + buttons
├─ Drawer         — edge panel (top/bottom/left/right) with backdrop, swipe-to-close
├─ Input          — text input backed by a hidden native <input> (IME, paste, suggestions)
├─ MaskedFrame    — border/mask wrapper for any Container
└─ RadioGroup     — wrapper: makes CheckBox items behave as radio buttons
```

### Quick Start

```ts
import { Application } from 'pixi.js';

const app = new Application();
await app.init({ width: 800, height: 600, backgroundColor: 0x1099bb });
document.body.appendChild(app.canvas);
// Then add components to app.stage — see Usage below.
```

Full options for every component are in the references below.

## Usage

Each snippet shows the minimal construction; full option tables live in the references.

```ts
// FancyButton — state views, text, icon, animations, nine-slice, content fitting
const button = new FancyButton({
    defaultView: 'button_default.png', text: 'Submit', icon: 'icon.png',
    padding: 10, contentFittingMode: 'default',
    nineSliceSprite: [10, 10, 10, 10], // texture views only
    animations: { hover: { props: { scale: { x: 1.1, y: 1.1 } }, duration: 100 } },
});
button.onPress.connect(() => {});
button.enabled = false;   // → disabled state view
button.setState('hover'); // force state; also .text, .padding, .removeView('iconView')

// Button / ButtonContainer — lightweight variants
const btn = new ButtonContainer(new Graphics().rect(0, 0, 100, 40).fill(0x3366ff));

// CheckBox — two-state toggle with optional label
const checkbox = new CheckBox({
    style: { unchecked: 'off.png', checked: 'on.png', text: { fill: 0xffffff } },
    text: 'Accept terms',
});
checkbox.onCheck.connect((checked) => {});
checkbox.forceCheck(true); // no signal

// RadioGroup — mutually exclusive CheckBoxes
const radioGroup = new RadioGroup({
    items: [new CheckBox({ style: { unchecked: 'off.png', checked: 'on.png' }, text: 'A' })],
    type: 'vertical', elementsMargin: 10, selectedItem: 0,
});
radioGroup.onChange.connect((id, text) => {});
radioGroup.selectItem(1); // also .selected, .value, .addItems, .removeItems(ids)

// Slider — single value (drag anywhere on bg; step snaps to nearest multiple)
const slider = new Slider({ bg: 'bg.png', fill: 'fill.png', slider: 'handle.png', min: 0, max: 100, value: 50, step: 5, showValue: true });
slider.onUpdate.connect((v) => {}); // during drag AND on programmatic value set
slider.onChange.connect((v) => {});  // on release only

// DoubleSlider — range (value1 clamped ≤ value2)
const range = new DoubleSlider({ bg: 'bg.png', fill: 'fill.png', slider1: 'h.png', slider2: 'h.png', value1: 20, value2: 80 });
range.onChange.connect((v1, v2) => {});

// Progress bars — progress is 0–100
const bar = new ProgressBar({ bg: 'bg.png', fill: 'fill.png' }); bar.progress = 65;
const circular = new CircularProgressBar({ backgroundColor: 0x222222, fillColor: 0x3366ff, lineWidth: 8, radius: 50, cap: 'round', value: 75 });

// Input — text entry backed by a hidden native <input> (IME, paste, suggestions)
const input = new Input({ bg: 'input_bg.png', // required
    placeholder: 'Enter text...', maxLength: 50, secure: false, align: 'left', padding: 8 });
input.onChange.connect((text) => {}); // every user change; NOT on programmatic value =
input.onEnter.connect((text) => {});  // editing ended — Enter, Escape, or focus loss

// Select — dropdown (FancyButton + ScrollBox of FancyButtons)
const select = new Select({
    closedBG: 'select_closed.png', openBG: 'select_open.png',
    selected: 0, visibleItems: 5, // dropdown height = item height × visibleItems
    items: { items: ['A', 'B', 'C'], backgroundColor: 0x222222, width: 200, height: 40, radius: 5 },
});
select.onSelect.connect((id, text) => {});
select.value; // -1 until picked
select.open(); select.close(); select.toggle();

// ScrollBox — scrollable container (dynamic rendering, drag + wheel, proximity)
const scrollBox = new ScrollBox({ background: 0x111111, width: 400, height: 300, radius: 10, type: 'vertical', elementsMargin: 10, padding: 10, proximityRange: 100 });
scrollBox.addItem(c); scrollBox.addItems([a, b]); scrollBox.removeItem(0);
scrollBox.scrollTop(); scrollBox.scrollBottom(); scrollBox.scrollTo(5); scrollBox.scrollToPosition({ x: 0, y: 100 });
scrollBox.onScroll.connect((value) => {}); // number, or {x, y} when bidirectional
scrollBox.onProximityChange.connect(({ item, index, inRange }) => {});

// List — auto-arranging layout (type defaults to 'bidirectional')
const list = new List({ elementsMargin: 10, padding: 10, maxWidth: 400 });
list.addChild(c); list.addItems([a, b]); list.removeItem(0); list.arrangeChildren();

// Dialog — modal (backdrop + panel + title + scrollable content + buttons)
const dialog = new Dialog({
    background: new Graphics().roundRect(0, 0, 400, 200, 15).fill(0x222222), // required
    title: 'Confirm', content: 'Are you sure?', width: 400, height: 200, padding: 20,
    buttons: [{ text: 'Cancel' }, { text: 'OK' }], // objects → FancyButton; FancyButton/Button instances ok
    closeOnBackdropClick: false, // Dialog default is false — set true to close on backdrop tap
});
dialog.onSelect.connect((index, text) => {});
dialog.onClose.connect(() => {});
dialog.open(); dialog.close(); dialog.isOpen;

// Drawer — edge panel (new in 2.4); slides from bottom | top | left | right
const drawer = new Drawer({
    background: new Graphics().roundRect(0, 0, 400, 300, 20).fill(0xffffff), // required
    position: 'bottom', width: 400, height: 300, padding: 20,
    content: new Text({ text: 'Content', style: { fill: 0x000000 } }), // Container or Container[]
    swipeToClose: true, // default true — swipe outward >50px closes
    animations: { open: { props: {}, duration: 300 }, close: { props: {}, duration: 300 } },
});
drawer.setScreenSize(app.screen.width, app.screen.height); // default 800x600; parent must be screen-centred
drawer.onClose.connect(() => {}); // after close animation finishes
view.addChild(drawer); drawer.open();

// MaskedFrame — border/mask wrapper; Switcher — base toggle
const frame = new MaskedFrame({ target: 'avatar.png', mask: 'avatar_mask.png', borderWidth: 3, borderColor: 0xffffff });
const switcher = new Switcher(['off.png', 'on.png'], 'onPress', 0);
switcher.onChange.connect((state) => {}); // boolean for 2 views, id number for 3+
```

## Gotchas

- **Signals, not events** — `button.onPress.connect(handler)` returns a connection; remove with `connection.disconnect()`. `connect(callback, order)` takes a priority; `signal.disconnectAll()` removes all.
- **No manual ticker for component animations** — `FancyButton` (with `animations`), `Dialog`, `Drawer` register their own `Ticker.shared` callback, removed in `destroy()`. Add `Ticker.shared.add(() => Group.shared.update())` only for your own tweens.
- **Dialog vs Drawer backdrop-click default differs** — `Dialog` closes on backdrop click only when `closeOnBackdropClick` is explicitly `true`; `Drawer` does so unless explicitly `false`.
- **`background` is required** — `Drawer`/`Dialog` throw when `options.background` is omitted.
- **Drawer needs `setScreenSize` + a screen-centred parent** — it positions from the screen centre (defaults 800×600).
- **Drawer `isOpen`/`onClose` lag the close animation** — they happen after the close tween completes (instant without `animations.close`). `show()`/`hide()` alias `open()`/`close()`; swipe-to-close is outward-only with a >50px threshold; content is always wrapped in an internal ScrollBox.
- **Input `bg` is required** — missing it logs `Input: bg is not defined...` (console.error, not a throw).
- **Input `onEnter` means "editing ended"** — Enter, Escape, *or* focus loss. `onChange` fires on every user change but not on programmatic `value =` sets. The caret blinks via the shared ticker; `destroy()` detaches window-level listeners — call it when removing inputs. Android focuses the hidden field after a 100ms delay.
- **NineSliceSprite needs textures** — views must be texture names or `Texture` instances. Shape differs: `FancyButton`/`Dialog`/`Drawer`/`Input` take `[l, t, r, b]`; `ProgressBar` takes `{ bg: [l,t,r,b], fill: [l,t,r,b] }`.
- **ScrollBox dynamic rendering** — off-screen items get `renderable = false`; all render while dragging, hide 2s after release. The wheel listener is on `document` (capture phase) and `globalScroll` defaults to `true` — `destroy()` removes it.
- **ScrollBox type defaults to `vertical`; List type defaults to `bidirectional`** — different defaults, different roles.
- **Slider** — drag snaps to nearest `step` multiple (zero/non-finite → 1); `onUpdate` fires on programmatic `value =` sets too; `onChange` only on release. DoubleSlider clamps `value1 ≤ value2`.
- **Dialog `onSelect` emits (index, text)** — text is `''` for raw `Button` instances; plain objects in `buttons` become `FancyButton`s. Open/close animate scale 0.8 ⇄ 1; without `animations` it is instant.
- **Select `value` is -1 until picked** — dropdown height = item height × `visibleItems` (default 5).
- **RadioGroup wraps CheckBox instances** — mutual exclusivity via `forceCheck()`; `removeItems(ids)` takes an array. CheckBox labels are clickable; `forceCheck()` skips `onCheck`.
- **List auto-arranges on child add** — batch `addItems([...])` arranges once; layout is anchor/pivot-aware (children align by visual bounds).
- **Button `enabled` needs a view** — setting `enabled` before `button.view` logs an error and does nothing. Switcher `onChange` payload: boolean for 2 views, id number for 3+.
- **Progress is 0–100** — percentages, not 0–1.
- **Peer dependency** — `pixi.js ^8.6.2`; v2.x pairs with PixiJS v8.x. No default export — always named imports.
- **`destroy()` cleanup** — `ScrollBox`, `Input`, `Dialog`, `Drawer`, animated `FancyButton` attach ticker callbacks and/or global listeners. `SliderBase`/`ButtonEvents` are internal bases — use the concrete classes.

## References

- [01-installation-setup](references/01-installation-setup.md) — Installation, peer/runtime dependencies, Signal API, import patterns, ticker setup, asset loading, types
- [02-fancybutton](references/02-fancybutton.md) — FancyButton API, state views, text/icon, content fitting, animations, offsets, nine-slice, runtime updates
- [03-button](references/03-button.md) — Button, ButtonContainer, ButtonEvents — lightweight button with custom views
- [04-checkbox-radio](references/04-checkbox-radio.md) — CheckBox, RadioGroup — toggle states, labels, mutual exclusion
- [05-sliders](references/05-sliders.md) — Slider, DoubleSlider, SliderBase — single/range selection, step, fill, value display
- [06-progress](references/06-progress.md) — ProgressBar, CircularProgressBar — linear and arc progress indicators
- [07-input](references/07-input.md) — Input — hidden-native-field architecture, signals, selection, secure mode, padding
- [08-select](references/08-select.md) — Select — dropdown composition, items, scroll box, open/close/toggle
- [09-scrollbox](references/09-scrollbox.md) — ScrollBox — scrollable container, dynamic rendering, drag/wheel scroll, proximity, scroll control
- [10-list](references/10-list.md) — List — auto-layout, vertical/horizontal/bidirectional arrangement, padding, margins
- [11-dialog](references/11-dialog.md) — Dialog — modal overlay, backdrop, title/content/buttons, animations, open/close
- [12-drawer](references/12-drawer.md) — Drawer — edge panel positions, screen sizing, swipe-to-close, backdrop, animations
- [13-switcher-maskedframe](references/13-switcher-maskedframe.md) — Switcher base class, MaskedFrame border/mask wrapper
