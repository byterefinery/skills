---
name: docx-preview-0-3-7
description: Renders DOCX documents as semantic HTML in the browser. Use when displaying .docx files in web apps, building document viewers, or converting Word docs to HTML. Supports headers, footers, footnotes, tables, equations, images, and page breaks. Requires jszip peer dependency. Browser-only (no Node.js DOM).
metadata:
  tags:
    - javascript
    - browser
    - rendering
---

# docx-preview 0.3.7

## Overview

`docx-preview` renders DOCX files as semantic HTML in the browser. It parses the Office Open XML structure and produces styled HTML elements — not canvas or image-based rendering. The library depends on `jszip` and runs in browsers only (requires `document`/`HTMLElement`).

Three entry points:

- `renderAsync(data, bodyContainer, styleContainer?, options?)` — parse + render in one call
- `parseAsync(data, options?)` — parse only, returns internal `WordDocument`
- `renderDocument(document, options?)` — render a parsed document to DOM nodes

## Usage

### Installation

```bash
npm install docx-preview
# jszip is a required peer dependency
npm install jszip
```

### Basic render (ES modules)

```js
import { renderAsync } from 'docx-preview';

const container = document.getElementById('document');

const blob = await fetch('/document.docx').then(r => r.blob());
await renderAsync(blob, container);
```

### Basic render (script tag)

```html
<script src="https://unpkg.com/jszip/dist/jszip.min.js"></script>
<script src="https://unpkg.com/docx-preview@0.3.7/dist/docx-preview.js"></script>
<script>
  const container = document.getElementById('document');
  const blob = /* Blob from file input, fetch, etc. */;
  docx.renderAsync(blob, container).then(() => console.log('done'));
</script>
```

### With options

```js
import { renderAsync, defaultOptions } from 'docx-preview';

const options = {
  ...defaultOptions,
  className: 'my-docx',
  ignoreFonts: true,
  useBase64URL: true,
  renderChanges: true,
};

await renderAsync(blob, container, null, options);
```

### Separate style container

Render styles to a different element (e.g., a `<style>` tag in `<head>`):

```js
const bodyContainer = document.getElementById('document-body');
const styleContainer = document.getElementById('document-styles');

await renderAsync(blob, bodyContainer, styleContainer);
```

### Parse then render (two-step)

Useful when modifying the document model before rendering:

```js
import { parseAsync, renderDocument } from 'docx-preview';

const doc = await parseAsync(blob);
// ... inspect or modify doc ...
const nodes = await renderDocument(doc);

container.innerHTML = '';
for (const node of nodes) {
  container.appendChild(node);
}
```

### Custom h function (experimental)

Override the default DOM factory for SSR, testing, or custom rendering:

```js
import { renderAsync, h } from 'docx-preview';

const customH = (elem) => {
  // wrap or transform elements before creating DOM nodes
  if (elem.tagName === 'table') {
    elem.className = (elem.className || '') + ' custom-table';
  }
  return h(elem);
};

await renderAsync(blob, container, null, { h: customH });
```

### TIFF/WMF image preprocessing

The library does not render TIFF or WMF images natively. Preprocess with `tiff.js` / `WMFJS` before passing to `renderAsync`:

```js
// Preprocess TIFF → PNG and WMF → SVG inside the DOCX zip
// See references/01-options.md for the full preprocessor pattern
let processedBlob = await preprocessDocx(originalBlob);
await renderAsync(processedBlob, container);
```

## Gotchas

- **Browser only** — requires `document`, `HTMLElement`, `Node`. Does not work in Node.js without jsdom or similar.
- **jszip is required** — `docx-preview` depends on it but does not bundle it. Install `jszip` explicitly.
- **`styleContainer` defaults to `bodyContainer`** — passing `null` means styles go into the same element as content. To separate them, pass a distinct element.
- **Page breaks are not automatic** — the library only breaks on explicit `<w:br w:type="page"/>` or `<w:lastRenderedPageBreak/>` markers. Real-time page calculation is not implemented. Set `ignoreLastRenderedPageBreak: false` to honor Word-inserted break points.
- **`ignoreLastRenderedPageBreak` defaults to `true`** — Word editors insert these markers but the library ignores them by default. Set to `false` if you need Word's page breaks.
- **TIFF and WMF images are not supported** — preprocess with `tiff.js` and `WMFJS` respectively, or convert before upload.
- **`useBase64URL: false` is default** — images use `URL.createObjectURL()`. Set to `true` if you need self-contained HTML (e.g., for saving or embedding). Base64 increases payload size.
- **`renderChanges` and `renderComments` are experimental** — track changes and comment rendering may have edge cases. Default is `false`.
- **Only `renderAsync` is stable API** — `parseAsync` and `renderDocument` are experimental; internal structures may change between versions.
- **`className` option is a prefix** — all generated class names are prefixed with this value (default `"docx"`). Changing it means default CSS selectors won't match.
- **TOC fields are not supported** — the library does not evaluate field codes, so `{ TOC }` fields render as literal text.
- **`h` function is experimental** — the custom renderer API may change. Use the default unless you have a specific need.

## References

- [01-options](references/01-options.md) — Full Options reference with defaults and descriptions
