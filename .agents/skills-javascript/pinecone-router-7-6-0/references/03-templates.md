# Templates

## Inline Templates

Add an empty `x-template` attribute to render the template's children when the route matches. Content is inserted after the `<template>` tag (same behavior as `x-if`).

```html
<template x-route="/" x-template>
  <h1>Home</h1>
  <p>Multiple children work too</p>
</template>
```

## External Templates

Specify one or more URLs to fetch HTML content from:

```html
<!-- Single template -->
<template x-route="/" x-template="/views/home.html"></template>

<!-- Multiple templates -->
<template x-route="/dashboard" x-template="['/views/header.html', '/views/body.html']"></template>
```

Templates are fetched with `fetch()`, cached in memory, and inserted into the DOM after the corresponding `<template>` tag. Cache is cleared on browser page reload.

## Modifiers

### `.target.id`

Render the template inside a specific element by ID instead of after the template tag:

```html
<template x-route="/profile/:id" x-template.target.app="/profile.html"></template>

<div id="app"></div>
```

Set a default target globally:

```js
PineconeRouter.settings({ targetID: 'app' })
```

### `.preload`

Fetch templates at `low` priority after the first page load, without waiting for the route to match:

```html
<template x-route="notfound" x-template.preload="/404.html"></template>
```

Enable preloading globally:

```js
PineconeRouter.settings({ preload: true })
```

### `.interpolate`

Replace named route parameters in template URLs at render time:

```html
<template x-route="/dynamic/:name" x-template.interpolate="/api/:name.html"></template>
```

On `/dynamic/foo`, this fetches `/api/foo.html`. On `/dynamic/bar`, it fetches `/api/bar.html`.

> `.preload` and `.interpolate` cannot be combined since preloaded URLs can't depend on route params.

### Combining modifiers

```html
<template x-route="/page" x-template.preload.target.app="/page.html"></template>
```

## Embedded Scripts

Templates can contain `<script>` elements that execute when the route is matched:

```html
<!-- /template.html -->
<div x-data="hello">
  <h1 x-text="message"></h1>
</div>
<script>
  Alpine.data('hello', () => ({
    message: 'Hello world',
    init() {
      console.log('Component initialized')
    },
  }))
</script>
```

### Template re-rendering behavior

Templates do **not** re-render when params change on the same route. `init()` runs only once until the user navigates away and returns. For reactive param changes, use `x-effect` or `$watch`:

```html
<div x-data="content" x-effect="loadData"></div>

<script>
  Alpine.data('content', () => ({
    loading: false,
    data: null,
    async loadData() {
      this.loading = true
      const res = await fetch(`/api/${this.$params.slug}.json`)
      this.data = await res.json()
      this.loading = false
    },
  }))
</script>
```

## `x-run` Directive

Control when embedded scripts execute.

### `x-run.once`

Run the script only once per route visit:

```html
<script x-run.once>
  console.log('Runs once per route visit')
</script>
```

Add an `id` to make it once globally (across all routes):

```html
<script x-run.once id="init-analytics">
  // Runs once ever, even if included in multiple templates
</script>
```

### `x-run:on="condition"`

Only run when the Alpine expression evaluates to true:

```html
<script x-run:on="$router.context.route === '/profile'">
  // Only runs on /profile route
</script>
```

The expression has access to the Alpine data stack of both the template element and the target element.

### Combined

```html
<script x-run.once:on="isAdmin">
  // Runs once if isAdmin is true
</script>
```

## Template Lifecycle

1. Route matches → handlers run
2. If route has templates, `pinecone:start` fires
3. External templates are fetched (or served from cache)
4. Content is cloned and Alpine scope is applied
5. Scripts are evaluated (respecting `x-run` directives)
6. Content is inserted into DOM via `Alpine.mutateDom()`
7. `Alpine.initTree()` runs on each clone
8. `pinecone:end` fires after all templates render

On route change away, `Alpine.destroyTree()` runs on each clone and elements are removed.

## Fetch Errors

When a template fetch fails, a `pinecone:fetch-error` event is dispatched to `document` with `detail: { error, url }`. The template renders empty content and loading continues.
