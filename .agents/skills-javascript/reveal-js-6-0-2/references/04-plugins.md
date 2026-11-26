# Plugins

Bundled with reveal.js 6.0.2 (built files in `dist/plugin/`, npm subpath exports in `package.json`):

| Plugin | Global | npm import | Purpose |
|---|---|---|---|
| highlight | `RevealHighlight` | `reveal.js/plugin/highlight` | Code syntax highlighting via highlight.js; provides `data-line-numbers` stepping. Ships `reveal.js/plugin/highlight/monokai.css` for colors |
| markdown | `RevealMarkdown` | `reveal.js/plugin/markdown` | Inline (data-markdown + script template) and external Markdown slides |
| math | `RevealMath` with factory methods `.KaTeX`, `.MathJax2`, `.MathJax3`, `.MathJax4` | `reveal.js/plugin/math` | LaTeX typesetting; pick one engine factory, e.g. `plugins: [RevealMath.KaTeX]` |
| notes | `RevealNotes` | `reveal.js/plugin/notes` | Speaker notes and the speaker view (S key); opens `speaker-view.html` in a separate window |
| search | `RevealSearch` | `reveal.js/plugin/search` | In-deck text search |
| zoom | `RevealZoom` | `reveal.js/plugin/zoom` | Alt+click (Ctrl+click on Linux) zooms towards any element; click again to zoom out |

## Registering plugins

- `Reveal.initialize({ plugins: [ ... ] })` — entries are plugin objects or factory functions
- Script tags: each plugin script exposes its global; load `dist/reveal.js` first, then plugin scripts, then call `initialize`
- Programmatic: `Reveal.registerPlugin(plugin)` — reveal.js waits for all registered plugins to initialize before it is ready, as long as they are registered before `Reveal.initialize()` is called
- Introspection: `Reveal.hasPlugin(id)`, `Reveal.getPlugin(id)`, `Reveal.getPlugins()`

## Plugin interface

```ts
interface RevealPlugin {
  id: string;
  init?(reveal: RevealApi): void | Promise<void>;
  destroy?(): void;
}
```

Plugin factories (e.g. `RevealMath.KaTeX`) return a `RevealPlugin`.

## highlight config

`highlight: { highlightOnLoad?, escapeHTML?, beforeHighlight? }`

## math engines

- `katex` config: `local` (local script path), `version`, `delimiters` (`{ left, right, display }` arrays), `ignoredTags`
- `mathjax2` config: `mathjax` (script URL), `config`, `tex2jax` (e.g. `inlineMath`, `skipTags`)
- `mathjax3` config: `mathjax`, `tex` (`inlineMath`), `options` (`skipHtmlTags`)
- `mathjax4` config: `mathjax`, `tex` (`inlineMath`, `displayMath`, `macros`), `options`, `startup`, `output`

## Legacy script dependencies

`dependencies: [{ src, async?, callback?, condition? }]` loads external scripts at init (the pre-plugin mechanism). Prefer the `plugins` array for new decks.
