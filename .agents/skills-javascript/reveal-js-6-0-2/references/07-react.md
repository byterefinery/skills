# @revealjs/react

The React wrapper ships in the repo under `react/` and is published as the separate package `@revealjs/react` (source: `react/README.md`).

## Installation

```bash
npm i @revealjs/react reveal.js react react-dom
```

The package ships only the React bindings — you still import the Reveal CSS, themes, and plugins yourself.

## Set up a deck

```tsx
import { Deck, Slide } from '@revealjs/react';
import 'reveal.js/reveal.css';
import 'reveal.js/theme/black.css';

export function Presentation() {
  return (
    <Deck>
      <Slide>
        <h1>Hello</h1>
      </Slide>
      <Slide background="#111827">
        <h2>Second slide</h2>
      </Slide>
    </Deck>
  );
}
```

## Components

- `Deck` — creates one Reveal instance on mount, destroys it on unmount
- `Slide` — a slide; supports Reveal slide props (`background`, `backgroundImage`, `backgroundColor`, `visibility`, `autoAnimate`, `transition`, `transitionSpeed`, `autoSlide`, `notes`, `backgroundInteractive`, `preload`) and passes through raw `data-*` attributes to the rendered `<section>`
- `Stack` — groups slides into a vertical column
- `Fragment` — reveals content one step at a time (`animation` prop, `as`/`asChild` for the rendered tag)
- `Code` — syntax-highlighted block via the highlight plugin (`language`, `lineNumbers`)
- `Markdown` — renders Reveal-compatible Markdown slides without registering the Reveal markdown plugin; accepts string children, a `markdown` prop, or `src` for external markdown, with first-class `separator`, `verticalSeparator`, `notesSeparator`, `elementAttributesSeparator`, `slideAttributesSeparator` props and `options` passthrough for other marked settings

## Configure Reveal

Pass any Reveal configuration through the `config` prop on `Deck` (shallow-compared each render; `reveal.configure()` only fires when a value changes). Plugins register separately via `plugins` and are applied once at initialization (the prop is captured on first mount and ignored afterwards):

```tsx
<Deck
  config={{ width: 1280, height: 720, hash: true, transition: 'slide' }}
  plugins={[RevealHighlight]}
>
  <Slide>Configured deck</Slide>
</Deck>
```

## Events and API access

- Event props on `Deck`: `onReady`, `onSync`, `onSlideChange`, `onFragmentShown`, ... (wired with `deck.on()` after init, swapped automatically when the callback changes)
- `useReveal()` — call the Reveal API from components inside the deck tree (`deck?.next()`)
- `deckRef` — access the instance outside the component tree: `const deckRef = useRef<RevealApi | null>(null)`; `<Deck deckRef={deckRef}>`

## How it works

- `Deck` calls `reveal.sync()` when the rendered slide structure changes (slides added, removed, reordered, regrouped into stacks)
- `Slide` handles slide-level `data-*` updates locally with `reveal.syncSlide()`, so ordinary content updates do not trigger a full deck sync
- `Markdown` uses `marked` plus the same separator and comment-attribute conventions as Reveal's core markdown plugin (`.slide:` and `.element:` comment syntax)
