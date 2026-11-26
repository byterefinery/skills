---
name: solid-icons-1-2-0
description: SolidJS icon library (v1.2.0) bundling 17 tree-shakeable SVG icon packs — Tabler, Font Awesome, Bootstrap, Heroicons, Ionicons, Remix, Material Design, Ant Design, Feather, Simple Icons, and more — as reactive components. Use when adding SVG icons to a SolidJS or Solid Start project, importing icons from a solid-icons pack subpath, or building custom icons with CustomIcon.
license: MIT
compatibility: Requires the solid-icons npm package and solid-js (peer dependency, any version).
metadata:
  tags:
    - javascript
    - frontend
    - ui
    - icons
    - solidjs
---
# solid-icons 1.2.0

## Overview

solid-icons (v1.2.0, MIT) is a SolidJS icon library exposing 17 SVG icon packs as tree-shakeable, reactive components. Each pack is a separate subpath export (`solid-icons/tb`, `solid-icons/fa`, …) and each icon is a named export that renders an `<svg>` with full SolidJS reactivity — prop changes update the rendered element reactively.

- Just import and declare in JSX — works out of the box
- Tree shakeable (`sideEffects: false`) — only imported icons are bundled
- Compatible with SSR and Solid Start static generation
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

```jsx
import { TbBrandSolidjs } from "solid-icons/tb";

<TbBrandSolidjs size={24} color="#2c4f7c" />;
```

Component names are derived from the icon's file path: capitalized pack abbreviation, optional style segment (the subfolder containing the SVG), then the file name with dashes removed and each segment's first letter uppercased — original casing is otherwise preserved. See [01-component-naming](references/01-component-naming.md) for the derivation rules.

### Props

Icon components accept any SVG element prop plus these custom ones:

| Key     | Default             | Notes                                     |
| ------- | ------------------- | ----------------------------------------- |
| `size`  | `1em`               | Number or string; `1em` follows font size |
| `color` | `currentColor`      | Inherits from CSS                         |
| `class` | `undefined`         |                                           |
| `title` | `undefined`         | Injected as an SVG `<title>` element (a11y) |
| `style` | `undefined`         | Merged with `overflow: visible`           |

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
- **Style subfolders are baked into the name.** Packs that organize SVGs into style subfolders prepend the folder name (capitalized) to the icon name, e.g. `FaSolidAnchorCircleCheck`. Two folders get special-cased mappings, `filled` → `Fill` and `outlined` → `Outline`.
- **`size` defaults to `1em`, not pixels.** Icons follow the surrounding font size unless you pass a number (e.g. `size={24}`) or an explicit string.
- **`title` renders inside the SVG.** It is injected into the element's innerHTML next to the icon markup as a `<title>` element, not as an attribute.
- **Pack licenses vary.** The library itself is MIT, but the icons come from upstream projects with their own licenses — several are CC BY 4.0 or CC BY-SA 3.0, which can require attribution. The repo README tells you to check each project's license accordingly.
- **When working on the library source, icon packs are git submodules.** Cloning solid-icons does not pull the icon data; `postinstall` runs `git submodule update --init --recursive`. Building the library requires Node ^16.14.0, `yarn`, and `yarn build` (add `--isolate="<abbr>"` to rebuild one pack, `--web` to build the web output).

## References

- [01-component-naming](references/01-component-naming.md) — How icon component names are derived from file paths; style and per-pack filename normalization
