# JavaScript API Reference

## Initialization

### Global (default)

```js
Reveal.initialize({
  hash: true,
  transition: 'slide',
  plugins: [RevealHighlight, RevealMarkdown],
});
```

Automatically finds `<div class="reveal">` in the DOM.

### Constructor (multiple decks)

```js
const deck = new Reveal(document.querySelector('.my-deck'), {
  embedded: true,
  keyboardCondition: 'focused',
  plugins: [RevealHighlight],
});
deck.initialize();
```

### ES Module Import

```js
import Reveal from 'reveal.js';
import RevealHighlight from 'reveal.js/plugin/highlight';

const deck = new Reveal({ plugins: [RevealHighlight] });
await deck.initialize();
```

## Navigation

```js
Reveal.slide(indexh, indexv, fragmentIndex);  // Go to specific slide
Reveal.slide(2);                               // Horizontal slide 2
Reveal.slide(2, 1);                            // Slide 2.1 (vertical)
Reveal.slide(2, 1, 0);                         // Slide 2.1, fragment 0

Reveal.left();    // Navigate left
Reveal.right();   // Navigate right
Reveal.up();      // Navigate up
Reveal.down();    // Navigate down
Reveal.prev();    // Previous (fragment > vertical > horizontal)
Reveal.next();    // Next (fragment > vertical > horizontal)

// Aliases
Reveal.navigateLeft();
Reveal.navigateRight();
Reveal.navigateUp();
Reveal.navigateDown();
Reveal.navigatePrev();
Reveal.navigateNext();
```

## State Queries

```js
Reveal.getIndexh();          // Current horizontal index
Reveal.getIndexv();          // Current vertical index
Reveal.getIndices();         // { indexh, indexv }
Reveal.getTotalSlides();     // Total slide count
Reveal.getScale();           // Current scale factor

Reveal.isFirstSlide();       // Boolean
Reveal.isLastSlide();        // Boolean
Reveal.isVerticalSlide();    // Boolean (current slide is in a vertical stack)

Reveal.isReady();            // Boolean (initialization complete)
Reveal.isOverview();         // Boolean (overview mode active)
Reveal.isPaused();           // Boolean (presentation paused)
Reveal.isAutoSliding();      // Boolean (auto-slide active)
```

## Slide Access

```js
Reveal.getSlides();                        // All slide elements
Reveal.getHorizontalSlides();              // Top-level slides
Reveal.getSlidePastCount();                // Number of slides already visited
Reveal.getSlideBackground(slide);          // Background element for a slide
Reveal.getSlideAttributes(slide);          // { data: {}, state: '' }
Reveal.getParentSlide(slide);              // Parent of a vertical slide

Reveal.getPreviousSlide();                 // Previously shown slide
Reveal.getCurrentSlide();                  // Currently shown slide

Reveal.getSlideUrl(slide);                 // URL hash for a slide
Reveal.getSlidePath(slide);                // { h, v } indices for a slide
Reveal.getSlide(slide);                    // Get slide by element

Reveal.getQueryHash();                     // Current query params as object
```

## Slide Modification

```js
Reveal.configure({ transition: 'fade' });  // Reconfigure at runtime
Reveal.sync();                              // Sync with DOM changes
Reveal.syncSlide(slide);                    // Sync a single slide
Reveal.syncFragments(slide);                // Re-index fragments on a slide
Reveal.removeHiddenSlides();                // Remove data-visibility="hidden" slides
```

## Overview Mode

```js
Reveal.toggleOverview(true);    // Enter overview
Reveal.toggleOverview(false);   // Exit overview
Reveal.toggleOverview();        // Toggle
```

## Pause

```js
Reveal.pause();                 // Pause (blackout)
Reveal.resume();                // Resume
Reveal.togglePause();           // Toggle
```

## Jump to Slide

```js
Reveal.toggleJumpToSlide(true); // Show jump-to-slide UI
Reveal.toggleJumpToSlide(false);// Hide
```

## Auto-Slide

```js
Reveal.toggleAutoSlide(true);   // Start auto-sliding
Reveal.toggleAutoSlide(false);  // Stop
Reveal.isAutoSliding();         // Check if active
```

## Destroy

```js
Reveal.destroy();               // Uninitialize, clean up DOM and events
```

## Events

### Listening

```js
Reveal.on('slidechanged', (event) => {
  console.log(event.indexh, event.indexv, event.currentSlide);
});
```

### Available Events

| Event | Data | Description |
|---|---|---|
| `beforeslidechange` | `{ indexh, indexv, origin }` | Before slide changes. Call `event.preventDefault()` to cancel |
| `slidechanged` | `{ indexh, indexv, previousSlide, currentSlide, origin }` | After slide changes |
| `slidetransitionend` | `{ indexh, indexv, currentSlide }` | After slide transition animation ends |
| `ready` | `{ indexh, indexv, currentSlide }` | After initialization completes |
| `resize` | `{ oldScale, scale, size }` | When scale changes |
| `paused` | — | Presentation paused |
| `resumed` | — | Presentation resumed |
| `overviewshown` | — | Overview mode entered |
| `overviewhidden` | — | Overview mode exited |
| `fragmentshown` | `{ fragment, fragments }` | Fragment activated |
| `fragmenthidden` | `{ fragment, fragments }` | Fragment deactivated |
| `initialized` | `{ }` | Alias for `ready` |
| `slidevisible` | — | Fired on the slide element when it becomes visible |
| `sync` | — | After `Reveal.sync()` completes |
| `slidesync` | `{ slide }` | After `Reveal.syncSlide(slide)` completes |

### Custom State Events

Slides with `data-state` fire custom events:

```html
<section data-state="edit-mode">
```

```js
Reveal.on('edit-mode', () => {
  console.log('Edit mode active');
});
```

### Removing Listeners

```js
function handler(event) { /* … */ }
Reveal.on('slidechanged', handler);
Reveal.off('slidechanged', handler);
```

## PostMessage API

Control reveal.js from another window:

```js
revealWindow.postMessage(JSON.stringify({
  method: 'slide',
  args: [2, 0]
}), '*');
```

All API methods are available via postMessage. Enable with `postMessage: true` (default).

## Multiple Presentations

```js
let deck1 = new Reveal(document.querySelector('.deck1'), {
  embedded: true,
  keyboardCondition: 'focused',
  plugins: [RevealHighlight],
});
deck1.initialize();

let deck2 = new Reveal(document.querySelector('.deck2'), {
  embedded: true,
  keyboardCondition: 'focused',
  plugins: [RevealMarkdown],
});
deck2.initialize();
```

Each deck is independent. Use `embedded: true` and `keyboardCondition: 'focused'` for proper behavior.

## Version

```js
console.log(Reveal.VERSION); // "6.0.1"
```
