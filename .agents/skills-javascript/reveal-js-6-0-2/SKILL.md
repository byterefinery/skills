---
name: reveal-js-6-0-2
description: >
  Creates and configures reveal.js 6.0.2 HTML presentations. Use when building
  slide decks with nested vertical slides, auto-animate transitions, Markdown
  slides, syntax-highlighted code, LaTeX math, speaker notes, PDF export,
  scroll view, or React-based decks. Covers npm and CDN installation, ES module
  and script-tag initialization, configuration options with defaults, slide
  markup (backgrounds, fragments, transitions, state, visibility), layout
  helpers, built-in plugins (highlight, markdown, math, notes, search, zoom),
  the JavaScript API and events, keyboard shortcuts, lightbox previews,
  themes, and the @revealjs/react wrapper.
license: MIT
metadata:
  tags:
    - javascript
    - presentations
    - slides
    - html
---

# reveal-js 6.0.2

## Overview

reveal.js is an open-source HTML presentation framework for creating interactive slide decks that run in any browser. A presentation is a plain HTML file containing a `<div class="reveal"><div class="slides">` container of `<section>` slides, started with a `Reveal.initialize({ … })` call.

Core features (from the 6.0.2 source, demo deck, and examples):

- Nested vertical slides (sections inside sections)
- Fragments (step-by-step element reveals)
- Auto-Animate (matching elements animate between consecutive slides)
- Markdown authoring (inline or external file)
- Syntax-highlighted code (highlight.js plugin)
- LaTeX math via KaTeX or MathJax 2/3/4 (math plugin)
- Speaker notes with a separate speaker view (notes plugin)
- Zoom-to-element and in-deck search (zoom, search plugins)
- Per-slide backgrounds (color, image, gradient, video, iframe)
- Transitions (none, fade, slide, convex, concave, zoom)
- PDF export (print view) and a scrollable single-page scroll view
- React wrapper package `@revealjs/react` (shipped in the repo under `react/`)

## Usage

### Installation

```bash
npm install reveal.js
```

Published files: `dist/` (built core, plugins, themes), `css/`, `js/`, `index.html`, `demo.html`. Entry points: ESM `dist/reveal.mjs`, UMD `dist/reveal.js`, styles `reveal.js/reveal.css` + `reveal.js/reset.css`, themes `reveal.js/theme/<name>.css`.

### Minimal presentation

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>My Presentation</title>
  <link rel="stylesheet" href="reveal.css" />
  <link rel="stylesheet" href="theme/black.css" />
</head>
<body>
  <div class="reveal">
    <div class="slides">
      <section>First slide</section>
      <section>Second slide</section>
    </div>
  </div>
  <script src="reveal.js"></script>
  <script>Reveal.initialize({ hash: true });</script>
</body>
</html>
```

Serve over HTTP (any static server). `file://` breaks runtime fetching of external Markdown files.

### With plugins (script tags)

```html
<script src="dist/reveal.js"></script>
<script src="dist/plugin/zoom.js"></script>
<script src="dist/plugin/notes.js"></script>
<script src="dist/plugin/search.js"></script>
<script src="dist/plugin/markdown.js"></script>
<script src="dist/plugin/highlight.js"></script>
<script>
  Reveal.initialize({
    hash: true,
    plugins: [RevealZoom, RevealNotes, RevealSearch, RevealMarkdown, RevealHighlight],
  });
</script>
```

Each plugin script exposes a global (e.g. `RevealHighlight`); the math plugin exposes `RevealMath` with `KaTeX`, `MathJax2`, `MathJax3`, `MathJax4` factory functions.

### With plugins (ES modules)

```js
import Reveal from 'reveal.js';
import RevealZoom from 'reveal.js/plugin/zoom';
import RevealNotes from 'reveal.js/plugin/notes';
import RevealMarkdown from 'reveal.js/plugin/markdown';
import RevealHighlight from 'reveal.js/plugin/highlight';
import RevealMath from 'reveal.js/plugin/math';

Reveal.initialize({
  plugins: [RevealZoom, RevealNotes, RevealMarkdown, RevealHighlight, RevealMath.KaTeX],
});
```

### Vertical (nested) slides

Nest `<section>` elements inside a parent `<section>` to make a vertical stack:

```html
<section>
  <section>Vertical slide 1</section>
  <section>Vertical slide 2</section>
</section>
```

Link to any slide with `#/horizontal/vertical` (e.g. `<a href="#/2/1">`) when `hash: true`.

### Fragments

Add `class="fragment"` to any element to reveal it one step at a time. Animation classes: `fade-out`, `fade-up`, `fade-down`, `fade-left`, `fade-right`, `fade-in-then-out`, `fade-in-then-semi-out`, `grow`, `shrink`, `strike`, `highlight-red`, `highlight-blue`, `highlight-green`, `highlight-current-red`, `highlight-current-blue`, `highlight-current-green` (any string is accepted).

### Auto-Animate

Put `data-auto-animate` on consecutive slides; elements matching by `data-id` (or by position) animate between them. Per-slide: `data-auto-animate-easing`, `data-auto-animate-unmatched`, `data-auto-animate-id`; per-element `data-auto-animate-delay`; `data-auto-animate-restart` on the later slide of a pair re-animates from scratch. Details in references/03-auto-animate.md.

