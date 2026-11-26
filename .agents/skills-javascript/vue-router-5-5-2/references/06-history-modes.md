# History Modes

`createRouter({ history, routes })` — the `history` option is required.

## HTML5 mode — `createWebHistory(base?)`

Uses `history.pushState` and the History API. Clean URLs (`/users/eduardo`). Needs server configuration so deep links and reloads return the app (see below). `base` is the base path (e.g., `'/my-app'`).

## Hash mode — `createWebHashHistory(base?)`

Uses `location.hash` — no server configuration needed, works on any static host, but URLs carry a `#` (`/#/users/eduardo`). When running from local files (`file://`), hash history ignores the base parameter; URLs always use the `#` prefix.

## Memory mode — `createMemoryHistory()`

Ignores the browser URL entirely with an internal URL stack. Used for SSR and unit tests; you control navigation with `history.push()`/`replace()`.

## Base paths

`createWebHistory('/base')` prefixes all routes with `/base`. Useful when the app is served under a subpath.

## Server configurations (HTML5 mode)

All paths must serve the same `index.html` so the client can resolve the route:

- **Apache** — `RewriteEngine` rules forwarding non-file/non-directory requests to `/`.
- **nginx** — `try_files $uri $uri/ /index.html`.
- **Node.js / Express** — use the `connect-history-api-fallback` middleware to serve `index.html` for client-side paths.
- **IIS** — `rewrite` rules for non-existing resources.
- **Caddy** — `try_files {path} /index.html`.
- **Static hosts** — Firebase (rewrite to `/index.html`), Netlify (`/*` → `/index.html` redirect or `_redirects`), Vercel (rewrites in `vercel.json`), Azure Static Web Apps (`routes.json` fallback).

## Caveat

HTML5 mode requires the server fallback; without it, reloading a deep link returns 404. If you cannot configure the server, use hash mode.
