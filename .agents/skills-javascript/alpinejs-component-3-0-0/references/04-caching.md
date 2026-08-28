# Caching

The plugin keeps two bounded in-memory caches, module-level and shared across all component instances:

- **Template fragments by template id** — limit 200
- **Remote fetch promises by normalized URL** — limit 200

## Behavior

- **LRU eviction** — reading an entry counts as use, so when a cache is full the least recently read entry is evicted.
- **Parse once, render many** — on-page templates are parsed into a fragment once and cloned per render; remote responses are parsed once and the *promise* is cached, so overlapping renders of the same URL share a single request.
- **Failed fetches are evicted** — a promise that rejects is dropped (only if it is still the cached one), so the next render of that URL retries the request. Successful fragments stay cached for the document's lifetime, up to the 200-entry bound.
- **Memory trade-off** — a page cycling through many large remote templates keeps up to 200 parsed trees in memory.
- **No invalidation** — nothing else clears the caches. If you mutate the content of an on-page `<template id>` after its first render, the stale cached fragment keeps being served; re-parse only happens on page reload.