### Code with line highlighting

```html
<pre data-id="code"><code class="hljs javascript" data-trim data-line-numbers="|4,8-11|17|22-24">
  // code here
</code></pre>
```

`|` separates highlight steps (each becomes a fragment), commas list lines, dashes mark ranges. `data-trim` strips common leading whitespace. The highlight plugin is required for `hljs` classes and line-number steps.

### Slide backgrounds

`data-background` (color or image), `data-background-gradient`, `data-background-size`, `data-background-repeat`, `data-background-position`, `data-background-video` (comma-separated sources), `data-background-video-muted`, `data-background-iframe` + `data-background-interactive`, `data-background-transition`, plus per-slide `data-transition`. A background on a parent section applies to its whole vertical stack. Full table in references/02-slide-markup.md.

### Markdown slides

```html
<!-- inline -->
<section data-markdown>
  <script type="text/template">
    ## Slide 1
    ---
    ## Slide 2
  </script>
</section>

<!-- external file -->
<section data-markdown="slides.md" data-separator="^\n\n\n" data-separator-vertical="^\n\n"></section>
```

Attribute comments work inside Markdown: `<!-- .slide: data-background="#000" -->` and `- item <!-- .element: class="fragment" -->`. Details in references/02-slide-markup.md.

### Keyboard shortcuts (default mode)

| Keys | Action |
|---|---|
| `N`, `SPACE` | Next slide |
| `P`, `SHIFT SPACE` | Previous slide |
| `←`/`H`, `→`/`L`, `↑`/`K`, `↓`/`J` | Navigate left / right / up / down |
| `ALT` + arrows | Navigate, skipping fragments |
| `SHIFT` + arrows | Jump to first/last slide (top/bottom of a stack) |
| `HOME`, `END` | First / last horizontal slide |
| `B`, `.&nbsp;.` | Pause (blackout) |
| `A` | Toggle auto-sliding |
| `F` | Fullscreen |
| `G` | Jump-to-slide input |
| `ESC`, `O` | Slide overview |
| `?`, `F1` | Help overlay |
| `S` | Speaker view (requires notes plugin) |

With `navigationMode: 'linear'` the arrows/Space/N/L/J all advance and P/H/K step back. Press `?` in a running deck for the built-in list.

## Gotchas

- **Serve over HTTP, not `file://`** — external Markdown is fetched at runtime and will not load from a file URL.
- **Script-tag load order matters** — load `reveal.js` before the plugin scripts; each plugin file defines the global referenced in `plugins: [...]`.
- **Code highlighting needs the highlight plugin** — `hljs` classes and `data-line-numbers` steps come from the plugin, not core; include its `monokai.css` stylesheet for colors.
- **Auto-Animate matching** — elements animate when they share a `data-id` (or match by position) and both slides carry `data-auto-animate`. Use `data-auto-animate-id` to separate independent sequences and `data-auto-animate-restart` to re-animate a pair.
- **`<script type="text/template">` inside `data-markdown` sections** — prevents the browser from parsing HTML inside Markdown code samples (e.g. JSX); the plugin reads the raw text.
- **`data-trim` on `<code>`** — without it, source indentation shows up in the rendered code.
- **The React wrapper is the separate package `@revealjs/react`** (not `@reveal.js/react`); its `plugins` prop is captured once at first mount, so register plugins on the initial `Deck` render.
- **PDF export** — open the deck with `?print-pdf` (legacy query, still supported) or set `view: 'print'`, then use the browser print / save-as-PDF dialog. `pdfSeparateFragments` and `pdfMaxPagesPerSlide` control page layout.
- **Scroll view is a mode, not a separate build** — `view: 'scroll'` renders a tall scrollable page; it also activates automatically below `scrollActivationWidth` (default 435px).
- **Multiple decks on one page** — use `new Reveal(element, { embedded: true, keyboardCondition: 'focused' })` per deck. Keyboard shortcuts are ignored while typing in inputs/textareas regardless.
- **Themes are plain CSS links** — swap the `<link>` href to change themes at runtime; no re-initialization needed.

## References

- [01-configuration](references/01-configuration.md) — Every config option with its default
- [02-slide-markup](references/02-slide-markup.md) — Slide attributes, backgrounds, fragments, transitions, state, media, speaker notes
- [03-auto-animate](references/03-auto-animate.md) — Auto-Animate matching and per-element controls
- [04-plugins](references/04-plugins.md) — Built-in plugins, plugin interface, dependency loading
- [05-layout-helpers](references/05-layout-helpers.md) — r-fit-text, r-stretch, r-stack, r-hstack, r-vstack, r-frame
- [06-api](references/06-api.md) — JavaScript API methods and events
- [07-react](references/07-react.md) — @revealjs/react components and hooks
- [08-pdf-scroll](references/08-pdf-scroll.md) — PDF export and scroll view
- [09-themes](references/09-themes.md) — Built-in themes and custom theme creation
- [10-lightbox](references/10-lightbox.md) — Lightbox preview overlays
