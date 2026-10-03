# Assets — Images, Fonts, CSS

## next/image

Use `next/image` instead of `<img>` for optimization (proper sizing, lazy loading, modern formats, CLS prevention).

```tsx
import Image from 'next/image'

<Image src="/hero.jpg" alt="..." width={1920} height={1080} priority />
<Image src="/hero.jpg" alt="..." fill sizes="(max-width: 768px) 100vw, 33vw" />
```

- **Static imports** (`import logo from '@/assets/logo.png'`) are auto-optimized with no config; relative imports are resolved at build time.
- **Remote images** require config (15 uses `remotePatterns`; the old `domains` option is gone). `remotePatterns` accepts objects or `new URL('https://example.com/account/**')` shorthands:

```js
const nextConfig = {
  images: {
    remotePatterns: [
      { protocol: 'https', hostname: 'images.example.com', pathname: '/avatars/**' },
    ],
    localPatterns: [{ pathname: '/uploads/**' }],  // allow local paths, block others
    // loader: imgix or a custom loaderFile for CDNs
    // deviceSizes / imageSizes to tune breakpoints
    // qualities to restrict the ?q= values
    // minimumCacheTTL for CDN caches
    // unoptimized: true to skip optimization entirely
  },
}
```

- `fill` + `sizes` for responsive cover images; `priority` for above-the-fold (disables lazy loading); `placeholder="blur"` + `blurDataURL` for blur-up; `loading="lazy"` (default) / `"eager"`.
- SVGs are not raster-optimized; `unoptimized` renders a plain tag.
- A relative `src` that bypasses the file system (query strings on local images) is blocked by default — allow it via `localPatterns` or use `unoptimized`.

## next/font

Self-hosts fonts automatically (zero layout shift, local files, no external requests). The legacy `@next/font` package was **removed in 15** — import from `next/font`.

```tsx
// next/font/google — hundreds of Google fonts, no download step
import { Inter } from 'next/font/google'
const inter = Inter({ subsets: ['latin'], display: 'swap', variable: '--font-inter' })

// next/font/local — your own files
import { Geist } from 'next/font/local'
const geist = Geist({ src: './fonts/geist.woff2', weight: '400', display: 'swap' })
```

- Apply via the returned `className` or CSS variable: `<body className={inter.variable}>` then `font-family: var(--font-inter)`.
- `display: 'swap'` (default) — show fallback font first, swap when loaded.
- `sizeAdjust` corrects metric differences when swapping between similar fonts; `weight`/`style`/`subsets` narrow what's bundled.
- Define variable fonts once and reuse the `--font-*` variable across the design system.

## CSS

- **Global CSS** can be imported in the **root layout** (`app/layout.tsx`) or, in the Pages Router, in `_app.js`. Importing global CSS anywhere else errors.
- **CSS Modules** (`.module.css`) work in any component; class names are scoped.
- **Tailwind CSS** — the default scaffold; 15 works with both v3 and v4 (v4 uses the `@tailwindcss/postcss` plugin, no config file needed).
- **Sass/Less** — supported out of the box (`.scss`/`.less`); `sassOptions` config for custom behavior.
- **CSS-in-JS** — experimental support in the App Router (15); prefer CSS Modules/Tailwind for stable behavior.
- `@layer` rules are supported; use them to keep vendor CSS below your overrides.
- Keep critical above-the-fold styles in global CSS in the root layout to avoid FOUC.

## Public folder and static assets

- `public/` files are served at the root path as-is (`public/images/logo.png` → `/images/logo.png`); no optimization, no bundling.
- Use `public/` for files that must keep their name/URL (robots.txt, sitemaps, uploads). Everything renderable should go through `next/image` or imports instead.
- `public/` is the only folder that can be omitted from git and still work; do not import from it with `import` — reference by URL.
