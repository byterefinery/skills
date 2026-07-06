# Built-in Plugins Reference

## Highlight (Syntax Highlighting)

Based on [highlight.js](https://highlightjs.org/). Provides code syntax highlighting and line-number-based fragment steps.

### Registration

```js
import RevealHighlight from 'reveal.js/plugin/highlight';
Reveal.initialize({ plugins: [RevealHighlight] });
```

```html
<link rel="stylesheet" href="dist/plugin/highlight/monokai.css" />
<script src="dist/plugin/highlight.js"></script>
```

### Configuration

```js
Reveal.initialize({
  highlight: {
    highlightOnLoad: true,    // Auto-highlight on init
    escapeHTML: true,          // Escape HTML entities
    beforeHighlight: (hljs) => { /* customize hljs before use */ }
  },
  plugins: [RevealHighlight]
});
```

### Line Numbers with Fragments

```html
<pre><code class="hljs javascript" data-trim data-line-numbers="|4,8-11|17|22-24">
// Each pipe-separated group becomes a fragment
</code></pre>
```

Format: `start-end` for ranges, `N` for single lines, comma to separate, pipe for steps.

### Line Number Offset

```html
<pre><code class="hljs" data-trim data-line-numbers data-ln-start-from="287">
</code></pre>
```

Set `data-ln-start-from` to offset line numbers.

## Markdown

Parses Markdown inside slides using [marked](https://marked.js.org/). Supports inline templates and external files.

### Registration

```js
import RevealMarkdown from 'reveal.js/plugin/markdown';
Reveal.initialize({ plugins: [RevealMarkdown] });
```

### Inline Markdown

```html
<section data-markdown>
  <script type="text/template">
    ## Title
    Content
    ---
    ## Next slide
  </script>
</section>
```

Default separator: `---` (horizontal rule pattern). Vertical slides: use `data-separator-vertical`.

### External File

```html
<section data-markdown="slides.md"
         data-separator="^\n\n\n"
         data-separator-vertical="^\n\n"
         data-separator-notes="^Note:">
</section>
```

In the `.md` file, separate horizontal slides with three blank lines, vertical slides with two blank lines. Speaker notes with `Note:` prefix.

### Slide Attributes in Markdown

```markdown
<!-- .slide: data-background="#000000" data-transition="zoom" -->
## Slide with dark background
```

### Element Attributes in Markdown

```markdown
- Item 1 <!-- .element: class="fragment" data-fragment-index="2" -->
- Item 2 <!-- .element: class="fragment" data-fragment-index="1" -->
```

### Code Blocks with Line Numbers

```markdown
```javascript [3,5-7]
const x = 1;
```
```

Format: ````[language line-nums]` or ````[offset: line-nums]` for line offset.

### Configuration

```js
Reveal.initialize({
  markdown: {
    smartypants: true,       // Curly quotes
    animateLists: true,       // Auto-fragment list items
    // All marked.js options supported:
    breaks: true,
    gfm: true,
    // …
  },
  plugins: [RevealMarkdown]
});
```

## Math (LaTeX)

Supports four typesetters: MathJax 2 (default), MathJax 3, MathJax 4, and KaTeX.

### Registration

```js
import RevealMath from 'reveal.js/plugin/math';

// Choose typesetter:
Reveal.initialize({
  plugins: [RevealMath.KaTeX]           // Fastest
  // plugins: [RevealMath.MathJax2]     // Default, most compatible
  // plugins: [RevealMath.MathJax3]
  // plugins: [RevealMath.MathJax4]     // Latest
});
```

### Inline Math

```html
<p>The value of \(x\) is \(y^2\).</p>
```

### Display Math

```html
\[E = mc^2\]
```

Or:

```html
$$E = mc^2$$
```

### Math with Fragments

```html
<div class="fragment">
  \[\begin{aligned}
    \dot{x} &= \sigma(y-x) \\
    \dot{y} &= \rho x - y - xz
  \end{aligned}\]
</div>
```

### KaTeX Configuration

```js
Reveal.initialize({
  katex: {
    version: 'latest',
    delimiters: [
      { left: '$$',  right: '$$',  display: true },
      { left: '$',   right: '$',   display: false },
      { left: '\\(', right: '\\)', display: false },
      { left: '\\[', right: '\\]', display: true }
    ]
  },
  plugins: [RevealMath.KaTeX]
});
```

### MathJax 4 Configuration

```js
Reveal.initialize({
  mathjax4: {
    tex: {
      inlineMath: [['$', '$'], ['\\(', '\\)']],
      displayMath: [['$$', '$$'], ['\\[', '\\]']],
      macros: {
        R: '\\mathbb{R}',
        set: ['\\left\\{#1 \\; ; \\; #2\\right\\}', 2]
      }
    },
    options: {
      skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code']
    }
  },
  plugins: [RevealMath.MathJax4]
});
```

## Notes (Speaker View)

Provides a separate speaker notes window with timer, upcoming slide preview, and notes display.

### Registration

```js
import RevealNotes from 'reveal.js/plugin/notes';
Reveal.initialize({ plugins: [RevealNotes] });
```

### Writing Notes

```html
<section>
  <h2>Slide Title</h2>
  <p>Visible content</p>
  <aside class="notes">
    These notes are only visible in the speaker view.
    Supports <strong>HTML</strong> and Markdown.
  </aside>
</section>
```

### In Markdown

```markdown
## Slide Title

Content

Note: This appears in speaker notes.
```

### Opening Speaker View

Press `S` during the presentation. Opens a new window with:
- Current slide (large)
- Upcoming slide preview
- Speaker notes
- Timer (with optional pacing based on `defaultTiming`)
- Navigation controls

### Configuration

```js
Reveal.initialize({
  showNotes: false,       // Show notes to all viewers
  defaultTiming: 120,     // Seconds per slide for pacing timer
  plugins: [RevealNotes]
});
```

## Search

Full-text search across all slides. Press `Ctrl+Shift+F` (or `Cmd+Shift+F` on Mac).

### Registration

```js
import RevealSearch from 'reveal.js/plugin/search';
Reveal.initialize({ plugins: [RevealSearch] });
```

No configuration needed. Search overlay appears with keyboard shortcut.

## Zoom

Zoom into any element by holding `Alt` (or `Ctrl` on Linux) and clicking. Click again to zoom out.

### Registration

```js
import RevealZoom from 'reveal.js/plugin/zoom';
Reveal.initialize({ plugins: [RevealZoom] });
```

Uses [zoom.js](http://lab.hakim.se/zoom-js) internally.

## Custom Plugin Structure

Create a custom plugin as a factory function:

```js
const MyPlugin = {
  id: 'my-plugin',
  init: function(reveal) {
    // Access reveal.js API via `reveal`
    reveal.on('slidechanged', (event) => {
      console.log('Slide changed to', event.indexh, event.indexv);
    });
  }
};

export default MyPlugin;
```

Register:

```js
import MyPlugin from './my-plugin.js';
Reveal.initialize({ plugins: [MyPlugin] });
```

## Loading Order

Always load `reveal.js` before plugins. When using script tags:

```html
<script src="dist/reveal.js"></script>
<script src="dist/plugin/highlight.js"></script>
<script src="dist/plugin/markdown.js"></script>
<script src="dist/plugin/math.js"></script>
<script src="dist/plugin/notes.js"></script>
<script>
  Reveal.initialize({
    plugins: [RevealHighlight, RevealMarkdown, RevealMath.KaTeX, RevealNotes]
  });
</script>
```
