# Metadata and OG Images

Next.js generates all `<head>` tags from metadata APIs — never hand-write `<head>` in the App Router (the Pages Router `<Head>` component is the legacy equivalent).

## Static metadata

Export a `Metadata` object from a layout or page (Server Components only). Nested metadata merges with parents, children win per-field:

```tsx
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: {
    default: 'My App',                 // used when no page title
    template: '%s | My App',           // %s replaced by the page title
  },
  description: '...',
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://example.com',
    siteName: 'My App',
    images: [{ url: '/og.png', width: 1200, height: 630, alt: 'My App' }],
  },
  twitter: { card: 'summary_large_image' },
  icons: { icon: '/favicon.ico', apple: '/apple-icon.png' },
  alternates: { canonical: '/', languages: { 'en-US': '/en', de: '/de' } },
  metadataBase: new URL('https://example.com'),
}
```

Common fields: `title`, `description`, `keywords`, `authors`, `creator`, `applicationName`, `category`, `openGraph`, `twitter`, `icons`, `alternates` (canonical, prev/next, languages, media), `formatDetection`, `other`. `metadataBase` (or the `METADATA_BASE` env var) makes relative URLs in metadata absolute.

`meta` charset and `viewport` are always added automatically — don't duplicate them.

## Generated metadata

For per-route dynamic metadata, export `generateMetadata` (async; `params` is a Promise in 15):

```tsx
import type { Metadata, ResolvingMetadata } from 'next'

type Props = { params: Promise<{ slug: string }> }

export async function generateMetadata({ params }: Props, parent: ResolvingMetadata): Promise<Metadata> {
  const { slug } = await params
  const post = await fetch(`https://.../${slug}`).then((r) => r.json())
  return { title: post.title, description: post.excerpt }
}
```

- The `parent` argument carries resolved metadata from parent segments.
- There is a sibling `generateViewport` for dynamic viewport options.
- **Viewport is a separate export since Next 14** — `export const viewport: Viewport = { themeColor: '#000', width: 'device-width', initialScale: 1 }` (putting viewport in `metadata` errors).

## File conventions (static or code-generated)

Drop these in a route folder (or `app/` for app-wide):

| File | Purpose |
|---|---|
| `icon.svg` / `icon.png` | Favicon (generated if `.js/.ts/.tsx`) |
| `apple-icon.png` | Apple touch icon |
| `opengraph-image.(png\|jpg\|jpeg\|gif)` | OG image; `.tsx` generates one at request time |
| `twitter-image.(png\|jpg\|jpeg\|gif)` | Twitter/X card image |
| `robots.txt` or `robots.ts` | Crawl rules (`.ts` can be dynamic) |
| `sitemap.xml` or `sitemap.ts` | Sitemap (`.ts` can generate entries) |
| `manifest.js` | PWA manifest |

Generated image files (`.js/.ts/.tsx`) are rendered with `imageResponse` and accept `{ params, searchParams }` (Promises in 15):

```tsx
import { imageResponse } from 'next/og'

export const runtime = 'edge' // or nodejs

export default async function Image({
  params,
}: { params: Promise<{ slug: string }> }) {
  const { slug } = await params
  const post = await fetch(`https://.../${slug}`).then((r) => r.json())
  return imageResponse(
    (
      <div tw="flex h-full w-full flex-col items-start justify-start p-16">
        <p tw="text-5xl">{post.title}</p>
      </div>
    ),
    { width: 1200, height: 630 }
  )
}
```

## Tips

- Set `metadata` in the root layout for sitewide defaults, override per section/page — don't repeat fields.
- OG images should be 1200×630; keep generated OG images fast (they render on demand).
- For SEO-critical pages, validate the emitted `<head>` in devtools after building, not just in dev.
- `htmlLimitedBots` config can hide app shell markup from AI crawlers without affecting normal SEO.
