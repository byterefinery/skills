# Forms

Complete reference for Oat's form system.

## Field Container

`data-field` attribute wraps label + input + hint/error. Provides spacing and auto-layout.

```html
<label data-field>
  Name
  <input type="text" placeholder="Enter name" />
</label>
```

For selects (label is separate):

```html
<div data-field>
  <label>Select</label>
  <select>
    <option value="">Choose...</option>
    <option value="a">Option A</option>
  </select>
</div>
```

## Input Types

### Text, Email, Password, URL, Tel, Number, Search

```html
<label data-field>
  Email
  <input type="email" placeholder="you@example.com" />
</label>
```

### Textarea

```html
<label data-field>
  Message
  <textarea placeholder="Your message..."></textarea>
</label>
```

Auto-height, min 5rem, vertical resize.

### Select

```html
<div data-field>
  <label>Option</label>
  <select aria-label="Select an option">
    <option value="">Select...</option>
    <option value="a">A</option>
    <option value="b">B</option>
  </select>
</div>
```

Custom chevron, no appearance.

### Checkbox

```html
<label data-field>
  <input type="checkbox" /> I agree to terms
</label>
```

Inline-flex layout, custom checkmark.

### Radio

```html
<fieldset class="hstack">
  <legend>Preference</legend>
  <label><input type="radio" name="pref"> Option A</label>
  <label><input type="radio" name="pref"> Option B</label>
  <label><input type="radio" name="pref"> Option C</label>
</fieldset>
```

### Switch

```html
<label data-field>
  <input type="checkbox" role="switch" /> Notifications
</label>
```

Uses `role="switch"` on checkbox. Animated thumb.

### Range

```html
<label data-field>
  Volume
  <input type="range" min="0" max="100" value="50" />
</label>
```

Custom thumb, hover scale effect.

### File

```html
<label data-field>
  File
  <input type="file" />
</label>
```

`::file-selector-button` styled to match theme.

### Date/Time

```html
<label data-field>
  Date
  <input type="date" />
</label>
<label data-field>
  DateTime
  <input type="datetime-local" />
</label>
```

## Input Group

`<fieldset class="group">` for inline input combinations.

```html
<fieldset class="group">
  <legend>https://</legend>
  <input type="url" placeholder="subdomain">
  <select>
    <option>.example.com</option>
    <option>.example.net</option>
  </select>
  <button>Go</button>
</fieldset>

<fieldset class="group">
  <input type="text" placeholder="Search" />
  <button>Go</button>
</fieldset>
```

Children are flex items. First/last get border radius. Border between children is transparent unless focused.

## Hint Text

`[data-hint]` inside `data-field` container.

```html
<label data-field>
  Password
  <input type="password" aria-describedby="pw-hint" />
  <small id="pw-hint" data-hint>Min 8 characters</small>
</label>
```

Small, muted text below the input.

## Validation Errors

`aria-invalid="true"` on the field container or input reveals `.error` elements.

```html
<label data-field aria-invalid="true">
  Email
  <input type="email" aria-invalid="true" aria-describedby="email-err" />
  <div id="email-err" class="error" role="status">
    Please enter a valid email
  </div>
</label>
```

- `.error` is `display: none` by default
- Shown when parent has `aria-invalid="true"` or contains an element with `aria-invalid="true"`
- Red border on invalid inputs, red focus ring

### Native Validation

`:user-invalid` pseudo-class also triggers error styling:

```html
<label data-field>
  Email
  <input type="email" required />
  <div class="error">Invalid email</div>
</label>
```

The error shows when the user has interacted and the value is invalid.

## Disabled State

```html
<label data-field>
  Disabled
  <input type="text" value="Cannot edit" disabled />
</label>
```

Opacity 0.5, muted background, not-allowed cursor.

## Focus Ring

```css
:where(input, textarea, select):focus {
  border-color: var(--ring);
  box-shadow: 0 0 0 2px rgb(from var(--ring) r g b / 0.2);
}
```

Ring color controlled by `--ring` variable.

## Fieldset

```html
<fieldset>
  <legend>Personal Info</legend>
  <label data-field>
    Name
    <input type="text" />
  </label>
  <label data-field>
    Email
    <input type="email" />
  </label>
</fieldset>
```

Bordered box with rounded corners, padding.

## Accessibility

- `label` elements auto-associate with child inputs
- `aria-describedby` links inputs to hint/error elements
- `aria-invalid` signals validation state
- `role="status"` on error messages for screen readers
- `:focus-visible` outline for keyboard navigation
- `fieldset`/`legend` for grouping related controls
