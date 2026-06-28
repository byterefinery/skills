# Route Matching

## Declaring Routes

Routes are declared on `<template>` elements using the `x-route` directive:

```html
<div x-data="app">
  <template x-route="/"></template>
  <template x-route="/about"></template>
  <template x-route="/users/:id"></template>
  <template x-route="notfound"></template>
</div>
```

Routes can also be added programmatically via `PineconeRouter.add()`.

## Segment Types

### Literal

Matches an exact path segment.

```
/about        → matches /about
/users/list   → matches /users/list
```

### Named (`:name`)

Captures a single path segment into a named parameter.

```
/users/:id        → /users/42        → { id: "42" }
/books/:genre/:title → /books/fiction/dune → { genre: "fiction", title: "dune" }
```

### Optional (`:name?`)

Captures a segment if present; matches without it.

```
/profile/:name?   → /profile          → { name: undefined }
/profile/:name?   → /profile/john     → { name: "john" }
```

### Rest (`:name+`)

Captures one or more remaining segments as a single string (slashes included).

```
/files/:path+   → /files/docs/report.pdf      → { path: "docs/report.pdf" }
/files/:path+   → /files/a/b/c                → { path: "a/b/c" }
/files/:path+   → /files                      → no match (requires at least one segment)
```

### Wildcard (`:name*`)

Captures zero or more remaining segments.

```
/files/:path*   → /files                    → { path: undefined }
/files/:path*   → /files/docs               → { path: "docs" }
/files/:path*   → /files/docs/report.pdf    → { path: "docs/report.pdf" }
```

### Suffix

Matches a segment with a required file extension.

```
/movies/:title.mp4   → /movies/avatar.mp4   → { title: "avatar" }
/movies/:title.mp4   → /movies/avatar.avi   → no match
```

### Suffix Pattern

Matches a segment with one of several allowed extensions (regex alternation).

```
/movies/:title.(mp4|mov)   → /movies/avatar.mp4   → { title: "avatar" }
/movies/:title.(mp4|mov)   → /movies/avatar.mov   → { title: "avatar" }
/movies/:title.(mp4|mov)   → /movies/avatar.avi   → no match
```

## Matching Rules

- **Trailing slashes are normalized** — `/about` and `/about/` match the same route
- **Matching is case-insensitive** — `/About` matches `/about`
- **First match wins** — routes are checked in insertion order; more specific routes should be declared before general ones
- **Empty path defaults to `/`** — if the path resolves to empty string, it becomes `/`

## Accessing Params

Three ways to access route parameters:

```html
<!-- 1. Magic helper in Alpine templates -->
<span x-text="$params.name"></span>

<!-- 2. Context parameter in handlers -->
<script>
  function handler(context) {
    console.log(context.params.name)
  }
</script>

<!-- 3. Global context from JavaScript -->
<script>
  console.log(PineconeRouter.context.params.name)
  // or window.PineconeRouter.context.params.name
</script>
```

## Named Routes

Add an optional name to a route using the `x-route:name` value syntax:

```html
<template x-route:name="/test"></template>
```

Or programmatically:

```js
PineconeRouter.add('/test', { name: 'myRoute' })
```

Access the name inside handlers:

```js
function handler(context) {
  console.log(context.route.name) // "myRoute"
}
```

If no name is supplied, the route's path is used as the name. Names don't have to be unique.

## notfound Route

`notfound` is a reserved route name. A default `notfound` route is created on initialization that logs an error to console. Override it by declaring:

```html
<template x-route="notfound" x-template="/404.html"></template>
```

`notfound` is the only route that can be re-added without throwing a duplicate error.
