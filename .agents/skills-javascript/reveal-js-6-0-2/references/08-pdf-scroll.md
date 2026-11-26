# PDF export and scroll view

## PDF export

Two ways to get the print layout:

1. Append `?print-pdf` to the deck URL — legacy query, still supported (the core checks `window.location.search` for `print-pdf`)
2. Set `view: 'print'` in config — renders the presentation so it can be printed to PDF

The print view adds the `reveal-print` and `print-pdf` classes to the document root. From there, use the browser's print dialog / save-as-PDF.

PDF-relevant config:

| Option | Default | Notes |
|---|---|---|
| `pdfMaxPagesPerSlide` | `Infinity` | Maximum pages a single slide may expand onto |
| `pdfSeparateFragments` | `true` | Print each fragment on a separate page |
| `pdfPageHeightOffset` | `-1` | Height offset compensating in-browser vs CLI printing differences |

The demo deck links to https://revealjs.com/pdf-export/ for the full instructions.

## Scroll view

A single-page, tall scrollable rendering of the deck with scroll-triggered animations (source: `examples/scroll.html`, `js/config.ts`).

- `view: 'scroll'` in config enables it
- `scrollLayout` — `'full'` (default; each slide as tall as the viewport) or `'compact'` (slides as small as possible, several visible at once on tall screens)
- `scrollSnap` — `'mandatory'` (default) always snap, `'proximity'` snap when close, `false` continuous scrolling
- `scrollProgress` — `'auto'` (default) scrollbar while scrolling, `true` always, `false` never
- `scrollActivationWidth` — default 435; the scroll view activates automatically when the viewport is narrower than this
- Fragments and Auto-Animate are scroll-triggered in this view
- Vertical stacks still work (nested sections), and `hash: true` keeps deep links functional
