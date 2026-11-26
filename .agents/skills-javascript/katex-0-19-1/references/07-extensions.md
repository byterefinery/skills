# Extensions and Libraries

From `docs/libs.md` (v0.19.1).

## KaTeX-provided extensions

| Extension | What it does |
|---|---|
| [Auto-render](https://katex.org/docs/autorender.html) | Automatically renders all of the math inside text (`renderMathInElement`) |
| [Copy-tex](https://github.com/KaTeX/KaTeX/tree/main/contrib/copy-tex) | When selecting and copying KaTeX-rendered elements, copies their LaTeX source to the clipboard. No CSS file since v0.16 — remove any `copy-tex.css` import or `<link>`. |
| [`math/tex` Custom Script Type](https://github.com/KaTeX/KaTeX/tree/main/contrib/mathtex-script-type) | Automatically displays LaTeX math inside `<script>` tags with `type="math/tex"` |
| [mhchem](https://github.com/KaTeX/KaTeX/tree/main/contrib/mhchem) | Write beautiful chemical equations easily (`\ce`, `\pu`); see 03-mhchem.md |

All five extensions (including render-a11y-string) are exported via package.json `exports` as `katex/contrib/<name>` for both `require` and `import`, plus `.` (core) with a `./*` wildcard fallback.

## Third-party libraries

**AsciiMath** — convert AsciiMath to TeX first, then call KaTeX: [asciimath2tex](https://github.com/christianp/asciimath2tex).

**Android** — [KaTeXView](https://github.com/judemanutd/KaTeXView): Android library using Khan Academy KaTeX for TeX math rendering.

**Angular2+** — [ng-katex](https://github.com/garciparedes/ng-katex): Angular module for math expressions with TeX syntax.

**Canvas** — [canvas-latex](https://github.com/CurriculumAssociates/canvas-latex): renders math on HTML5 canvas; supports CreateJS and PIXI.

**iOS** — [KaTeX-iOS](https://github.com/ianarawjo/KaTeX-iOS): UIView rendering TeX with KaTeX; [KatexUtils](https://cocoapods.org/pods/KatexUtils): CocoaPods solution for newer iOS versions.

**Jekyll** — [JekTex](https://github.com/yagarea/jektex): fast, highly configurable Jekyll plugin for GitHub Pages-compatible math.

**React** — [react-latex](https://github.com/zzish/react-latex) (KaTeX-based component), [react-katex](https://github.com/talyssonoc/react-katex).

**Ruby** — [katex-ruby](https://github.com/glebm/katex-ruby): server-side rendering for Rails, Hanami, and Sprockets apps.

**Rust** — [katex-rs](https://github.com/xu-cheng/katex-rs): Rust bindings for server-side rendering.

**Sphinx** — [sphinxcontrib-katex](https://github.com/hagenw/sphinxcontrib-katex): Sphinx extension to (pre-)render math with KaTeX.

**Vue** — [vue-katex](https://github.com/lucpotage/vue-katex): Vue plugin for TeX expressions.

**Web Components** — [katex-element](https://github.com/georges-gomes/katex-element) (framework-independent `<katex-element>`), [katex-expression](https://github.com/navsgh/katex-expression) (Stencil-based).

**WeChat Mini Program** — [@rojer/katex-mini](https://github.com/rojer95/katex-mini).

## Demo page

The repo's `static/` directory is a live test page (published as `https://katex.org/#demo`): a textarea of TeX input plus an options panel controlling `displayMode`, `leqno`, `fleqn`, `throwOnError`, `strict` (error/warn/ignore), `output` (htmlAndMathml/html/mathml), `trust`, and `macros` (JSON textarea, default `{ "\\f": "#1f(#2)" }`), with context text before and after the render target. Rendering is a direct `katex.render(input, mathElement, options)` call; errors are caught and shown in an `aria-live` alert area. Useful as a reference for wiring any option set to a live preview, and for sharing permalinks (options + code are encoded in the `?data=` query parameter).
