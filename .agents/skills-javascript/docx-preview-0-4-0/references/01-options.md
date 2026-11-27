# docx-preview Options

Full `Options` interface for `renderAsync`, `parseAsync`, and `renderDocument`. Defaults from `defaultOptions` (v0.4.0); descriptions from the project README API section.

Pass a `Partial<Options>` — omitted fields fall back to `defaultOptions`.

| Option | Type | Default | Description |
|---|---|---|---|
| `className` | `string` | `"docx"` | Class name/prefix for default and document style classes |
| `inWrapper` | `boolean` | `true` | Enables rendering of a wrapper around document content |
| `hideWrapperOnPrint` | `boolean` | `false` | Disables wrapper styles on print |
| `ignoreWidth` | `boolean` | `false` | Disables rendering width of page |
| `ignoreHeight` | `boolean` | `false` | Disables rendering height of page |
| `ignoreFonts` | `boolean` | `false` | Disables fonts rendering |
| `breakPages` | `boolean` | `true` | Enables page breaking on page breaks |
| `ignoreLastRenderedPageBreak` | `boolean` | `true` | Disables page breaking on `lastRenderedPageBreak` elements |
| `experimental` | `boolean` | `false` | Enables experimental features (tab stops calculation) |
| `trimXmlDeclaration` | `boolean` | `true` | If true, XML declaration is removed from XML documents before parsing |
| `useBase64URL` | `boolean` | `false` | If true, images/fonts/etc. are converted to base 64 URLs; otherwise `URL.createObjectURL` is used |
| `renderChanges` | `boolean` | `false` | Enables experimental rendering of document changes (insertions/deletions) |
| `renderHeaders` | `boolean` | `true` | Enables headers rendering |
| `renderFooters` | `boolean` | `true` | Enables footers rendering |
| `renderFootnotes` | `boolean` | `true` | Enables footnotes rendering |
| `renderEndnotes` | `boolean` | `true` | Enables endnotes rendering |
| `renderComments` | `boolean` | `false` | Enables experimental comments rendering |
| `renderAltChunks` | `boolean` | `true` | Enables altChunks (HTML parts) rendering |
| `debug` | `boolean` | `false` | Enables additional logging |
| `h` | `(elemOrText: HElement \| Node \| string) => Node` | `defaultOptions.h` | Experimental hook for HTML rendering, subject to change |

## Notes

- `renderAsync(data, bodyContainer, styleContainer?, options?)` — `styleContainer` receives `STYLE` nodes (styles, numberings, fonts); if `null`/omitted, `bodyContainer` is used for everything.
- `h` receives an `HElement` (`{ ns?, tagName, className?, style?, children?, ...props }`), an existing `Node`, or a `string`; the default factory creates DOM nodes with `document.createElement` / `createElementNS` (HTML, SVG, and MathML namespaces are supported via `ns`).
- Spread `defaultOptions` when overriding so a future default change does not silently flip behavior: `{ ...defaultOptions, useBase64URL: true }`.

## Custom h function (experimental)

`h` is the DOM factory hook: the renderer calls it for every virtual element (`HElement`), existing `Node`, or text `string`. Public type (from `dist/docx-preview.d.ts`, v0.4.0):

```ts
export type HElement = {
    ns?: string;  // namespace URI — source `ns` enum: html (xhtml), svg, mathML
    tagName: string;  // "#fragment", "#comment", or a tag name
    className?: string;
    style?: Record<string, string> | string;
    children?: (HElement | Node | string)[];
} & Record<string, any>;

// in Options:
h: (elemOrText: HElement | Node | string) => Node;  // "experimental, subject to change"
```

Default factory behavior (from `src/html.ts`):

- `string` → `document.createTextNode`
- existing `Node` → returned as-is
- `tagName: "#fragment"` → `DocumentFragment`
- `tagName: "#comment"` → comment node (text = `children[0]`)
- `ns` set → `createElementNS(ns, tagName)` (SVG/MathML), otherwise `createElement`
- `className` → `class` attribute; `style` → string goes to the `style` attribute, object is merged into `element.style`
- remaining props → set as **element properties** (not attributes), skipped when `undefined`
- `children` → rendered recursively through `h`

**`h` is not exported from the package in v0.4.0** — the runtime exports only `defaultOptions`, `parseAsync`, `renderAsync`, `renderDocument` (plus types). You cannot wrap the default factory; customizing means providing your own complete `h` implementation:

```js
function customH(elemOrText) {
    if (typeof elemOrText === "string") return document.createTextNode(elemOrText);
    if (elemOrText instanceof Node) return elemOrText;

    const { ns, tagName, className, style, children, ...props } = elemOrText;

    if (tagName === "#fragment") return document.createDocumentFragment();
    if (tagName === "#comment") return document.createComment(children[0]);

    const result = ns
        ? document.createElementNS(ns, tagName)
        : document.createElement(tagName);

    if (className) result.setAttribute("class", className);
    if (typeof style === "string") result.setAttribute("style", style);
    else if (style) Object.assign(result.style, style);
    for (const [key, value] of Object.entries(props))
        if (value !== undefined) result[key] = value;

    // custom hook: mark paragraphs for CSS/tests
    if (tagName === "p") result.setAttribute("data-docx-paragraph", "true");

    children?.forEach((c) => result.appendChild(customH(c)));
    return result;
}

await renderAsync(blob, container, null, { h: customH });
```
