# 07 — Recipes

Copy-paste patterns for common MUI tasks.

## Contents

1. [Dark mode toggle (v6 colorSchemes)](#dark-mode-toggle)
2. [Form with validation](#form-with-validation)
3. [Responsive drawer + app bar](#responsive-drawer--app-bar)
4. [Enhanced table (sort, select, paginate)](#enhanced-table)
5. [Autocomplete combobox](#autocomplete-combobox)
6. [Composition and ref forwarding](#composition-and-ref-forwarding)
7. [New button variant via theme](#new-button-variant)
8. [Fixed content offset under app bar](#fixed-content-offset)

## Dark mode toggle

The v6 way: `colorSchemes` + `useColorScheme` (no `ThemeProvider` re-render churn, tab sync, no SSR flicker with CSS variables).

```tsx
// theme.ts — 'use client' if Next.js
import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  cssVariables: true,                 // required for manual toggle without flicker
  colorSchemes: { dark: true },        // enables light + dark schemes
  // cssVariables: { colorSchemeSelector: 'class' },  // manual toggle selector
});
export default theme;
```

```tsx
import { useColorScheme } from '@mui/material/styles';

export function ModeSwitcher() {
  const { mode, setMode } = useColorScheme();
  // mode is undefined on first render — guard it (hydration safety)
  if (mode === undefined) return null;
  return (
    <select value={mode} onChange={(e) => setMode(e.target.value)}>
      <option value="system">System</option>
      <option value="light">Light</option>
      <option value="dark">Dark</option>
    </select>
  );
}
```

- Default mode follows the OS; force with `<ThemeProvider defaultMode="dark">`.
- Per-mode styles: `theme.applyStyles('dark', {...})` inside `sx`/`styled` — never `theme.palette.mode === 'dark'` branches. `applyStyles` exists on **every** v6 theme (with or without `cssVariables`), but with `cssVariables: true` it generates mode-scoped CSS (no runtime re-render).
- Use arrays, not object spreads: `[{ bg: '#e5e5e5' }, (theme) => theme.applyStyles('dark', { bg: '#1c1c1c' })]` — spreading can lose the ordering/specificity the utility relies on.
- SSR flicker prevention with manual toggling: render `<InitColorSchemeScript attribute="class" />` (attribute must match `colorSchemeSelector`) before `<main>` in the root layout, and add `suppressHydrationWarning` on `<html>`.
- `storageManager={null}` on `ThemeProvider` disables persistence (resets on refresh); pass a custom manager for non-localStorage backends.
- `<ThemeProvider disableTransitionOnChange>` for instant scheme switches.

Legacy alternative (still works, less capable): `createTheme({ palette: { mode: 'dark' } })` + `useMediaQuery('(prefers-color-scheme: dark)')` + swapping themes. If both `colorSchemes` and `palette` are set, `palette` wins.

## Form with validation

Controlled form with `TextField` (text, select, checkbox, adornment, multiline):

```tsx
import * as React from 'react';
import { Button, Checkbox, Container, FormControlLabel, MenuItem, TextField } from '@mui/material';

export default function SignupForm() {
  const [form, setForm] = React.useState({
    name: '', email: '', role: '', terms: false, bio: '',
  });
  const [errors, setErrors] = React.useState({});

  const validate = (next) => {
    const e = {};
    if (!next.name.trim()) e.name = 'Name is required';
    if (!/^\S+@\S+\.\S+$/.test(next.email)) e.email = 'Invalid email';
    if (!next.role) e.role = 'Pick a role';
    if (!next.terms) e.terms = 'You must accept the terms';
    return e;
  };

  const setField = (field) => (ev) => {
    const value = field === 'terms' ? ev.target.checked : ev.target.value;
    const next = { ...form, [field]: value };
    setForm(next);
    setErrors((prev) => ({ ...prev, [field]: undefined, ...validate(next) }));
  };

  const submit = async (ev) => {
    ev.preventDefault();
    if (Object.keys(validate(form)).length) return;
    await save(form);
  };

  return (
    <Container maxWidth="sm">
      <form onSubmit={submit} noValidate>
        <TextField label="Name" required value={form.name}
                   error={Boolean(errors.name)} helperText={errors.name}
                   onChange={setField('name')} />
        <TextField label="Email" type="email" required fullWidth margin="normal"
                   value={form.email}
                   error={Boolean(errors.email)} helperText={errors.email}
                   onChange={setField('email')} />
        <TextField select label="Role" required margin="normal" value={form.role}
                   error={Boolean(errors.role)} helperText={errors.role}
                   onChange={setField('role')}>
          <MenuItem value="">None</MenuItem>
          <MenuItem value="dev">Developer</MenuItem>
          <MenuItem value="design">Designer</MenuItem>
        </TextField>
        <TextField label="Bio" multiline minRows={2} margin="normal"
                   value={form.bio} onChange={setField('bio')} />
        <FormControlLabel
          control={<Checkbox checked={form.terms} onChange={setField('terms')} />}
          label="I accept the terms"
        />
        <Button type="submit" variant="contained" disabled={!!Object.values(errors).some(Boolean)}>
          Sign up
        </Button>
      </form>
    </Container>
  );
}
```

Notes: `error` + `helperText` per field; `noValidate` on the form to run your own validation; `select` on `TextField` turns it into a Select (keep `MenuItem`s as children); `required` shows the asterisk (pair with `aria-required` for full a11y when using custom validation).

## Responsive drawer + app bar

Permanent drawer on desktop, temporary (swipeable) on mobile, with a fixed app bar:

```tsx
import * as React from 'react';
import { AppBar, Box, Drawer, Toolbar, Typography, useMediaQuery, useTheme } from '@mui/material';

const DRAWER_WIDTH = 280;

export function Layout({ children }) {
  const theme = useTheme();
  const isDesktop = useMediaQuery(theme.breakpoints.up('md'));
  const [mobileOpen, setMobileOpen] = React.useState(false);

  const drawer = (
    <Box role="presentation" sx={{ width: { xs: '100%', sm: DRAWER_WIDTH } }}>
      {/* nav List here */}
    </Box>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar position="fixed" sx={{ zIndex: (t) => t.zIndex.drawer + 1 }}>
        <Toolbar>
          <Typography variant="h6">App</Typography>
        </Toolbar>
      </AppBar>
      <Box component="nav" sx={{ width: { md: DRAWER_WIDTH } }} aria-label="navigation">
        {isDesktop ? (
          <Drawer variant="permanent" open>
            <Toolbar />
            {drawer}
          </Drawer>
        ) : (
          <Drawer variant="temporary" open={mobileOpen}
                  onClose={() => setMobileOpen(false)}>
            {drawer}
          </Drawer>
        )}
      </Box>
      <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
        <Toolbar />   {/* spacer so content clears the fixed AppBar */}
        {children}
      </Box>
    </Box>
  );
}
```

## Enhanced table

Sort, row selection, and pagination (the canonical MUI enhanced table):

```tsx
function EnhancedTable() {
  const [order, setOrder] = React.useState('asc');
  const [orderBy, setOrderBy] = React.useState('name');
  const [selected, setSelected] = React.useState([]);
  const [page, setPage] = React.useState(0);
  const [rowsPerPage, setRowsPerPage] = React.useState(5);

  const handleSort = (prop) => {
    const nextOrder = order === 'asc' && orderBy === prop ? 'desc' : 'asc';
    setOrder(nextOrder); setOrderBy(prop);
  };

  const handleSelectAll = (e) => {
    setSelected(e.target.checked ? rows.map((r) => r.id) : []);
  };
  const handleSelectRow = (e, id) => {
    setSelected((prev) => e.target.checked ? [...prev, id] : prev.filter((x) => x !== id));
  };

  return (
    <TableContainer component={Paper}>
      <Toolbar sx={{ bgcolor: 'background.paper' }}>
        {selected.length > 0 && <Typography>{selected.length} selected</Typography>}
      </Toolbar>
      <Table sx={{ minWidth: 650 }} aria-label="enhanced table">
        <TableHead>
          <TableRow>
            <TableCell padding="checkbox">
              <Checkbox indeterminate={selected.length > 0 && selected.length < rows.length}
                        checked={selected.length === rows.length}
                        onChange={handleSelectAll} />
            </TableCell>
            {['Name', 'Age'].map((col) => (
              <TableCell key={col} sortDirection={orderBy === col.toLowerCase() ? order : false}>
                <TableSortLabel active={orderBy === col.toLowerCase()}
                                direction={orderBy === col.toLowerCase() ? order : 'asc'}
                                onClick={() => handleSort(col.toLowerCase())}>
                  {col}
                </TableSortLabel>
              </TableCell>
            ))}
          </TableRow>
        </TableHead>
        <TableBody>
          {rows.slice(page * rowsPerPage, (page + 1) * rowsPerPage).map((row) => (
            <TableRow key={row.id} hover sx={{ '&.Mui-selected': { bgcolor: 'primary.main', color: 'common.white' } }}
                      selected={selected.includes(row.id)}>
              <TableCell padding="checkbox">
                <Checkbox checked={selected.includes(row.id)} onChange={(e) => handleSelectRow(e, row.id)} />
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      <TablePagination
        component="tfoot"
        rowsPerPageOptions={[5, 10, 25]}
        count={rows.length}
        page={page}
        onPageChange={(e, p) => setPage(p)}
        rowsPerPage={rowsPerPage}
        onRowsPerPageChange={(e) => { setRowsPerPage(+e.target.value); setPage(0); }}
      />
    </TableContainer>
  );
}
```

(Keep the exact closing tags balanced when adapting — the pattern is: Checkbox column, `TableSortLabel` headers, selected-row styling via the `.Mui-selected` state class, and `TablePagination` 0-based.)

## Autocomplete combobox

Object options with free-solo create-new option:

```tsx
const [options, setOptions] = React.useState([
  { title: 'The Godfather', id: 1 },
  { title: 'Pulp Fiction', id: 2 },
]);
const [value, setValue] = React.useState(null);

const createOption = (title) => {
  const newOption = { title, id: Math.max(0, ...options.map((o) => o.id)) + 1 };
  setOptions([...options, newOption]);
  return newOption;
};

<Autocomplete
  value={value}
  onChange={(e, v) => setValue(v)}
  options={options}
  getOptionLabel={(o) => o.title}
  isOptionEqualToValue={(o, v) => o.id === v.id}
  filterOptions={(x) => x}                 // no client filtering → show "Add X" option
  renderOption={(props, option, { selected }) => (
    <li {...props}>
      {option.title} {selected ? '✓' : ''}
    </li>
  )}
  renderInput={(params) => <TextField {...params} label="Movie" size="small" />}
/>
```

For a "creatable" combobox: set `freeSolo`, `selectOnFocus`, `clearOnBlur`, `handleHomeEndKeys`, and append an `Add "<query>"` option when the query isn't in the list; in `onChange`, if `created` was passed via the event, insert the option first.

## Composition and ref forwarding

Wrapping an MUI component (preserve props + ref + class names):

```tsx
import { forwardRef } from 'react';
import Button from '@mui/material/Button';

export const ForwardedButton = forwardRef(function ForwardedButton(
  { className, ...other }, ref,
) {
  return <Button className={className} ref={ref} {...other} />;
});
```

Rules:

- Spread `...other` last on the DOM-level component so user props win.
- `ref` must reach the underlying DOM node — MUI components forward ref by default ("The ref is forwarded to the root element" in the API docs).
- Custom components used as children of `Tooltip`, transitions, or `Autocomplete renderInput` must forward ref and spread props (including `style` for transitions).
- Prefer `styled()` over wrapping when you only need styles + one extra prop.
- TS trouble with the `component` prop: wrap (above) or cast `styled(...)` results.

## New button variant

Add a `dashed` variant without touching components:

```js
const theme = createTheme({
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          variants: [
            {
              props: { variant: 'dashed' },
              style: { textTransform: 'none', border: `2px dashed ${blue[500]}` },
            },
            {
              props: { variant: 'dashed', color: 'secondary' },
              style: { border: `4px dashed ${red[500]}` },
            },
          ],
        },
      },
    },
  },
});

<Button variant="dashed" color="secondary">Custom</Button>
```

TypeScript: augment the component module:

```tsx
declare module '@mui/material/Button' {
  interface ButtonPropsVariantOverrides { dashed: true }
}
```

## Fixed content offset

Content hidden under a fixed `AppBar` — pick one:

```jsx
// 1. sticky instead of fixed (simplest)
<AppBar position="sticky">

// 2. spacer Toolbar
<AppBar position="fixed"><Toolbar>...</Toolbar></AppBar>
<Toolbar />

// 3. styled offset using the toolbar mixin
const Offset = styled('div')(({ theme }) => theme.mixins.toolbar);
```
