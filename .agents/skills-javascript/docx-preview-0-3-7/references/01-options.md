# Options Reference

All options are merged with `defaultOptions`. Pass a partial object — only the keys you want to override.

## Options Table

| Option | Type | Default | Description |
|---|---|---|---|
| `className` | `string` | `"docx"` | Class name prefix for all generated style classes |
| `inWrapper` | `boolean` | `true` | Wrap document content in a container element |
| `hideWrapperOnPrint` | `boolean` | `false` | Hide wrapper styling when printing |
| `ignoreWidth` | `boolean` | `false` | Skip rendering page width |
| `ignoreHeight` | `boolean` | `false` | Skip rendering page height |
| `ignoreFonts` | `boolean` | `false` | Skip font embedding/rendering |
| `breakPages` | `boolean` | `true` | Enable page breaking on explicit page break markers |
| `ignoreLastRenderedPageBreak` | `boolean` | `true` | Skip `<w:lastRenderedPageBreak/>` markers (Word-inserted). Set `false` to honor them |
| `experimental` | `boolean` | `false` | Enable experimental features (tab stop calculation) |
| `trimXmlDeclaration` | `boolean` | `true` | Strip XML declaration from embedded XML before parsing |
| `useBase64URL` | `boolean` | `false` | Encode images/fonts as base64 data URLs instead of `URL.createObjectURL()` |
| `renderHeaders` | `boolean` | `true` | Render page headers |
| `renderFooters` | `boolean` | `true` | Render page footers |
| `renderFootnotes` | `boolean` | `true` | Render footnotes |
| `renderEndnotes` | `boolean` | `true` | Render endnotes |
| `renderChanges` | `boolean` | `false` | Experimental: render track-changes (insertions/deletions) |
| `renderComments` | `boolean` | `false` | Experimental: render document comments |
| `renderAltChunks` | `boolean` | `true` | Render altChunks (embedded HTML parts) |
| `debug` | `boolean` | `false` | Enable console logging for debugging |
| `h` | `function` | built-in | Custom DOM factory function (experimental) |

## Default Options

```js
const defaultOptions = {
    ignoreHeight: false,
    ignoreWidth: false,
    ignoreFonts: false,
    breakPages: true,
    debug: false,
    experimental: false,
    className: "docx",
    inWrapper: true,
    hideWrapperOnPrint: false,
    trimXmlDeclaration: true,
    ignoreLastRenderedPageBreak: true,
    renderHeaders: true,
    renderFooters: true,
    renderFootnotes: true,
    renderEndnotes: true,
    useBase64URL: false,
    renderChanges: false,
    renderComments: false,
    renderAltChunks: true,
    h: h // built-in DOM factory
};
```

## Page Break Behavior

The library breaks pages only at explicit markers:

1. **Manual page break** — `<w:br w:type="page"/>` — inserted when user adds a page break
2. **Application page break** — `<w:lastRenderedPageBreak/>` — inserted by editors like MS Word (requires `ignoreLastRenderedPageBreak: false`)
3. **Section change** — paragraph page settings change (e.g., portrait → landscape)

Real-time page breaking is not implemented — it requires size recalculation on every insertion, which would impact performance.

**Recommendation:** For reliable page breaks, insert manual breaks in the document or use `ignoreLastRenderedPageBreak: false` to honor Word's markers.

## TIFF/WMF Preprocessing

The library does not render TIFF or WMF images. Use this pattern to preprocess:

```js
async function preprocessDocx(blob) {
    let zip = await JSZip.loadAsync(blob);
    const files = zip.file(/[.](tiff|wmf)$/);

    if (files.length === 0) return blob;

    for (const f of files) {
        const buffer = await f.async('uint8array');

        if (f.name.endsWith('.tiff')) {
            // Requires tiff.js: https://github.com/mattdesl/tiff.js
            const tiff = new Tiff({ buffer });
            const pngBlob = await new Promise(res =>
                tiff.toCanvas().toBlob(b => res(b), 'image/png')
            );
            zip.file(f.name, pngBlob);
        }
        else if (f.name.endsWith('.wmf')) {
            // Requires WMFJS (from rtf.js): https://github.com/nickninjajackson/rtf.js
            const renderer = new WMFJS.Renderer(buffer);
            const svg = renderer.render({
                width: '1000px',
                height: '800px',
                xExt: 1000,
                yExt: 800,
                mapMode: 8, // preserve aspect ratio
            }).firstChild;
            svg.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
            svg.removeAttribute('width');
            svg.removeAttribute('height');
            zip.file(f.name, svg.outerHTML);
        }
    }

    // Update content types: image/x-wmf → image/svg+xml
    const contentType = zip.file('[Content_Types].xml');
    if (contentType) {
        const text = await contentType.async('text');
        zip.file('[Content_Types].xml', text.replace(/image\/x-wmf/g, 'image/svg+xml'));
    }

    return await zip.generateAsync({ type: 'blob' });
}
```

## Custom h Function

The `h` function is the DOM factory. It converts virtual element descriptions into real DOM nodes. Signature:

```ts
type HElement = {
    ns?: string;
    tagName: string;
    className?: string;
    style?: Record<string, string> | string;
    children?: (HElement | Node | string)[];
} & Record<string, any>;

function h(elem: HElement | Node | string): Node;
```

The default implementation handles:
- `#fragment` → `DocumentFragment`
- `#comment` → comment node
- Regular tags → `createElement` or `createElementNS`
- Strings → `createTextNode`
- Namespaced elements (SVG, MathML)

To customize, wrap the default `h`:

```js
import { renderAsync, h as defaultH } from 'docx-preview';

const customH = (elem) => {
    if (typeof elem !== 'string' && !(elem instanceof Node)) {
        // Add data attributes for all paragraphs
        if (elem.tagName === 'p') {
            elem['data-docx-paragraph'] = 'true';
        }
    }
    return defaultH(elem);
};

await renderAsync(blob, container, null, { h: customH });
```
