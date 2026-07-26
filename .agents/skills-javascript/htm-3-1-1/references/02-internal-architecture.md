# HTM 3.1.1 — Internal Architecture

## Pipeline Overview

HTM processes tagged templates in two phases:

1. **`build(statics)`** — parses static template strings into an operation list (compiled once, cached)
2. **`evaluate(h, built, fields, args)`** — executes the operation list, driving `h()` calls to produce results

```
Template Literal
    │
    ▼
build(statics)  ──►  Operation List (cached per bound function)
    │
    ▼
evaluate(h, built, values)  ──►  h() calls  ──►  Result
```

The `regular` function in `src/index.mjs` orchestrates this pipeline with caching:

```js
const CACHES = new Map();  // Map<bound-function, Map<statics, operation-list>>

const regular = function(statics) {
    let tmp = CACHES.get(this);
    if (!tmp) {
        tmp = new Map();
        CACHES.set(this, tmp);
    }
    tmp = evaluate(this, tmp.get(statics) || (tmp.set(statics, tmp = build(statics)), tmp), arguments, []);
    return tmp.length > 1 ? tmp : tmp[0];
};
```

## Operation List Format

`build()` produces an array of operations. Each operation is a type code followed by its data. The first element (`built[0]`) serves as a dynamicness bitmask during evaluation.

### Operation constants

| Constant | Value | Meaning |
|---|---|---|
| `MODE_SLASH` | 0 | After self-closing `/` (also used as `CHILD_APPEND` in MINI) |
| `MODE_TEXT` | 1 | Default — outside of tags |
| `CHILD_RECURSE` | 2 | Recursively evaluate nested operation list |
| `TAG_SET` | 3 | Set the element's tag name |
| `PROPS_ASSIGN` | 4 | Merge object into props via `Object.assign` |
| `MODE_PROP_SET` / `PROP_SET` | 5 | Set a single property `props[name] = value` |
| `MODE_PROP_APPEND` / `PROP_APPEND` | 6 | Append to property value `props[name] += value` |

### Operation encoding

Each operation in the array follows one of these patterns:

- `[TAG_SET, fieldIndex, stringValue]` — if `fieldIndex` is truthy, tag is `fields[fieldIndex-1]`; otherwise tag is `stringValue`
- `[PROPS_ASSIGN, fieldIndex, 0]` — spread `fields[fieldIndex-1]` into props
- `[PROP_SET, 0, value, propName]` — set `props[propName] = value` (static)
- `[PROP_SET, fieldIndex, 0, propName]` — set `props[propName] = fields[fieldIndex-1]` (dynamic)
- `[PROP_APPEND, 0, value, propName]` — append `value` to `props[propName]`
- `[CHILD_APPEND, 0, value]` — append static child `value`
- `[CHILD_RECURSE, 0, nestedOperationList]` — evaluate child element

The `fields` array is `arguments` from the tagged template call (statics + values).

### Dynamicness bitmask (`built[0]`)

After evaluation, `built[0]` tracks whether the element depends on dynamic values:

- Bit 0 (`1`): element has at least one dynamic (interpolated) value
- Bit 1 (`2`): a child element is dynamic

This bitmask enables the caching optimization: if `built[0] === 0`, the element is fully static and its result can be cached directly.

## Caching

### Cache structure

```js
const CACHES = new Map();
// CACHES.get(boundHtmlFunction) → Map<statics, operationList>
```

Each bound `html` function gets its own cache. `htm.bind(h1)` and `htm.bind(h2)` never share cached operation lists.

### Cache flow

1. Look up `CACHES.get(this)` — the cache for this bound function
2. Look up `cache.get(statics)` — the operation list for this template shape
3. If not cached, call `build(statics)` and store the result
4. Call `evaluate(h, built, fields, args)` to produce the result

### In-place optimization (cache invalidation)

After the first evaluation, `evaluate()` rewrites the operation list:

```js
// If child element was static (child[0] === 0):
// CHILD_RECURSE, 0, [...]  →  CHILD_APPEND, 0, precomputedResult
built[i-2] = CHILD_APPEND;   // change operation type
built[i] = tmp;              // store the result directly
```

This means:
- **First call**: full parse + recursive evaluation of children
- **Subsequent calls**: static children are replaced with pre-computed results, skipping recursion entirely
- **Dynamic children**: still recurse (bit 1 of `built[0]` is set)

### Disabling caching

Three approaches:

1. **Use `htm/mini`** — `MINI = true`, caching disabled by default, uses flat arrays
2. **Set `this[0] = 3`** in your `h()` function — marks the bound function as always dynamic, bypassing cache reuse
3. **Create fresh bound functions** — `htm.bind(h)` returns a new function with empty cache each time

## `build()` — State Machine Parser

The parser is a character-by-character state machine:

### Modes

| Mode | Value | Entered when |
|---|---|---|
| `MODE_SLASH` | 0 | After a self-closing `/` |
| `MODE_TEXT` | 1 | Default — outside of tags |
| `MODE_WHITESPACE` | 2 | After whitespace inside a tag |
| `MODE_TAGNAME` | 3 | After `<` |
| `MODE_COMMENT` | 4 | After `!--` in tag name |
| `MODE_PROP_SET` | 5 | After `=` in attribute |
| `MODE_PROP_APPEND` | 6 | After first value token in attribute |

