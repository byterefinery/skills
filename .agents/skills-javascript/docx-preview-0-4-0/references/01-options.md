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
