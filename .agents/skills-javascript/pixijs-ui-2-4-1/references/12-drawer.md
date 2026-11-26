# Drawer — Edge Panel (new in 2.4)

A panel that slides in from an edge of the screen (`bottom` by default, plus `top`, `left`, `right`), with an optional backdrop, swipe-to-close, and a scrollable content area. Like `Dialog`, it opens/closes instantly or with a tween — but it **slides** (position) instead of scaling.

## Positioning Model

The drawer lays itself out **relative to the screen centre**:

- Add it to a container that is centred on the screen (e.g., `app.stage` children positioned so the drawer's origin is at screen centre, or a centred holder container).
- Call `drawer.setScreenSize(width, height)` to tell it the screen size. **Defaults to 800×600 if you forget.**
- `setScreenSize` also re-anchors an *open* drawer (and stops any in-flight slide) so it stays glued to the correct edge after resizes.

Open positions: bottom ⇒ `(-w/2, h/2 - drawerHeight)`; top ⇒ `(-w/2, -h/2)`; left ⇒ `(-w/2, -h/2)`; right ⇒ `(w/2 - drawerWidth, -h/2)`. Closed position is the open position shifted one drawer size off-screen in the edge direction. Top/bottom drawers span the full screen width; left/right drawers span the full screen height (the background is resized accordingly).

## Options (`DrawerOptions`)

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `background` | view | — | **Required.** Panel background; omitted ⇒ throws `Drawer background is not defined. Please provide options.background.` |
| `position` | `'bottom' \| 'top' \| 'left' \| 'right'` | `'bottom'` | Screen edge the drawer is attached to (this option is the edge, **not** a coordinate) |
| `content` | `Container \| Container[]` | — | Content; always wrapped in an internal vertical `ScrollBox` offset by `padding` |
| `width` | `number` | — | Panel width (visible width for left/right drawers). `ScrollBox` width = width − 2×padding |
| `height` | `number` | — | Panel height (visible height for top/bottom drawers). `ScrollBox` height = height − 2×padding |
| `padding` | `number` | `20` | Content inset |
| `backdrop` | view | — | Backdrop view; omitted ⇒ large tinted `Sprite` (10000×10000 at −5000,−5000) |
| `backdropColor` | `number` | `0x000000` | Tint of the generated backdrop |
| `backdropAlpha` | `number` | `0.5` | Alpha of the generated backdrop when open |
| `scrollBox` | `ScrollBoxOptions` | — | Options for the internal ScrollBox (spread over defaults: black bg, vertical, margin 10, padding 10) |
| `animations` | `{ open?: { props, duration? }, close?: { props, duration? } }` | — | Without them the drawer opens/closes instantly. Only `duration` is used (default 300); `props` is accepted but currently unused |
| `closeOnBackdropClick` | `boolean` | **`true`** | Closes on backdrop tap unless explicitly `false` (opposite of Dialog's default) |
| `swipeToClose` | `boolean` | **`true`** | Swipe gesture closes the drawer (see below) |
| `nineSliceSprite` | `[number, number, number, number]` | — | Nine-slice for the background (texture name/Texture only; Container warns and is used as-is) |
| + `ContainerOptions` (except `position`) | | | `position` is taken by the drawer edge — use `x`/`y` to move the drawer |

## API

| Member | Description |
|--------|-------------|
| `onClose` | `Signal<() => void>` — emitted **after** the close animation finishes (or immediately when there is no close animation) |
| `isOpen` | `boolean` — becomes false only after the close animation has finished |
| `open()` / `show()` | Slide in; with `animations.open`, tweens backdrop alpha 0 → backdropAlpha and the panel from the closed to the open position (duration default 300). Any in-flight close is stopped first |
| `close()` / `hide()` | Slide out; with `animations.close`, tweens to the closed position, then hides and emits `onClose`. Any in-flight open is stopped first |
| `setScreenSize(width, height)` | Update screen dimensions; resizes the background to span the full edge and re-anchors an open drawer |
| `destroy(options?)` | Detaches the shared-ticker callback, stops tweens, and destroys the internal `ScrollBox` (releasing its ticker callback and document wheel listener) |

## Swipe-to-Close

Enabled by default (`swipeToClose: true`). A pointerdown on the panel records the start position; on pointerup/pointerupoutside the displacement is measured:

| Position | Closing gesture |
|----------|-----------------|
| `bottom` | swipe **down** (Δy > 50) |
| `top` | swipe **up** (Δy < −50) |
| `left` | swipe **left** (Δx < −50) |
| `right` | swipe **right** (Δx > 50) |

The release point past the drawer edge counts too — a flick down a bottom drawer usually ends below it. Displacements under 50px or in the opposite direction do nothing.

## Structure

Child order: `backdrop` (first), then `innerView` (the panel: `backgroundView` + `contentView`, the latter holding the `ScrollBox`). The drawer is `visible = false` until `open()`. It registers its own `Ticker.shared` callback in the constructor and removes it in `destroy()`.

## Example

```ts
const drawer = new Drawer({
    background: new Graphics().roundRect(0, 0, 400, 300, 20).fill(0xffffff),
    content: new Text({
        text: 'Swipe up to close this drawer',
        style: { fill: 0x000000, fontSize: 18, wordWrap: true, wordWrapWidth: 360 },
    }),
    width: 400,
    height: 300,
    padding: 20,
    position: 'bottom',
    backdropColor: 0x000000,
    backdropAlpha: 0.5,
    closeOnBackdropClick: true,
    swipeToClose: true,
    animations: {
        open: { props: {}, duration: 300 },
        close: { props: {}, duration: 300 },
    },
});

// Tell the drawer the screen size (defaults to 800x600 otherwise)
drawer.setScreenSize(app.screen.width, app.screen.height);

drawer.onClose.connect(() => console.log('Drawer closed'));

view.addChild(drawer); // view is centred on the screen
drawer.open();
```
