# Configuration Options

All options passed to `Reveal.initialize({ … })` or `Reveal.configure({ … })`. Options can also be set via URL query params (e.g., `?transition=fade&autoSlide=5000`).

## Presentation Size

| Option | Default | Description |
|---|---|---|
| `width` | `960` | Slide width in px or CSS string (e.g., `"80%"`) |
| `height` | `700` | Slide height in px or CSS string |
| `margin` | `0.04` | Empty space ratio around content (0–1) |
| `minScale` | `0.2` | Minimum scale factor |
| `maxScale` | `2.0` | Maximum scale factor |
| `disableLayout` | `false` | Disable auto-scaling; use custom CSS layout |

## Navigation

| Option | Default | Description |
|---|---|---|
| `controls` | `true` | Show navigation arrows. Also `"speaker"` for speaker view only |
| `controlsTutorial` | `true` | Show control hints on first use |
| `controlsLayout` | `"bottom-right"` | Arrow placement: `"edges"` or `"bottom-right"` |
| `controlsBackArrows` | `"faded"` | Back arrow visibility: `"faded"`, `"hidden"`, `"visible"` |
| `progress` | `true` | Show progress bar |
| `navigationMode` | `"default"` | `"default"`, `"linear"`, or `"grid"` |
| `loop` | `false` | Loop presentation |
| `shuffle` | `false` | Randomize slide order on load |
| `rtl` | `false` | Right-to-left presentation direction |
| `touch` | `true` | Enable touch/swipe navigation |
| `mouseWheel` | `false` | Navigate with mouse wheel |
| `keyboard` | `true` | Enable keyboard navigation |
| `keyboardCondition` | `null` | `"focused"` for embedded decks; or a function |
| `overview` | `true` | Enable slide overview (ESC) |
| `jumpToSlide` | `true` | Enable jump-to-slide shortcut |

## Appearance

| Option | Default | Description |
|---|---|---|
| `center` | `true` | Vertically center slide content |
| `transition` | `"slide"` | `"none"`, `"fade"`, `"slide"`, `"convex"`, `"concave"`, `"zoom"` |
| `transitionSpeed` | `"default"` | `"default"`, `"fast"`, `"slow"` |
| `backgroundTransition` | `"fade"` | Background transition style (same values as `transition`) |
| `hideInactiveCursor` | `true` | Hide cursor when inactive |
| `hideCursorTime` | `5000` | ms before cursor hides |

## Hash and History

| Option | Default | Description |
|---|---|---|
| `hash` | `false` | Add slide index to URL hash |
| `hashOneBasedIndex` | `false` | Use 1-based indexing in hash |
| `history` | `false` | Push to browser history (implies `hash: true`) |
| `respondToHashChanges` | `true` | Navigate on hash change |

## Slide Number

| Option | Default | Description |
|---|---|---|
| `slideNumber` | `false` | Show slide number. Also `"h.v"`, `"h/v"`, `"c"`, `"c/t"`, or a function |
| `showSlideNumber` | `"all"` | `"all"`, `"print"`, `"speaker"` |

## Fragments

| Option | Default | Description |
|---|---|---|
| `fragments` | `true` | Enable fragments globally |
| `fragmentInURL` | `true` | Include fragment index in URL |
| `sortFragmentsOnSync` | `true` | Auto-sort fragment indices on `sync()` |

## Auto-Animate

| Option | Default | Description |
|---|---|---|
| `autoAnimate` | `true` | Enable auto-animate globally |
| `autoAnimateMatcher` | `null` | Custom element matcher function |
| `autoAnimateEasing` | `"ease"` | CSS easing string |
| `autoAnimateDuration` | `1.0` | Duration in seconds |
| `autoAnimateUnmatched` | `true` | Fade unmatched elements |
| `autoAnimateStyles` | see below | CSS properties to animate |

Default animated styles: `opacity`, `color`, `background-color`, `padding`, `font-size`, `line-height`, `letter-spacing`, `border-width`, `border-color`, `border-radius`, `outline`, `outline-offset`.

## Auto-Slide

