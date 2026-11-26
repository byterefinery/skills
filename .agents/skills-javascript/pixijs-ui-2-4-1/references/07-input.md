# Input — Text Entry (v2.4 architecture)

In v2.4.x `Input` was rewritten around a **hidden native `<input>` element**: the text, caret, and selection live in that field, so typing, IME composition, autocorrect, suggestions, and paste behave exactly as the platform does them. The component draws what the field holds. It is built in layers:

- `InputView` — state, background, sizing, placeholder, cursor
- `InputText` — creates, measures and lays out the text
- `InputSelection` — caret, selection and pointer gestures on the canvas
- `InputTouch` — gestures on the hidden field on touch devices
- `Input` — runs the editing session

## Options (`InputOptions`)

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `bg` | `Sprite \| Graphics \| Texture \| string` | — | **Required.** Background; string = texture name. Omitting it logs `Input: bg is not defined, please define it.` (console.error) |
| `textStyle` | `PixiTextStyle` | — | Style of the entered text |
| `TextClass` | `Text \| BitmapText \| HTMLText` | `Text` | Class used to draw text and placeholder |
| `placeholder` | `string` | — | Placeholder shown when idle and empty |
| `value` | `string` | `''` | Initial value |
| `maxLength` | `number` | — | Max length in UTF-16 code units; also applied to pasted text and keyboard suggestions (which the native limit does not cover) |
| `secure` | `boolean` | `false` | Draws each character as `*` and makes the hidden field `type="password"`; toggleable later via `input.secure` |
| `align` | `'left' \| 'center' \| 'right'` | `'left'` | Text alignment while it fits |
| `padding` | `Padding` | — | Text padding: `number`, `[v, h]`, `[t, r, b, l]`, or `{ top?, right?, bottom?, left? }` |
| `cleanOnFocus` | `boolean` | `false` | Clear the value each time editing starts |
| `addMask` | `boolean` | `false` | Mask the text so it is clipped when it overflows the bg |
| `nineSliceSprite` | `[number, number, number, number]` | — | Nine-slice for the bg (texture name/Texture instances only) |
| `inputAttributes` | `Record<string, string>` | defaults | Attributes for the hidden field, merged over defaults (`autocomplete`/`autocapitalize`/`autocorrect` off, `spellcheck` false, password-manager ignore flags). Use it for `inputmode` or `enterkeyhint` |
| + `ContainerOptions` | | | Passed through to the container |

## Signals

| Signal | Parameters | Description |
|--------|-----------|-------------|
| `onChange` | `(text: string)` | Fires on every **user** change: typing, deleting, pasting, keyboard suggestions. **Not** fired when `value` is set from code or cleared by `cleanOnFocus`. During an IME composition that exceeds `maxLength`, the cut waits until the composition commits. |
| `onEnter` | `(text: string)` | Fires **once when editing ends** — Enter, Escape, or focus leaving the input (press elsewhere, Tab, dismissed keyboard) — with the current value. |

## Properties & Methods

| Member | Type | Description |
|--------|------|-------------|
| `value` | `string` | Get/set the text (mirrors the hidden field while editing) |
| `secure` | `boolean` | Get/set secure mode |
| `bg` | view | Get/set background (previous bg is destroyed) |
| `padding` | `[number, number, number, number]` | Get/set padding |
| `placeholder` | string | Placeholder text |
| `selectionStart` / `selectionEnd` | `number` | Caret/selection range in the value |
| `selectionDirection` | `'forward' \| 'backward' \| 'none'` | Which end of a selection holds the caret |
| `width` / `height` / `setSize` | — | Resize; nine-slice-aware when set |
| `destroy(options?)` | — | Detaches window listeners, ticker callback, and the hidden field |

## Editing Session

1. A tap on the input marks activation; the hidden field is created, seeded with the current value, and focused (on **Android after a 100ms delay** to stop the keyboard being dismissed instantly).
2. While editing, the canvas shows the text, a blinking caret (blink runs on `Ticker.shared`, added in the constructor), and the selection highlight (alpha 0.35 in the text colour). The caret is hidden while a range is selected, like native fields.
3. Taps place the caret; **double-click selects a word** (multi-click counting with distance checks; only the primary button); drags select ranges, and holding past an overflow edge auto-scrolls.
4. Enter or Escape ends the session; so does focus genuinely leaving (a press on the canvas itself re-focuses the hidden field instead of ending the session). `onEnter` emits the final value.
5. `maxLength` is enforced in UTF-16 code units, including pastes and suggestions; over-long IME text is cut when the composition commits.

## Gotchas

- **`onEnter` ≠ "Enter was pressed"** — it is the session-end signal (Enter, Escape, or blur).
- **Programmatic `value =` sets do not emit `onChange`** — the hidden field is written directly so the next keystroke edits the new string.
- **The hidden field is emptied before removal** so password managers have nothing to offer to save.
- **Window-level listeners** (`click`/`touchstart` for activation, `pointerdown` and `contextmenu` in capture phase) are added in the constructor and removed in `destroy()` — call `destroy()` when removing inputs.
- **Caret blink needs the shared ticker** — the tick callback is registered in the constructor; without a running ticker the caret won't blink.

## Example

```ts
const input = new Input({
    bg: Sprite.from('input.png'),
    placeholder: 'Enter text',
    padding: { top: 11, right: 11, bottom: 11, left: 11 }, // or [11, 11, 11, 11], [11, 11], or 11
});

input.onChange.connect((text) => console.log('typing:', text));
input.onEnter.connect((text) => console.log('submitted:', text));
input.value = 'Hello';
input.secure = true;
```
