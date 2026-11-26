# JavaScript API

The `RevealApi` surface from reveal.js 6.0.2 (`js/reveal.d.ts`). Access via the global `Reveal` (UMD), the default export (ESM), or an instance from `new Reveal(element, options)`.

## Lifecycle

- `Reveal.initialize(options?)` — starts the deck; returns a promise resolving on the `ready` event
- `Reveal.configure(options)` — merges config; may be called multiple times
- `Reveal.destroy()` — undoes DOM changes and removes event listeners
- `Reveal.isReady()`
- `Reveal.VERSION` — version string

## Sync (DOM changed after init)

- `sync()` — resync the whole presentation after adding/removing slides or changing structure
- `syncSlide(slide)` — cheaper single-slide refresh (e.g. new `data-background-image`); dispatches `slidesync`
- `syncFragments(slide)` — reindex fragments on a slide
- `layout()` — apply the JavaScript-controlled layout rules
- `removeHiddenSlides()` — strip `data-visibility="hidden"` slides from the DOM (already done automatically at init)

## Navigation

- `slide(horizontal?, vertical?, fragment?, origin?)`
- `left() / right() / up() / down()` — accept `{ skipFragments? }`
- `prev() / next()` — prev prioritizes previous fragment, then previous vertical slide, then previous horizontal slide (next mirrors)
- Aliases: `navigateLeft`, `navigateRight`, `navigateUp`, `navigateDown`, `navigatePrev`, `navigateNext`
- `navigateFragment(index?, offset?)` — -1 hides all fragments; returns whether anything changed
- `prevFragment() / nextFragment()` — booleans
- `availableRoutes({ includeFragments? })` — `{ left, right, up, down }`
- `availableFragments()` — `{ prev, next }`

## State

- `getState()` — `{ indexh, indexv, indexf, paused, overview, ... }`
- `setState(state)`
- `getProgress()` — 0..1 through the deck
- `getIndices(slide?)` — `{ h, v, f }`
- `isFirstSlide()`, `isLastSlide()`, `isLastVerticalSlide()`
- `isVerticalSlide(slide?)`
- `isPaused()`, `isOverview()`, `isAutoSliding()`, `isSpeakerNotes()`, `isPrintingPDF()`, `isFocused()`
- `hasHorizontalSlides()`, `hasVerticalSlides()`, `hasNavigatedHorizontally()`, `hasNavigatedVertically()`

## Slides

- `getSlides()`, `getHorizontalSlides()`, `getVerticalSlides()`
- `getSlide(x, y?)`, `getCurrentSlide()`, `getPreviousSlide()`
- `getSlideBackground(x | slide, y?)`
- `getSlideNotes(slide?)` — from `data-notes` or `<aside class="notes">`
- `getSlidesAttributes()`, `getSlidePastCount(slide?)` (flattened index), `getTotalSlides()`
- `loadSlide(slide, { excludeIframes? })`, `unloadSlide(slide)`
- `shuffle(slides?)`

## Toggles

- `toggleHelp(override?)`, `toggleOverview(override?)`, `togglePause(override?)`, `toggleAutoSlide(override?)`

## Preview / lightbox

- `showPreview(url)` — opens an iframe preview overlay
- `hidePreview()` — closes any open overlay

## Keyboard

- `addKeyBinding(keyCode | { keyCode, key, description }, callbackOrApiMethodName)`
- `removeKeyBinding(keyCode)`
- `triggerKey(keyCode)`
- `registerKeyboardShortcut(key, value)` — adds an entry to the help overlay

## Config, geometry, DOM

- `getConfig()`, `getQueryHash()`, `getSlidePath(slide?)`
- `getComputedSlideSize(presentationWidth?, presentationHeight?)` — `{ width, height, presentationWidth, presentationHeight }`
- `getScale()`
- `getRevealElement()`, `getSlidesElement()`, `getViewportElement()`, `getBackgroundsElement()`

## Events

`Reveal.on(type, listener)` / `Reveal.off(type, listener)` (`addEventListener`/`removeEventListener` are legacy aliases). Events dispatched in 6.0.2:

`ready`, `beforeslidechange`, `slidechanged`, `slidetransitionend`, `slidesync`, `sync`, `fragmentshown`, `fragmenthidden`, `overviewshown`, `overviewhidden`, `paused`, `resumed`, `autoslidepaused`, `autoslideresumed`, `previewimage`, `previewvideo`, `previewiframe`, `closeoverlay`, `showhelp`, `resize`, `visible`, `hidden`, `autoanimate`

Plus custom events named after each slide's `data-state` value (e.g. `Reveal.on('customevent', fn)`).

Payloads: `slidechanged` carries `indexh`/`indexv`/`indexf` (and `origin`); `fragmentshown`/`fragmenthidden` carry `fragment`; `slidesync` carries `slide`.

## Multiple instances

`new Reveal(document.querySelector('.deck'), { embedded: true, progress: false, keyboardCondition: 'focused', plugins: [...] })` per deck container — see `examples/multiple-presentations.html`. Each instance has its own API: `deck1.on('slidechanged', ...)`, `deck2.slide(1)`, etc.