| Option | Default | Description |
|---|---|---|
| `autoSlide` | `0` | ms between slides (0 = only with `data-autoslide` attribute) |
| `autoSlideStoppable` | `true` | Stop auto-slide on user input |
| `autoSlideMethod` | `null` | Custom navigation function for auto-slide |
| `defaultTiming` | `null` | Average seconds per slide (pacing timer in speaker view) |

## Embedded Media

| Option | Default | Description |
|---|---|---|
| `autoPlayMedia` | `null` | `true` = all autoplay, `false` = none, `null` = respect `data-autoplay` |
| `preloadIframes` | `null` | `true` = preload in viewDistance, `false` = only when visible, `null` = respect `data-preload` |
| `preventIframeAutoFocus` | `false` | Stop iframes from stealing focus |

## Embedded Mode

| Option | Default | Description |
|---|---|---|
| `embedded` | `false` | Presentation in a portion of the screen |
| `postMessage` | `true` | Expose API via `window.postMessage` |
| `postMessageEvents` | `false` | Post all events to parent window |

## Help and Pause

| Option | Default | Description |
|---|---|---|
| `help` | `true` | Show help overlay on `?` key |
| `pause` | `true` | Allow pausing (B or `.` key) |

## Speaker Notes

| Option | Default | Description |
|---|---|---|
| `showNotes` | `false` | Show speaker notes to all viewers |
| `showHiddenSlides` | `false` | Keep `data-visibility="hidden"` slides visible |

## View Distance

| Option | Default | Description |
|---|---|---|
| `viewDistance` | `3` | Slides preloaded ahead/behind |
| `mobileViewDistance` | `2` | View distance on mobile |

## Display

| Option | Default | Description |
|---|---|---|
| `display` | `"block"` | CSS display mode for slides |

## Parallax Background

| Option | Default | Description |
|---|---|---|
| `parallaxBackgroundImage` | `""` | CSS background image string |
| `parallaxBackgroundSize` | `""` | CSS background-size string |
| `parallaxBackgroundRepeat` | `""` | CSS background-repeat string |
| `parallaxBackgroundPosition` | `""` | CSS background-position string |
| `parallaxBackgroundHorizontal` | `null` | Pixels to shift horizontally per step |
| `parallaxBackgroundVertical` | `null` | Pixels to shift vertically per step |

## Scroll View

| Option | Default | Description |
|---|---|---|
| `view` | `null` | `"print"` for PDF, `"scroll"` for scroll view |
| `scrollLayout` | `"full"` | `"full"` (viewport-height slides) or `"compact"` |
| `scrollSnap` | `"mandatory"` | `"mandatory"`, `"proximity"`, or `false` |
| `scrollProgress` | `"auto"` | `"auto"`, `true`, or `false` |
| `scrollActivationWidth` | `435` | Auto-activate scroll view below this viewport width |

## PDF Export

| Option | Default | Description |
|---|---|---|
| `pdfMaxPagesPerSlide` | `Infinity` | Max pages a slide can span in PDF |
| `pdfSeparateFragments` | `true` | Each fragment on its own PDF page |
| `pdfPageHeightOffset` | `-1` | Height offset for PDF pages |

## Plugin Config

| Option | Default | Description |
|---|---|---|
| `highlight` | `{}` | Highlight plugin config (`highlightOnLoad`, `escapeHTML`, `beforeHighlight`) |
| `markdown` | `{}` | Markdown plugin config (all `marked` options + `separator`, `verticalSeparator`, `notesSeparator`, `smartypants`, `animateLists`) |
| `katex` | `{}` | KaTeX config (`local`, `version`, `delimiters`, `ignoredTags`) |
| `mathjax2` | `{}` | MathJax 2 config |
| `mathjax3` | `{}` | MathJax 3 config |
| `mathjax4` | `{}` | MathJax 4 config |
| `plugins` | `[]` | Array of plugin instances |
| `dependencies` | `[]` | Legacy dependency array |

## Focus

| Option | Default | Description |
|---|---|---|
| `focusBodyOnPageVisibilityChange` | `true` | Refocus body on page visibility change |

## Preview Links

| Option | Default | Description |
|---|---|---|
| `previewLinks` | `false` | Open external links in iframe preview overlay |
