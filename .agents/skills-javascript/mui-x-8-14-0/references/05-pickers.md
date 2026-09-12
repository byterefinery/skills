# Date and Time Pickers

`@mui/x-date-pickers` (Community) and `@mui/x-date-pickers-pro` (range pickers). Values are instances of your chosen date library — MUI X does not store plain `Date`s unless you use the Moment/Day.js adapters with Date values.

- [Setup: adapter + provider](#setup-adapter--provider)
- [Component families](#component-families)
- [Controlled value](#controlled-value)
- [Views and the v8 Next action](#views-and-the-v8-next-action)
- [Fields](#fields)
- [Validation and disabling](#validation-and-disabling)
- [Localization](#localization)
- [Shortcuts](#shortcuts)
- [Customization](#customization)
- [Range pickers (Pro)](#range-pickers-pro)
- [Testing](#testing)

## Setup: adapter + provider

Exactly one adapter per app, matching the installed date library:

```tsx
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
// alternatives:
// import { AdapterDateFnsV2 } from '@mui/x-date-pickers/AdapterDateFnsV2';
// import { AdapterLuxon } from '@mui/x-date-pickers/AdapterLuxon';
// import { AdapterMoment } from '@mui/x-date-pickers/AdapterMoment';

<LocalizationProvider dateAdapter={AdapterDayjs} locale="en" formatLocale="en">
  <App />
</LocalizationProvider>;
```

- Wrap the app root once; don't repeat providers per component.
- Special adapters: `AdapterDateFnsJalali`, `AdapterMomentJalaali`, `AdapterMomentHijri` for non-Gregorian calendars.
- TypeScript: the adapter overrides the global `PickerValidDate` type. If it resolves to `any` (adapter imported outside the TS project), add `import type {} from '@mui/x-date-pickers/AdapterDayjs';`.

## Component families

Three axes per component: **what** (date / time / date-time), **interaction** (field vs picker vs calendar/clock), **container** (responsive / desktop / mobile / static):

| What | Field (no popover) | Picker (popover) | Bare |
|---|---|---|---|
| Date | `DateField` | `DatePicker` | `DateCalendar` |
| Time | `TimeField` | `TimePicker` | `TimeClock` |
| Date + time | `DateTimeField` | `DateTimePicker` | — |
| Date range (Pro) | `SingleInputDateRangeField` / `MultiInputDateRangeField` | `DateRangePicker` | `DateRangeCalendar` |
| DateTime range (Pro) | `SingleInputDateTimeRangeField` / `MultiInput...` | `DateTimeRangePicker` | — |
| Time range (Pro, new v8) | `SingleInputTimeRangeField` / `MultiInputTimeRangeField` | `TimeRangePicker` | — |

Container variants per picker: `DatePicker` (responsive: desktop popover above md, mobile bottom sheet below), `DesktopDatePicker`, `MobileDatePicker`, `StaticDatePicker` (no popover, no field — calendar only).

## Controlled value

```tsx
const [value, setValue] = React.useState<Dayjs | null>(null);
<DatePicker value={value} onChange={(v) => setValue(v)} />;
```

- `value` — `Date | null` (library-specific via `PickerValidDate`); range pickers take `[start, end]`.
- `onChange(value, context)` — `context.context` identifies the trigger (`picker` vs `field`); `context.validationError` when invalid.
- `referenceDate` — the date shown when `value` is null (default: today). For ranges: `referenceDate: [startRef, endRef]`.
- `minDate` / `maxDate` — hard bounds (disable outside dates).
- v8: partially filled field values (e.g. day entered, month not) are treated as `null` in `onChange` until complete.
- `closeOnSelect` — default updated in v8 for some components (date picks close the picker; time does not by default) — see migration notes.

## Views and the v8 Next action

v8 breaking change: pickers **no longer auto-switch** between date and time views, nor between the start and end positions of a range. The user explicitly clicks the **Next** action in the action bar (and **Previous** to go back). If you need programmatic view control:

- `views` — restrict which views are available, e.g. `['years', 'months', 'days', 'hours', 'minutes']` on `DateTimePicker`.
- `openView`, `onViewChange`, `onSelectedRangePositionChange` (ranges: which input the calendar targets).
- `hideDefaultActions` / `actions` on the action bar to add custom buttons.

## Fields

Fields are section-based text inputs (v8: new accessible DOM structure — each editable section is its own input-like element):

- `DateField`, `TimeField`, `DateTimeField` (and range field variants).
- Editable sections are configured by the field; `shouldDisableSection(section)` disables one (e.g. `shouldDisableSection="month"`).
- `onSectionChange`, `onEnter`/`onBlur` for per-section logic.
- Keyboard: arrow keys move between sections, `Enter` submits (v8 fixed form submission on Enter with the accessible DOM).
- Range fields: `MultiInputDateRangeField` (two inputs, start/end) vs `SingleInputDateRangeField` (one input, "start – end" text with two editable parts).

## Validation and disabling

- `shouldDisableDate(date)` / `shouldDisableTime(date, 'hours' | 'minutes' | 'seconds')` — return true to grey out.
- `shouldError` — custom error text for the helper line.
- `validate` / `shouldDisableDate` interplay: `minDate`/`maxDate` are separate from `shouldDisableDate`.
- `disablePast` / `disableFuture` shorthands.
- Field error state: `slotProps.field` or `error` prop.

## Localization

- `locale` on `LocalizationProvider` sets calendar text (day names, months, week start) via the adapter's locale.
- `formatLocale` for value formatting in fields.
- `format` / `formats` override patterns (library-specific, e.g. `format={{ year: 'numeric' }` style objects per adapter).
- `weekDayFormat`, `yearMonthFormat` on calendars.
- Day order and month-year order follow the locale.

## Shortcuts

```tsx
<DatePicker
  shortcuts={[
    { label: 'Today', onClick: (setDate, value) => setDate(value?.startOf('day') ?? startOfToday) },
    { label: 'Start of month', ... },
  ]}
/>;
```

`shortcuts` array with `label`, `onClick(setValue, current)`, optional `autoFocus`. Custom shortcut component via `slots.shortcut`.

## Customization

- `slots` / `slotProps`: `field`, `layout` (whole popover content), `toolbar` (calendar top bar), `openPicker` (custom open button replacing the default adornment), `calendar`, `clock`, `desktopAnchor`, `inputAdornment`, `actionBar`.
- `slotProps.field` to style the underlying TextField (all standard TextField props pass through).
- Custom opening button: `slots.openPicker` + `slotProps.openPicker` (component receives `onOpen`/`onClose`/`onToggle`).
- `disableOpenPicker` (deprecated in v8 — use `slots.openPicker: null` or a no-op instead).
- `ThemeProvider` + `themeAugmentation`: `import type {} from '@mui/x-date-pickers/themeAugmentation';` then `MuiDatePicker`, `MuiDateCalendar`, …
- Mobile pickers: v8 allows **field editing on mobile pickers** (⏩ change); default fields for range pickers changed (⏩).

## Range pickers (Pro)

```tsx
import { DateRangePicker } from '@mui/x-date-pickers-pro/DateRangePicker';

const [range, setRange] = React.useState<[Dayjs, Dayjs] | null>(null);
<DateRangePicker value={range} onChange={setRange} />;
```

- `value`: `[start, end]` (or null); `onChange` gives the tuple.
- `DateRangeCalendar` — dual-calendar range selection; `rangePosition` (`start`/`end`) tells which end the calendar edits; `onRangePositionChange`.
- `TimeRangePicker` (new in v8): duration-based time ranges.
- `shouldDisableDate` receives `(date, rangePosition)` in range components.
- Single/multi input variants control whether start/end share one input.

## Testing

- Responsive components switch DOM by viewport — pin width in tests or test the `Desktop`/`Mobile` variants directly.
- Fields: sections are separate elements; query by section role/label, not the whole input value.
- Date library timezones: set a fixed TZ in the test env to keep adapter output deterministic.
