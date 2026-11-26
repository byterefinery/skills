---
name: docx-preview-0-4-0
description: Renders DOCX documents as semantic HTML in the browser. Use when displaying .docx files in web apps, building document viewers, or converting Word docs to HTML. Supports headers, footers, footnotes, endnotes, tables, numbering, equations, and images. Requires jszip and a browser DOM.
license: Apache-2.0
metadata:
  tags:
    - javascript
    - browser
    - rendering
---

# docx-preview 0.4.0

## Overview

`docx-preview` (docxjs) renders DOCX files as semantic HTML in the browser — real styled HTML elements, not canvas or image rendering, so output is limited by what HTML can express. It parses the Office Open XML structure of the document and produces styled HTML with page wrappers.

Three entry points:

- `renderAsync(data, bodyContainer, styleContainer?, options?)` — parse + render in one call; the only stable API
- `parseAsync(data, options?)` — parse only, returns the internal `WordDocument` (experimental)
- `renderDocument(document, options?)` — render a parsed document to DOM nodes (experimental)

`data` accepts `Blob | ArrayBuffer | Uint8Array` — anything `JSZip.loadAsync` supports. Rendered features include text runs and underlines, line spacing, numbering, tables with spans, page layout and sections, footnotes, endnotes, headers/footers, track changes (revisions), equations (MathML), and embedded images.

## Usage

### Installation

```bash
npm install docx-preview   # jszip comes along as a dependency
```

For script tag usage, load jszip first — the UMD build expects the global `JSZip`:

```html
<script src="https://unpkg.com/jszip/dist/jszip.min.js"></script>
<script src="https://unpkg.com/docx-preview@0.4.0/dist/docx-preview.min.js"></script>
```

### Basic render (script tag)

```html
<script>
    var docData = /* document Blob */;
    docx.renderAsync(docData, document.getElementById("container"))
        .then(x => console.log("docx: finished"));
</script>
```

### Basic render (ES modules)

```js
import { renderAsync } from 'docx-preview';

const container = document.getElementById('document');
const blob = await fetch('/document.docx').then(r => r.blob());
await renderAsync(blob, container);
```

### With options

Spread `defaultOptions` and override what you need:

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

Pass a third argument to render styles (numberings, fonts) into a different element, e.g. a `<style>` tag in `<head>`:

```js
const bodyContainer = document.getElementById('document-body');
const styleContainer = document.getElementById('document-styles');

await renderAsync(blob, bodyContainer, styleContainer);
```

### Parse then render (experimental)

`renderAsync` is `parseAsync` + `renderDocument`; split them to inspect or modify the document model in between:

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

### TIFF/WMF image preprocessing

The library does not render TIFF or WMF images. The repo demo includes a preprocessor that converts them inside the DOCX zip (TIFF → PNG via `tiff.js`, WMF → SVG via `WMFJS`) before calling `renderAsync`. Full pattern in [02-demos](references/02-demos.md).

## Gotchas

- **Browser only** — rendering uses `document`/`HTMLElement` directly. It does not work in Node.js without a DOM implementation.
- **Only `renderAsync` is stable** — the maintainer states the parsing/rendering internals may change at any point; `parseAsync` and `renderDocument` are the experimental/internal API (`renderAsync = parseAsync + renderDocument`).
- **Page breaks are not calculated in real time** — pages break only on explicit `<w:br w:type="page"/>`, on `<w:lastRenderedPageBreak/>` markers (requires `ignoreLastRenderedPageBreak: false`), or on page setting changes (e.g. portrait → landscape). Real-time page calculation is not implemented because it requires size re-calculation on each insertion.
- **`ignoreLastRenderedPageBreak` defaults to `true`** — editors like MS Word insert these markers, but the library ignores them by default. Set it to `false` to honor Word's page breaks.
- **TOC fields are not supported** — field codes are not evaluated, so `{ TOC }` fields render as literal text and a table of contents cannot be extracted.
- **Thumbnails are not part of the library** — the demo's thumbnail view is an example only; the maintainer notes HTML rendering is not efficient for thumbnails.
- **TIFF and WMF images are not rendered natively** — preprocess them in the zip (see [02-demos](references/02-demos.md)) or convert before upload.
- **`useBase64URL` defaults to `false`** — images/fonts use `URL.createObjectURL()`. Set to `true` for self-contained HTML (e.g. saving or embedding), at the cost of larger payload.
- **`renderChanges` and `renderComments` are experimental** — track-changes and comment rendering may have edge cases; both default to `false`.
- **`className` is a prefix** — default generated class names are prefixed with `docx` (e.g. `docx-wrapper`, `docx-page-1`). Changing it means existing CSS selectors stop matching.
- **`styleContainer` defaults to `bodyContainer`** — passing `null` (or omitting) puts `<style>` nodes into the body container along with content.
- **`h` option is experimental** — the custom HTML factory hook is subject to change; use the default unless you need SSR or custom rendering.

## References

- [01-options](references/01-options.md) — Full `Options` reference with defaults
- [02-demos](references/02-demos.md) — TIFF/WMF preprocessor and thumbnail example from the repo demo
