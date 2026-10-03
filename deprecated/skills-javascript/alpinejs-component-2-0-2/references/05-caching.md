# Caching Reference

## Overview

The plugin maintains three bounded in-memory caches to avoid repeated DOM queries, network requests, and stylesheet compilation. All caches use a Map with a maximum entry count; when the limit is exceeded, the oldest entry is evicted (FIFO).

## Cache system

### Bounded cache implementation

```js
function createBoundedCache(limit = 100) {
  const cache = new Map()
  cache.maxEntries = limit
  return cache
}

function setBoundedCacheEntry(cache, key, value) {
  cache.set(key, value)
  while (cache.size > cache.maxEntries) {
    const oldestKey = cache.keys().next().value
    cache.delete(oldestKey)
  }
}
```

- Caches are standard `Map` instances with a `maxEntries` property
- On insert, if size exceeds limit, the oldest key (first inserted) is deleted
- Eviction is FIFO — no LRU tracking

---

## Template fragment cache

**Limit:** 200 entries  
**Key:** Template id (trimmed string)  
**Value:** `DocumentFragment` (cloned from `<template>.innerHTML`)

### Behavior

1. On `x-component="'template-id'"`, the cache is checked first
2. If not cached, the `<template>` element is looked up by `id` in the document
3. Its `innerHTML` is parsed into a `DocumentFragment` and stored
4. On subsequent renders, the cached fragment is cloned via `cloneNode(true)`

### Miss handling

If no `<template id="...">` exists in the document, a console warning is logged and `null` is returned. Nothing is cached for misses.

### Memory notes

Cached fragments are `DocumentFragment` objects holding cloned DOM nodes. For large templates, this adds to memory usage. The 200-entry limit bounds total impact.

---

## Remote template cache

**Limit:** 200 entries  
**Key:** Normalized URL (absolute href)  
**Value:** Promise resolving to HTML string

### Behavior

1. On `x-component.url="'/path.html'"`, the URL is resolved to an absolute href
2. The cache is checked for an existing promise
3. If not cached, a `fetch()` promise is created and stored immediately
4. The HTML text is awaited from the cached promise
5. On success, the HTML string is parsed into a fragment and cloned

### Shared promises

Multiple concurrent requests for the same URL share the same promise. The fetch executes once; all awaiters receive the same result.

### Failed fetch eviction

If a fetch fails (network error, non-OK status), the cache entry is deleted:

```js
catch (fetchError) {
  remoteTemplateCache.delete(normalizedUrl)
  throw fetchError
}
```

This allows retries to trigger fresh fetches. Successful responses stay cached.

### Non-OK responses

Responses with non-2xx status throw: `Request failed (<status>) for <url>`. The cache entry is removed.

---

## Adopted stylesheet cache

**Limit:** 100 entries  
**Key:** Sorted style target list (comma-joined)  
**Value:** `CSSStyleSheet` instance

### Behavior

1. Style targets are normalized: trimmed, deduplicated, sorted alphabetically
2. The sorted list is joined with `,` to form the cache key
3. If not cached, document stylesheets are collected, processed, and compiled
4. A new `CSSStyleSheet` is created and populated via `replaceSync()`
5. The stylesheet is cached and assigned to `shadowRoot.adoptedStyleSheets`

### Key normalization examples

| Input | Cache key |
|---|---|
| `"card,typography"` | `"card,typography"` |
| `"typography, card"` | `"card,typography"` |
| `"card, card"` | `"card"` |
| `"global"` | `"global"` |

Sorting ensures that `x-component-styles="a,b"` and `x-component-styles="b,a"` hit the same cache entry.

---

## Cache limits summary

| Cache | Limit | Key | Value |
|---|---|---|---|
| Template fragments | 200 | Template id | `DocumentFragment` |
| Remote responses | 200 | Normalized URL | Promise\<string\> |
| Adopted stylesheets | 100 | Sorted target list | `CSSStyleSheet` |

## Eviction behavior

When a cache exceeds its limit, the oldest entry (first inserted) is evicted. There is no LRU tracking — entries are evicted in insertion order.

For high-traffic pages with many unique templates or URLs, consider:
- Keeping template count within cache limits
- Reusing template ids across components
- Using consistent style target lists to maximize stylesheet cache hits

## Gotchas

- **Caches are in-memory only** — no `localStorage`, `sessionStorage`, or `Cache API`. A page reload clears all caches.
- **Remote cache stores promises, not results** — the cached value is the fetch promise itself. If the promise settles (success or failure), it stays cached (except on failure, when it's evicted).
- **No cache invalidation API** — the plugin does not expose methods to manually clear or invalidate cache entries. Caches are managed internally.
- **Template DOM changes are not reflected** — if a `<template>` element's content changes after the first render, the cached fragment is stale. The cache is keyed by id, not by content hash.
- **Stylesheet cache key is sorted** — `x-component-styles="a,b"` and `x-component-styles="b,a"` produce the same cache key. This is intentional for deduplication.
