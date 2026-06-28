# Component Syntax in htm

## Opening Components

In htm, components are opened with `<${ComponentName}>`. The `${}` is required — without it,
the tag name is treated as a literal HTML tag name string.

```js
const Foo = ({ name }) => html`<h1>${name}</h1>`;

// Correct — evaluates Foo as a component reference
html`<${Foo} />`
html`<${Foo} name=${name}>content</${Foo}>`

// Wrong — "Foo" is a literal string tag name
html`<Foo />`        // h('Foo', null, [])
html`<Foo>hi</Foo>`  // h('Foo', null, 'hi')
```

This applies to class components, function components, and any callable that accepts
`(type, props, ...children)`.

## Closing Components

### Self-closing

```js
html`<${Foo} />`
html`<${Foo}/>`
html`<${Foo} name=${name} />`
```

No children are passed. Equivalent to `h(Foo, { name })`.

### Explicit end tag

The closing tag must use the same `<${...}>` syntax:

```js
html`<${Foo}>content</${Foo}>`
html`<${Foo} x=${1}>content</${Foo}>`
```

The closing tag `<${Foo}>` passes the component reference as the type. The closing tag
does not accept props — only the opening tag does.

### Auto-close with `<//>`

`<//>` closes the most recently opened unclosed tag:

```js
html`<${Foo}>content<//>`
html`<div>content<//>`
```

This is a htm feature not available in JSX. It works for both HTML elements and components.

## Nesting

### Nested components with explicit closing

```js
html`
  <${Outer}>
    <${Inner} />
    text between
    <${Inner} x=${1} />
  </${Outer}>
`
```

### Nested components with auto-close

```js
html`
  <${Outer}>
    <${Inner} /><//>
`
// Equivalent to:
// <${Outer}><${Inner} /></${Outer}>
```

### Mixed closing styles

```js
html`<${A}><${B}></${B}>text<//>`
// <${B}></${B}> explicitly closes B
// <//> auto-closes A
```

### Deep nesting with `<//>`

Each `<//>` closes the innermost open tag:

```js
html`<${A}><${B}><${C}><//>after C<//>after B<//>`
// Equivalent to:
// <${A}><${B}><${C}></${C}>after C</${B}>after B</${A}>
```

## Dynamic Components

Components can be referenced through variables, computed values, or imports:

```js
const components = { Header, Footer, Main };
const name = 'Header';
html`<${components[name]} />`;

// From an array
const items = [Foo, Bar, Baz];
html`<${items[0]} />`;

// Conditional
html`<${condition ? Foo : Bar} />`;
```

## Dynamic tag names (not components)

The same `<${}>` syntax works for dynamic HTML tag names:

```js
const level = 2;
const tag = `h${level}`;
html`<${tag}>Heading</${tag}>`;
// Produces h('h2', null, 'Heading')
```

## Components with children

```js
const Layout = ({ children }) => html`<main>${children}</main>`;

html`
  <${Layout}>
    <h1>Title</h1>
    <p>Content</p>
  </${Layout}>
`
```

Children can be text, elements, expressions, or arrays:

```js
html`
  <${List}>
    ${items.map(item => html`<${Item} data=${item} />`)}
  </${List}>
`
```

## Self-closing vs opening with no content

```js
html`<${Foo} />`       // h(Foo, null) — no children argument
html`<${Foo}></${Foo}>` // h(Foo, null) — empty children
html`<${Foo}><//>`      // h(Foo, null) — empty children
```

All three produce equivalent results for most hyperscript implementations.

## Common mistakes

### Forgetting `${}` in component tags

```js
// Wrong — literal tag name "MyComponent"
html`<MyComponent />`

// Correct
html`<${MyComponent} />`
```

### Using JSX closing syntax

```js
// Wrong in htm — </MyComponent> is parsed as literal tag close
html`<${MyComponent}></MyComponent>`

// Correct
html`<${MyComponent}></${MyComponent}>`
// Or use auto-close
html`<${MyComponent}><//>`
```

### Forgetting `<//>` on open tags

```js
// This is NOT valid — the tag is never closed
html`<${Foo}>content`

// Correct
html`<${Foo}>content<//>`
html`<${Foo}>content</${Foo}>`
```
