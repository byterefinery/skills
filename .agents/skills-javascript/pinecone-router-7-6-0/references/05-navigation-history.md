# Navigation History

## Overview

Pinecone Router maintains its own navigation history independent of the browser's `history` API. It tracks all visited paths, excludes duplicates and redirects, and provides programmatic back/forward navigation.

## Accessing History

```html
<!-- Magic helper in Alpine templates -->
<button @click="$history.back()">Back</button>
<button x-show="$history.canGoBack()">Has history</button>

<!-- From JavaScript -->
<script>
  PineconeRouter.history.back()
  PineconeRouter.history.entries // array of paths
  PineconeRouter.history.index   // current position
</script>
```

## API

| Method | Description |
|---|---|
| `$history.back()` | Navigate to previous entry |
| `$history.forward()` | Navigate to next entry |
| `$history.canGoBack()` | Returns `true` if back is possible |
| `$history.canGoForward()` | Returns `true` if forward is possible |
| `$history.to(index)` | Navigate to a specific history index |
| `$history.entries` | Array of all visited paths |
| `$history.index` | Current position in the entries array |

## History Behavior

### Duplicate suppression

Navigating to the same path while already on it does not create a new entry:

```
On /home → click link to /home → history unchanged
```

### Redirect exclusion

If a handler redirects during navigation, the intermediate path is not added to history. Only the final destination is recorded:

```
On /home → visit /profile/old (handler redirects to /profile/new)
History: ['/home', '/profile/new']  (not /profile/old)
```

### Branch trimming

If you go back in history then navigate to a new path, forward entries are discarded:

```
History: ['/a', '/b', '/c'], index: 2
→ back() → index: 1
→ navigate('/d') → History: ['/a', '/b', '/d'], index: 2
```

### Browser integration

- On normal navigation, `history.pushState()` is called (unless `pushState: false`)
- On `popstate` (browser back/forward), the router navigates to the URL path
- On first page load, the path is registered in history without calling `pushState`

## UI Patterns

### Back/Forward buttons with disabled state

```html
<button @click="$history.back()" :disabled="!$history.canGoBack()">
  ← Back
</button>
<button @click="$history.forward()" :disabled="!$history.canGoForward()">
  Forward →
</button>
```

### History breadcrumb

```html
<template x-for="(entry, i) in $history.entries" :key="i">
  <span :class="{ 'font-bold': i === $history.index }" x-text="entry"></span>
  <span x-show="i < $history.entries.length - 1"> / </span>
</template>
```

## pushState Setting

Set `pushState: false` to disable `history.pushState()` calls. The URL won't change on navigation, but Pinecone Router's internal history still tracks paths:

```js
PineconeRouter.settings({ pushState: false })
```

This is useful for embedded applications or if you manage browser history yourself.
