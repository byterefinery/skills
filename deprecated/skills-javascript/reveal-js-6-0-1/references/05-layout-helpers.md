# Layout Helpers Reference

## r-fit-text

Automatically scales text to fill its container. Applied via `class="r-fit-text"`:

```html
<h2 class="r-fit-text">FIT TEXT</h2>
```

Uses [Fitty](https://github.com/richard-zhang-digital/fitty) library. Works on any text element. The text scales to be as large as possible within the container bounds.

```html
<h2 class="r-fit-text">SHORT</h2>
<h2 class="r-fit-text">BOTH TITLES AUTO-SIZE</h2>
```

## r-stretch

Makes an element as tall as possible while staying within slide bounds:

```html
<img src="image.png" class="r-stretch">
<video src="video.mp4" class="r-stretch">
```

Preserves aspect ratio. Works on images, videos, and any block element. The element fills available vertical space after accounting for sibling elements.

```html
<section>
  <h2>Title</h2>
  <img src="large-image.png" class="r-stretch">
  <p>Image byline</p>
</section>
```

## r-stack

Stacks child elements on top of each other (absolute positioning). Used with fragments to show elements in sequence at the same position:

```html
<div class="r-stack">
  <img class="fragment" src="image1.png" width="400" height="300">
  <img class="fragment" src="image2.png" width="400" height="300">
  <img class="fragment" src="image3.png" width="400" height="300">
</div>
```

Each fragment replaces the previous one at the exact same position. Combine with `fade-in-then-out` for crossfade:

```html
<div class="r-stack">
  <p class="fragment fade-in-then-out">One</p>
  <p class="fragment fade-in-then-out">Two</p>
  <p class="fragment fade-in-then-out">Three</p>
</div>
```

## r-hstack

Horizontal flexbox layout:

```html
<div class="r-hstack">
  <div>Column 1</div>
  <div>Column 2</div>
  <div>Column 3</div>
</div>
```

Supports Flexbox utility classes:
- `justify-start`, `justify-center`, `justify-end`, `justify-between`, `justify-around`
- `items-start`, `items-center`, `items-end`

```html
<div class="r-hstack justify-center items-center">
  <div>Centered items</div>
</div>
```

## r-vstack

Vertical flexbox layout:

```html
<div class="r-vstack">
  <div>Row 1</div>
  <div>Row 2</div>
  <div>Row 3</div>
</div>
```

Same alignment utilities as `r-hstack`:

```html
<div class="r-vstack items-start">
  <div>Left-aligned</div>
</div>
```

## Combining Helpers

Nest helpers for complex layouts:

```html
<div class="r-hstack">
  <div class="r-vstack">
    <h3>Left Column</h3>
    <img src="img.png" class="r-stretch">
  </div>
  <div class="r-vstack">
    <h3>Right Column</h3>
    <div class="r-stack">
      <div class="fragment">Step 1</div>
      <div class="fragment">Step 2</div>
    </div>
  </div>
</div>
```

## With Auto-Animate

Layout helpers work with auto-animate. Elements inside helpers can have `data-id` for cross-slide animation:

```html
<section data-auto-animate>
  <div class="r-hstack justify-center">
    <div data-id="box1" style="background:#999;width:50px;height:50px;margin:10px"></div>
    <div data-id="box2" style="background:#999;width:50px;height:50px;margin:10px"></div>
    <div data-id="box3" style="background:#999;width:50px;height:50px;margin:10px"></div>
  </div>
</section>
<section data-auto-animate>
  <div class="r-stack">
    <div data-id="box1" style="background:cyan;width:300px;height:300px"></div>
    <div data-id="box2" style="background:magenta;width:200px;height:200px"></div>
    <div data-id="box3" style="background:yellow;width:100px;height:100px"></div>
  </div>
</section>
```

## CSS Classes Summary

| Class | Type | Purpose |
|---|---|---|
| `r-fit-text` | Text | Auto-size text to container |
| `r-stretch` | Media/Block | Stretch to fill vertical space |
| `r-stack` | Container | Stack children absolutely |
| `r-hstack` | Container | Horizontal flexbox |
| `r-vstack` | Container | Vertical flexbox |

Alignment utilities (for hstack/vstack):
- `justify-start`, `justify-center`, `justify-end`, `justify-between`, `justify-around`
- `items-start`, `items-center`, `items-end`
