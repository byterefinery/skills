# 02 — Styling

The `sx` prop, the `styled` utility, MUI class names, and global/theming style APIs.

## Contents

1. [The sx prop](#the-sx-prop)
2. [Theme-aware properties in sx](#theme-aware-properties-in-sx)
3. [Responsive and container-query values](#responsive-and-container-query-values)
4. [The styled utility](#the-styled-utility)
5. [sx vs styled](#sx-vs-styled)
6. [Class names and overrides](#class-names-and-overrides)
7. [Theme overrides (defaultProps, styleOverrides, variants)](#theme-overrides)
8. [GlobalStyles](#globalstyles)
9. [Cascade layers](#cascade-layers)
10. [CSS theme variables](#css-theme-variables)

## The sx prop

`sx` is a theme-aware superset of CSS accepted by every MUI component and by `Box`:

```jsx
<Box
  sx={{
    p: 2,                    // theme-aware spacing
    color: 'primary.main',   // palette path
    m: { xs: 2, md: 3 },     // responsive value
    '&:hover': { color: 'red' },  // nested selectors
    '@media print': { display: 'none' },
  }}
/>
```

- Values can be an **object**, a **function of theme**, or an **array** of objects/functions. Later array indices override earlier ones (higher index = higher specificity), which is the idiomatic way to do conditional styles:

```jsx
<Box sx={[
  { mr: 2, color: 'red' },
  (theme) => ({ '&:hover': { color: theme.palette.primary.main } }),
  foo && { color: 'grey' },
]}/>
```

- **Callbacks must be the whole value** (v6 deprecates per-key callbacks):

```diff
- sx={{ height: (theme) => theme.spacing(10) }}
+ sx={(theme) => ({ height: theme.spacing(10) })}
```

Codemod: `npx @mui/codemod@latest v6.0.0/sx-prop path/to/file-or-folder`.
- **TypeScript type widening**: a style object in a variable widens literals to `string`. Fix with `as const` or inline the object.
- Passing `sx` through your own component: destructure it out and forward to the MUI component; do not re-create it.
- **Dynamic values** (changing every render, e.g. a color picker): use an inline `style` attribute / CSS variable instead of `sx` to avoid inserting new `<style>` tags per render.

## Theme-aware properties in sx

Properties that map to the theme when given non-CSS values:

| Property | Behavior |
|---|---|
| `m`, `mt`, `mr`, `mb`, `ml`, `mx`, `my` / `p`, `pt`, `pr`, `pb`, `pl`, `px`, `py` | multiply by `theme.spacing` (8px) |
| `gap`, `rowGap`, `columnGap` | multiply by `theme.spacing` |
| `color`, `backgroundColor` (alias `bgcolor`) | palette path string: `'primary.main'` |
| `borderColor` | palette path string |
| `border` | number = `Nx solid black` |
| `borderRadius` | number = N × `theme.shape.borderRadius` |
| `boxShadow` | number = index into `theme.shadows` |
| `zIndex` | key of `theme.zIndex` (e.g. `'tooltip'`) |
| `width`, `height`, `min/max*` | number in (0, 1] → percentage; number ≥ 1 → px |
| `fontFamily`, `fontSize`, `fontStyle`, `fontWeight` | `theme.typography` keys; `fontWeight: 'light'` = `fontWeightLight` |
| `typography` | whole variant: `typography: 'body1'` spreads `theme.typography.body1` |
| `displayPrint` | display only under `@media print` |

Any valid CSS property also works. System props on components (`<Box mt={2}/>`) are **deprecated in v6** — use `sx={{ mt: 2 }}`.

## Responsive and container-query values

All sx properties accept `{ xs, sm, md, lg, xl }` objects (later keys win on wider screens):

```jsx
sx={{ width: { xs: '100%', sm: 320 }, p: { xs: 1, md: 3 } }}
```

Container queries (v6):

- `theme.containerQueries.up('sm')` → `'@container (min-width: 600px)'` (same method set as `theme.breakpoints`); named context: `theme.containerQueries('sidebar').up('500px')`.
- Shorthand in sx: `sx={{ padding: { '@40em': 4, '@20em': 2, '@': 0 } }}`. Unitless = px; keep units consistent within one property or ordering breaks. An ancestor needs `container-type`.

## The styled utility

`styled` (re-exported from Emotion) creates reusable styled components:

```tsx
import { styled } from '@mui/material/styles';
import Button, { ButtonProps } from '@mui/material/Button';

interface CustomButtonProps extends ButtonProps {
  severity?: 'error' | 'success';
}

const CustomButton = styled(Button, {
  // don't leak custom props to the DOM
  shouldForwardProp: (prop) => prop !== 'severity',
})<CustomButtonProps>(({ theme, severity }) => ({
  backgroundColor: severity === 'error' ? theme.palette.error.main : theme.palette.primary.main,
  '&:hover': { backgroundColor: theme.palette.primary.dark },
}));

<CustomButton severity="error">Delete</CustomButton>
```

- Use `shouldForwardProp` for every custom prop you read.
- Styling MUI components with `styled` works; for TypeScript, cast the result when composing: `styled(Button)({...}) as typeof Button`.
- Components as selectors: `styled('div')({ '& .MuiButton-root': {...} })` — if you hit `TypeError: Cannot convert a Symbol value to a string`, follow the "components selector" docs (type the component with a `Classes` prop).
- `theme.applyStyles(mode, styles)` inside `styled`/`sx` for light/dark branches (preferred over `theme.palette.mode` checks).

## sx vs styled

| | `sx` | `styled` |
|---|---|---|
| Use when | one-off, inline overrides | reusable component, dynamic prop-driven styles |
| Specificity | higher (applied after theme overrides) | default (theme overrides can beat it) |
| Output | generated classes | generated classes |

Rule of thumb: `sx` for "this instance", `styled` for "this component everywhere", theme overrides for "all instances of a MUI component".

## Class names and overrides

MUI generates class names following `[hash]-Mui[ComponentName]-[slot]`, e.g. `.css-abc123-MuiButton-root`. The hashed part is **unstable**; only target the stable global part.

Stable global classes:

- Component root/slot: `MuiButton-root`, `MuiButton-label`, `MuiSlider-thumb`, `MuiTextField-root`, ...
- State classes (pseudo-class-like specificity): `.Mui-active`, `.Mui-checked`, `.Mui-completed`, `.Mui-disabled`, `.Mui-error`, `.Mui-expanded`, `.Mui-focusVisible`, `.Mui-focused`, `.Mui-readOnly`, `.Mui-required`, `.Mui-selected`.

Override a nested slot from a parent with `sx`:

```jsx
<Slider sx={{ '& .MuiSlider-thumb': { borderRadius: 0 } }} />
```

Override a state: increase specificity with component + state (`.MuiMenuItem-root.Mui-selected`); **never** style a bare `.Mui-*` state class (it would hit every component).

`components`/`componentsProps` (inner-element overrides) and composed-class strings (e.g. `'& .MuiButton-text'` composed names) are deprecated in v6 — prefer stable global classes above; see [09-v6-migration](09-v6-migration.md).

## Theme overrides

Inside `createTheme`:

```js
const theme = createTheme({
  components: {
    MuiButton: {
      defaultProps: {
        variant: 'contained',      // default prop values for every Button
        disableRipple: true,       // e.g. kill the ripple app-wide
        color: 'primary',
      },
      styleOverrides: {
        root: {                    // slot name; 'root' = outermost element
          borderRadius: 8,
        },
        label: { textTransform: 'none' },
      },
      variants: [                  // prop-based styles (array; order matters, last wins)
        { props: { variant: 'dashed' }, style: { border: '2px dashed' } },
        { props: (props) => props.variant === 'dashed' && props.color !== 'secondary', style: { color: 'black' } },
      ],
    },
  },
});
```

- `defaultProps` also applies to all descendants of that component.
- `styleOverrides` keys are **slot names** from the component's DOM structure (check the component's anatomy docs). Values are CSS objects or `(theme) => object`.
- `variants` live inside the slot (`styleOverrides.root.variants` for root styles). `props` can be an object or a callback. Add new variant names (e.g. `variant: 'dashed'`) with TS module augmentation on the component module (`interface ButtonPropsVariantOverrides { dashed: true }`).
- Slot ownerState callbacks (`root: ({ ownerState, theme }) => ({...})`) are **deprecated** — use `variants`.
- The `sx` prop always beats theme `styleOverrides`.
- The theme's `components` key is NOT tree-shakable; for heavy one-off customizations, compose a new component instead.

## GlobalStyles

`GlobalStyles` injects global CSS (supports theme callback; hoist to a static constant to avoid re-rendering):

```jsx
import GlobalStyles from '@mui/material/GlobalStyles';

const globalStyles = (
  <GlobalStyles
    styles={(theme) => ({
      'h1': { fontFamily: theme.typography.fontFamily },
      '@keyframes mui-auto-fill': { from: { display: 'block' } },
    })}
  />
);
```

Use it for raw HTML elements, global resets, or injecting keyframes. Alternative: extend `MuiCssBaseline.styleOverrides`.

## Cascade layers

Wrap MUI output in `@layer mui` so other styling solutions (Tailwind v4, CSS Modules) can override without `!important`:

- SPA: `<StyledEngineProvider enableCssLayer>` (from `@mui/material/styles`) + declare layer order in global CSS: `@layer theme, base, mui, components, utilities;`
- Next.js App Router: `<AppRouterCacheProvider options={{ enableCssLayer: true }}>` + same layer-order CSS.
- Next.js Pages Router: `createCache({ enableCssLayer: true })` in `_document.tsx`, pass the same cache to `AppCacheProvider` in `_app.tsx`.

## CSS theme variables

Enable per-app: `createTheme({ cssVariables: true })` (+ `ThemeProvider`).

- Generates `:root { --mui-palette-primary-main: #1976d2; ... }`; components then use `var(--mui-...)` instead of raw values — great for debugging and for injecting the user's chosen theme before hydration.
- `theme.vars` mirrors the theme structure with the variable values: `theme.vars.palette.primary.main` → `var(--mui-palette-primary-main)`. TypeScript: `import type {} from '@mui/material/themeCssVarsAugmentation';`
- Plain CSS can use `var(--mui-palette-grey-50)` directly.
- Custom tokens: add key/value pairs to the theme (optionally per `colorSchemes.light/dark`); access via `theme.vars.palette.yourToken`. Augment `Palette`/`PaletteOptions` for TS.
- **Channel tokens**: `theme.vars.palette.primary.mainChannel` = `'25 118 210'` (space-separated). Build translucent colors with `rgba(${...mainChannel} / 0.12)` — use `/`, never `,`.
- Prefix: `createTheme({ cssVariables: { cssVarPrefix: 'any' } })` (or `''` to remove `--mui`).
- `disableCssColorScheme: true` stops generating the CSS `color-scheme` property.
- With `cssVariables`, `theme.applyStyles()` output has **higher specificity** than plain styles — override inside `applyStyles` too.
- Trade-offs for SSR: bigger HTML (both light + dark vars emitted), slightly longer FCP, but much shorter TTI in dark mode.
- `CssVarsProvider` and `extendTheme` from v5 are **stable** in v6 (and their features now live on `ThemeProvider` + `createTheme`).

See [01-setup-and-theming](01-setup-and-theming.md) for the theme API and [07-recipes](07-recipes.md) for dark-mode switching with these variables.
