# `@dom-expressions/babel-plugin-jsx`

The mature JSX→DOM compiler. Treats lowercase tags as HTML elements, mixed-case tags as components. Converts JSX into `template(html, flag)` constants + minimal traversal + runtime bindings. This is what Solid 1.x/2.x ship, and it is the behavior oracle the Rust compiler mirrors.

## How the output works

A static template becomes one `_$template(`<html>`, flag)` call; every render clones it (`cloneNode(true)` is dramatically faster than `document.createElement` per node) and walks it with precomputed traversal paths (`firstChild`, `nextSibling`). Only dynamic holes get `insert`/`effect`/`className`/event registrations. The example in the repo README compiles a `<tr>` table row into:

```js
const _tmpl$ = _$template(`<tr>…static skeleton…</tr>`, 16);
// per render:
const _el$ = _tmpl$.cloneNode(true),
  _el$2 = _el$.firstChild, _el$3 = _el$2.nextSibling, /* … */;
_$insert(_el$2, itemId);                    // static value: insert once
_el$4.$$click = e => select(item, e);       // delegated event
_$insert(_el$4, () => item.label);          // dynamic: effect-wrapped
_$effect(() => selected(), _v$ => _$className(_el$, itemId === _v$ ? "danger" : ""));
_$delegateEvents(["click"]);
```

The **wrapping heuristic**: JSX expressions containing function calls or property access are wrapped in reactive getters/effects; simple literals and plain variables are not. `effectWrapper` (default `effect`) names the wrapper; `staticMarker` (default `@static` comment prefix) forces the compiler to treat an expression as static — a compile-time assertion, not a reactivity primitive; only use it when you can prove the expression is non-reactive for the element's lifetime.

## Options

| Option | Type | Default | Notes |
|---|---|---|---|
| `moduleName` | `string` | **required** | runtime module to import helpers from (e.g. `"dom"`, `"dom/server"`) |
| `generate` | `"dom" \| "ssr"` | `"dom"` | output mode |
| `hydratable` | `boolean` | `false` | emit hydration markers (`pl-` ids) |
| `delegateEvents` | `boolean` | `true` | auto event delegation on camelCase |
| `wrapConditionals` | `boolean` | `true` | smart conditional detection; optimizes boolean/ternary expressions |
| `contextToCustomElements` | `boolean` | `false` | set current render context on Custom Elements and slots for Context API with Web Components |
| `builtIns` | `boolean \| string[]` | `false` | component exports to auto-import when seen in JSX |
| `effectWrapper` | `string` | `"effect"` | reactive wrapper function name |
| `staticMarker` | `string` | `"@static"` | comment prefix marking an expression static |
| `memoWrapper` | `string` | `"memo"` | memo function name |
| `validate` | `boolean` | `true` | check HTML nesting that browsers would "correct" and break DOM walks |
| `omitNestedClosingTags` | `boolean` | `false` | drop unnecessary closing tags from template output |
| `omitLastClosingTag` | `boolean` | `true` | drop trailing tag when it has no closing parents |
| `omitQuotes` | `boolean` | `true` | drop quotes around safe attribute values |
| `omitAttributeSpacing` | `boolean` | `true` | omit space before next attribute for quoted attrs; `false` for strict parsers |
| `requireImportSource` | `string \| false` | `false` | only transform files whose `@jsxImportSource` pragma matches |
| `inlineStyles` | `boolean` | `true` | inline string/`Record<string,string>` style attributes into templates; disable under strict CSP |

## Special bindings

### `ref`

`ref={variable}` assigns the element to the variable; `ref={fn}` calls `fn(element)`.

### Events (`on*`)

CamelCase `onClick` = delegated (bubbles/composed) or Level-1 `on_____` fallback. Bound value passing: `onClick={[handler, item.id]}` → `handler(item.id, e)`. Delegates are owned by render roots, removed on root disposal, and work in Shadow DOM when events are composed. Keep custom delegated events lowercase.

### Spreads (`{...props}`)

Order of independent binding updates is **not** guaranteed.

## Components and fragments

Components are just capitalized tags; dynamic props become getter accessors (remember: property access triggers — don't destructure reactive props outside computations). `props.children` may be a node, function, string, or array; non-expression children evaluate lazily on access. Fragments `<></>` compile to arrays.

## Where it's used

- Solid (via `babel-preset-solid` / `vite-plugin-solid`) — with `contextToCustomElements` and custom `moduleName`/`builtIns`.
- ko-jsx, mobx-jsx — same plugin, different runtime module.
- The Rust `@dom-expressions/compiler` mirrors its option set and pass structure; parity is enforced by a cross-mode fixture-union ratchet.
