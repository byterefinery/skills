# Caching in htm

## How caching works

htm caches the parsed template structure for each unique template string. When the same
template is used again, htm returns the same result object reference (for static templates).

```js
const a = html`<div>static</div>`;
const b = html`<div>static</div>`;
a === b;  // true — same cached object
```

This optimization means:
- Static templates are parsed only once
- Identical static templates share the same result object
- Dynamic values still cause fresh evaluation

## When caching applies

Caching applies to **fully static** subtrees — templates with no `${}` interpolations:

```js
// Cached — no dynamic values
html`<div>hello</div>`
html`<div class=foo></div>`

// Not cached — has dynamic values
html`<div>${name}</div>`
html`<div class=${cls}></div>`
```

## Cache scope

Each `htm.bind(h)` call creates an independent cache. Templates are not shared across
different bindings:

```js
const html1 = htm.bind(h1);
const html2 = htm.bind(h2);

html1`<div>a</div>` === html1`<div>a</div>`;  // true — same cache
html1`<div>a</div>` === html2`<div>a</div>`;  // false — different caches
```

## Staticness bits (`this[0]`)

When htm calls your `h()` function, `this[0]` contains a 2-bit flag describing the
dynamic-ness of the current element:

| `this[0]` | Props | Children |
|-----------|-------|----------|
| `0` | static | all static |
| `1` | dynamic | all static |
| `2` | static | some dynamic |
| `3` | dynamic | some dynamic |

You can read these bits to optimize your h function:

```js
function h(type, props, ...children) {
  const bits = this[0];
  if (bits === 0) {
    // Fully static — can use fast path or caching
  }
  return { type, props, children };
}
```

## Forcing static treatment

Modify `this[0]` to force a subtree to be treated as static (enabling caching):

```js
function h(type, props, ...children) {
  if (props['@static']) {
    this[0] &= ~3;  // clear both bits → treat as static
  }
  return { type, props, children };
}

// Now this will be cached:
const x = () => html`<div @static>${dynamicValue}</div>`;
x() === x();  // true
```

## Disabling caching entirely

Three options:

### 1. Use `htm/mini`

htm/mini is a smaller build (~450 bytes) that disables caching by default:

```js
import htm from 'htm/mini';
const html = htm.bind(h);
```

### 2. Set `this[0] = 3` in h function

```js
function h(type, props, ...children) {
  this[0] = 3;  // mark everything as dynamic
  return { type, props, children };
}
```

### 3. Copy nodes in h function

```js
function h(type, props, ...children) {
  return { type, props: { ...props }, children: [...children] };
}
```

## Caching with dynamic children

When a template has dynamic children, the parent is not cached but static children
within it may still be reused:

```js
html`<div>${dynamic}<span>static</span></div>`
// The <span>static</span> part can be cached
// The <div> wrapper is re-evaluated each time
```

After first evaluation, htm rewrites the operation list in-place: dynamic child references
become direct value references (`CHILD_RECURSE` → `CHILD_APPEND`), optimizing subsequent
evaluations.

## Caching implications

### Benefits
- Zero re-parsing for static templates
- Object identity for static subtrees (useful for memoization)
- Reduced memory for repeated template usage

### Pitfalls
- **Mutating return values**: If your `h()` function mutates the returned object, cached
  references will share the mutation. Always return new objects or use htm/mini.
- **Unexpected identity**: `a === b` for identical static templates. If your code relies
  on object identity for uniqueness, this will break.
- **Memory**: Cached templates stay in memory for the lifetime of the binding.

## htm vs htm/mini comparison

| Feature | htm | htm/mini |
|---------|-----|----------|
| Size | ~600 bytes | ~450 bytes |
| Caching | Yes | No |
| Staticness bits | Yes | No |
| `this` context | Operation list | Same |
| In-place optimization | Yes | No |
