# Sections

Sections are the primary control structure in Mustache. They render blocks of text zero or more times based on the value of a key.

## Syntax

```
{{#key}}...{{/key}}
```

The behavior depends entirely on the type and value of `key` in the current context.

## Falsy values

If the key does not exist, or resolves to a falsy value, the block is **not rendered**:

- `null`
- `undefined`
- `false`
- `0`
- `NaN`
- `""` (empty string)
- `[]` (empty array)

```js
Mustache.render(
  '{{#show}}Visible{{/show}}',
  { show: false }
);
// "" (empty)

Mustache.render(
  '{{#count}}Has count{{/count}}',
  { count: 0 }
);
// "" (empty — 0 is falsy)
```

## Truthy scalar values

Non-falsy scalars (`true`, non-zero numbers, non-empty strings) render the block once with the current context unchanged:

```js
Mustache.render(
  '{{#active}}User is active{{/active}}',
  { active: true }
);
// "User is active"
```

## Objects as context

When the section value is an object (or non-empty string or number), the block is rendered once with the context shifted to that value:

```js
Mustache.render(
  '{{#user}}{{name}} is from {{city}}{{/user}}',
  {
    user: { name: 'Alice', city: 'Portland' }
  }
);
// "Alice is from Portland"
```

Parent context is still accessible for keys not found in the shifted context:

```js
Mustache.render(
  '{{#user}}{{name}} works at {{company}}{{/user}}',
  {
    company: 'Acme',
    user: { name: 'Alice' }
  }
);
// "Alice works at Acme"
```

## Arrays — iteration

Non-empty arrays render the block once per item, with context shifted to each item:

```js
Mustache.render(
  '{{#items}}<li>{{name}}</li>{{/items}}',
  {
    items: [
      { name: 'Apple' },
      { name: 'Banana' },
      { name: 'Cherry' }
    ]
  }
);
// "<li>Apple</li><li>Banana</li><li>Cherry</li>"
```

### Arrays of primitives

Use `{{.}}` to reference the current item:

```js
Mustache.render(
  '{{#tags}}#{{.}} {{/tags}}',
  { tags: ['js', 'css', 'html'] }
);
// "#js #css #html "
```

### Functions inside array items

When items have function properties, those functions are called with the item as `this`:

```js
Mustache.render(
  '{{#beatles}}{{name}}{{/beatles}}',
  {
    beatles: [
      { first: 'John', last: 'Lennon', name: function () { return this.first + ' ' + this.last; } },
      { first: 'Paul', last: 'McCartney', name: function () { return this.first + ' ' + this.last; } }
    ]
  }
);
// "John LennonPaul McCartney"
```

## Higher-order sections (lambdas)

When the section value is a **function**, it is treated as a higher-order section. The function is called with the current view as `this` and must return another function that receives `(text, render)`:

```js
const view = {
  name: 'Tater',
  bold: function () {
    return function (text, render) {
      return '<b>' + render(text) + '</b>';
    };
  }
};

Mustache.render('{{#bold}}Hi {{name}}.{{/bold}}', view);
// "<b>Hi Tater.</b>"
```

### Parameters

- `text` — the literal, un-rendered block text between `{{#key}}` and `{{/key}}`
- `render` — a function that renders `text` with the current context

### Common patterns

**Transform output:**

```js
uppercase: function () {
  return function (text, render) {
    return render(text).toUpperCase();
  };
}
```

**Conditional wrapping:**

```js
maybeWrap: function () {
  return function (text, render) {
    return this.shouldWrap ? '<div>' + render(text) + '</div>' : render(text);
  };
}
```

**Numeric transform:**

```js
number: function () {
  return function (text, render) {
    return +render(text);  // parse as number
  };
}
```

### Important notes

- The outer function is called with `this` = current view
- The inner function receives raw template text, not rendered output
- If the inner function returns `null` or `undefined`, nothing is output
- The `render` function uses the current context, so variables inside the block resolve correctly
