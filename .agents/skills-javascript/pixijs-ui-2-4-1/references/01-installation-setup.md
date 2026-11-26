# Installation & Setup

## Installation

```sh
npm install @pixi/ui@2.4.1
# or
yarn add @pixi/ui@2.4.1
# or
pnpm add @pixi/ui@2.4.1
```

## Peer Dependencies

PixiUI v2.4.1 requires `pixi.js ^8.6.2` as a peer dependency. Install PixiJS first:

```sh
npm install pixi.js @pixi/ui@2.4.1
```

### Compatibility Matrix

| PixiJS | PixiUI |
|--------|--------|
| v7.x   | v1.x   |
| v8.x   | v2.x   |

### Runtime Dependencies

`@pixi/ui` has one runtime dependency:

- **`tweedle.js`** (^2.1.0) — tweening engine used by `FancyButton`, `Dialog`, and `Drawer` animations.

The `Signal` class used by every component is implemented inside the package (`src/utils/Signal.ts`) and exported from the root — `typed-signals` is **not** a dependency.

## Signal API

All component events are `Signal` instances exported by `@pixi/ui`:

```ts
import { Signal, SignalConnection } from '@pixi/ui';

const connection: SignalConnection = signal.connect(callback, order = 0);
connection.disconnect();  // returns false if already removed
connection.enabled;       // get/set: disable a listener without removing it

signal.disconnect(callback);  // remove the first listener with that callback
signal.disconnectAll();       // remove every listener
signal.hasConnections();      // true if at least one listener is connected
signal.getConnectionsCount(); // number of connected listeners
```

- Listeners run in ascending `order`, then connection order. A listener connected while the signal is emitting runs on the next emit; one disconnected mid-emit does not run.

## Import Patterns

No default export. Always use named imports:

```ts
// Import specific components
import { FancyButton, ScrollBox, Drawer } from '@pixi/ui';

// All available exports
import {
    Button,
    ButtonContainer,
    ButtonEvents,
    CheckBox,
    CircularProgressBar,
    Dialog,
    DoubleSlider,
    Drawer,
    FancyButton,
    Input,
    List,
    MaskedFrame,
    ProgressBar,
    RadioGroup,
    ScrollBox,
    Select,
    Signal,
    Slider,
    SliderBase,
    Switcher,
} from '@pixi/ui';
```

## Ticker Setup

`FancyButton` (when created with the `animations` option), `Dialog`, and `Drawer` each register their own `Ticker.shared` callback in the constructor (`() => Group.shared.update()`) and remove it in `destroy()`. You do **not** need to add a ticker callback for these components.

If you write your own `tweedle.js` tweens (e.g., animating a plain container), register one manually:

```ts
import { Ticker } from 'pixi.js';
import { Group } from 'tweedle.js';

// Register once at application startup — only needed for custom tweens
Ticker.shared.add(() => Group.shared.update());
```

`Input` and `ScrollBox` also run on `Ticker.shared` (caret blink, easing); PixiJS starts the shared ticker automatically with the renderer, so nothing extra is needed in a normal `Application`.

## Application Setup

```ts
import { Application } from 'pixi.js';

const app = new Application();
await app.init({
    width: 800,
    height: 600,
    backgroundColor: 0x1099bb,
    antialias: true,
    resolution: window.devicePixelRatio,
});

document.body.appendChild(app.canvas);
```

## Asset Loading

Load textures before passing their names to components:

```ts
import { Assets } from 'pixi.js';

// Load individual assets
await Assets.load('button_default.png');
await Assets.load('button_hover.png');

// Load bundles
await Assets.loadBundle('ui', [
    'button_default.png',
    'button_hover.png',
    'button_pressed.png',
    'input_bg.png',
    'slider_bg.png',
    'slider_handle.png',
]);

// Or use manifest
await Assets.loadBundle('ui-manifest');
```

After loading, reference by name (string) in component options:

```ts
const button = new FancyButton({
    defaultView: 'button_default.png',
    hoverView: 'button_hover.png',
});
```

## TypeScript

Full type definitions are included. Import types directly:

```ts
import type {
    ButtonOptions,
    ScrollBoxOptions,
    SliderOptions,
    DoubleSliderOptions,
    InputOptions,
    SelectOptions,
    SelectItemsOptions,
    DialogOptions,
    DrawerOptions,
    DrawerPosition,
    CheckBoxOptions,
    MaskedFrameOptions,
    MaskedProgressBarOptions,
    ListOptions,
    ListType,
    ContentFittingMode,
} from '@pixi/ui';
```
