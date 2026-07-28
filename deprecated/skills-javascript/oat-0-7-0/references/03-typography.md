---
title: Typography
---

# Typography

All typographic elements are styled automatically without classes.

## Headings

Six levels (`h1`–`h6`) with responsive fluid sizing via `clamp()`:

```html
<h1>Heading 1</h1>  <!-- clamp(1.75rem, 1.5rem + 1.1vw, 2.25rem) -->
<h2>Heading 2</h2>  <!-- clamp(1.5rem, 1.3rem + 0.8vw, 1.875rem) -->
<h3>Heading 3</h3>  <!-- clamp(1.25rem, 1.1rem + 0.5vw, 1.5rem) -->
<h4>Heading 4</h4>  <!-- clamp(1.125rem, 1.05rem + 0.3vw, 1.25rem) -->
<h5>Heading 5</h5>  <!-- 1.125rem -->
<h6>Heading 6</h6>  <!-- 1rem -->
```

All headings use `font-weight: var(--font-semibold)` (600) and `line-height: 1.25`. First child headings have zero top margin.

## Paragraphs

```html
<p>Paragraphs have bottom margin and overflow-wrap: break-word.</p>
```

Last-child paragraphs have zero bottom margin.

## Links

```html
<a href="#">Styled links use --primary color with underline and hover effect.</a>
```

Links use `text-underline-offset: 2px` and transition color on hover.

## Inline Code and Code Blocks

```html
<code>Inline code</code>
<pre><code>Code blocks with monospace font</code></pre>
```

Inline code: smaller font, `--faint` background, small border radius.
Code blocks: padded, `--faint` background, horizontal scroll overflow.

## Blockquote

```html
<blockquote>Cited text with left border and muted color.</blockquote>
```

Left border using `--border`, italic, `--muted-foreground` color.

## Horizontal Rule

```html
<hr>
```

Top border using `--border`, generous vertical margin.

## Lists

```html
<ul>
  <li>Unordered list with disc markers</li>
  <li>Padded and spaced</li>
</ul>

<ol>
  <li>Ordered list with decimal markers</li>
  <li>Padded and spaced</li>
</ol>
```

## Text Formatting

```html
<strong>Bold text</strong>       <!-- font-weight: 600 -->
<b>Bold text</b>                 <!-- font-weight: 600 -->
<em>Italic text</em>             <!-- font-style: italic -->
<i>Italic text</i>               <!-- font-style: italic -->
<small>Smaller text</small>      <!-- font-size: 0.875rem -->
<mark>Highlighted text</mark>    <!-- warning-colored background -->
```

## Hidden Content

```html
<div hidden>This is hidden</div>
<!-- or -->
<div style="display: none;">Also hidden</div>
```

## Focus Visible

```html
<!-- Any focusable element gets a visible focus ring -->
<button>Focusable</button>
```

Focus ring: `2px solid var(--ring)` with `2px` offset.

## Disabled States

```html
<button disabled>Disabled</button>
<!-- or -->
<button aria-disabled>Visually disabled</button>
```

Disabled elements: `cursor: not-allowed`, `opacity: 0.5`.

## Media Elements

```html
<img src="photo.jpg" alt="Description">
<picture>...</picture>
<video src="video.mp4" controls></video>
<canvas></canvas>
<svg></svg>
```

All media elements: `max-width: 100%`.

## Body and Main

```html
<body>
  <!-- font-family: var(--font-sans), font-size: var(--text-regular), line-height: 1.5 -->
  <!-- background: var(--background), color: var(--foreground) -->
  <!-- -webkit-font-smoothing: antialiased -->

  <main>
    <!-- padding-block-start: var(--space-8) -->
  </main>
</body>
```

## HTML Element

```html
<html>
  <!-- tab-size: 4 -->
</html>
```

## Global Reset

- `box-sizing: border-box` on all elements and pseudo-elements
- `margin: 0` on all elements
- `-webkit-tap-highlight-color: transparent` on all elements
- `overflow-wrap: break-word` on headings and paragraphs
