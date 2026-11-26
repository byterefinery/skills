# Styling and selectors

## Style

Style follows CSS conventions as closely as possible — properties usually share names and behaviour with their CSS namesakes, plus Cytoscape-specific extras. **CSS specificity rules are completely ignored: for a given property on a given element, the last matching selector wins.**

### Formats

The `style` init option (or `cy.style()`) accepts three formats:

**Plain JSON** (most common):

```js
style: [
  { selector: 'node', style: { 'background-color': 'red' } }
]
```

**String** (e.g. loaded from a server) — trailing semicolons on every property except the last are **mandatory**; parsing fails without them:

```js
style: 'node { background-color: green; }'
```

**Function** (stylesheet builder):

```js
style: cytoscape.stylesheet()
  .selector('node')
    .style({ 'background-color': 'blue' })
```

`css` can be used in place of `style` (`.selector(...).css(...)` or `{ selector: ..., css: ... }`).

### Function values

A style property value can be a function, evaluated per element:

```js
style: {
  selector: 'node',
  style: {
    'background-color': function( ele ){ return ele.data('bg') }
    // equivalent to: 'background-color': 'data(bg)'
  }
}
```

Caveats: function values may be expensive (memoize them); a stylesheet with function values cannot be serialised to JSON; the function must not read other style values and must not mutate element or graph state — depend only on `ele.data()`, `ele.scratch()`, `cy.data()`, `cy.scratch()`.

## Selectors

Selectors work like CSS selectors on DOM elements, but over graph element collections. Wherever a selector is accepted, a filter function may be used instead.

- **Group** — `node`, `edge`, `*`
- **Class** — `.foo`
- **ID** — `#foo` (same as `[id = 'foo']`)
- **Data** — `[foo]` (defined, i.e. not `undefined`; `null` counts as defined), `[^foo]` (not defined), `[?foo]` (truthy), `[!foo]` (falsey), `[foo = 'bar']`, `[foo != 2]`, `[num > 2]`, `[num >= 2]`, `[num < 2]`, `[num <= 2]`
- **Comma** joins selectors (logical OR): `cy.elements('node#j, edge[source = "j"]')`
- **Compound** (adjacency): e.g. `$node -> node` edge selectors, `$node node` compound selectors — powerful but expensive (traversals required)
- **Dot-notation** into nested data: `node[name.first = "Jerry"]`, `node[labels.0 = "Person"]`

Rules and traps:

- String values must be quoted: `node[name = "Jerry"]` works, `node[name = Jerry]` does not.
- Special characters in IDs/field names need escaping: `#some\$funky\@id`. Characters that need escaping include `( ^ $ \ / ( ) | ? + * [ ] { } , . )`. Prefer alphanumeric IDs, or a data selector (`[id = "some$funky@id"]`) when you must use special characters.
- `cy.$('#id')` (single ID selector) is optimised to use the ID lookup table; `cy.getElementById('id')` is still the fastest by-ID access.
