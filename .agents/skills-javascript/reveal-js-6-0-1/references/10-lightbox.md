# Lightbox Preview Overlays Reference

reveal.js 6.0.1 has built-in lightbox support for images, videos, and iframes. No external plugin needed.

## Image Previews

### Same Image

```html
<img src="thumbnail.png" data-preview-image>
```

Clicking the image opens a full-size overlay of the same image.

### Different Preview Image

```html
<img src="thumbnail.png" data-preview-image="fullsize.png">
```

Show a thumbnail but preview a different (larger) image.

### From a Link

```html
<a href="#" data-preview-image="image.png">
  Click to preview image
</a>
```

### Fit Modes

```html
<img src="image.png" data-preview-image data-preview-fit="contain">
<img src="image.png" data-preview-image data-preview-fit="cover">
```

- `contain` — Fit entire image in viewport (default)
- `cover` — Fill viewport, may crop

## Video Previews

### From an Image

```html
<img src="poster.png" data-preview-video="video.mp4">
```

### From a Video Element

```html
<video src="video.mp4" data-preview-video height="100"></video>
```

### From a Link

```html
<a href="#" data-preview-video="video.mp4">
  Watch video
</a>
```

## Iframe Previews (Link Previews)

### Enable Globally

```js
Reveal.initialize({ previewLinks: true });
```

With `previewLinks: true`, all external links open in an iframe overlay instead of navigating away.

### Per-Link Control

```html
<a href="https://example.com">Opens normally</a>
<a href="https://example.com" data-preview-link>Opens in overlay</a>
<a href="https://example.com" data-preview-link="false">Never opens in overlay</a>
```

- `data-preview-link` — Force preview overlay
- `data-preview-link="false"` — Disable preview (even if `previewLinks: true`)

### From an Image

```html
<img src="icon.png" data-preview-link="https://example.com">
```

Clicking the image opens the URL in an iframe overlay.

## Disabling Link Previews

```js
Reveal.initialize({ previewLinks: false });
```

With `previewLinks: false` (default), only explicit `data-preview-*` attributes trigger overlays.

## Keyboard Controls

In the lightbox overlay:
- `Escape` — Close overlay
- Arrow keys — Navigate (if applicable)

## Styling

The lightbox is built into reveal.js CSS. Customize with:

```css
.reveal-overlay {
  /* Custom overlay styles */
}

.reveal-overlay .overlay-background {
  /* Background styling */
}
```

## Examples

### Gallery Layout

```html
<section>
  <h2>Image Gallery</h2>
  <div class="r-hstack" style="gap: 1rem;">
    <figure>
      <img height="80" src="thumb1.png" data-preview-image="full1.png" data-preview-fit="contain">
      <figcaption>Photo 1</figcaption>
    </figure>
    <figure>
      <img height="80" src="thumb2.png" data-preview-image="full2.png" data-preview-fit="contain">
      <figcaption>Photo 2</figcaption>
    </figure>
    <figure>
      <img height="80" src="thumb3.png" data-preview-image="full3.png" data-preview-fit="contain">
      <figcaption>Photo 3</figcaption>
    </figure>
  </div>
</section>
```

### Mixed Preview Types

```html
<section>
  <div class="r-hstack items-start">
    <!-- Image preview -->
    <img src="small.png" data-preview-image>

    <!-- Video preview -->
    <img src="poster.png" data-preview-video="video.mp4">

    <!-- Link preview -->
    <a data-preview-link href="https://example.com">Visit site</a>
  </div>
</section>
```

## Attributes Summary

| Attribute | Element | Purpose |
|---|---|---|
| `data-preview-image` | `<img>`, `<a>` | Preview image in overlay |
| `data-preview-image="URL"` | `<img>`, `<a>` | Preview a different image URL |
| `data-preview-video` | `<img>`, `<video>`, `<a>` | Preview video in overlay |
| `data-preview-video="URL"` | `<img>`, `<video>`, `<a>` | Preview a specific video URL |
| `data-preview-link` | `<a>`, `<img>` | Open URL in iframe overlay |
| `data-preview-link="false"` | `<a>` | Disable link preview |
| `data-preview-fit` | `<img>` | `"contain"` or `"cover"` for image fit |
