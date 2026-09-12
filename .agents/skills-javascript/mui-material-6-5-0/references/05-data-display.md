# 05 — Data Display

Typography, Table, List, Card, and the small display primitives.

## Contents

1. [Typography](#typography)
2. [Table](#table)
3. [List](#list)
4. [Card](#card)
5. [Chip](#chip)
6. [Avatar](#avatar)
7. [Badge](#badge)
8. [Alert](#alert)
9. [Progress](#progress)
10. [Skeleton](#skeleton)
11. [Icons](#icons)

## Typography

```jsx
<Typography variant="h1" component="h2" gutterBottom align="center" noWrap color="textSecondary">
  Title
</Typography>
```

- `variant` — `h1`-`h6`, `subtitle1/2`, `body1/2`, `caption`, `button`, `inherit` (default `body1`).
- Style is independent from the semantic element: `component`/`variantMapping` change the tag, not the style. Avoid duplicate `h1`s with `variant="h1" component="h2"`.
- `color` accepts theme color names (e.g., `textSecondary`) but is **not** a system prop in v6 — arbitrary theme paths go through `sx`.
- `gutterBottom` (1em bottom margin), `noWrap`, `align`, `paragraph`, `sx`.
- Without the component, theme keys work anywhere: `sx={{ ...theme.typography.h5 }}`.

## Table

Mapping of native `<table>` elements + helpers:

- `Table` (optionally inside `TableContainer` for horizontal scroll; `stickyHeader` for pinned headers)
- `TableHead`, `TableBody`, `TableFooter`
- `TableRow` (`hover`, `selected`, `onClick`, `component`)
- `TableCell` (renders `th` in head, `td` in body; `align`, `padding`, `size="small"`, `scope`, `variant`)
- `TablePagination` — rows-per-page + range controls; **page is 0-based**
- `TableSortLabel` — clickable column header with sort arrow (`active`, `direction`, `onClick`)

```jsx
<TableContainer>
  <Table stickyHeader size="small">
    <TableHead>
      <TableRow>
        <TableCell><TableSortLabel active direction="asc" onClick={...}>Name</TableSortLabel></TableCell>
      </TableRow>
    </TableHead>
    <TableBody>
      <TableRow hover>
        <TableCell>Ada</TableCell>
      </TableRow>
    </TableBody>
  </Table>
</TableContainer>
```

- `dense` look: `size="small"` on `Table`/`TableCell`.
- Sorting & selecting & pagination: full recipe in [07-recipes](07-recipes.md).
- `TablePagination.rowsPerPageOptions` accepts numbers or `{ value, label }` objects (e.g., `{ value: -1, label: 'All' }`); `ActionsComponent` for custom prev/next buttons.
- Virtualization: pair with `react-window`/`react-virtuoso`. Large datasets → MUI X `DataGrid`.
- Accessibility: give tables a caption (screen readers announce it).

## List

Vertical index of items:

- `List` (`dense`, `subheader`, `component="nav"`, `aria-label`)
- `ListItem` (plain wrapper; `inset`, `disableGutters`, `secondaryAction`) — the v5 `button` prop is **removed**; use `ListItemButton`
- `ListItemButton` (the clickable item: `selected`, `autoFocus`, `disabled`, `edge="end"`, `component` for routing)
- `ListItemText` (`primary`, `secondary`, `primaryTypographyProps`, `secondaryTypographyProps`)
- `ListItemIcon` / `ListItemAvatar` / `ListItemSecondaryAction`
- `ListSubheader` (group label; sticky-on-scroll by default inside a scrollable list container)
- `Collapse` for expandable/nested rows (pair with `TransitionProps={{ unmountOnExit }}`)

```jsx
<List dense>
  <ListItemButton component={RouterLink} to="/x" selected={active}>
    <ListItemIcon><InboxIcon /></ListItemIcon>
    <ListItemText primary="Inbox" secondary="3 unread" />
  </ListItemButton>
  <ListItem disableGutters><Divider /></ListItem>
</List>
```

- 3+ lines of text: set `alignItems="flex-start"` on the row to keep the icon at the top.
- `ListItem` inside a component with its own gutters: `disableGutters`.

## Card

Surface for a single subject; `Paper` underneath.

- `Card` (`variant="outlined"`, elevation via Paper)
- `CardHeader` (`title`, `subheader`, `avatar`, `action`, `titleTypographyProps`)
- `CardMedia` — `image` (background-image on a div; set `height` explicitly) or `src` + `component="img"|"video"|"picture"|"iframe"` for real media elements
- `CardContent`
- `CardActions` (button row)
- `CardActionArea` — makes a region the whole card's click target (`component={Link}` supported)

```jsx
<Card>
  <CardActionArea component={RouterLink} to="/post/1">
    <CardMedia component="img" height="140" image={url} alt="..." />
    <CardContent>
      <Typography variant="h5">Title</Typography>
    </CardContent>
  </CardActionArea>
  <CardActions>
    <Button size="small">Share</Button>
  </CardActions>
</Card>
```

## Chip

Compact element for input, attribute, or action.

- `label` (text; objects render nothing without `renderIcon`/`deleteIcon`...), `avatar`, `icon` (leading ornaments)
- `variant` `filled` (default) / `outlined`; `color`; `size` `medium`/`small`
- `onClick` (focusable, clickable), `onDelete` (shows delete icon; keyboard: Backspace/Delete deletes, Escape blurs), `disabled`, `deleteIcon` (custom)
- Multiline: `sx={{ height: 'auto' }}` + label style `whiteSpace: 'normal'`.

## Avatar

- `src`/`srcSet` (image), string children (letter), icon children, `alt`
- Fallback chain on image error: children → first letter of `alt` → generic person icon
- `variant` `circular` (default)/`rounded`/`square`; size via CSS width/height
- `AvatarGroup` — stacked avatars; `max` (default 3), `total` (count without data), `renderSurplus`, `spacing` `small`/`medium`/number
- Pair with `Badge` for online status dots.

## Badge

Small notification indicator on its child.

- `badgeContent`, `color` (default `default`; `error` for notifications), `max` (shows `99+`), `showZero`, `invisible` (keeps layout space)
- `variant="dot"` for presence indicators (replaces the old `dot` prop); `overlap` `rectangular`/`circular`; `anchorOrigin` for corner placement
- Provide `aria-label` — badge content alone is not reliably announced.

## Alert

In-flow severity message (not modal, not floating).

```jsx
<Alert severity="warning" variant="outlined" onClose={...} action={<Button size="small">Undo</Button>} icon={false}>
  Disk almost full.
</Alert>
```

- `severity`: `success` (default), `info`, `warning`, `error`
- `variant`: `filled` (default), `outlined`
- `onClose` shows a close icon unless `action`/`icon={false}`; `icon`/`iconMapping` override per-severity icons
- `AlertTitle` child for a bold heading line
- Outlined Alert inside a Snackbar: add `sx={{ bgcolor: 'background.paper' }}` or content bleeds through.
- Pair with `Snackbar` for floating toasts (see [06-overlays](06-overlays-and-navigation.md)).

## Progress

- `LinearProgress` — indeterminate by default; `determinate` with `value` (0-100), `variant="buffer"` with `aria-valuetext`, `color`, `disableShimmer`
- `CircularProgress` — `size`, `thickness`, `variant="determinate"` with `value`, `color`, `disableShimmer`
- Accessible: label the context ("Loading...") for screen readers.

## Skeleton

Loading placeholder (perceived performance).

```jsx
{item ? <img src={item.src} width={210} height={118} alt={item.title}/> :
       <Skeleton variant="rectangular" width={210} height={118} />}
```

- `variant`: `text` (default — sized by font), `rectangular`, `rounded`, `circular`
- `animation`: `pulse` (default), `wave`, `none`
- Dimension inference: inside `Typography` (em-based height) or wrap the real component as `children` to copy its size.
- On black backgrounds, override `backgroundColor`.

## Icons

Three approaches:

1. **`@mui/icons-material` SVG components** (preferred): 2,100+ icons.

```jsx
import AddIcon from '@mui/icons-material/Add';            // Filled (default)
import { DeleteOutlined } from '@mui/icons-material';     // named import
<AddIcon fontSize="small" color="primary" htmlColor="red" />
```

   - Theme suffixes: `...Outlined`, `...Rounded`, `...TwoTone`, `...Sharp`.
   - Names are PascalCase (`delete_forever` → `DeleteForever`); exceptions `ThreeDRotation`, `FourK`, `ThreeSixty`.
   - Props: `fontSize` (`inherit`, `small`, `medium`, `large`), `color` (theme role or `disabled`/`action`), `htmlColor` (raw CSS), `titleAccess` (a11y title), `sx`.
   - Each icon renders `data-testid="AddIcon"` — useful in tests.
   - **Bundle/dev speed**: path imports are fastest in dev; named root imports need `babel-plugin-import` (or Next.js ≥13.5's `optimizePackageImports`). Never import deeper than 2 levels.

2. **`SvgIcon`** — wrapper for custom SVG (`viewBox` 24x24 default, `inheritViewBox` for arbitrary):

```jsx
<SvgIcon>
  <path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z" />
</SvgIcon>
```

   Or `createSvgIcon(<path .../>, 'Home')` to make a named icon component; `component` prop + svgr for `.svg` files.

3. **`Icon`** — font icons (ligature-based); requires the Material Icons font loaded; `<Icon>star</Icon>`; `baseClassName` for other fonts (e.g., `material-icons-two-tone`, Font Awesome `fa fa-...` with padding override in theme).

Accessibility: decorative icons are `aria-hidden` automatically; semantic icons need `titleAccess` (SVG) or a visually-hidden text alternative (font).
