# Slide markup

Markup patterns from the reveal.js 6.0.2 demo deck (`demo.html`) and `examples/`.

## Deck structure

- Container: `<div class="reveal"><div class="slides"> ... </div></div>`
- Every `<section>` inside the container is a slide
- `<section>` nested inside a `<section>` = vertical stack (stepped with up/down arrows)
- Deep links: `<a href="#/2/1">` targets horizontal/vertical indices; slides with an `id` can be linked via `#/id`
- `data-visibility="hidden"` — slide exists in source but is hidden from the presentation; `showHiddenSlides: true` shows them

## Slide attributes

| Attribute | Example | Purpose |
|---|---|---|
| `data-background` | `data-background="#dddddd"` or `data-background="image.png"` | Background color or image (all CSS color formats work) |
| `data-background-color` | `data-background-color="#000000"` | Background color (alternative attribute) |
| `data-background-gradient` | `data-background-gradient="linear-gradient(to bottom, #283b95, #17b2c3)"` | CSS gradient background |
| `data-background-size` | `data-background-size="cover"` or `"100px"` | CSS background-size |
| `data-background-repeat` | `data-background-repeat="repeat"` | CSS background-repeat (tiled images) |
| `data-background-position` | `data-background-position="center"` | CSS background-position |
| `data-background-video` | `data-background-video="video.mp4,video.webm"` | Comma-separated video sources as background |
| `data-background-video-muted` | boolean attribute | Mute a background video |
| `data-background-iframe` | `data-background-iframe="https://example.com/embed"` | Iframe as full-slide background |
| `data-background-interactive` | boolean attribute | Allow mouse interaction with an iframe background |
| `data-background-transition` | `data-background-transition="zoom"` | Per-slide background transition style |
| `data-transition` | `data-transition="fade"` | Per-slide content transition (none/fade/slide/convex/concave/zoom) |
| `data-state` | `data-state="customevent"` | Adds the state name as a class to the document element while the slide is active, and fires a custom event of the same name |
| `data-autoslide` | `data-autoslide="4000"` | Auto-advance interval for this slide (milliseconds) |
| `data-id` | `data-id="code"` | Auto-Animate element identity |

A background set on a parent `<section>` applies to the entire vertical stack; slides inside the stack can override with their own `data-background`.

## Fragments

- `class="fragment"` on any element reveals it one navigation step at a time
- Animation classes (the `FragmentAnimation` type): fade-out, fade-up, fade-down, fade-left, fade-right, fade-in-then-out, fade-in-then-semi-out, grow, shrink, strike, highlight-red, highlight-blue, highlight-green, highlight-current-red, highlight-current-blue, highlight-current-green
- Fragments are also stepped through in the speaker notes window

## Speaker notes

Two ways to attach notes to a slide (both are read by `getSlideNotes()`):

1. `data-notes="Short note"` attribute on the `<section>`
2. `<aside class="notes"> Longer notes </aside>` inside the slide

Notes show in the speaker view (S key, notes plugin). `showNotes: true` renders them to all viewers.

## Code blocks

- `<pre><code class="hljs javascript">...</code></pre>` — the highlight.js plugin does the highlighting
- `data-trim` strips common leading whitespace from all lines
- `data-line-numbers` — pipe separates steps (each step is a fragment), comma lists lines, dash marks ranges: `data-line-numbers="|4,8-11|17|22-24"`
- In Markdown, append the same spec to the code fence language tag, e.g. a javascript fence with `[1|3-5]` or with an offset like `[287: 2|4,6]`
- To embed raw HTML-like code (JSX, HTML samples), wrap the code in `<script type="text/template">...` so the browser does not parse it; the plugin extracts the raw text

## Media in slides

- `data-autoplay` on `<video>`, `<audio>`, `<iframe>` — plays when the slide becomes visible (global override: `autoPlayMedia` config)
- `data-src` on iframes for lazy loading — loaded when the slide enters the view distance (see `preloadIframes`)
- Audio/video can live inside fragments and play when the fragment is revealed

## Slide state and events

A slide with `data-state="customevent"` adds the class `customevent` to the document element while active, and you can listen to it:

```js
Reveal.on('customevent', () => {
  console.log('"customevent" has fired');
});
```

## Transitions

- Global: `transition` config (default `'slide'`), `transitionSpeed`, `backgroundTransition`
- Per-slide: `data-transition`, `data-background-transition`
- Per-load: query params, e.g. `?transition=zoom`
