---
name: solid-icons-2-0-0
description: SolidJS icon library (v2.0.0) bundling 17 tree-shakeable SVG icon packs — Tabler, Font Awesome, Bootstrap, Heroicons, Ionicons, Remix, Material Design, Ant Design, Feather, Simple Icons, and more — as reactive components. Supports SolidJS 2.0 and 1.x, plus Astro and TanStack Start, and ships a built-in Vite plugin for instant dev startup. Use when adding SVG icons to a SolidJS, Solid Start, Astro, or TanStack Start project, importing icons from a solid-icons pack subpath, or building custom icons with CustomIcon.
license: MIT
compatibility: Requires the solid-icons npm package and solid-js (peer dependency >=1.7.0 || ^2.0.0); the vite plugin from solid-icons/vite requires Vite
metadata:
  tags:
    - javascript
    - frontend
    - ui
    - icons
    - solidjs
---

# solid-icons 2.0.0

## Overview

solid-icons (v2.0.0, MIT) is a SolidJS icon library exposing 17 SVG icon packs as tree-shakeable (`sideEffects: false`), reactive components. Each pack is a separate subpath export (`solid-icons/tb`, `solid-icons/fa`, …) and each icon is a named export that renders an `<svg>` with full SolidJS reactivity — prop changes update the rendered element reactively.

- Compatible with SolidJS 2.0 and SolidJS 1.x (plus Astro, TanStack Start, and SolidStart)
- Compatible with Solid Start static generation and SSR — the icon template renders via `innerHTML` on the server and clones a cached `DocumentFragment` on the client
- Tree shakeable — only the icons you import are bundled
- Built-in Vite plugin (`solid-icons/vite`) for instant `vite dev` cold starts
- Just import and declare in JSX — works out of the box
- First-class TypeScript support
- `CustomIcon` component for custom SVGs, reusing the same `IconTemplate` all library icons use

## Usage

### Install

```bash
npm install solid-icons --save
# or
yarn add solid-icons
```

### Importing from a pack

Import icons directly from their pack prefix:

```jsx
import { TbBrandSolidjs } from "solid-icons/tb";
import { FaSolidHeart } from "solid-icons/fa";

function App() {
  return (
    <div>
      <TbBrandSolidjs size={24} color="#2c4f7c" />
      <FaSolidHeart size={20} color="red" />
    </div>
  );
}
```

Component names are derived from the icon's file path — capitalized pack abbreviation, optional style segment (the subfolder containing the SVG), then the file name with only the first letter of each dash segment uppercased. See [01-component-naming](references/01-component-naming.md) for the derivation rules.

### Vite plugin (recommended for development)

Each icon pack contains thousands of icons. To prevent Vite from scanning or pre-bundling massive icon sets during `vite dev`, add the lightweight `solidIcons` plugin to your Vite config. It transforms icon imports on-the-fly into virtual modules that load only the requested icons, giving instant cold starts:

```ts
// vite.config.ts
import { defineConfig } from "vite";
import solid from "vite-plugin-solid";
import { solidIcons } from "solid-icons/vite";

export default defineConfig({
  plugins: [solid(), solidIcons()],
});
```

The plugin is dev-only (`apply: "serve"`, `enforce: "pre"`) — production builds resolve pack imports normally and rely on tree shaking.

### Props

Icon components accept any SVG element prop plus these custom ones:

| Key     | Default             | Notes                                              |
| ------- | ------------------- | -------------------------------------------------- |
| `size`  | `1em`               | Number or string; `1em` follows the font size     |
| `color` | `currentColor`      | Inherits from CSS                                  |
| `class` | `undefined`         |                                                    |
| `title` | `undefined`         | Icon title for a11y, injected as an SVG `<title>` |
| `style` | `undefined`         | CSS properties, merged with `overflow: visible`    |

### Custom icons

For your own SVGs, use `CustomIcon` from the package root. It takes an `IconTree` — `a` for the SVG element attributes, `c` for the inner SVG markup:

