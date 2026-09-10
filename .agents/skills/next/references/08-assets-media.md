# Assets and media — images, fonts, CSS, metadata

Image optimization, fonts, styling, and metadata conventions in Next.js 16, including the v16 image security changes.

## Contents

- [next/image](#nextimage)
- [Images config (v16 defaults)](#images-config-v16-defaults)
- [next/font](#nextfont)
- [CSS](#css)
- [Metadata](#metadata)
- [OpenGraph and icon files](#opengraph-and-icon-files)
- [sitemap and robots](#sitemap-and-robots)

## next/image

Use `<Image>` from `next/image` for all content images — it handles resizing, lazy loading, and modern formats.

```tsx
import Image from 'next/image'

export default function Page() {
  return <Image src="/assets/photo.png" alt="Photo" width={400} height={300} />
}
```

- Provide `width`/`height` (or `fill` with a relatively-positioned parent) so layout shift is avoided.
- Remote images require `images.remotePatterns` in config (the old `images.domains` is **deprecated** in 16).
- **Local images with query strings** (`/assets/p?v=1`) are blocked by default (enumeration-attack protection) — allow them explicitly with `images.localPatterns: [{ pathname: '/assets/**', search: '?v=1' }]`.
- `next/legacy/image` is deprecated — use `next/image`.
- `priority` for LCP images, `loading="lazy"|"eager"`, `quality` (coerced to the nearest value in `images.qualities`), `sizes` for responsive srcset.

## Images config (v16 defaults)

| Key | v16 default | Note |
| --- | --- | --- |
| `minimumCacheTTL` | **14400 (4h)** | was 60s; set `60` to restore frequent revalidation |
| `imageSizes` | `[16 removed]` → 32, 48, 64, 96, 128, 256, 384 | add `16` back if needed (devicePixelRatio 2 usually makes 16px irrelevant) |
| `qualities` | **`[75]`** | was all; set `[50, 75, 100]` for multiple levels |
| `maximumRedirects` | **3** | was unlimited; `0` disables |
| `dangerouslyAllowLocalIP` | `false` | local-IP optimization (SSRF) blocked; enable only for private networks with split-horizon DNS |
| `localPatterns` | — | required for local `src` with query strings |
| `remotePatterns` | — | protocol/hostname/pathname rules for remote sources |

## next/font

Built-in font optimization — self-hosting, subsetting, and CSS variables:

```tsx
// app/layout.tsx
import { Geist } from 'next/font/google'
const geist = Geist({ subsets: ['latin'], variable: '--font-geist' })
export default function RootLayout({ children }) {
  return (
    <html lang="en" className={geist.variable}>
      <body>{children}</body>
    </html>
  )
}
```

- `next/font/google` — Google fonts with `subsets`, `weight`, `style`, `display`, `variable`.
- `next/font/local` — self-hosted files (`.woff2` preferred).
- Fonts are served from the app (no third-party requests); the `variable` CSS custom property is the integration point for Tailwind etc.

## CSS

- **Global CSS**: import in the root `app/layout.tsx` (or any layout). Global stylesheets from `node_modules` are allowed in the App Router.
- **CSS Modules**: `module.css` files, imported per component, work in both server and client components.
- **CSS-in-JS** libraries (styled-components, Emotion) require the Babel/SWC compiler setup — see the css-in-js guide; many projects prefer Tailwind.
- `useLightningcss` config enables Lightning CSS (minification + modern features).
- **Sass**: `sassOptions` config; Turbopack has no tilde (`~`) import prefix (use `turbopack.resolveAlias: { '~*': '*' }` as an escape hatch); modern Sass API via sass-loader 16.

## Metadata

Two exports from layout/page files:

```tsx
export const metadata: Metadata = {
  title: 'ACME — Home',
  description: '...',
  openGraph: { images: '/og.png' },
}

export const viewport: Viewport = {
  themeColor: '#000',
  width: 'device-width',
}
```

- `metadata` and `viewport` are **separate exports** (viewport was split out in 14).
- `generateMetadata()` for dynamic values. Under Cache Components, `generateMetadata`/`generateViewport` follow the same rules as components: `use cache` for external data, or a dynamic-marker pattern for genuinely runtime-dependent metadata (you cannot wrap `generateMetadata` in `<Suspense>`).
- Title templates: `metadataBase` (required for absolute OG URLs) + `title: { template: '%s | ACME' }`.

## OpenGraph and icon files

File conventions (in `app/` or nested per route; `.jpg/.jpeg/.png/.gif` supported, plus `.ts/.tsx/.js` for generated):

| File | Purpose |
| --- | --- |
| `favicon.ico` / `icon.jpg` / `apple-icon.jpg` | Favicons |
| `opengraph-image.jpg` | OG image for social sharing |
| `twitter-image.jpg` | Twitter/X card image |
| `manifest.ts` | PWA manifest |

Generated OG images use `ImageResponse` from `next/og`. In 16 the generation function's props are **Promises** — `params` and `id` must be awaited in an `async` default export (see [01-upgrade-to-v16](01-upgrade-to-v16.md)); `generateImageMetadata` still receives sync `params`.

## sitemap and robots

- `app/sitemap.ts` — `export default function sitemap()`, optionally `generateSitemaps()` for large sites. In 16, the `id` passed from `generateSitemaps` to the sitemap function is a **Promise** — await it.
- `app/robots.ts` — returns a `robots` object (or `Response`).

Both are file conventions, not routes in the URL sense — they emit standard files at `/sitemap.xml` and `/robots.txt`.
