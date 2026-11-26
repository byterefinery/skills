# Dialog — Modal

Modal dialog: backdrop + background panel + optional title + scrollable content + button row. Open/close are instant or tweened (scale 0.8 ⇄ 1) with `tweedle.js`.

## Options (`DialogOptions`)

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `background` | view | — | **Required.** Panel background; omitted ⇒ throws `Dialog background is not defined. Please provide options.background.` |
| `backdrop` | view | — | Backdrop view; omitted ⇒ a large tinted `Sprite` (10000×10000, centred on the dialog) |
| `backdropColor` | `number` | `0x000000` | Tint of the generated backdrop |
| `backdropAlpha` | `number` | `0.5` | Alpha of the generated backdrop (also the target alpha during open animation) |
| `title` | `string \| number \| Text \| BitmapText \| HTMLText` | — | Title text, centred at the top (anchor 0.5, 0) |
| `content` | `string \| number \| Container \| Container[]` | — | Content: string/number becomes a text view; array items are added one by one |
| `width` / `height` | `number` | — | Dialog size (panel is resized for `NineSliceSprite`/`Graphics` backgrounds when both are set) |
| `padding` | `number` | `20` | Padding around content, title offset, and button row inset |
| `buttons` | `(ButtonOptions \| FancyButton \| Button)[]` | — | Button row config or instances (plain objects become `FancyButton`s) |
| `buttonList` | `ListOptions<Container>` | — | Layout options for the button row (`List`, horizontal, margin 10) |
| `scrollBox` | `ScrollBoxOptions` | — | Options for the internal content `ScrollBox` (bidirectional, spread over defaults) |
| `animations` | `{ open?: Animation, close?: Animation }` | — | `{ props, duration? }`; without them the dialog appears/disappears instantly |
| `closeOnBackdropClick` | `boolean` | **`false`** | **Must be set explicitly to `true`** — backdrop click does NOT close by default |
| `nineSliceSprite` | `[number, number, number, number]` | — | Nine-slice for the panel (texture name/Texture only; Container warns and is used as-is) |
| + `ContainerOptions` | | | Passed through to the container |

## API

| Member | Description |
|--------|-------------|
| `onSelect` | `Signal<(buttonIndex: number, buttonText: string) => void>` — fires when a button is pressed; text is `''` for raw `Button` instances |
| `onClose` | `Signal<() => void>` — fires when the dialog is closed (immediately, or at the end of the close animation) |
| `isOpen` | `boolean` — open state |
| `open()` / `show()` | Show; with `animations.open` tweens backdrop alpha 0 → backdropAlpha and panel scale 0.8 → 1 |
| `close()` / `hide()` | Hide; with `animations.close` tweens back, then emits `onClose` |
| `destroy(options?)` | Removes the shared-ticker callback and destroys the internal `ScrollBox` (which releases its document wheel listener) |

## Structure

- Child order: `backdrop` (first, offset to cover the screen), then `innerView` (the panel) containing `contentView`.
- The panel's anchor/pivot is centred (0.5, 0.5) so `width`/`height` scale around the middle.
- Internal `ScrollBox` is sized to the dialog minus padding, title height, and the button row height; it is bidirectional with `padding: 10`, `elementsMargin: 10` defaults (overridable via `scrollBox`).
- The dialog registers its own `Ticker.shared` callback in the constructor (for tweens) and removes it in `destroy()` — no manual ticker registration.

## Gotchas

- **`closeOnBackdropClick` defaults to false** (unlike `Drawer`, where it defaults to true). Set it explicitly if you expect backdrop taps to close.
- **`onClose` timing** — with a close animation it fires when the tween completes; without one, synchronously in `close()`.
- **Button text in `onSelect`** — plain `ButtonOptions` objects become `FancyButton`s (text available); `FancyButton` instances report their `text`; raw `Button` instances emit `''`.
- **`destroy()` cascades to the ScrollBox** — needed to release the document wheel listener the internal ScrollBox attaches.

## Example

```ts
const dialog = new Dialog({
    background: new Graphics().roundRect(0, 0, 400, 200, 20).fill(0xffffff),
    title: 'Confirm',
    content: 'Are you sure?',
    width: 400,
    height: 200,
    padding: 20,
    buttons: [
        { text: 'Cancel', defaultView: new Graphics().roundRect(0, 0, 80, 30, 5).fill(0x444444) },
        { text: 'OK', defaultView: new Graphics().roundRect(0, 0, 80, 30, 5).fill(0x3366ff) },
    ],
    animations: {
        open: { props: {}, duration: 300 },
        close: { props: {}, duration: 300 },
    },
});

dialog.onSelect.connect((index, text) => console.log(`Button ${index} clicked: ${text}`));
dialog.onClose.connect(() => console.log('closed'));
dialog.open();
```
