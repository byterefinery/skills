---
name: reveal-js-6-0-1
description: >
  Creates and configures reveal.js 6.0.1 HTML presentations. Use when building slide decks with
  nested vertical slides, auto-animate transitions, Markdown sources, code highlighting
  (highlight.js), LaTeX math (KaTeX/MathJax), speaker notes, PDF export, scroll view, or
  React-based presentations. Covers installation via npm or CDN, all configuration options,
  slide attributes (backgrounds, fragments, transitions, visibility), layout helpers
  (r-fit-text, r-stretch, r-stack, r-hstack, r-vstack), built-in plugins
  (highlight, markdown, math, notes, search, zoom), the JavaScript API, React wrapper
  components (Deck, Slide, Stack, Fragment, Code, Markdown), lightbox previews, themes,
  and PDF/scroll-view export modes.
metadata:
  tags:
    - javascript
    - presentations
    - slides
    - html
---

# reveal-js 6.0.1

## Overview

reveal.js is an open-source HTML presentation framework. It produces interactive slide decks that run in any browser. Core features include nested vertical slides, auto-animate transitions between slides, Markdown authoring, syntax-highlighted code, LaTeX math, speaker notes with a separate viewer, PDF export, a scrollable single-page view, and a React wrapper library.

Install as an npm package (`npm install reveal.js`) or load from a CDN. Presentations are ordinary HTML files with a `<div class="reveal"><div class="slides">…</div></div>` structure and a `Reveal.initialize({ … })` call.

## Usage

### Installation

```bash
npm install reveal.js
```

### Minimal Presentation

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>My Presentation</title>
  <link rel="stylesheet" href="node_modules/reveal.js/dist/reveal.css" />
  <link rel="stylesheet" href="node_modules/reveal.js/dist/theme/black.css" />
</head>
<body>
  <div class="reveal">
    <div class="slides">
      <section>First slide</section>
      <section>Second slide</section>
    </div>
  </div>
  <script src="node_modules/reveal.js/dist/reveal.js"></script>
  <script>Reveal.initialize({ hash: true });</script>
</body>
</html>
```

Serve with any static server (e.g., `npx vite`, `npx serve .`, `python -m http.server`).

### With Plugins (ES modules)

```js
import Reveal from 'reveal.js';
import RevealHighlight from 'reveal.js/plugin/highlight';
import RevealMarkdown from 'reveal.js/plugin/markdown';
import RevealNotes     from 'reveal.js/plugin/notes';
import RevealMath      from 'reveal.js/plugin/math';

Reveal.initialize({
  plugins: [RevealHighlight, RevealMarkdown, RevealNotes, RevealMath.KaTeX],
});
```

### With Plugins (script tags)

```html
<script src="dist/reveal.js"></script>
<script src="dist/plugin/highlight.js"></script>
<script src="dist/plugin/markdown.js"></script>
<script src="dist/plugin/notes.js"></script>
<script src="dist/plugin/math.js"></script>
<script>
  Reveal.initialize({
    plugins: [RevealHighlight, RevealMarkdown, RevealNotes, RevealMath.KaTeX],
  });
</script>
```

### Vertical (Nested) Slides

Nest `<section>` elements inside a parent `<section>` to create a vertical stack:

```html
<section>
  <section>Vertical slide 1</section>
  <section>Vertical slide 2</section>
</section>
```

Space/Enter navigates through all slides (horizontal and vertical). Up/Down arrows navigate within a vertical stack.

### Fragments

Add `class="fragment"` to any element to reveal it step by step:

```html
<section>
  <h2>Step by step</h2>
  <p class="fragment">First</p>
  <p class="fragment">Second</p>
  <p class="fragment grow">Third (grows)</p>
</section>
```

Fragment styles: `fade-out`, `grow`, `shrink`, `fade-out`, `fade-up`, `fade-down`, `fade-left`, `fade-right`, `fade-in-then-out`, `fade-in-then-semi-out`, `highlight-red`, `highlight-blue`, `highlight-green`.

### Auto-Animate

Add `data-auto-animate` to consecutive slides. Elements with matching `data-id` are animated between slides:

```html
<section data-auto-animate>
  <h2 data-id="title">Hello</h2>
  <div data-id="box" style="background:cyan;width:50px;height:50px"></div>
</section>
<section data-auto-animate>
  <h2 data-id="title" style="color:red">Hello</h2>
  <div data-id="box" style="background:magenta;width:150px;height:100px"></div>
</section>
```

Per-slide controls: `data-auto-animate-easing`, `data-auto-animate-duration`, `data-auto-animate-unmatched`, `data-auto-animate-id` (to group separate animation sequences), `data-auto-animate-restart`.

### Code with Line Highlights

```html
<pre data-id="code"><code class="hljs javascript" data-trim data-line-numbers="|4,8-11|17">
// code here
</code></pre>
```

Pipe (`|`) separates highlight steps (each becomes a fragment). Comma separates lines, dash for ranges.

### Slide Backgrounds

| Attribute | Example |
|---|---|
| `data-background` | `data-background="#283b95"` or `data-background="image.png"` |
| `data-background-gradient` | `data-background-gradient="linear-gradient(to bottom, #283b95, #17b2c3)"` |
| `data-background-size` | `data-background-size="cover"` or `100px` |
| `data-background-repeat` | `data-background-repeat="repeat"` |
| `data-background-position` | `data-background-position="center"` |
| `data-background-video` | `data-background-video="video.mp4,video.webm"` |
| `data-background-iframe` | `data-background-iframe="https://example.com"` |
| `data-background-transition` | `data-background-transition="zoom"` |
| `data-background-interactive` | enables mouse interaction with iframe backgrounds |

### Markdown Slides

Inline:

```html
<section data-markdown>
  <script type="text/template">
    ## Title
    Content here
    ---
    ## Next slide
  </script>
