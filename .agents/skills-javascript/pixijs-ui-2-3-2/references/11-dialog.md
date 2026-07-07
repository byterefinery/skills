# Dialog

Modal dialog component with backdrop, title, scrollable content, and action buttons.

## Constructor

```ts
const dialog = new Dialog(options: DialogOptions);
```

## Options (`DialogOptions`)

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `background` | `GetViewSettings` | required | Dialog panel background |
| `backdrop` | `GetViewSettings` | — | Custom backdrop view |
| `backdropColor` | `number` | `0x000000` | Backdrop tint color |
| `backdropAlpha` | `number` | `0.5` | Backdrop opacity |
| `title` | `AnyText` | — | Title text (string, Text, BitmapText, HTMLText) |
| `content` | `AnyText \| Container \| Container[]` | — | Dialog content |
| `width` | `number` | — | Dialog width |
| `height` | `number` | — | Dialog height |
| `padding` | `number` | `20` | Internal padding |
| `buttons` | `(ButtonOptions \| FancyButton \| Button)[]` | — | Action buttons |
| `buttonList` | `ListOptions` | — | Button row layout options |
| `scrollBox` | `ScrollBoxOptions` | — | Content scroll options |
| `animations` | `{open?, close?}` | — | Open/close tween animations |
| `closeOnBackdropClick` | `boolean` | `false` | Close when backdrop clicked |
| `nineSliceSprite` | `[number, number, number, number]` | — | Nine-slice for background |

## Animation Type

```ts
type Animation = {
    props: Record<string, any>;  // scale, alpha, x, y, etc.
    duration?: number;           // ms (default: 300)
};
```

## Properties

| Property | Type | Description |
|----------|------|-------------|
| `isOpen` | `boolean` | Whether dialog is currently open |
| `onSelect` | `Signal<(buttonIndex, buttonText) => void>` | Button selection signal |
| `onClose` | `Signal<() => void>` | Dialog close signal |

## Methods

| Method | Description |
|--------|-------------|
| `open()` | Show dialog (with animation if configured) |
| `close()` | Hide dialog (with animation if configured) |
| `show()` | Alias for `open()` |
| `hide()` | Alias for `close()` |

## Example

```ts
const dialog = new Dialog({
    background: new Graphics().roundRect(0, 0, 400, 200, 15).fill(0x222222),
    backdropColor: 0x000000,
    backdropAlpha: 0.6,
    title: new Text({ text: 'Confirm Action', style: { fill: 0xffffff, fontSize: 20 } }),
    content: 'Are you sure you want to delete this item? This cannot be undone.',
    width: 400,
    height: 200,
    padding: 20,
    buttons: [
        {
            text: 'Cancel',
            defaultView: new Graphics().roundRect(0, 0, 80, 30, 5).fill(0x444444),
        },
        {
            text: 'Delete',
            defaultView: new Graphics().roundRect(0, 0, 80, 30, 5).fill(0xcc3333),
        },
    ],
    animations: {
        open: {
            props: { scale: { x: 1, y: 1 } },
            duration: 200,
        },
        close: {
            props: { scale: { x: 0.8, y: 0.8 } },
            duration: 200,
        },
    },
    closeOnBackdropClick: true,
});

// Add to stage once
app.stage.addChild(dialog);

// Open
dialog.open();

// Handle button clicks
dialog.onSelect.connect((index, text) => {
    if (index === 1) {
        console.log('User confirmed deletion');
    }
    dialog.close();
});

// Handle close
dialog.onClose.connect(() => {
    console.log('Dialog closed');
});
```

## Content Types

### String content

```ts
content: 'This is a plain text message.'
// Creates a Text view inside ScrollBox
```

### Container content

```ts
content: myContainer
// Adds the container directly to ScrollBox
```

### Array of containers

```ts
content: [container1, container2, container3]
// Adds each container to ScrollBox
```

## Button Types

Buttons can be passed as:

1. **ButtonOptions** (object) — Creates a `FancyButton` internally
2. **FancyButton** instance — Used directly, `text` read from instance
3. **Button** instance — Used directly, text is empty string

```ts
buttons: [
    { text: 'OK', defaultView: /* ... */ },          // ButtonOptions → FancyButton
    new FancyButton({ text: 'Cancel', /* ... */ }),  // FancyButton instance
    new Button(view),                                // Button instance
]
```

## Internal Structure

```
Dialog (Container)
├─ backdrop: Container          — Full-screen overlay (10000x10000, centered at 0,0)
├─ innerView: Container         — Dialog panel
   ├─ contentView: Container    — Title + ScrollBox + buttons
   │  ├─ titleText: PixiText    — Title (if provided)
   │  ├─ scrollBox: ScrollBox   — Scrollable content area
   │  └─ buttonContainer: List  — Horizontal list of buttons
```

## Animation Setup

Animations require `tweedle.js` ticker:

```ts
import { Ticker } from 'pixi.js';
import { Group } from 'tweedle.js';

Ticker.shared.add(() => Group.shared.update());
```

Without the ticker, animated dialogs will snap to final state without tweening.

## NineSlice Background

Pass a texture name or Texture instance for `background` to use NineSliceSprite:

```ts
const dialog = new Dialog({
    background: 'dialog_panel.png',
    nineSliceSprite: [15, 15, 15, 15],
    width: 400,
    height: 300,
    // ...
});
```

With NineSlice, `width` and `height` resize the NineSliceSprite while preserving corner proportions.
