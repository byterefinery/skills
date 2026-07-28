---
title: Media
---

# Media

## Avatar

Avatars use `<figure>` with `data-variant="avatar"`. Supports text, images, and grouped stacks.

### Text Avatar

```html
<figure data-variant="avatar">JD</figure>
```

Circular container with initials, `--primary` text on `--muted` background.

### Image Avatar

```html
<figure data-variant="avatar">
  <img src="avatar.jpg" alt="John Doe">
</figure>
```

Image fills the circular container with `object-fit: cover`.

### Sizes

```html
<figure data-variant="avatar" class="small">JD</figure>
<figure data-variant="avatar">JD</figure>
<figure data-variant="avatar" class="large">JD</figure>
```

| Size | Class | Dimensions |
|---|---|---|
| Small | `.small` | 2rem × 2rem |
| Default | — | 2.5rem × 2.5rem |
| Large | `.large` | 3.25rem × 3.25rem |

Custom size via CSS variable:

```html
<figure data-variant="avatar" style="--sz: 4rem">JD</figure>
```

### Grouped Avatars

Use `role="group"` on a parent `<figure>` to stack avatars with overlapping edges:

```html
<figure data-variant="avatar" role="group">
  <figure data-variant="avatar">
    <img src="alice.jpg" alt="Alice">
  </figure>
  <figure data-variant="avatar">
    <img src="bob.jpg" alt="Bob">
  </figure>
  <figure data-variant="avatar">JD</figure>
</figure>
```

- Avatars overlap with negative margin
- Each avatar gets a `2px` border matching `--background` for separation
- Last avatar has no negative margin

### Grouped Sizes

```html
<figure data-variant="avatar" role="group" class="small">
  <figure data-variant="avatar">A</figure>
  <figure data-variant="avatar">B</figure>
  <figure data-variant="avatar">C</figure>
</figure>

<figure data-variant="avatar" role="group" class="large">
  <figure data-variant="avatar">A</figure>
  <figure data-variant="avatar">B</figure>
</figure>
```

Group size classes (`.small`, `.large`) control child avatar sizes and overlap spacing.

## Images

Generic `<img>`, `<picture>`, `<video>`, `<canvas>`, `<svg>` all have `max-width: 100%` set automatically.

```html
<img src="photo.jpg" alt="Description">
<picture>
  <source srcset="photo.webp" type="image/webp">
  <img src="photo.jpg" alt="Description">
</picture>
<video src="video.mp4" controls></video>
```
