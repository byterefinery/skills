# Layout helpers

CSS utility classes from reveal.js 6.0.2 (source: `examples/layout-helpers.html`, `demo.html`).

| Class | Purpose |
|---|---|
| `r-fit-text` | Resizes the text to be as large as possible within its container |
| `r-stretch` | Makes an element as tall as possible while remaining within the slide bounds |
| `r-stack` | Stacks multiple elements on top of each other — combine with fragments so only the active one shows |
| `r-hstack` | Lays child elements out horizontally |
| `r-vstack` | Lays child elements out vertically |
| `justify-center` | Centers the children of an `r-hstack`/`r-vstack` (used as `class="r-hstack justify-center"`) |
| `r-frame` | Styled frame/box wrapper (used for framed images and callouts) |

All helpers are plain CSS classes — combine freely with fragments (`class="fragment fade-in-then-out"`) and Auto-Animate (the hstack/vstack examples use `data-auto-animate` on the parent slide).