### State variables

- `buffer` — accumulates characters for the current token (tag name, prop name, prop value, text)
- `quote` — active quote character (`"` or `'`), empty string when not in quotes
- `current` — the current operation list being built (nested via array references)
- `propName` — the property name being set (captured before `=`)
- `mode` — current parsing state

### Key transitions

- **`<` in MODE_TEXT**: commit text buffer, push new element context (`current = [0]`), enter MODE_TAGNAME
- **`>`**: commit current prop/text, return to MODE_TEXT
- **`/` followed by `>` or whitespace+`>`**: self-close, pop element context (`current = current[0]`), push `CHILD_RECURSE` or `CHILD_APPEND`
- **whitespace after tag name**: commit tag name, enter MODE_WHITESPACE
- **`=` in tag**: enter MODE_PROP_SET, capture `propName = buffer`
- **`!--` in MODE_TAGNAME**: enter MODE_COMMENT, ignore until `-->`
- **`${...}` boundary**: commit current buffer, record interpolation index, resume after value
- **`...` in MODE_WHITESPACE + field**: emit `PROPS_ASSIGN` operation

### Comment handling

The comment mode tracks the last two characters:

```js
if (buffer === '--' && char === '>') {
    mode = MODE_TEXT;
    buffer = '';
} else {
    buffer = char + buffer[0];  // keep last 2 chars
}
```

This allows multi-line comments and dynamic content within comments.

### `MINI` mode differences

When `MINI = true` (in `htm/mini`), `build()` returns a flat array `[tag, props, ...children]` instead of an operation list. No caching, no `CHILD_RECURSE`, no in-place optimization. The `evaluate()` function is bypassed entirely — `build()` directly calls `h()`.

## `evaluate()` — Operation Executor

Walks the operation list, accumulating `args = [type, props, ...children]`, then calls `h.apply(null, args)`:

### Processing rules

1. **`TAG_SET`**: set `args[0] = value` (the element type)
2. **`PROPS_ASSIGN`**: `args[1] = Object.assign(args[1] || {}, value)` (merge spread)
3. **`PROP_SET`**: `(args[1] = args[1] || {})[name] = value` (set property)
4. **`PROP_APPEND`**: `args[1][name] += (value + '')` (string-append to property)
5. **`CHILD_RECURSE`**: recursively `evaluate()` child operation list, push result to `args`
6. **`CHILD_APPEND`**: push static child value to `args`

### Nested element handling

For `CHILD_RECURSE`, the child's operation list is set as `this` for the `h()` call:

```js
tmp = h.apply(value, evaluate(h, value, fields, ['', null]));
```

This enables per-element cache lookups and the dynamicness bitmask optimization.

### In-place rewrite

After evaluating a `CHILD_RECURSE`:

```js
if (value[0]) {
    built[0] |= 2;  // mark parent as having dynamic child
} else {
    // Static child — rewrite operation in-place
    built[i-2] = CHILD_APPEND;  // change from RECURSE to APPEND
    built[i] = tmp;             // store pre-computed result
}
```

## `treeify()` — Analysis Helper

`treeify(built, fields)` converts an operation list into a human-readable tree:

```js
{
  tag: 'div',
  props: [ { id: ['hello'] }, spreadObject ],
  children: [ { tag: 'span', props: [], children: ['text'] } ]
}
```

Props are represented as an array of objects (to preserve spread ordering). Each individual prop value is an array of string parts (to represent concatenation).

Used by `babel-plugin-htm` and the test suite. Not exported in distribution builds.

## Module variants

| Entry | MINI | Caching | Description |
|---|---|---|---|
| `htm` | `false` | Yes | Full build with operation lists and caching |
| `htm/mini` | `true` | No | Flat arrays, no caching, ~50 bytes smaller |
| `htm/preact` | `false` | Yes | Pre-bound to Preact `h`, re-exports Preact core |
| `htm/preact/standalone` | `false` | Yes | Preact + HTM + hooks bundled, single import |
| `htm/react` | `false` | Yes | Pre-bound to `React.createElement` |

## Source file layout

```
src/
├── index.mjs           — main entry, caching wrapper (regular function)
├── index.d.ts          — TypeScript declarations
├── cjs.mjs             — CommonJS / global export wrapper
├── build.mjs           — build(), evaluate(), treeify()
├── constants.mjs       — MINI = false (used by main build)
├── constants-mini.mjs  — MINI = true (aliased for htm/mini build)
└── integrations/
    ├── preact/
    │   ├── index.mjs          — htm.bind(h) + re-export Preact core
    │   ├── index.d.ts         — TypeScript declarations
    │   └── standalone.mjs     — Preact + hooks + htm bundled
    └── react/
        ├── index.mjs          — htm.bind(createElement)
        └── index.d.ts         — TypeScript declarations
```

## Build system

The `microbundle` build aliases `./constants.mjs` to `./constants-mini.mjs` for the `htm/mini` variant:

```bash
microbundle src/index.mjs -o ./mini/index.js \
  --alias ./constants.mjs=./constants-mini.mjs
```

This swaps `MINI = false` to `MINI = true` at build time, selecting the flat-array code path in `build()`.
