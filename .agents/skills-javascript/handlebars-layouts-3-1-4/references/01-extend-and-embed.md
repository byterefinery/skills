# extend and embed

## extend

### Signature

```
{{#extend "partialName"}}...{{/extend}}
{{#extend "partialName" customContext}}...{{/extend}}
{{#extend "partialName" key=value other={{expr}}}}...{{/extend}}
{{#extend "partialName" customContext key=value}}...{{/extend}}
```

### Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `partialName` | String | Yes | Name of the registered partial to extend |
| `customContext` | Object | No | Custom context object merged into template data |
| `hash` | Object | No | Key-value pairs merged into template context |

### Context Merging

`extend` builds the final context via `mixin({}, this, customContext, hash)` — later sources override earlier:

1. Current context (`this`) — the rendering context at the point of `{{#extend}}`
2. `customContext` — optional object argument (second positional)
3. `hash` — `key=value` attributes on the `extend` call

```handlebars
{{!-- hash attributes override current context --}}
{{#extend "layout" title="Override Title" showNav=true}}
    {{#content "body"}}
        <p>title is now "Override Title"</p>
    {{/content}}
{{/extend}}
```

### Partial Resolution

`extend` looks up the partial in `handlebars.partials[name]`:

- If the partial is a compiled function, it is used directly
- If the partial is a string, it is compiled via `handlebars.compile()` on first use
- If the partial is `null` or `undefined`, an error is thrown: `Missing partial: 'name'`

```js
// String — compiled lazily
handlebars.registerPartial('layout', '<html>{{#block "body"}}{{/block}}</html>');

// Pre-compiled — used directly
handlebars.registerPartial('layout', handlebars.compile('<html>{{#block "body"}}{{/block}}</html>'));
```

### Stack Mechanism

When `extend` runs, the body of the `{{#extend}}` block (containing `content` helpers) is pushed onto `$$layoutStack` as a function. When the layout partial renders and hits `{{#block "name"}}`, `applyStack` is called — it shifts functions from the stack and executes them, which queues `content` actions onto `$$layoutActions`.

This means content overrides are not resolved until the layout partial actually renders a `block` helper.

### Custom Context Object

The optional second argument passes a context object. This matches Handlebars' native partial context syntax:

```handlebars
{{!-- Pass user object as context to the layout --}}
{{#extend "layout" user}}
    {{#content "body"}}
        <p>Welcome, {{name}}</p>
    {{/content}}
{{/extend}}
```

Combined with hash attributes:

```handlebars
{{#extend "layout" user title="User Page" isAdmin=true}}
    {{#content "body"}}
        <p>{{name}} is {{#if isAdmin}}admin{{else}}user{{/if}}</p>
    {{/content}}
{{/extend}}
```

## embed

### Signature

```
{{#embed "partialName"}}...{{/embed}}
{{#embed "partialName" customContext}}...{{/embed}}
{{#embed "partialName" key=value}}...{{/embed}}
```

### Parameters

Same signature as `extend`, but with critical difference: **embed resets internal state**.

### Context Reset

Before calling `extend`, `embed` creates a fresh context copy and nulls out both internal properties:

```js
var context = mixin({}, this || {});
context.$$layoutStack = null;
context.$$layoutActions = null;
```

This means:

- Block actions defined inside `embed` are scoped to the embedded partial only
- The embedded partial can define its own `block` helpers without leaking into the parent layout
- Nested `embed` calls each create their own isolated scope

### When to Use embed vs extend

Use `extend` for page-level layout inheritance. Use `embed` for component-level partials that define their own blocks:

```handlebars
{{!-- Page extends main layout --}}
{{#extend "layout"}}
    {{#content "body"}}
        {{!-- Media component is embedded — it has its own blocks --}}
        {{#embed "media"}}
            {{#content "image"}}
                <img src="photo.jpg" />
            {{/content}}
            {{#content "body"}}
                <p>Caption text</p>
            {{/content}}
        {{/embed}}

        {{!-- Another embed — isolated from the first --}}
        {{#embed "media"}}
            {{#content "image"}}
                <img src="photo2.jpg" />
            {{/content}}
            {{#content "body"}}
                <p>Another caption</p>
            {{/content}}
        {{/embed}}
    {{/content}}
{{/extend}}
```

### embed Inside Loops

`embed` works correctly inside `{{#each}}` and other iteration helpers. Each iteration gets a fresh isolated context:

```handlebars
{{#extend "layout"}}
    {{#content "body"}}
        {{#each users}}
            {{#embed "user-card" name showBanner=isActive}}
                {{#content "body"}}
                    <p>{{first}} {{last}}</p>
                {{/content}}
            {{/embed}}
        {{/each}}
    {{/content}}
{{/extend}}
```

The `name` and `showBanner=isActive` hash attributes are merged into each embedded `user-card` partial's context.

### embed and Parent Context Access

Inside `embed`, use `../` depth references to access parent context data:

```handlebars
{{#extend "layout"}}
    {{#content "body"}}
        {{#each items}}
            {{#embed "card"}}
                {{#content "body"}}
                    <p>{{../../globalVar}} — {{this.name}}</p>
                {{/content}}
            {{/embed}}
        {{/each}}
    {{/content}}
{{/extend}}
```
