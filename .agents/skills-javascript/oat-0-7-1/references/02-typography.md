# Typography

All text elements are styled automatically — no classes needed.

## Headings

Six heading levels with responsive `clamp()` font sizes:

```html
<h1>Heading 1</h1>  <!-- clamp(1.75rem, 1.5rem + 1.1vw, 2.25rem) -->
<h2>Heading 2</h2>  <!-- clamp(1.5rem, 1.3rem + 0.8vw, 1.875rem) -->
<h3>Heading 3</h3>  <!-- clamp(1.25rem, 1.1rem + 0.5vw, 1.5rem) -->
<h4>Heading 4</h4>  <!-- clamp(1.125rem, 1.05rem + 0.3vw, 1.25rem) -->
<h5>Heading 5</h5>  <!-- 1.125rem -->
<h6>Heading 6</h6>  <!-- 1rem (same as body text) -->
```

All headings use `font-weight: var(--font-semibold)` (600) and `line-height: 1.25`.

## Paragraphs

```html
<p>Styled with margin-block-end and overflow-wrap: break-word.</p>
```

## Text formatting

```html
<strong>Bold</strong>        <!-- font-weight: semibold -->
<b>Bold</b>
<em>Italic</em>
<i>Italic</i>
<small>Small text</small>    <!-- 0.875rem -->
<code>Inline code</code>     <!-- monospace, faint bg, rounded -->
<mark>Highlighted</mark>     <!-- warning-tinted background -->
```

## Links

```html
<a href="#">Underlined, primary color, hover opacity transition</a>
```

## Code blocks

```html
<pre><code>function hello() {
  console.log('Hello');
}</code></pre>
```

Monospace font, faint background, rounded corners, horizontal scroll overflow.

## Blockquotes

```html
<blockquote>
  Left border, italic, muted foreground color.
</blockquote>
```

## Horizontal rule

```html
<hr>  <!-- 1px solid border, spaced vertically -->
```

## Lists

```html
<ul>
  <li>Disc bullet, indented</li>
  <li>Items have margin-block-end</li>
</ul>

<ol>
  <li>Decimal numbering</li>
  <li>Same spacing as unordered</li>
</ol>
```

## Font variables

```css
--font-sans: system-ui, sans-serif;
--font-mono: ui-monospace, Consolas, monospace;

--text-1: clamp(1.75rem, 1.5rem + 1.1vw, 2.25rem);  /* h1 */
--text-2: clamp(1.5rem, 1.3rem + 0.8vw, 1.875rem);  /* h2 */
--text-3: clamp(1.25rem, 1.1rem + 0.5vw, 1.5rem);   /* h3 */
--text-4: clamp(1.125rem, 1.05rem + 0.3vw, 1.25rem); /* h4 */
--text-5: 1.125rem;
--text-6: 1rem;
--text-7: 0.875rem;
--text-8: 0.75rem;
--text-regular: var(--text-6);

--leading-normal: 1.5;
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 600;
```
