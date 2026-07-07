# Installation & Setup

## Installation

```sh
npm install @pixi/ui
# or
yarn add @pixi/ui
# or
pnpm add @pixi/ui
```

## Peer Dependencies

PixiUI v2.3.2 requires `pixi.js ^8.6.2` as a peer dependency. Install PixiJS first:

```sh
npm install pixi.js@^8.6.2 @pixi/ui@2.3.2
```

### Compatibility Matrix

| PixiJS | PixiUI |
|--------|--------|
| v7.x   | v1.x   |
| v8.x   | v2.x   |

### Runtime Dependencies

PixiUI bundles two dependencies:
- **`tweedle.js`** (^2.1.0) — animation/tweening engine for `FancyButton` and `Dialog` animations
- **`typed-signals`** (^2.5.0) — type-safe signal/slot event system used by all components

## Import Patterns

No default export. Always use named imports:

```ts
// Import specific components
import { FancyButton, ScrollBox, CheckBox } from '@pixi/ui';

// All available exports
import {
    Button,
    ButtonContainer,
    ButtonEvents,
    CheckBox,
    CircularProgressBar,
    Dialog,
    DoubleSlider,
    FancyButton,
    Input,
    List,
    MaskedFrame,
    ProgressBar,
    RadioGroup,
    ScrollBox,
    Select,
    Slider,
    SliderBase,
    Switcher,
} from '@pixi/ui';
```

## Ticker Setup

Components that use animations (`FancyButton` with `animations` option, `Dialog` with `animations` option) require the shared ticker to update tweens:

```ts
import { Ticker } from 'pixi.js';
import { Group } from 'tweedle.js';

// Register once at application startup
Ticker.shared.add(() => Group.shared.update());
```

This is only needed if you use animated FancyButtons or animated Dialogs. Static components (CheckBox, Slider, Input, etc.) do not require this.

## Application Setup

```ts
import { Application } from 'pixi.js';
import { Group } from 'tweedle.js';
import { Ticker } from 'pixi.js';

const app = new Application();
await app.init({
    width: 800,
    height: 600,
    backgroundColor: 0x1099bb,
    antialias: true,
    resolution: window.devicePixelRatio,
    preference: 'webgl',
    autoStart: true,
});

document.body.appendChild(app.canvas);

// Required for FancyButton/Dialog animations
Ticker.shared.add(() => Group.shared.update());
```

## Asset Loading

Load textures before passing them to components:

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
    CheckBoxOptions,
    MaskedFrameOptions,
    MaskedProgressBarOptions,
    ListOptions,
    ListType,
    ContentFittingMode,
    Offset,
} from '@pixi/ui';
```
