# HTM 3.1.1 — Syntax Reference

## Tagged Template Invocation

```js
const html = htm.bind(h);
html`<tag prop=${value}>content</tag>`;
```

The bound tag function receives `(strings: TemplateStringsArray, ...values: any[])` from the JavaScript engine. It parses the static strings, interpolates dynamic values, and calls `h()` with the result.

## Element Syntax

### Opening tags

```
<div>              — named HTML element
<${Foo}>           — component (JS expression)
<div id=foo>       — unquoted attribute value (no whitespace/special chars)
<div id="foo">     — double-quoted attribute value
<div id='foo'>     — single-quoted attribute value
```

### Self-closing

```
<div />            — space before slash
<div/>             — no space before slash
```

Both forms are equivalent. The `/` must appear before `>` to trigger self-close.

### Closing tags

```
</div>             — standard closing tag (HTML element names only)
<//>               — auto-close nearest open tag (works for any tag type)
</${Foo}>          — explicit component end tag (expression re-evaluated)
```

### Boolean attributes

Bare attribute names (no `=`) always produce `true`:

```js
html`<input disabled />`;              // { disabled: true }
html`<input disabled checked />`;      // { disabled: true, checked: true }
html`<div draggable />`;               // { draggable: true }
```

## Attribute Values

### Static values

```js
html`<a href="/path" />`;      // { href: '/path' }
html`<a href=/path />`;        // { href: '/path' } (unquoted)
html`<a href="" />`;           // { href: '' } (empty string)
```

### Dynamic values

```js
html`<a href=${url} />`;       // { href: url } (direct value, no coercion)
html`<a href=${1} />`;         // { href: 1 } (number preserved, not stringified)
```

Note: dynamic prop values are passed directly to `h()` without string coercion. The hyperscript function decides how to handle them.

### Mixed static + dynamic (concatenated as strings)

```js
html`<a href="/user/${id}" />`;     // { href: '/user/42' }
html`<a href=${a}${b} />`;          // { href: '11' } (string concat)
html`<a href=${a}mid${b} />`;       // { href: '1mid2' }
html`<a href=/before/${'foo'}/>`;   // { href: '/before/foo' }
```

When static text surrounds a dynamic value in a property, all parts are concatenated as strings.

### Spread props

```js
html`<div ...${props} />`;           // Object.assign into props
html`<div a ...${props} b />`;       // { a: true, ...props, b: true }
html`<div ...${a} ...${b} />`;       // Object.assign({}, a, b)
html`<div x=1 ...${{ c: 'bar' }} />`; // { x: '1', c: 'bar' }
```

Spread (`...${...}`) merges into the props object via `Object.assign()`. Order matters — later spreads override earlier ones. The original spread object is never mutated.

## Children

### Text content

```js
html`<div>Hello</div>`;             // children: ['Hello']
html`<div>Hello World</div>`;       // children: ['Hello World']
```

### Dynamic expressions

```js
html`<div>${expr}</div>`;           // children: [expr]
html`<div>before${x}after</div>`;   // children: ['before', x, 'after']
html`<div>${null}</div>`;           // children: [null]
```

### Nested elements

```js
html`<div><span /></div>`;          // children: [h('span', null)]
html`<div><a /><b /></div>`;        // children: [h('a', null), h('b', null)]
```

### Mixed content

```js
html`<div>text<span />more</div>`;  // children: ['text', h('span', null), 'more']
```

### Whitespace trimming

Leading and trailing whitespace around text nodes is stripped (newline + surrounding whitespace):

```js
html`<div>
  Hello
</div>`;   // children: ['Hello'] — surrounding whitespace stripped
```

The regex used is `/^\s*\n\s*|\s*\n\s*$/g` — it removes leading/trailing newline with surrounding whitespace.

## Special Constructs

### HTML comments

```js
html`<div><!-- comment --></div>`;           // comment fully stripped
html`<div><!-- ${expr} --></div>`;           // dynamic content in comment stripped
html`<div><!-- multi
  line --></div>`;                            // multi-line comments stripped
```

Comments use the `<!-- ... -->` syntax. The parser tracks `--` state and exits on `-->`. Comments produce no output whatsoever.

### Multiple roots (fragments)

```js
html`<div /><span />`;   // [h('div', null), h('span', null)]
```

Multiple top-level elements return an array. Single element returns directly. Empty template returns `undefined`.

### Non-element roots

```js
html`plain text`;        // 'plain text'
html`${1}`;              // 1
html`a${1}b`;            // ['a', 1, 'b']
```

Templates with no `<` are treated as raw text/expression content.

## Component-specific syntax

### Dynamic tag names

```js
const tag = 'div';
html`<${tag} />`;        // h('div', null)

function Foo() { return html`<div />`; }
html`<${Foo} />`;        // h(Foo, null)
```

### Auto-close with `<//>`

```js
const Comp = () => html`<div />`;
html`<${Comp}><//>`;     // auto-closes <${Comp}>
html`<${Comp} prop=val><//>`;  // props applied, then auto-closed
```

`<//>` closes the most recently opened tag regardless of its name. This is essential when the component reference is a variable and you can't write `</${Comp}>`.

### Explicit component end tags

```js
html`<${Header}>content</${Header}>`;  // Header expression re-evaluated in close tag
```

The expression in the closing tag is evaluated again — it should resolve to the same component.

## Edge Cases

### Slash in tag/prop names (triggers self-close)

```js
html`<ab/ba>`;               // self-closes as <ab>, 'ba' ignored
html`<a pr/op=v>`;           // { pr: true }, self-closed, 'op=v' ignored
html`<abba pr/op=value>`;    // { pr: true }, self-closed
```

A `/` in the tag name or property name position triggers self-close of the element.

### Slash in property values

```js
html`<a href=val/ue><//>`;   // { href: 'val/ue' } — slash preserved in value
html`<a href=value/>`;       // { href: 'value' } — slash is closing marker, self-closes
html`<a href=value/ ><//>`;  // { href: 'value/' } — slash preserved, space prevents self-close
```

The `/` only triggers self-close when followed by `>` (or whitespace then `>` does NOT self-close).

### NUL characters (preserved)

```js
html`<a b="\0"></a>`;        // { b: '\0' } — NUL in attribute values
html`<a>\0</a>`;             // children: ['\0'] — NUL in text
html`<a>\0${'foo'}</a>`;     // children: ['\0', 'foo']
```

### Empty attribute name

```js
html`<a ""="foo" />`;        // { '': 'foo' } — empty string is valid prop key
```

### Hyphens in attribute names

```js
html`<a data-value custom-attr />`;  // { 'data-value': true, 'custom-attr': true }
```

### Quoted attribute values with dynamic interpolation

```js
html`<a href="before${x}after" />`;  // { href: 'before' + x + 'after' }
html`<a href="${x}" />`;             // { href: x } (quotes don't force string coercion)
```

Quotes around dynamic values don't change behavior — the value is still passed through directly.

### Property value coercion rules

- Pure dynamic values (`href=${x}`): passed as-is, no coercion
- Mixed static+dynamic (`href="/${x}"`): all parts string-concatenated
- Pure static (`href="/path"`): string literal

### Multiple root with mixed types

```js
html`<div />text<span />`;  // [h('div'), 'text', h('span')]
```

Arrays can contain elements and text mixed.
