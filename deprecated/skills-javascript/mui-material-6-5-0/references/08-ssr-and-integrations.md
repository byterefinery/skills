# 08 — SSR & Integrations

Server rendering, Next.js, useMediaQuery SSR, testing, localization, routing, bundle size, CSP.

## Contents

1. [Server rendering with Emotion](#server-rendering)
2. [Next.js App Router](#nextjs-app-router)
3. [Next.js Pages Router](#nextjs-pages-router)
4. [useMediaQuery and SSR](#usemediaquery-and-ssr)
5. [Testing](#testing)
6. [Localization](#localization)
7. [Routing libraries](#routing-libraries)
8. [Styled-components interop](#styled-components-interop)
9. [Minimizing bundle size](#minimizing-bundle-size)
10. [Content Security Policy](#content-security-policy)

## Server rendering

Without extracted CSS, SSR pages flicker (FOUC) while the client injects styles. The protocol: **a fresh Emotion cache per request** → render the tree under `CacheProvider` + `ThemeProvider` → extract CSS → embed `<style>` tags in `<head>` → client reuses the same cache configuration.

```js
// createEmotionCache.js — shared between server and client
import createCache from '@emotion/cache';
export default function createEmotionCache() {
  return createCache({ key: 'css' });
}
```

```jsx
// server (Express)
import createEmotionServer from '@emotion/server/create-instance';

function handleRender(req, res) {
  const cache = createEmotionCache();                 // NEW cache per request
  const { extractCriticalToChunks, constructStyleTagsFromChunks } =
    createEmotionServer(cache);

  const html = ReactDOMServer.renderToString(
    <CacheProvider value={cache}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <App />
      </ThemeProvider>
    </CacheProvider>,
  );

  const emotionCss = constructStyleTagsFromChunks(extractCriticalToChunks(html));
  res.send(renderFullPage(html, emotionCss));          // inject ${css} into <head>
}
```

```jsx
// client
const cache = createEmotionCache();                    // same key/config as server
ReactDOM.hydrateRoot(document.querySelector('#root'),
  <CacheProvider value={cache}>
    <ThemeProvider theme={theme}><CssBaseline /><App /></ThemeProvider>
  </CacheProvider>);
```

Rules:

- Never share one cache between requests (styles leak across pages).
- Server and client must use identical `key`/options and the same MUI version.
- SSR is strict about configuration — when rendering breaks, diff against a working reference implementation piece by piece.
- Reference implementation: `examples/material-ui-express-ssr` in the MUI repo.

## Next.js App Router

```bash
npm install @mui/material-nextjs @emotion/cache
```

```tsx
// app/layout.tsx
import { AppRouterCacheProvider } from '@mui/material-nextjs/v15-appRouter';
// v15-appRouter for Next 15+; use v14-appRouter / v13-appRouter etc. for older Next

export default function RootLayout(props) {
  return (
    <html lang="en">
      <body>
        <AppRouterCacheProvider>{props.children}</AppRouterCacheProvider>
      </body>
    </html>
  );
}
```

- `AppRouterCacheProvider` collects CSS on the server while Next streams HTML; it keeps styles in `<head>`.
- Custom cache options: `options={{ key: 'css' }}`; cascade layers: `options={{ enableCssLayer: true }}`.
- **Font optimization**: `next/font/google`'s `Roboto({ weight: ['300','400','500','700'], variable: '--font-roboto' })`, put `roboto.variable` on `<body>`, and in a `'use client'` theme file set `typography.fontFamily: 'var(--font-roboto)'`.
- CSS theme variables: add `cssVariables: true` to the theme; combine with `<InitColorSchemeScript attribute="class" />` + `suppressHydrationWarning` on `<html>` for flicker-free manual dark toggling.

## Next.js Pages Router

```bash
npm install @mui/material-nextjs @emotion/cache @emotion/server
```

```tsx
// pages/_document.tsx
import { DocumentHeadTags, documentGetInitialProps } from '@mui/material-nextjs/v15-pagesRouter';

export default function MyDocument(props) {
  return (
    <Html lang="en">
      <Head><DocumentHeadTags {...props} /></Head>
      <body><Main /><NextScript /></body>
    </Html>
  );
}
MyDocument.getInitialProps = async (ctx) => documentGetInitialProps(ctx);
```

```tsx
// pages/_app.tsx
import { AppCacheProvider } from '@mui/material-nextjs/v15-pagesRouter';

export default function MyApp(props) {
  return <AppCacheProvider {...props}>{/* <Head>...</Head>, page */}</AppCacheProvider>;
}
```

- Custom cache: `documentGetInitialProps(ctx, { emotionCache: createEmotionCache({ enableCssLayer: true }) })` — and pass the same cache from `_app` (create it there and pass via props) so client/server match.
- Cascade layers: `createCache({ enableCssLayer: true })` in both places.
- `plugins` option lets you collect additional SSR styles (JSS, styled-components).

## useMediaQuery and SSR

`useMediaQuery(query | (theme) => query, { noSsr, defaultMatches, ssrMatchMedia })`:

- No default theme — the callback form requires a `ThemeProvider` ancestor.
- Client-only usage: `{ noSsr: true }` skips the double render (no effect under React 18 `createRoot`).
- SSR: the server must provide a `matchMedia` implementation. Guess device from user-agent (`ua-parser-js`) or client hints, and emulate with `css-mediaquery`:

```js
const ssrMatchMedia = (query) => ({ matches: mediaQuery.match(query, { width: isMobile ? '0px' : '1024px' }) });
// via theme: MuiUseMediaQuery.defaultProps = { ssrMatchMedia }
```

- Prefer pure CSS for responsiveness first (`sx` display, `theme.breakpoints.up(...)`); JS breakpoints are a last resort (hydration trade-offs).
- `'(prefers-color-scheme: dark)'` works on the client; on SSR it always resolves to the default (false) — acceptable for dark-mode detection.

## Testing

- Test userspace behavior, not MUI internals: query `input`, `[role="textbox"]`, `getByRole`, `getByText`. Avoid snapshot tests.
- **jsdom lacks `window.matchMedia`** — polyfill with `css-mediaquery`:

```js
function createMatchMedia(width) {
  return (query) => ({
    matches: mediaQuery.match(query, { width }),
    addEventListener: () => {}, removeEventListener: () => {},
  });
}
window.matchMedia = createMatchMedia(1024);
```

- **Ripple/interactions in v6**: wrap pointer events in `act` and await: `await act(async () => { fireEvent.mouseDown(button); });` — affects all buttons, Checkbox, Chip, Radio, Switch, Tabs (v6 ripple performance change).
- Icons expose `data-testid="AddIcon"` etc. for queries.
- `unstable_createMuiStrictModeTheme()` exists to quiet StrictMode warnings in dev.

## Localization

```jsx
import { createTheme, ThemeProvider } from '@mui/material/styles';
import { frFR } from '@mui/material/locale';

const theme = createTheme({ palette: { primary: { main: '#1976d2' } } }, frFR);
```

- ~100 locales from `@mui/material/locale` (`zhCN`, `jaJP`, ...); second argument of `createTheme`.
- Localized strings cover TablePagination, Pagination, Rating labels, Stepper, etc.
- `Rating` in non-English: pass `getLabelText` (use the locale's `components.Rating.label`).
- MUI X components have their own localization APIs.

## Routing libraries

MUI doesn't depend on a router. Wire your own via the `component` prop (it accepts any component, and native/HTML props pass through):

```jsx
import { Link as RouterLink } from 'react-router-dom';
import Link from '@mui/material/Link';

<Link component={RouterLink} to="/dashboard">Dashboard</Link>
```

- Works on `Link`, `Button`, `ListItemButton`, `Tab`, `BottomNavigationAction`, `PaginationItem` (via `Pagination`'s `LinkComponent`), `Chip` (`component`), etc.
- `ListItemButton component="a" href="..."` for plain anchors.
- `Tabs` navigation: `component={RouterLink}` + `to` on each `Tab`.

## Styled-components interop

MUI can run on styled-components via `@mui/styled-engine-sc` + bundler aliasing — but **styled-components does not work with SSR** MUI apps (babel plugin limitation); use Emotion for SSR. For mixing with other CSS-in-JS or Tailwind, prefer class-based styling + cascade layers (`enableCssLayer`) over engine swapping.

## Minimizing bundle size

- Named imports from `@mui/material` tree-shake fine in modern bundlers — no special setup needed in production.
- **Dev startup**: named imports from `@mui/icons-material` can be ~6x slower than path imports. Fix with path imports (`import AddIcon from '@mui/icons-material/Add'`) or `babel-plugin-import` (Next.js ≥ 13.5 does this automatically via `optimizePackageImports`).
- Supported import depth: 1st level (`@mui/material`) and 2nd level (`@mui/material/Button`, `@mui/icons-material/Add`) only. Deeper paths are private — guard with ESLint `no-restricted-imports` patterns `@mui/*/*/*`.
- The theme `components` key is not tree-shakable; keep it lean.
- CDN usage downloads the whole library — fine for prototypes, not production.

## Content Security Policy

SSR + Emotion uses a **per-request nonce** (Base64 of a UUIDv4):

```js
header('Content-Security-Policy').set(
  `default-src 'self'; style-src 'self' 'nonce-${nonce}';`,
);
```

- Pass the nonce into the `<style>` tags rendered on the server and into the Emotion cache: `createCache({ key, nonce, prepend: true })` under `CacheProvider`.
- SPA with inline styles: enable the `style-src-attr` directive for the `style` attribute used by dynamic values.
- Dynamic `sx` values that change per render: prefer inline CSS variables via the `style` prop (see the sx dynamic-values note in [02-styling](02-styling.md)) to avoid many `<style>` insertions.
