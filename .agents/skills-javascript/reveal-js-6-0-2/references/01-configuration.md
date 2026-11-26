# Configuration

All options accepted by `Reveal.initialize({ ... })` / `Reveal.configure({ ... })` in reveal.js 6.0.2, with defaults (from `js/config.ts`). Upstream docs: https://revealjs.com/config/

## Sizing and layout

| Option | Default | Notes |
|---|---|---|
| `width` | `960` | Normal presentation size (number or CSS string); aspect ratio preserved when scaled |
| `height` | `700` | Normal presentation height |
| `margin` | `0.04` | Fraction of display size left empty around content |
| `minScale` | `0.2` | Smallest factor content may be scaled down to |
| `maxScale` | `2.0` | Largest factor content may be scaled up to |
| `center` | `true` | Vertical centering of slides |
| `disableLayout` | `false` | Disable default scaling/centering so you can use custom CSS layout |
| `display` | `'block'` | Display mode used to show slides |
| `rtl` | `false` | Right-to-left presentation direction |
| `navigationMode` | `'default'` | `'default'` per-axis arrows, space steps all; `'linear'` left/right step through everything; `'grid'` moving right from a stack lands at the same vertical index |
| `loop` | `false` | Loop the presentation |
| `shuffle` | `false` | Randomize slide order on load |
| `touch` | `true` | Touch navigation on touch devices |
| `mouseWheel` | `false` | Navigate via mouse wheel |

## Chrome

| Option | Default | Notes |
|---|---|---|
| `controls` | `true` | `true`/`false`, or `'speaker'` to show control arrows only in the speaker view |
| `controlsTutorial` | `true` | Hint animations (e.g. bouncing arrow on first vertical slide) |
| `controlsLayout` | `'bottom-right'` | `'edges'` or `'bottom-right'` |
| `controlsBackArrows` | `'faded'` | `'faded'` / `'hidden'` / `'visible'` |
| `progress` | `true` | Progress bar |
| `slideNumber` | `false` | `boolean` or format string `'h.v'` / `'h/v'` / `'c'` / `'c/t'`, or a function returning the formatted number |
| `showSlideNumber` | `'all'` | `'all'` / `'print'` / `'speaker'` |
| `hideInactiveCursor` | `true` | Hide cursor when inactive |
| `hideCursorTime` | `5000` | ms before the cursor is hidden |

## URL, hash and history

| Option | Default | Notes |
|---|---|---|
| `hash` | `false` | Put the current slide in the URL hash (enables `#/1/2` deep links) |
| `respondToHashChanges` | `true` | Follow hash changes |
| `hashOneBasedIndex` | `false` | Use 1-based index in # links to match slide numbers |
| `jumpToSlide` | `true` | Enable the jump-to-slide shortcut (`G`) |
| `history` | `false` | Push each slide change to browser history; implies `hash: true` |

## Keyboard

| Option | Default | Notes |
|---|---|---|
| `keyboard` | `true` | `boolean`, or a map `{ [keyCode]: 'apiMethod' | (event) => ... }` for custom bindings |
| `keyboardCondition` | `null` | `null`, `'focused'` (embedded decks only capture keys when focused), or `event => boolean` that blocks events when it returns `false` |

## Fragments

| Option | Default | Notes |
|---|---|---|
| `fragments` | `true` | Turn fragments on/off globally |
| `fragmentInURL` | `true` | Include the current fragment in the URL |
| `sortFragmentsOnSync` | `true` | Automatically sort and index fragments at each `Reveal.sync()` |

## Media

| Option | Default | Notes |
|---|---|---|
| `autoPlayMedia` | `null` | Global override for video/audio/iframe autoplay. `null` only autoplay when `data-autoplay` is present, `true` always, `false` never |
| `preloadIframes` | `null` | `null`: iframes with `data-src` + `data-preload` load within viewDistance, `data-src`-only when visible. `true`: all `data-src` iframes load within viewDistance. `false`: only when visible |
| `preventIframeAutoFocus` | `false` | Stop embedded iframes from stealing focus |
| `previewLinks` | `false` | Open links in an iframe preview overlay; `data-preview-link="false"` opts a link out |

## Auto-Animate

| Option | Default | Notes |
|---|---|---|
| `autoAnimate` | `true` | Globally disable auto-animation |
| `autoAnimateMatcher` | `null` | Custom element matcher deciding which elements animate between slides |
| `autoAnimateEasing` | `'ease'` | Default easing for auto-animate transitions |
| `autoAnimateDuration` | `1.0` | Seconds to animate each element |
| `autoAnimateUnmatched` | `true` | Fade unmatched elements in |
| `autoAnimateStyles` | see below | CSS properties that can be auto-animated. Position and scale are matched separately, so top/left/width/height/margin are not needed. Default list: opacity, color, background-color, padding, font-size, line-height, letter-spacing, border-width, border-color, border-radius, outline, outline-offset |

