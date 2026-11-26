# React Wrapper Reference

The `@reveal.js/react` package provides React components that wrap reveal.js. Components are located under `react/` in the main repo.

## Installation

```bash
npm install reveal.js @reveal.js/react
```

## Components

### Deck

Root component. Wraps the entire presentation.

```jsx
import { Deck } from '@reveal.js/react';
import RevealHighlight from 'reveal.js/plugin/highlight';
import RevealMarkdown  from 'reveal.js/plugin/markdown';

function App() {
  return (
    <Deck
      config={{ hash: true, transition: 'slide' }}
      plugins={[RevealHighlight, RevealMarkdown]}
      onReady={(deck) => console.log('Ready', deck)}
      onSlideChange={(event) => console.log('Slide', event.indexh)}
    >
      <Slide>First slide</Slide>
      <Slide>Second slide</Slide>
    </Deck>
  );
}
```

**Props:**
- `config` — RevealConfig object
- `plugins` — Array of plugin instances
- `onReady` — `(deck: RevealApi) => void`
- `onSync` — `(event) => void`
- `onSlideSync` — `(event) => void`
- `onSlideChange` — `(event) => void`
- `onSlideTransitionEnd` — `(event) => void`
- `onFragmentShown` — `(event) => void`
- `onFragmentHidden` — `(event) => void`
- `onOverviewShown` — `(event) => void`
- `onOverviewHidden` — `(event) => void`
- `onPaused` — `(event) => void`
- `onResumed` — `(event) => void`
- `deckRef` — Ref callback or RefObject for the RevealApi instance
- `className` — Additional CSS classes
- `style` — Inline styles

### Slide

Individual slide component. Maps to `<section>`.

```jsx
import { Slide } from '@reveal.js/react';

<Slide background="#283b95">
  <h2>Colored slide</h2>
</Slide>

<Slide backgroundImage="https://example.com/bg.png" backgroundSize="cover">
  <h2>Image background</h2>
</Slide>

<Slide transition="zoom" autoAnimate>
  <h2 data-id="title">Animated</h2>
</Slide>
```

**Props:**
- `background` — Background color
- `backgroundImage` — Background image URL
- `backgroundVideo` — Background video URL(s)
- `backgroundVideoLoop` — Loop background video
- `backgroundVideoMuted` — Mute background video
- `backgroundIframe` — Iframe background URL
- `backgroundColor` — Background color
- `backgroundGradient` — CSS gradient
- `backgroundSize` — Background size
- `backgroundPosition` — Background position
- `backgroundRepeat` — Background repeat
- `backgroundOpacity` — Background opacity
- `backgroundTransition` — Background transition style
- `backgroundInteractive` — Enable iframe interaction
- `visibility` — `"hidden"` to hide slide
- `autoAnimate` — Enable auto-animate
- `autoAnimateId` — Auto-animate group ID
- `autoAnimateRestart` — Force restart
- `autoAnimateUnmatched` — Handle unmatched elements
- `autoAnimateEasing` — CSS easing
- `autoAnimateDuration` — Duration in seconds
- `autoAnimateDelay` — Delay in seconds
- `transition` — Slide transition
- `transitionSpeed` — Transition speed
- `autoSlide` — Auto-slide duration (ms)
- `notes` — Speaker notes
- `preload` — Preload slide content
- Any other props are forwarded as HTML attributes

### Stack

Creates a vertical slide stack.

```jsx
import { Stack } from '@reveal.js/react';

<Stack>
  <Slide>Vertical slide 1</Slide>
  <Slide>Vertical slide 2</Slide>
  <Slide>Vertical slide 3</Slide>
</Stack>
```

### Fragment

Incremental reveal element.

```jsx
import { Fragment } from '@reveal.js/react';

<Slide>
  <Fragment>First</Fragment>
  <Fragment className="grow">Second (grows)</Fragment>
  <Fragment className="fade-out">Third (fades out)</Fragment>
</Slide>
```

**Props:**
- `className` — Fragment animation class (e.g., `"grow"`, `"fade-out"`)
- `fragmentIndex` — Custom ordering index
- All other props forwarded as HTML attributes

### Code

Syntax-highlighted code block with optional line numbers.

```jsx
import { Code } from '@reveal.js/react';

<Slide>
  <Code lang="javascript" totalLines={5}>
    {`const x = 1;
const y = 2;
const z = 3;`}
  </Code>
</Slide>
```

**Props:**
- `lang` — Language for syntax highlighting
- `totalLines` — Total line count (for line number display)
- `lineNumbers` — Line numbers string (e.g., `"1,3-5"`)
- All other props forwarded to `<pre><code>`

### Markdown

Render Markdown content as slides.

```jsx
import { Markdown } from '@reveal.js/react';

<Markdown
  data={`## Title\n\nContent here\n\n---\n\n## Next slide`}
  separator="^\n---\n$"
/>
```

**Props:**
- `data` — Markdown string
- `separator` — Horizontal slide separator regex
- `verticalSeparator` — Vertical slide separator regex
- `notesSeparator` — Notes separator regex
- `attributes` — Slide attributes pattern

## Hook

### useReveal

Access the Reveal API instance from within any child of `<Deck>`:

```jsx
import { useReveal } from '@reveal.js/react';

function Controls() {
  const deck = useReveal();

  return (
    <button onClick={() => deck?.next()}>Next</button>
  );
}
```

Returns `RevealApi | null`.

## Example: Full Presentation

```jsx
import { Deck, Slide, Stack, Fragment, Code } from '@reveal.js/react';
import RevealHighlight from 'reveal.js/plugin/highlight';
import RevealMarkdown  from 'reveal.js/plugin/markdown';
import RevealNotes     from 'reveal.js/plugin/notes';
import 'reveal.js/dist/reveal.css';
import 'reveal.js/dist/theme/black.css';
import 'reveal.js/dist/plugin/highlight/monokai.css';

export default function Presentation() {
  return (
    <Deck
      config={{ hash: true, center: true }}
      plugins={[RevealHighlight, RevealMarkdown, RevealNotes]}
    >
      <Slide>
        <h1>My Presentation</h1>
        <p>By Author Name</p>
      </Slide>

      <Slide>
        <h2>Features</h2>
        <Fragment>Auto-animate</Fragment>
        <Fragment>Markdown</Fragment>
        <Fragment>Code highlighting</Fragment>
      </Slide>

      <Stack>
        <Slide>
          <h2>Vertical 1</h2>
        </Slide>
        <Slide>
          <h2>Vertical 2</h2>
        </Slide>
      </Stack>

      <Slide>
        <h2>Code</h2>
        <Code lang="javascript" totalLines={3}>
          {`const greet = (name) => {
  return \`Hello, \${name}!\`;
};`}
        </Code>
      </Slide>

      <Slide background="#1a1a2e">
        <h2>The End</h2>
      </Slide>
    </Deck>
  );
}
```

## Notes

- The Deck component creates and destroys the Reveal instance automatically
- Config changes trigger `Reveal.configure()` (shallow comparison)
- Slide structure changes trigger `Reveal.sync()`
- Plugins are registered once at initialization; changing the `plugins` prop after mount has no effect
- React StrictMode is supported — the instance survives unmount/remount cycles
