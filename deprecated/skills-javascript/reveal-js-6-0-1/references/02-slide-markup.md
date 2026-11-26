# Slide Markup Reference

## Basic Structure

```html
<div class="reveal">
  <div class="slides">
    <section>Horizontal slide 1</section>
    <section>Horizontal slide 2</section>
    <section>
      <section>Vertical slide 2.1</section>
      <section>Vertical slide 2.2</section>
    </section>
  </div>
</div>
```

Top-level `<section>` elements are horizontal slides. Nested `<section>` elements inside a parent create a vertical stack.

## Slide Attributes

### Backgrounds

```html
<section data-background="#283b95">
<section data-background="image.png">
<section data-background-gradient="linear-gradient(to bottom, #283b95, #17b2c3)">
<section data-background-size="cover">
<section data-background-repeat="repeat">
<section data-background-position="center">
<section data-background-opacity="0.5">
```

All CSS color formats are supported: hex, rgb, rgba, hsl, hsla, named colors.

### Video Backgrounds

```html
<section data-background-video="video.mp4,video.webm">
<section data-background-video data-background-video-loop data-background-video-muted>
```

Provide multiple formats for browser compatibility. Use `data-background-video-loop` for looping and `data-background-video-muted` to mute.

### Iframe Backgrounds

```html
<section data-background-iframe="https://example.com" data-background-interactive>
```

`data-background-interactive` enables mouse/keyboard interaction with the embedded page.

### Background Transitions

```html
<section data-background-transition="zoom">
```

Override the global `backgroundTransition` setting per slide. Values: `none`, `fade`, `slide`, `convex`, `concave`, `zoom`.

Background transitions can also be set globally via `Reveal.configure({ backgroundTransition: 'zoom' })`.

### Slide Transitions

```html
<section data-transition="zoom">
<section data-transition="zoom-in fade-out">
```

Single value applies to both in and out. Two values (space-separated) set separate in/out transitions.

Transition values: `none`, `fade`, `slide`, `convex`, `concave`, `zoom`. With directional suffixes: `zoom-in`, `zoom-out`, `fade-in`, `fade-out`, `slide-in`, `slide-out`, `convex-in`, `convex-out`, `concave-in`, `concave-out`.

### Visibility

```html
<section data-visibility="hidden">
```

Hidden slides are removed from the DOM during initialization (unless `showHiddenSlides: true`). They remain in the source and can be conditionally shown.

### Slide State

```html
<section data-state="customevent">
```

Adds `customevent` as a class on the `.reveal` wrapper when the slide is active. Multiple states: `data-state="edit-mode special"`.

Listen for state events:

```js
Reveal.on('customevent', () => {
  console.log('Custom event fired');
});
```

State classes are removed when navigating away from the slide.

### Auto-Slide Timing

```html
<section data-autoslide="5000">
```

Override the global `autoSlide` setting for a specific slide (value in ms).

### Notes

```html
<section>
  Slide content
  <aside class="notes">
    Speaker notes go here. Supports HTML and Markdown.
  </aside>
</section>
```

Notes are visible only in the speaker view (press `S`). They support full HTML markup.

## Fragments

### Basic Fragments

```html
<p class="fragment">Appears on next step</p>
```

### Fragment Styles

| Class | Effect |
|---|---|
| `fragment` | Fade in (default) |
| `fragment grow` | Scale up |
| `fragment shrink` | Scale down |
| `fragment fade-out` | Fade out |
| `fragment fade-up` | Slide up and fade |
| `fragment fade-down` | Slide down and fade |
| `fragment fade-left` | Slide left and fade |
| `fragment fade-right` | Slide right and fade |
| `fragment fade-in-then-out` | Fade in, then fade out on next step |
| `fragment fade-in-then-semi-out` | Fade in, then semi-transparent on next step |
| `fragment strike` | Strikethrough effect |
| `fragment highlight-red` | Highlight in red |
| `fragment highlight-green` | Highlight in green |
| `fragment highlight-blue` | Highlight in blue |
| `fragment highlight-current-red` | Highlight red only while current fragment |
| `fragment highlight-current-green` | Highlight green only while current fragment |
| `fragment highlight-current-blue` | Highlight blue only while current fragment |

### Fragment Ordering

```html
<p class="fragment" data-fragment-index="0">First</p>
<p class="fragment" data-fragment-index="2">Third</p>
<p class="fragment" data-fragment-index="1">Second</p>
```

Use `data-fragment-index` to control the order when fragments are not in DOM order.

### Fragments in `r-stack`

```html
<div class="r-stack">
  <img class="fragment" src="image1.png">
  <img class="fragment" src="image2.png">
  <img class="fragment" src="image3.png">
</div>
```

Stacked fragments replace each other in the same position.

## Code Blocks

### Basic

```html
<pre><code class="hljs javascript">
const x = 1;
</code></pre>
```

### With Trimming

```html
<pre><code class="hljs" data-trim>
  const x = 1;
  const y = 2;
</code></pre>
```

`data-trim` removes common leading whitespace from all lines.

### With Line Numbers and Highlights

```html
<pre><code class="hljs" data-trim data-line-numbers="1,5-10">
// code
</code></pre>
```

Multiple highlight steps (fragments):

```html
<pre><code class="hljs" data-trim data-line-numbers="|4,8-11|17|22-24">
// code
</code></pre>
```

Each pipe-separated group becomes a fragment step.

### HTML in Code

```html
<pre><code class="hljs" data-trim><script type="text/template">
  <div>Hello</div>
</script></code></pre>
```

Use `<script type="text/template">` inside `<code>` to prevent the browser from parsing HTML entities.

### No Escape

```html
<pre><code class="hljs" data-noescape>
<!-- Raw HTML rendered as-is -->
</code></pre>
```

`data-noescape` skips HTML entity escaping (use with caution).

## Media Elements

### Auto-play

```html
<video src="video.mp4" data-autoplay></video>
<audio src="audio.mp3" data-autoplay></audio>
<iframe src="https://example.com" data-autoplay></iframe>
```

Media with `data-autoplay` starts playing when the slide becomes visible and stops when navigating away.

### Controls

```html
<video src="video.mp4" controls></video>
<audio src="audio.mp3" controls></audio>
```

Standard HTML `controls` attribute shows native playback controls.

### Lazy Loading Iframes

```html
<iframe data-src="https://example.com"></iframe>
```

Use `data-src` instead of `src` for lazy loading. The iframe loads when the slide becomes visible.

Add `data-preload` to load within `viewDistance` instead of waiting for visibility.

## Links

### Internal Navigation

```html
<a href="#/2/3">Go to slide 2.3</a>
<a href="#/fragments">Go to slide with id "fragments"</a>
```

Fragmented links: `#/2/3/1` goes to slide 2.3, fragment 1.

### Navigate Down Arrow

```html
<a href="#/2/1" class="navigate-down">
  <img src="arrow.png" class="r-frame">
</a>
```

`class="navigate-down"` adds a bouncing arrow animation hint.

## Slide Content Attributes

### Preload

```html
<section data-preload>
```

Preload this slide's content (iframes, media) even when outside the view distance.

### Background Interactive

```html
<section data-background-iframe="..." data-background-interactive>
```

Enables pointer events on iframe backgrounds.
