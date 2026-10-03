# 03 — Layout Components

Box, Grid v2, Stack, Container, Paper, and AppBar.

## Contents

1. [Box](#box)
2. [Grid v2](#grid-v2)
3. [Stack](#stack)
4. [Container](#container)
5. [Paper](#paper)
6. [AppBar and Toolbar](#appbar-and-toolbar)
7. [Misc layout helpers](#misc-layout-helpers)

## Box

Generic theme-aware container — a `<div>` with `sx` and MUI System access:

```jsx
import Box from '@mui/material/Box';

<Box component="section" sx={{ p: 2, color: 'primary.main' }}>...</Box>
```

- Renders `<div>` by default; `component` swaps any element or component (e.g., `component="span"`, `component={RouterLink}`).
- Use Box for multipurpose layout; reach for Container/Stack/Paper when you want usage-specific props (see below).
- System props (`mt`, `p`, `display`, ...) on Box are **deprecated** — use `sx={{ mt: 2 }}`.

## Grid v2

`Grid2` was stabilized in v6 (the old `Grid`/`Unstable_Grid1` and the old `Hidden` are deprecated). It implements a **12-column flexbox** layout grid with CSS `gap` spacing.

```jsx
import Grid from '@mui/material/Grid2';

<Grid container spacing={2}>
  <Grid size={{ xs: 12, sm: 6 }}>Half at sm+</Grid>
  <Grid size={6} offset={1}>Offset</Grid>
  <Grid size="auto">Fits content</Grid>
  <Grid size="grow">Fills remaining space</Grid>
</Grid>
```

API:

| Prop | Meaning |
|---|---|
| `container` | Marks the grid as a flex container (a `Grid` is always a flex *item*) |
| `size` | Columns (1-12, number, per-breakpoint object, `'auto'`, or `'grow'`) |
| `offset` | Empty columns before the item (number or per-breakpoint object) |
| `spacing` | Gap between items — number/`theme.spacing` unit, string, or responsive object; converted via `theme.spacing()` |
| `rowSpacing` / `columnSpacing` | Independent row/column gaps |
| `columns` | Total column count (default 12), responsive |
| `direction` | Flex direction, responsive |

Rules:

- Widths are percentages — always fluid. Larger breakpoints override smaller ones (`size={{ xs: 12, sm: 6 }}`).
- No row spanning and no auto-placement of items — use CSS Grid if you need those.
- It is a *layout* grid, not a data grid (for data, use MUI X `DataGrid`).
- **v6 changes vs v5**: `xs`/`sm`/... props → `size`, `xsOffset` → `offset`, boolean `xs` → `size="grow"`, `disableEqualOverflow` removed (no more parent overflow), items no longer include spacing in their boxes (CSS gap), and the container does not stretch to full width by default — add `sx={{ width: '100%' }}` or `sx={{ flexGrow: 1 }}` (in a flex parent) when needed.
- Codemod: `npx @mui/codemod@latest v6.0.0/grid-v2-props <path>` (fix the `Unstable_Grid2` import first; pass custom breakpoints via `--jscodeshift='--muiBreakpoints=a,b'`).
- Nested containers inherit `columns`/`spacing` only when they are **direct** children of another container.

## Stack

One-dimensional flex container with gap-based spacing:

```jsx
import Stack from '@mui/material/Stack';

<Stack spacing={2} direction="row" divider={<Divider flexItem />}>
  <Typography>A</Typography>
  <Typography>B</Typography>
</Stack>
```

- `spacing` (number/string/responsive), `direction` (`column` default, responsive), `divider` (element rendered between children).
- **Limitations of the default implementation**: child margins are ignored (spacing is CSS-selector based). Set `useFlexGap` (per instance or `MuiStack.defaultProps.useFlexGap: true` in theme) to switch to CSS `gap`, which fixes margins and `white-space: nowrap` overflow (then set `minWidth: 0` on the item as needed).

## Container

Centers content horizontally; the basic page wrapper:

- `<Container maxWidth="sm">` — fluid, max-width from breakpoint key or number.
- `<Container fixed>` — fixed to the current breakpoint's min-width.
- Also `maxWidth="md"`, `disableGutters` (remove left/right padding).

## Paper

Elevated surface container:

- `elevation` 0-24 (default 1) → `theme.shadows[n]`; in dark mode higher elevation also lightens the background via `background-image` (overriding only `backgroundColor` won't remove it — override both).
- `variant="outlined"` for a flat bordered surface; `square` removes rounded corners.
- Use Box/Container for plain containers; Paper when you want Material elevation.

## AppBar and Toolbar

`AppBar` is a themed surface for headers; `Toolbar` is its content row (sets padding and height).

```jsx
<AppBar position="fixed">
  <Toolbar>
    <Typography variant="h6">Title</Typography>
  </Toolbar>
</AppBar>
```

- `position`: `fixed` (default), `absolute`, `sticky`, `static`, `relative`.
- `color`: `default`, `inherit`, `transparent`, or palette role. In dark mode `color` has no effect by default — set `enableColorOnDark` to force it.
- **Fixed app bars cover content** — three fixes: `position="sticky"`, render an empty `<Toolbar />` after the app bar, or a styled offset div using `theme.mixins.toolbar`.
- `variant="dense"` (desktop), `variant="prominent"` (taller, for heroes).
- `BottomAppBar` — bottom variant, pairs with `Fab`.

### useScrollTrigger

```js
import useScrollTrigger from '@mui/material/useScrollTrigger';

const trigger = useScrollTrigger({
  target: ref?.current,      // scroll container (default window)
  threshold: 100,            // px before trigger flips
  disableHysteresis: false,  // true = ignore scroll direction
});
```

Classic recipes: hide app bar on scroll down (`<Slide in={!trigger}>`), elevate on scroll (`elevation={trigger ? 8 : 0}`), back-to-top FAB.

## Misc layout helpers

- `Divider` — `<hr>`-like separator; `variant` (`fullWidth` default, `inset`, `middle`), `orientation="vertical"` (renders a `<div>` with ARIA in v6), `flexItem`, `textAlign` for wrapped children, `component="li"` inside Lists. Decorative dividers: `aria-hidden="true"`.
- `Hidden` — deprecated (v5 legacy); use `sx={{ display: { xs: 'none', md: 'block' } }}`.
- `NoSsr` — renders children only on the client; `defer` defers rendering by one screen frame, `fallback` shows placeholder content. For browser-only components (maps, canvas).
- `ImageList` — grid for image collections; `cols`, `rowHeight` (`number | 'auto'`), `gap` (px), `variant`: `standard` (default), `woven`, `quilted`, `masonry`; children `ListItem`/`ListItemAvatar` with `<img>`/`ListItemBar`.
- `Grid` (v1) — deprecated; use `Grid2`.
- `Portal` — `children` rendered into `document.body` (or a custom `container` DOM node); building block behind Modal.
- `Masonry` — Lab component (CSS grid masonry), `columns` responsive number; from `@mui/lab`.
