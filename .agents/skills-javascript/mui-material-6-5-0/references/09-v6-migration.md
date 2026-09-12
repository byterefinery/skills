# 09 — v6 Migration & Deprecations

What changed from v5 to v6 (6.5.0), what is stabilized, and what is deprecated.

## Contents

1. [Baseline and supported environments](#baseline)
2. [Breaking changes](#breaking-changes)
3. [Breaking changes affecting tests](#breaking-changes-affecting-tests)
4. [Breaking changes affecting types](#breaking-changes-affecting-types)
5. [Stabilized APIs](#stabilized-apis)
6. [Deprecated APIs (removed in v7)](#deprecated-apis)
7. [Codemods](#codemods)
8. [Pigment CSS](#pigment-css)

## Baseline

- UMD bundle removed (~2.5MB, 25% of v5 package size); use ESM CDNs (esm.sh) for CDN usage.
- **IE 11 support removed** (legacy bundle gone with it).
- Browser targets raised: Chrome 109+, Edge 121+, Firefox 115+, Safari/iOS 15.4+; Node 14+.
- Minimum React 17 (unchanged from v5); supports React 19. **Minimum TypeScript 4.7** (was 3.5).
- MUI X packages keep their own versioning — do not bump them with MUI.

## Breaking changes

### Grid2 (`Grid`)

Stabilized from `Unstable_Grid2`; imported as `@mui/material/Grid2`:

- `xs`/`sm`/`md`/`lg`/`xl` → **`size`** (number, per-breakpoint object, `'auto'`, `'grow'`); `xsOffset`/... → **`offset`**.
- Boolean `xs` (grow) → `size="grow"`.
- `disableEqualOverflow` removed (grid no longer overflows parent padding).
- Item spacing now via CSS `gap` — items no longer include spacing in their boxes.
- Container does not stretch to full width by default — add `sx={{ width: '100%' }}` or `sx={{ flexGrow: 1 }}` (flex parent) if needed.

```diff
-<Grid xs={12} sm={6} xsOffset={2}>
+<Grid size={{ xs: 12, sm: 6 }} offset={{ xs: 2 }}>
```

### ListItem

`autoFocus`, `button`, `disabled`, `selected` props **removed** — use `ListItemButton` (keeps all four). Class names moved: `listItemClasses.button` → `listItemButtonClasses.root`, etc.

### Accordion

- Summary is now wrapped in a `<h3>` heading (W3C pattern); since v6.3 the summary root is a `<button>` with `span` content (no `Typography`/`<p>` inside — use `component="span"`).
- Change heading level via `slotProps.heading.component`.

### Chip

Retains focus on Escape (consistent with other button-like components); restore old blur via `onKeyUp`.

### Divider

Vertical orientation renders a `<div>` (not `<hr>`) with WAI-ARIA attributes; update CSS that targeted `hr`. Use `dividerClasses.root` for selectors.

### Autocomplete

`onInputChange` gains `reason` values: `'blur'`, `'selectOption'`, `'removeOption'` (in addition to `'input'`, `'reset'`, `'clear'`).

### Typography

`color` is no longer a system prop — theme-path colors move to `sx` (`<Typography sx={{ color: 'primary.main' }}>`); palette role names still work on the prop.

### Button loading (v6.4+)

`@mui/lab`'s `LoadingButton` removed; `Button` and `IconButton` have `loading` (`boolean | null`).

```diff
-import { LoadingButton } from '@mui/lab';
+import { Button } from '@mui/material';
```

### useMediaQuery types

Deprecated `MuiMediaQueryList`, `MuiMediaQueryListEvent`, `MuiMediaQueryListListener` removed — use the DOM lib types (`MediaQueryList`, `MediaQueryListEvent`) or `(event: MediaQueryListEvent) => void`.

## Breaking changes affecting tests

Ripple performance rework — wrap pointer interactions in `act` and await (buttons, Checkbox, Chip, Radio, Switch, Tabs):

```diff
- fireEvent.click(button);
+ await act(async () => { fireEvent.mouseDown(button); });
```

## Breaking changes affecting types

`component` removed from `BoxOwnProps` (already on `Box`'s type) — affects `styled(Box)`: use `styled('div')` instead, or cast the result `as typeof Box`.

## Stabilized APIs

- `CssVarsProvider` and `extendTheme` (from `@mui/material/styles`) — stable; their features are also available directly on `ThemeProvider`/`createTheme` (`cssVariables: true`).
- **`theme.applyStyles(mode, styles)`** — the v6 utility for mode-specific styles, replacing `theme.palette.mode === 'dark'` checks. Works with `styled`, `sx`, and (planned) Pigment CSS.
- `Grid2` (see above), `ButtonGroup`, and the `colorSchemes` color-mode API.

## Deprecated APIs

Will be removed in the next major (v7); migrate at your own pace. The full list lives in the `migrating-from-deprecated-apis` doc; the main families:

- **Inner element overrides** — `components` / `componentsProps` (and per-component `*Component`/`*Props` props like `TransitionComponent`, `TransitionProps`, `PaperProps`, `BackdropProps`, `PaperComponent`) → `slots.*` / `slotProps.*`.
  - e.g. `Dialog TransitionComponent={Slide}` → `slots={{ transition: Slide }}`; `Dialog PaperProps={{...}}` → `slotProps={{ paper: {...} }}`; `Accordion TransitionComponent` → `slots.transition`; `CardMedia`'s `imgProps` → `slotProps.img`; `CardHeader titleTypographyProps` → `slotProps.titleTypography`.
- **Composed CSS class strings** — e.g. `ButtonClasses.text`-style composed slot names and `& .MuiX-y` composed selectors → stable global classes (`.MuiButton-root .MuiButton-text` style targeting) or `slotProps`.
- **System props** — `mt`, `p`, `display`, `color`, `gap`, `width`, `sx`-equivalent utility props on components → the `sx` prop.
- **Theme component variants** (the old `theme.components.MuiX.variants` top-level form) → inside `styleOverrides.<slot>.variants`.
- **`Divider light`** → `color` from the palette; **`Avatar imgProps`** → `slotProps.img`; **`AvatarGroup componentsProps`** → `slotProps`; **`Backdrop TransitionComponent`** → `slots.transition`; **`FilledInput components/componentsProps`** → `slots`/`slotProps`; **`FormControlLabel componentsProps`** → `slotProps.control`.
- **`useMediaQuery`** as a hook is not deprecated, but `Hidden` (v5 legacy component) is deprecated — use `sx` display values.

Practical rule for new v6 code: use `slotProps`/`slots`, stable global class names, and `sx` — never `componentsProps`/`*Props` props or system props.

## Codemods

v5 → v6 breaking changes:

```bash
npx @mui/codemod@latest v6.0.0/grid-v2-props <path>            # Grid2 size/offset
npx @mui/codemod@latest v6.0.0/list-item-button-prop <path>    # ListItem button → ListItemButton
npx @mui/codemod@latest v6.0.0/styled <path>                   # palette.mode → theme.applyStyles (styled)
npx @mui/codemod@latest v6.0.0/sx-prop <path>                  # palette.mode + sx callback deprecations
npx @mui/codemod@latest v6.0.0/system-props <path>             # system props → sx
npx @mui/codemod@latest v6.0.0/theme-v6 <theme-file>           # palette.mode in theme styleOverrides
```

Deprecated API migration (each component family has its own; `all` runs every one):

```bash
npx @mui/codemod@latest deprecations/text-field-props <path>   # *Props → slotProps
npx @mui/codemod@latest deprecations/dialog-props <path>       # TransitionComponent/PaperProps → slots/slotProps
npx @mui/codemod@latest deprecations/all <path>                # everything
```

Run `v6.0.0/theme-v6` only if you have a custom theme with `styleOverrides`.

## Pigment CSS

v6's opt-in, zero-runtime CSS-in-JS engine (build-time style extraction):

- Why: React Server Components compatibility (styles extracted at build time, no client-side recalculation), smaller bundles, no runtime injection.
- Opt-in in v6 via the `@pigment-css/react` packages (`createPigmentCache`, `<PigmentProvider>`); Material UI components work with it unchanged. Future MUI majors are likely to default to it.
- `theme.applyStyles()` is designed to work with it; `styled`/`sx` from `@mui/material/styles` are Emotion-based.
- Migration guide: `migrating-to-pigment-css` in the MUI docs.
