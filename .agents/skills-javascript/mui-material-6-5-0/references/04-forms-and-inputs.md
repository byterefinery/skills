# 04 — Forms & Inputs

TextField, the input anatomy, Select, choice controls, sliders/rating, Autocomplete, and buttons.

## Contents

1. [TextField](#textfield)
2. [Input anatomy and composition](#input-anatomy)
3. [Select](#select)
4. [Checkbox, Switch, Radio](#checkbox-switch-radio)
5. [Slider](#slider)
6. [Rating](#rating)
7. [Autocomplete](#autocomplete)
8. [ToggleButton](#togglebutton)
9. [Buttons](#buttons)
10. [Form labels and structure](#form-labels)

## TextField

Complete form control: label + input + helper text. Variants: `outlined` (default), `filled`, `standard`.

```jsx
import TextField from '@mui/material/TextField';

<TextField
  label="Email"
  type="email"
  required
  error={Boolean(error)}
  helperText={error || 'We never share your email.'}
  margin="normal"          // none | dense | normal (vertical spacing)
  size="small"             // medium | small
  fullWidth
/>
```

- Standard form attributes pass through: `type`, `required`, `disabled`, `name`, `value`/`onChange`, `inputProps` (raw `<input>` props), `inputRef`.
- `error` + `helperText` for validation feedback.
- `multiline` turns it into a textarea (auto-sizing; bound with `minRows`/`maxRows`, set `rows` to disable autosizing).
- `select` makes it a Select wrapper (see below).
- Label shrink can be wrong for number/datetime/Stripe inputs — force with `slotProps={{ inputLabel: { shrink: true } }}`.
- Native input properties not on `TextField` can be passed via `slotProps.htmlInput`.
- Performance with many TextFields: `MuiInputBase.defaultProps.disableInjectingGlobalStyles: true` + inject the auto-fill `@keyframes` once via `GlobalStyles`.

### InputAdornment

Prefix/suffix content (icons, actions) inside the input:

```jsx
<TextField
  InputProps={{
    startAdornment: <InputAdornment position="start"><SearchIcon /></InputAdornment>,
    endAdornment: <InputAdornment position="end">…</InputAdornment>,
  }}
/>
```

(v6 deprecates these in favor of `slotProps` — `InputProps` → `slotProps.input`, `inputProps` → `slotProps.htmlInput`; see [09-v6-migration](09-v6-migration.md).)

## Input anatomy

`TextField` composes: `FormControl` (context: label, error, focused, required, margin, size) + `InputLabel` + one of `OutlinedInput`/`FilledInput`/`Input` (all extending `InputBase`, the raw input with ripple/focus states) + `FormHelperText`.

Build custom controls directly from these parts, or read the surrounding `FormControl` context from a child with:

```js
import { useFormControl } from '@mui/material/FormControl';
// returns { variant, margin, size, color, error, focused, required, disabled,
//           fullWidth, hiddenLabel, adornedStart, adornment position setters,
//           onFocus, onBlur, onFilled, onEmpty }
```

## Select

Dropdown built on a hidden custom `<input>` (same styling/props as the text-field variants).

```jsx
<TextField
  select
  label="Age"
  value={age}
  onChange={(e) => setAge(e.target.value)}
  // helperText, error, size, margin all work
>
  <MenuItem value={10}>10</MenuItem>
  <MenuItem value={20}>20</MenuItem>
</TextField>
```

- **No `placeholder` prop** — render a `<MenuItem value="">None</MenuItem>` or use `Autocomplete`.
- Composed form: `FormControl` + `InputLabel` + `Select` + `MenuItem`s. With `outlined` variant the label is duplicated (once on `InputLabel`, once as `Select`'s `label` prop for accessibility).
- `NativeSelect` — native `<select>` (better mobile UX, full browser behavior).
- `multiple` → value is always an array; combine with `MenuItem` checkmarks (`selected`) or `Chip`s.
- `autoWidth` — size to content. `open`/`defaultOpen` control the popup.
- Grouping: `ListSubheader` children (or `<optgroup>` for native).
- **Accessibility**: a label is mandatory — `TextField select label` does it automatically, or pair `InputLabel id` with `Select labelId`.
- Complex needs (combobox, async, creatable, multiselect with chips) → **Autocomplete**.

## Checkbox, Switch, Radio

```jsx
<FormControlLabel
  control={<Checkbox checked={checked} onChange={handleChange} color="secondary" />}
  label="Subscribe"
/>
<Switch checked={on} onChange={onChange} />
<RadioGroup value={value} onChange={onChange} aria-label="view">
  <FormControlLabel value="a" control={<Radio />} label="A" />
</RadioGroup>
```

- `FormControlLabel` wraps the control with a label (clicking the label toggles); `margin="dense"` for tight lists.
- Radio: `RadioGroup` manages exclusivity; `value` on `FormControlLabel` (not on `Radio`).
- `color` (default `primary`; `secondary`/`error`/...), `disabled`, `inputProps={{ 'aria-label': ... }}` for standalone usage.
- These are ripple components — tests need `await act(async () => fireEvent.mouseDown(...))` in v6 (see [08-ssr-and-integrations](08-ssr-and-integrations.md)).

## Slider

```jsx
<Slider
  value={value}
  onChange={(e, v) => setValue(v)}
  defaultValue={30}
  min={0} max={100} step={5}
  marks={[{ value: 0 }, { value: 100, label: 'Max' }]}
  valueLabelDisplay="auto"   // always | auto | off
/>
```

- Controlled: `value` + `onChange`; uncontrolled: `defaultValue`.
- `step` (set `step={null}` + `marks` to snap only to the provided values), `shiftStep` (PageUp/Down granularity — keep it divisible by `step`), `marks={true}` or an array of `{ value, label }`.
- **Range slider**: pass an array to `value`/`defaultValue` (`[10, 50]`) — there is no `multiple` prop. Enforce minimum distance in `onChange` (the handler receives `activeThumb` as the third arg); `disableSwap` stops thumbs swapping on hover-drag.
- `track` — `false` removes the track, `'inverted'` inverts it; `scale` for non-linear value representation.
- `orientation="vertical"`, `size="small"`, `color`, `disabled`.

## Rating

Star rating (built on a hidden radio group — set a unique `name` in forms):

```jsx
<Rating name="rate" value={value} precision={0.5} onChange={(e, v) => setValue(v)} />
```

- `precision` (0.5, 1, 0.1...), `readOnly`, `size`, `emptyIcon`/`icon`, `valueLabelDisplay`.
- Non-English: provide `getLabelText`. Color-only indication must be supplemented with text (WCAG).

## Autocomplete

The power combobox (replacement for react-select/downshift). Two modes: **combo box** (pick from predefined options) and **free solo** (`freeSolo` — arbitrary input).

```jsx
<Autocomplete
  options={options}                      // string[] or objects
  getOptionLabel={(o) => o.label}        // required for object options
  isOptionEqualToValue={(o, v) => o.id === v.id}  // required for object options
  value={value}
  onChange={(e, v) => setValue(v)}
  inputValue={input}
  onInputChange={(e, v, reason) => setInput(v)}
  multiple                              // tags mode
  freeSolo
  groupBy={(o) => o.category}
  renderInput={(params) => <TextField {...params} label="Movie" />}
/>
```

- Two independent controlled states: `value`/`onChange` (selection) and `inputValue`/`onInputChange` (textbox). Control them separately.
- **Memoize the `value` array** in multiple mode — a new array per render re-renders the popup and breaks behavior.
- `filterOptions` — built-in case/accent-insensitive filter; `createFilterOptions({ matchFrom: 'start', limit: 100, stringify })` for customization; pass `(x) => x` to disable (server-side search).
- Async: load on open (`loading` prop) or search-as-you-type (fetch in `onInputChange`, disable filtering).
- `groupBy` requires options sorted by the same dimension (or duplicate headers appear); customize rendering with `renderGroup`.
- `multiple` + `limitTags`, fixed (disabled) tags, checkbox options.
- `renderInput` receives `params` — forward `ref` and `inputProps` (or use `params.InputProps`).
- Keyboard: set `event.defaultMuiPrevented = true` in `onKeyDown` to opt out of default handling (e.g., Enter).
- Virtualize large lists with `react-window` (`renderOption` + `getPopupProps`).
- Headless: `useAutocomplete()` hook (re-exported from `@mui/material`).
- `selectOnFocus`, `clearOnBlur`, `handleHomeEndKeys` — free-solo/creatable UX tuning.

## ToggleButton

Grouped radio/checkbox-like buttons:

```jsx
<ToggleButtonGroup value={align} exclusive onChange={(e, v) => setAlign(v)}>
  <ToggleButton value="left" aria-label="left"><AlignLeftIcon /></ToggleButton>
  ...
</ToggleGroup>
```

- `exclusive` (single) vs multiple (array value). Standalone `ToggleButton` also exists.
- Enforce "always one active" by ignoring `null`/`[]` in `onChange`.
- `size`, `color`, `orientation="vertical"`.

## Buttons

```jsx
<Button variant="contained" color="primary" size="small" startIcon={<AddIcon />} endIcon={<ArrowForwardIcon />}
        disabled loading fullWidth component={RouterLink} to="/x">
  Save
</Button>
```

- `variant`: `text` (default), `contained` (elevation — `disableElevation`), `outlined`.
- `color`: `primary` (default), `secondary`, `error`, `info`, `success`, `warning`, or `inherit`.
- `size`: `small`/`medium` (default)/`large`.
- **`loading`** (v6.4+, replaces `@mui/lab`'s `LoadingButton`): shows a spinner and disables. Value must be `boolean | null` — don't spread conditionals.
- `startIcon`/`endIcon` with spacing; `icon` for icon-only (or use `IconButton`).
- File upload: `component="label"` + visually hidden `<input type="file">`.
- `ButtonBase` — the low-level shared base (ripple, focus, touch ripple) for building custom interactive elements.
- **Disabled buttons**: `pointer-events: none` → no `not-allowed` cursor and no tooltips; override via `.MuiButtonBase-root:disabled { pointer-events: auto; cursor: not-allowed; }` if needed.
- `IconButton` — square icon button (`size`, `color`, `edge="start"|"end"` for app-bar placement, `loading` since v6.4, `badge` via `Badge`).
- `Fab` — floating action button; `size` large/small, `color`, `variant="extended"` (text next to icon). One per screen.
- `ButtonGroup` (v6) — wraps `Button`s (immediate children only) with shared `size`/`color`/`orientation`, `disableElevation`; supports split-button patterns.
- `component` prop for routing: `component={Link}` on any button (see [08-ssr-and-integrations](08-ssr-and-integrations.md)).

## Form labels

- `FormControl` — group container that provides label/error/focus context to children; `required`, `error`, `disabled`, `fullWidth`, `margin`, `size`, `component`.
- `FormLabel` — standalone label (used by ToggleButtonGroup etc.); `required` adds an asterisk.
- `FormControlLabel` — label + control (see Checkbox section).
- `FormHelperText` — helper/error line under inputs (`error`, `disabled`).