## Auto-sliding

| Option | Default | Notes |
|---|---|---|
| `autoSlide` | `0` | `0`: auto-slide only slides carrying `data-autoslide`; a positive number: all slides progress automatically at that interval; `false`: never |
| `autoSlideStoppable` | `true` | Stop auto-sliding after user input (enables the `A` toggle) |
| `autoSlideMethod` | `null` | Navigation method used when auto-sliding (defaults to navigateNext) |
| `defaultTiming` | `null` | Expected seconds per slide; drives the pacing timer in the speaker view |

## Transitions and parallax backgrounds

| Option | Default | Notes |
|---|---|---|
| `transition` | `'slide'` | `'none'` / `'fade'` / `'slide'` / `'convex'` / `'concave'` / `'zoom'` |
| `transitionSpeed` | `'default'` | `'default'` / `'fast'` / `'slow'` |
| `backgroundTransition` | `'fade'` | Transition style for full-page slide backgrounds |
| `parallaxBackgroundImage` | `''` | CSS image syntax, e.g. "a.jpg" |
| `parallaxBackgroundSize` | `''` | e.g. "3000px 2000px" |
| `parallaxBackgroundRepeat` | `''` | repeat / repeat-x / repeat-y / no-repeat / initial / inherit |
| `parallaxBackgroundPosition` | `''` | e.g. "top left" |
| `parallaxBackgroundHorizontal` | `null` | Pixels to move the parallax background per slide step |
| `parallaxBackgroundVertical` | `null` | Pixels to move the parallax background per slide step |

## View modes (print / scroll)

| Option | Default | Notes |
|---|---|---|
| `view` | `null` | `'print'`: render for PDF printing; `'scroll'`: tall scrollable page with scroll-triggered animations |
| `scrollLayout` | `'full'` | `'full'` slide is as tall as the viewport; `'compact'` slides are as small as possible (multiple visible on tall screens) |
| `scrollSnap` | `'mandatory'` | `false` continuous, `'proximity'` snap when close, `'mandatory'` always snap |
| `scrollProgress` | `'auto'` | Scrollbar shown while scrolling (`'auto'`), always (`true`), or never (`false`) |
| `scrollActivationWidth` | `435` | Viewport width below which the scroll view activates automatically |
| `pdfMaxPagesPerSlide` | `Infinity` | Max pages a single slide may span when printing |
| `pdfSeparateFragments` | `true` | Print each fragment on a separate page |
| `pdfPageHeightOffset` | `-1` | Height offset to compensate in-browser vs CLI printing differences |

## Misc

| Option | Default | Notes |
|---|---|---|
| `overview` | `true` | Enable slide overview (ESC/O) |
| `embedded` | `false` | Deck runs inside a limited portion of the screen |
| `help` | `true` | Show help overlay on `?` |
| `pause` | `true` | Allow pausing (blackout) |
| `showNotes` | `false` | Show speaker notes to all viewers |
| `showHiddenSlides` | `false` | Keep `data-visibility="hidden"` slides visible |
| `viewDistance` | `3` | Slides away from current that stay loaded/rendered |
| `mobileViewDistance` | `2` | Same for mobile devices |
| `postMessage` | `true` | Expose the reveal.js API through `window.postMessage` |
| `postMessageEvents` | `false` | Dispatch all reveal.js events to the parent window via postMessage |
| `focusBodyOnPageVisibilityChange` | `true` | Refocus body when page visibility changes so shortcuts work |

## Plugin sub-configs

Pass alongside the top-level options:

- `highlight` — `highlightOnLoad`, `escapeHTML`, `beforeHighlight` (see 04-plugins.md)
- `markdown` — marked.js options plus reveal separators: `separator`, `verticalSeparator`, `notesSeparator`, `attributes`; also `async`, `baseUrl`, `breaks`, `gfm`, `headerIds`, `headerPrefix`, `highlight`, `langPrefix`, `mangle`, `pedantic`, `renderer`, `sanitize`, `sanitizer`, `silent`, `smartLists`, `smartypants`, `tokenizer`, `walkTokens`, `xhtml`
- `katex` — `local`, `version`, `delimiters`, `ignoredTags`
- `mathjax2` / `mathjax3` / `mathjax4` — `mathjax` (script URL), `tex`/`tex2jax`, `options` (e.g. `skipHtmlTags`), `startup` (MathJax 4)
- `dependencies` — legacy script loading: array of `{ src, async?, callback?, condition? }`; prefer the `plugins` array for new decks
- `plugins` — array of plugin objects or factory functions