</section>
```

External file:

```html
<section data-markdown="slides.md"
         data-separator="^\n\n\n"
         data-separator-vertical="^\n\n">
</section>
```

Slide attributes in Markdown: `<!-- .slide: data-background="#000" -->`
Element attributes: `- Item <!-- .element: class="fragment" -->`

### Transitions

Per-slide: `data-transition="none|fade|slide|convex|concave|zoom"`
Separate in/out: `data-transition="zoom-in fade-out"`

### Lightbox Previews

- `data-preview-image` on `<img>` or `<a>` — opens image overlay
- `data-preview-video` on `<img>`, `<video>`, or `<a>` — opens video overlay
- `data-preview-link` on `<a>` or `<img>` — opens URL in iframe overlay
- `data-preview-fit="contain|cover"` — controls image fit in overlay

### Media

Add `data-autoplay` to `<video>`, `<audio>`, or `<iframe>` for auto-play on slide visibility. Use `data-background-video-muted` to mute background videos.

### Hidden Slides

`<section data-visibility="hidden">` — excluded from navigation but visible in source. Show with `showHiddenSlides: true` config.

### Slide State

`<section data-state="customevent">` adds `customevent` as a class on `<div class="reveal">` when the slide is active. Listen via `Reveal.on('customevent', callback)`.

## Gotchas

- **Always serve from a HTTP server** — loading the HTML file directly (`file://`) breaks external Markdown fetching, some plugin behaviors, and CORS-dependent features. Use `npx vite`, `npx serve .`, or any static server.
- **Plugin order matters** — register plugins in the `plugins` array; do not rely on global variable order. When using script tags, load `reveal.js` first, then plugins, then call `initialize`.
- **`data-line-numbers` requires the highlight plugin** — line highlighting and step fragments are provided by the highlight plugin, not core reveal.js. Without the plugin, `data-line-numbers` is ignored.
- **Auto-animate requires matching `data-id`** — elements are animated by matching `data-id` across consecutive slides. Without `data-id`, no animation occurs. Both slides need `data-auto-animate`.
- **`data-auto-animate-id` isolates sequences** — when you have multiple independent auto-animate groups, use different `data-auto-animate-id` values so reveal.js doesn't try to animate between unrelated slides.
- **Markdown code blocks with line numbers** — use the syntax ````[lang line-nums]` or ````[offset: line-nums]` inside Markdown slides. Example: ````javascript [3,5-7]`.
- **PDF export uses print CSS** — open with `?print-pdf` query param or set `view: 'print'` in config. The browser's print dialog then produces the PDF. Install Chrome's "Save as PDF" for best results.
- **Scroll view is a separate mode** — set `view: 'scroll'` for a single-page scrollable presentation. It works with fragments and auto-animate but disables the overview and some keyboard shortcuts.
- **React wrapper is a separate package** — `@reveal.js/react` is bundled inside the main repo under `react/`. Import from `@reveal.js/react` or build the React wrapper from source. Components are `Deck`, `Slide`, `Stack`, `Fragment`, `Code`, `Markdown`, plus `useReveal()` hook.
- **`<script type="text/template">` inside `<code>`** — use this pattern to prevent the browser from parsing HTML entities in code blocks. reveal.js extracts the raw content automatically.
- **`data-trim` on `<code>`** — trims common leading whitespace from all lines. Without it, indentation in HTML source shows up in the rendered code.
- **Themes are CSS-only** — swap themes by changing the `<link id="theme">` href. No JS reinitialization needed.
- **Multiple presentations on one page** — use `new Reveal(element, options)` with `embedded: true` and `keyboardCondition: 'focused'` per deck.

## References

- [01-configuration](references/01-configuration.md) — All configuration options with defaults
- [02-slide-markup](references/02-slide-markup.md) — Slide attributes, backgrounds, fragments, transitions, visibility
- [03-auto-animate](references/03-auto-animate.md) — Auto-animate transitions in detail
- [04-plugins](references/04-plugins.md) — Built-in plugins: highlight, markdown, math, notes, search, zoom
- [05-layout-helpers](references/05-layout-helpers.md) — r-fit-text, r-stretch, r-stack, r-hstack, r-vstack
- [06-api](references/06-api.md) — JavaScript API methods and events
- [07-react](references/07-react.md) — React wrapper components and hooks
- [08-pdf-scroll](references/08-pdf-scroll.md) — PDF export and scroll view
- [09-themes](references/09-themes.md) — Built-in themes and custom theme creation
- [10-lightbox](references/10-lightbox.md) — Lightbox preview overlays
