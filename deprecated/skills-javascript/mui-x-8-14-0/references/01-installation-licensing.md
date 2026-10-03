# Installation and licensing

MUI X packages by component and plan, peer dependencies, bundler setup, and the commercial license key.

## Packages

Install only the packages for the components you use, per plan:

```bash
# Data Grid
npm install @mui/x-data-grid            # Community
npm install @mui/x-data-grid-pro        # Pro
npm install @mui/x-data-grid-premium    # Premium

# Charts
npm install @mui/x-charts               # Community
npm install @mui/x-charts-pro           # Pro
npm install @mui/x-charts-premium       # Premium

# Date and Time Pickers
npm install @mui/x-date-pickers         # Community
npm install @mui/x-date-pickers-pro     # Pro

# Tree View
npm install @mui/x-tree-view            # Community
npm install @mui/x-tree-view-pro        # Pro

# License validation (Pro/Premium)
npm install @mui/x-license
```

## Peer dependencies

Every MUI X package has a peer dependency on `@mui/material` (install with `@emotion/react` and `@emotion/styled`) and on `react` / `react-dom` (^17 || ^18 || ^19). You do not need to install pickers to use Data Grid, etc.

Pickers additionally require exactly one of: `dayjs` (recommended for new apps — small bundle), `date-fns`, `luxon`, or `moment`. The adapter must match the installed library.

## Bundling / environment setup

The Data Grid ships CSS imports, which some environments cannot handle:

- **Vite** — works out of the box.
- **Next.js App Router** — works out of the box. **Pages Router** — add `transpilePackages: ['@mui/x-data-grid', '@mui/x-data-grid-pro', '@mui/x-data-grid-premium']` to `next.config`.
- **webpack** — add `style-loader` and `css-loader` rules for `.css`.
- **Vitest** — add the Data Grid packages to `test.deps.inline`.
- **Jest** — map CSS to a mock: `moduleNameMapper: { '\\.(css|less|scss|sass)$': 'identity-obj-proxy' }`.
- **Node.js** — register a no-op `.css` loader (e.g. `require.extensions['.css'] = () => null` with `require()`).

Charts and pickers need no special bundler configuration.

## Plans and upgrading

- **Community** — MIT, free forever. Base component per family.
- **Pro** — commercial. Adds multi-filtering/multi-sorting, column resizing and pinning, row reordering, tree data, range pickers, chart zoom and pan, `RichTreeViewPro`.
- **Premium** — commercial. Superset of Pro. Adds row grouping, aggregation, pivoting, Excel export, AI Assistant, `x-charts-premium`.

Paid packages are **supersets** of the community package. To upgrade: install the paid package and replace every import path and component name:

```diff
-import { DataGrid } from '@mui/x-data-grid';
+import { DataGridPro } from '@mui/x-data-grid-pro';
```

Known exception: the Data Grid `pagination` prop default changes between Community (on, cannot disable) and Pro/Premium (off). Enable it explicitly after upgrading.

## License key

Per the EULA, Pro/Premium may be used without a key for **30 days in non-production** (development, issue reproductions, benchmarks). After that, a commercial license is required to remove watermarks and console warnings.

Orders after May 13, 2022 receive keys compatible with MUI X `v5.11.0`+ only.

Call `setLicenseKey` once, **before React renders the first MUI X component**, **in the browser** (mount-time verification):

```tsx
import { LicenseInfo } from '@mui/x-license';
LicenseInfo.setLicenseKey('YOUR_LICENSE_KEY');
```

The key is validated offline — it is designed to be public in the bundle.

### Next.js patterns

- **App Router, `layout.tsx` with `'use client'`** — call `setLicenseKey` directly at the top of the layout.
- **App Router (recommended otherwise)** — create a client component that calls `setLicenseKey` and returns `null`, and render it in `layout.tsx`:

```tsx
'use client';
import { LicenseInfo } from '@mui/x-license';
LicenseInfo.setLicenseKey('YOUR_LICENSE_KEY');
export default function MuiXLicense() { return null; }
```

- **Pages Router** — call it in `pages/_app.tsx`.
- **Environment variable** — the key is validated server and client side, so expose it with a `NEXT_PUBLIC_` prefix: `LicenseInfo.setLicenseKey(process.env.NEXT_PUBLIC_MUI_X_LICENSE_KEY)`.

Hard-coding the key in git is the documented default; use the env var to keep it out of source-available code.

## Validation failures

If validation fails, the component renders with a watermark plus a console warning (dev and production). Possible errors:

1. **Missing license key** — trial applies or buy a license.
2. **Expired package version** — the installed version was released after your license term ended; renew or pin an older version.
3. **Expired license key** — the key still works forever in **production** for versions released before term end; development use requires renewal.
4. **Plan mismatch** — using a Premium feature (e.g. Data Grid Premium) with a Pro key.
5. **Component not in your license** — e.g. `ChartsPro`/`TreeViewPro` on a key that only covers Data Grid.
6. **Invalid license key** — typo or truncated key.
7. **`TypeError: extracting license expiry timestamp`** — new key format used on an MUI X package older than `v5.11.0`; upgrade the package.

Set `NODE_ENV=production` in your production build to keep the watermark off in production builds of expired-key apps (most bundlers do this automatically).

## Telemetry

MUI X collects anonymous telemetry (version, feature usage). Disable per component if required, e.g. `<DataGrid telemetry={false} />`; see the docs `guides/telemetry` page in the repo.