```jsx
import { CustomIcon } from "solid-icons";

const iconContent = {
  a: { fill: "currentColor", viewBox: "0 0 384 512" },
  c: '<path d="M384 319.1C384 425.9 297.9 512 192 512S0 425.87 0 320c0-58.67 27.82-106.8 54.57-134.1C69.54 169.3 96 179.8 96 201.5V287c0 35.17 27.97 64.5 63.16 64.94C194.9 352.5 224 323.6 224 288c0-88-175.1-96.12-52.15-277.2C185.35-8.92 216 .03 216 23.83 215.1 127 384 149.7 384 319.1z"/>',
};

<CustomIcon src={iconContent} size={24} color="#2c4f7c" />;
```

`IconTemplate(src, props)` is also exported if you want to build your own icon component.

### Icon packs

Import from `solid-icons/<abbreviation>`:

| Abbrev | Pack                  | License       | Pack version |
| ------ | --------------------- | ------------- | ------------ |
| `ai`   | Ant Design Icons      | MIT           | 4.4.2        |
| `bs`   | Bootstrap Icons       | MIT           | 1.13.1       |
| `bi`   | BoxIcons              | CC BY 4.0     | 2.1.4        |
| `fi`   | Feather               | MIT           | 4.29.2       |
| `fa`   | Font Awesome          | CC BY 4.0     | 6.7.0        |
| `hi`   | Heroicons             | MIT           | 2.2.0        |
| `im`   | IcoMoon Free          | CC BY 4.0     | 1.0.0        |
| `io`   | Ionicons              | MIT           | 8.0.13       |
| `ri`   | Remix Icon            | Apache 2.0    | 4.8.0        |
| `si`   | Simple Icons          | CC0 1.0       | 16.3.0       |
| `ti`   | Typicons              | CC BY-SA 3.0  | 2.1.2        |
| `vs`   | VS Code Icons         | CC BY 4.0     | 0.0.44       |
| `wi`   | Weather Icons         | SIL OFL 1.1   | 2.0.12       |
| `cg`   | css.gg                | MIT           | 2.1.4        |
| `tb`   | Tabler Icons          | MIT           | 3.36.0       |
| `oc`   | GitHub Octicons       | MIT           | 19.21.1      |
| `md`   | Material Design Icons | Apache 2.0    | 19.21.1      |

Browse every icon and its component name in the [icons explorer](https://solid-icons.vercel.app).

## Gotchas

- **Import icons from the pack subpath, not the package root.** The root (`solid-icons`) and `solid-icons/lib` export only `CustomIcon`, `IconTemplate`, and the TypeScript types — no icon components. Icons live in per-pack modules like `solid-icons/tb`.
- **Icon names are not true PascalCase.** The build uppercases only the first letter of each dash-separated file-name segment and keeps the rest as-is, so `brand-solidjs` becomes `TbBrandSolidjs`, not `TbBrandSolidJs`. When an icon import fails to resolve, check the explorer for the exact exported name.
- **Style subfolders are baked into the name.** Packs that organize SVGs into style subfolders prepend the folder name (capitalized) to the icon name, e.g. `FaSolidAnchorCircleCheck`. Two folder names are remapped by the `tinyStyles` table — `Filled` → `Fill` and `Outlined` → `Outline` — all others pass through.
- **Some packs normalize raw file names before naming.** Weather Icons drops the first 2 characters, IcoMoon Free and BoxIcons drop the first 3, and Octicons maps size variants (`12`/`16`/`24`) to no suffix / `2` / `3`. See [01-component-naming](references/01-component-naming.md).
- **`size` defaults to `1em`, not pixels.** Icons follow the surrounding font size unless you pass a number (e.g. `size={24}`) or an explicit string.
- **`title` renders inside the SVG.** It is injected into the element next to the icon markup as a `<title>` element, not as an attribute.
- **The vite plugin only applies to `vite dev`.** It sets `apply: "serve"`, so it never touches production builds — do not expect it to affect bundle size.
- **Pack licenses vary.** The library itself is MIT, but the icons come from upstream projects with their own licenses — several are CC BY 4.0 or CC BY-SA 3.0, which can require attribution. Check each pack's license accordingly.
- **When working on the library source, icon packs are git submodules.** Cloning solid-icons does not pull the icon data; run `yarn submodule` (`git submodule update --init --recursive`) first. Building the library requires Node >= 16, then `yarn build` (watch mode `yarn dev`, `--isolate="ai"` to rebuild one pack, `--web` for the web output).

## References

- [01-component-naming](references/01-component-naming.md) — How icon component names are derived from file paths; style and per-pack filename normalization
