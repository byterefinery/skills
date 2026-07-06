# PDF Export and Scroll View Reference

## PDF Export

### Method 1: Browser Print

1. Open the presentation with `?print-pdf` in the URL:
   ```
   https://example.com/presentation.html?print-pdf
   ```

2. Or set in config:
   ```js
   Reveal.initialize({ view: 'print' });
   ```

3. Press `Ctrl+P` (or `Cmd+P` on Mac) to open the print dialog

4. Select "Save as PDF" as the destination

5. Ensure "Background graphics" is enabled in print settings

### Method 2: CLI Tools

Use PhantomJS, wkhtmltopdf, or Puppeteer for headless PDF generation:

```bash
# With PhantomJS (reveal.js provides a script)
phantomjs node_modules/reveal.js/css/print/pdf.js http://example.com/presentation.html?print-pdf output.pdf
```

### PDF Configuration

```js
Reveal.initialize({
  pdfMaxPagesPerSlide: Infinity,   // Max pages per slide
  pdfSeparateFragments: true,       // Each fragment on separate page
  pdfPageHeightOffset: -1,          // Height offset for page calculation
});
```

- `pdfMaxPagesPerSlide` — Limits how many pages a single slide can expand to. Useful for slides with long code blocks or tables.
- `pdfSeparateFragments` — When `true`, each fragment step generates a separate page. Set to `false` for compact output.
- `pdfPageHeightOffset` — Compensates for environment differences in page height calculation.

### PDF Best Practices

- Use Chrome or Chromium for best results
- Enable "Background graphics" in print settings
- Test the output — some CSS effects (gradients, shadows) may not print
- Code blocks with many lines may overflow; use `pdfMaxPagesPerSlide` to control
- Speaker notes are not included in PDF output

## Scroll View

Scroll view renders the presentation as a single scrollable page. Fragments and auto-animate trigger on scroll.

### Activation

```js
Reveal.initialize({
  view: 'scroll',
});
```

Or via URL: `?view=scroll`

### Scroll Configuration

```js
Reveal.initialize({
  view: 'scroll',
  scrollLayout: 'full',              // 'full' or 'compact'
  scrollSnap: 'mandatory',           // 'mandatory', 'proximity', or false
  scrollProgress: 'auto',            // 'auto', true, or false
  scrollActivationWidth: 435,        // Auto-activate below this width
});
```

- `scrollLayout: 'full'` — Each slide fills the viewport height
- `scrollLayout: 'compact'` — Slides are smaller, multiple visible on tall screens
- `scrollSnap: 'mandatory'` — Always snap to slide boundaries
- `scrollSnap: 'proximity'` — Snap only when close to a slide
- `scrollSnap: false` — Free scrolling, no snapping
- `scrollProgress: 'auto'` — Show scrollbar while scrolling, hide when idle
- `scrollActivationWidth` — Responsive activation: auto-switch to scroll view when viewport is narrower than this width

### Scroll View Features

- **Fragments** — Trigger as they scroll into view
- **Auto-animate** — Animations trigger on scroll
- **Code highlights** — Line highlight fragments work on scroll
- **Backgrounds** — All background types supported
- **Media** — `data-autoplay` media plays on scroll visibility

### Scroll View Limitations

- No slide overview (ESC)
- No navigation controls (arrows)
- No progress bar (uses native scrollbar)
- Keyboard navigation limited
- Touch/swipe replaced by native scrolling

### Responsive Scroll View

Auto-activate scroll view on narrow viewports:

```js
Reveal.initialize({
  scrollActivationWidth: 435,  // Default
});
```

When the viewport width drops below `scrollActivationWidth`, scroll view activates automatically. When it grows above, it deactivates.

## Print View (Reader Mode)

The `view: 'print'` option is also accessible as `"reader"` for compatibility:

```js
Reveal.initialize({ view: 'reader' });
```

This is equivalent to `view: 'print'` and activates the PDF-friendly layout.

## Custom Print CSS

The print stylesheet is at `css/print/pdf.scss`. It handles:

- Removing controls, progress bar, and playback elements
- Setting static slide positions
- Creating `.pdf-page` wrapper elements
- Page break handling
- Fragment visibility in print mode

To customize print output, override styles in your own CSS:

```css
@media print {
  .reveal .slides section {
    /* Custom print styles */
  }
}
```
