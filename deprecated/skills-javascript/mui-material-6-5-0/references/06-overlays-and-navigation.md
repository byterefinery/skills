# 06 — Overlays & Navigation

Modal and the components built on it, floating surfaces, tooltips, snackbars, and navigational components.

## Contents

1. [Modal](#modal)
2. [Dialog](#dialog)
3. [Drawer](#drawer)
4. [Menu](#menu)
5. [Popover and Popper](#popover-and-popper)
6. [Tooltip](#tooltip)
7. [Snackbar](#snackbar)
8. [Tabs](#tabs)
9. [Breadcrumbs](#breadcrumbs)
10. [Pagination](#pagination)
11. [Stepper](#stepper)
12. [BottomNavigation](#bottomnavigation)
13. [SpeedDial](#speeddial)
14. [Accordion](#accordion)

## Modal

Low-level overlay: backdrop, scroll lock, focus trap, ARIA roles, stacking. Built on it: Dialog, Drawer, Menu, Popover.

```jsx
<Modal
  open={open}
  onClose={(e) => setOpen(false)}   // reasons: 'backdropClick', 'escapeKeyDown'
  aria-labelledby="title" aria-describedby="desc"
>
  <Box sx={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', p: 4, bgcolor: 'background.paper' }}>
    ...
  </Box>
</Modal>
```

- `keepMounted` — keep (hidden) content in the DOM when closed (SEO, expensive trees).
- `disablePortal` — required for SSR (no `createPortal` on the server); renders inline in that case.
- `container` — portal target (default `document.body`).
- Transitions: child must forward `style` + `ref`, take `in`, and call `onEnter`/`onExited`; built-in support for `react-transition-group` and `react-spring`.
- Nested modals: OK for simple cases (select inside dialog); avoid stacking more than two or two backdrops.
- Fixed-positioned elements shift when the modal locks scroll — apply the `.mui-fixed` class to elements that should be compensated.

## Dialog

Modal window composed of: `Dialog` + `DialogTitle` + `DialogContent`/`DialogContentText` + `DialogActions` (+ optional `Slide` transition).

```jsx
<Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
  <DialogTitle>Set scheduling</DialogTitle>
  <DialogContent><DialogContentText>...</DialogContentText>...</DialogContent>
  <DialogActions>
    <Button onClick={close}>Cancel</Button>
    <Button onClick={save}>Save</Button>
  </DialogActions>
</Dialog>
```

- `maxWidth` `xs`-`lg`/number + `fullWidth` (fill to max), `fullScreen` (responsive: `fullScreen={useMediaQuery(theme.breakpoints.down('md'))}`).
- `scroll="paper"` (content scrolls in the paper) vs `scroll="body"` (title pinned, body scrolls).
- Alert dialogs: no title, one question + actions.
- `TransitionComponent` swaps the default Grow (e.g., `Slide` for a bottom-sheet feel).
- `PaperProps` → v6: `slotProps.paper`.
- Non-modal pattern: `Dialog` with `keepMounted` + no backdrop interaction for cookie banners (community pattern).
- Draggable: pass `react-draggable`'s `Draggable` as `PaperComponent` (→ `slots.paper` in v6).
- For imperative dialogs, MUI Toolpad's `useDialogs` (alert/confirm/prompt).

## Drawer

Sidebar; `variant`: `temporary` (modal-ish, above content), `persistent` (pushes content), `permanent` (always visible; recommended desktop default).

```jsx
<Drawer
  variant="temporary"
  open={open}
  onClose={() => setOpen(false)}
  anchor="left"            // left | right | top | bottom
  ModalProps={{ keepMounted: true }}
>
  <Box sx={{ width: 280 }} role="presentation">
    <List>...</List>
  </Box>
</Drawer>
```

- `SwipeableDrawer` — touch swipe (2kB extra; `disableBackdropTransition={!iOS}`, `disableDiscovery={iOS}` for iOS; `edge` prop for a visible closed edge).
- Responsive recipe: `temporary` on mobile + `persistent` on desktop via `useMediaQuery` — see [07-recipes](07-recipes.md).
- `MiniDrawer` pattern: persistent narrow icon rail that expands on hover/click.
- Clip under a fixed app bar: `variant="permanent"` + an empty `<Toolbar />` as the drawer's first child.
- `elevation` (default 16); set content width explicitly (e.g., `sx={{ width: { xs: 280, sm: 300 } }}` on the paper).

## Menu

Popup of choices anchored to a trigger (uses Popover internally).

```jsx
const [anchorEl, setAnchorEl] = React.useState(null);
const open = Boolean(anchorEl);

<IconButton onClick={(e) => setAnchorEl(e.currentTarget)} aria-haspopup="true" aria-expanded={open}>
  <MoreVertIcon />
</IconButton>
<Menu anchorEl={anchorEl} open={open} onClose={(e) => setAnchorEl(null)}>
  <MenuItem onClick={() => setAnchorEl(null)}>Profile</MenuItem>
  <Divider />
  <MenuItem selected>Current</MenuItem>
</Menu>
```

- `anchorOrigin`/`transformOrigin` for positioning (e.g., open above the anchor).
- `dense` (on `MenuList`) for tighter lists; internal scroll for long menus via `slotProps.paper={{ style: { maxHeight: 320 } }}`.
- `variant` (default `selectedMenu`): initial focus goes to the selected item; `variant="menu"` skips it and focuses the menu list itself.
- `MenuList` — composable focus manager for building custom menus (e.g., with `Popper` instead of Popover, or without scroll blocking).
- Grouping via `ListSubheader`; context menus (right-click) via `onContextMenu` + `mousePosition` anchor.
- `MenuItem` = styled `ListItem` (icon/avatar/text/secondaryAction all work).
- The anchor element should be kept mounted while open (or use `anchorEl` state as above).

## Popover and Popper

- **`Popover`** — self-positioning popup with backdrop and focus handling; `anchorEl` (DOM node — **not** a ref object; use a ref-callback or state so the node exists), `open`, `onClose`, `anchorOrigin`, `transformOrigin`, `slotProps.paper`, `disableAutoFocus`, `keepMounted`.
- **`Popper`** — raw Popper.js positioning without backdrop/focus (lighter, non-modal); `anchorEl` (node), `open`, `placement` (12 options), `modifiers` (Popper.js modifiers, e.g., `offset`), `transition`.
- Both need DOM-node anchors: pass the node itself (from `e.currentTarget` in the handler, or a `ref` callback stored in state), never the ref object — React can't re-render on ref changes.
- Common trio for a custom dropdown: trigger + state + `Popper`/`Popover` + `Grow`/`Fade` transition.

## Tooltip

Hover/focus/tap text hint.

```jsx
<Tooltip title="Delete" arrow placement="top-start"
         enterDelay={400} disableInteractive={false}>
  <Button>Delete</Button>
</Tooltip>
```

- `placement` — 12 positions; `arrow` adds a pointer.
- Delays: `enterDelay` (default 100ms), `enterNextDelay`, `enterTouchDelay` (default 700ms), `leaveDelay`, `leaveTouchDelay`; `followCursor` (v6) makes the tooltip track the pointer.
- Listeners: `disableHoverListener`, `disableTouchListener`, `disableFocusListener`; `describeChild` marks the title as an accessible description.
- `disableInteractive` (default true) — set false to keep the pointer inside the tooltip (for links/inputs).
- Distance: `slotProps.popper={{ modifiers: [{ name: 'offset', options: { offset: [0, 8] } }] }}`.
- **Custom child components must spread props and forward ref** (Tooltip attaches listeners + ref); class components need a forwardRef wrapper.
- **Disabled elements** don't fire mouse events — wrap the disabled control in a `span` (or use `slotProps.tooltip`'s wrapper) so the tooltip still shows.
- `slotProps.tooltip` for styling the tooltip content.

## Snackbar

Floating toast for non-critical notifications.

```jsx
<Snackbar
  open={open}
  autoHideDuration={4000}
  onClose={handleClose}
  anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
  message="Saved"
  action={<Button size="small" color="inherit" onClick={undo}>Undo</Button>}
>
</Snackbar>
```

- `SnackbarContent` for custom message/action layout; swap the transition (default Grow) with `slots.transition` (Slide common).
- `onClose(event, reason)` — reasons include `'clickaway'`, `'escapeKeyDown'`; call `event.preventDefault()` in one handler when stacking to make Escape close only the topmost.
- Use `Alert` inside `Snackbar` for severity-styled toasts.
- With a mobile FAB: anchor above it (`anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}` + `sx={{ bottom: 88 }}` or a wrapper).
- Stacking many snackbars: use notistack or Toolpad's `useNotifications` (MUI does not stack them natively — show one at a time).
- Difference vs Alert (in-flow) vs Dialog (blocking, critical): snackbars never block interaction.

## Tabs

```jsx
<Tabs value={value} onChange={(e, v) => setValue(v)} aria-label="..."
      variant="scrollable" scrollButtons="auto" centered fullWidth>
  <Tab label="Overview" value={0} icon={<HomeIcon />} iconPosition="start" disabled />
</Tabs>
```

- `variant`: `standard` (default), `scrollable`, `fullWidth`; `centered`; `orientation="vertical"`; `allowScrollButtonsMobile`; `selectionFollowsFocus` (ARIA keyboard behavior switch).
- `Tab`: `label`, `icon` (all icons or all text, not mixed), `iconPosition`, `disabled`, `color`, `value` (anything hashable; default = index).
- Panels: plain conditional rendering with matching `value`, or `@mui/lab`'s `TabContext`/`TabList`/`TabPanel` (handles ARIA wiring: `aria-controls`/`aria-labelledby`/`role="tabpanel"`).
- Tabbed navigation: `component={Link}` on `Tab`.
- Ripple component — tests need the `act`/`mouseDown` pattern.

## Breadcrumbs

```jsx
<Breadcrumbs aria-label="navigation">
  <Typography color="text.disabled">Library</Typography>
  <Link underline="hover" color="inherit" href="#data">Data</Link>
  <Typography color="text.primary">Data Management</Typography>
</Breadcrumbs>
```

- `separator` (default `>`; `chevron` shows a `ChevronRightIcon`), `maxItems` (collapse middle), `slots`/`slotProps` for separators/items.
- Last item is typically a `Typography` (current page), previous items links.

## Pagination

Page-number list for SEO-friendly pagination (**1-based**).

```jsx
<Pagination count={10} page={page} color="primary"
  onChange={(e, p) => setPage(p)}
  siblingCount={1} boundaryCount={1}
  showFirstButton showLastButton size="large"
  renderItem={(item) => (
    <PaginationItem
      slots={{ previous: ArrowBackIcon, next: ArrowForwardIcon, first: FirstIcon, last: LastIcon }}
      {...item}
    />
  )}
/>
```

- `variant` `text` (default)/`outlined`; `shape` `circular` (default)/`rounded`; router integration via `component={Link}`.
- `TablePagination` instead for tables (**0-based**, rows-per-page).
- Headless `usePagination()` hook for custom rendering.

## Stepper

Multi-step wizard: `Stepper` + `Step` + `StepLabel` (+ optional `StepContent`, `StepButton`, `StepIcon`, `StepConnector`).

```jsx
<Stepper activeStep={active} alternativeLabel>
  <Step>
    <StepLabel>Select campaign</StepLabel>
  </Step>
  <Step>
    <StepLabel>Confirm</StepLabel>
    <StepContent>...</StepContent>
  </Step>
</Stepper>
```

- `activeStep` (0-based; `-1` = none), `orientation` `horizontal`/`vertical`, `nonLinear` (free navigation; you manage `completed`/`disabled` per step), `alternativeLabel` (labels below icons), `slotProps` for connectors.
- Errors: `error` prop on `Step` + custom `StepIcon`.
- `MobileStepper` — compact mobile variant (`variant`: `text`/`dots`/`progress`, `nextButton`/`backButton` or a custom `slots`).
- Step content unmounts when closed — `StepContent TransitionProps={{ unmountOnExit: false }}` to keep it.

## BottomNavigation

Mobile bottom bar, 3-5 destinations.

```jsx
<BottomNavigation value={val} onChange={(e, v) => setVal(v)} showLabels>
  <BottomNavigationAction label="Current" icon={<HomeIcon />} value="home" />
</BottomNavigation>
```

- `showLabels` (3 actions) vs icons-only for inactive (4-5 actions); `onChange` gives the new value (not an event index).
- Fixed: wrap in a fixed-position container.

## SpeedDial

FAB that expands into 3-6 actions.

```jsx
<SpeedDial
  icon={<AddIcon />}
  direction="up"
  ariaLabel="SpeedDial example"
  open={open} onOpen={() => setOpen(true)} onClose={() => setOpen(false)}
>
  <SpeedDialAction icon={<PrintIcon />} tooltipTitle="Print" tooltipPlacement="left" />
</SpeedDial>
```

- `open`/`onOpen`/`onClose` for control; `SpeedDialIcon` with `icon`/`openIcon`; `SpeedDialAction` requires `tooltipTitle` (a11y).
- `direction`: `up` (default), `down`, `left`, `right`; `onClose` receives `(event, reason)` with reasons `toggle`, `blur`, `mouseLeave`, `escapeKeyDown`.

## Accordion

Expandable sections: `Accordion` + `AccordionSummary` + `AccordionDetails` (+ optional `AccordionActions`).

```jsx
<Accordion expanded={expanded === 'p1'} onChange={(e, isExp) => setExpanded(isExp ? 'p1' : false)}>
  <AccordionSummary expandIcon={<ExpandMoreIcon />} aria-controls="p1-content" id="p1-header">
    <Typography>Is it accessible?</Typography>
  </AccordionSummary>
  <AccordionDetails>...</AccordionDetails>
</Accordion>
```

- `defaultExpanded`, `disabled`, `TransitionComponent`/`TransitionProps` (deprecated in favor of `slots.transition`/`slotProps.transition`).
- **v6 DOM change**: the summary is wrapped in a heading (`<h3>`) per the W3C Accordion pattern — since v6.3 the root is a `<button>` with `span` content. Style accordingly (no `Typography` `<p>` inside; use `component="span"`), and change the heading level with `slotProps.heading.component`.
- Controlled: `expanded` + `onChange(event, isExpanded)` per Accordion (manage the open id yourself).
