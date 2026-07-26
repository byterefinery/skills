---
title: Forms
---

# Forms

Form elements are styled automatically. Wrap inputs in `<label>` for proper association.

## Text Input

```html
<label data-field>
  Name
  <input type="text" placeholder="Enter your name" />
</label>
```

## Email Input

```html
<label data-field>
  Email
  <input type="email" placeholder="you@example.com" />
</label>
```

## Password Input with Hint

```html
<label data-field>
  Password
  <input type="password" placeholder="Password" aria-describedby="password-hint" />
  <small id="password-hint" data-hint>Minimum 8 characters</small>
</label>
```

## Select

```html
<div data-field>
  <label>Select</label>
  <select aria-label="Select an option">
    <option value="">Select an option</option>
    <option value="a">Option A</option>
    <option value="b">Option B</option>
  </select>
</div>
```

## Textarea

```html
<label data-field>
  Message
  <textarea placeholder="Your message..."></textarea>
</label>
```

Min-height: 5rem, resizable vertically.

## Checkbox

```html
<label data-field>
  <input type="checkbox" /> I agree to the terms
</label>
```

## Radio Buttons

```html
<fieldset class="hstack">
  <legend>Preference</legend>
  <label><input type="radio" name="pref">Option A</label>
  <label><input type="radio" name="pref">Option B</label>
  <label><input type="radio" name="pref">Option C</label>
</fieldset>
```

## Switch (Toggle)

Use `role="switch"` on a checkbox:

```html
<label data-field>
  <input type="checkbox" role="switch" />
  <span data-hint>Enable notifications</span>
</label>
```

## Range Slider

```html
<label data-field>
  Volume
  <input type="range" min="0" max="100" value="50" />
</label>
```

## File Input

```html
<label data-field>
  File
  <input type="file" />
</label>
```

## Date and Time Inputs

```html
<label data-field>
  Date and time
  <input type="datetime-local" />
</label>

<label data-field>
  Date
  <input type="date" />
</label>
```

## Disabled Input

```html
<label data-field aria-disabled>
  Disabled
  <input type="text" placeholder="Disabled" disabled />
  <span data-hint>This field is read-only</span>
</label>
```

## Input Groups

Use `class="group"` on `<fieldset>` to combine inputs with buttons or labels:

```html
<fieldset class="group">
  <legend>https://</legend>
  <input type="url" placeholder="subdomain">
  <select aria-label="TLD">
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

The `legend` inside a group is styled as an inline label attached to the left of the inputs.

## Fieldset

```html
<fieldset>
  <legend>Group Label</legend>
  <label><input type="text" placeholder="Field 1"></label>
  <label><input type="text" placeholder="Field 2"></label>
</fieldset>
```

Bordered container with padding.

## Validation Errors

Use `aria-invalid="true"` on field containers to reveal `.error` messages:

```html
<div data-field aria-invalid="true">
  <label for="email-input">Email</label>
  <input type="email" id="email-input" aria-invalid="true" aria-describedby="email-error" />
  <div id="email-error" class="error" role="status">Please enter a valid email</div>
</div>
```

The `.error` element is hidden by default and revealed when the parent `[data-field]` has `aria-invalid="true"` or contains an element with `aria-invalid="true"`.

## Field Container (`data-field`)

```html
<label data-field>
  Field label
  <input type="text" />
  <span data-hint>Helper text appears below the input</span>
</label>
```

- `margin-block-end: var(--space-4)`
- `[data-hint]` and `.error` elements are full-width below the input
- `.error` styled in `--danger` color, hidden until `aria-invalid="true"`

## Complete Form Example

```html
<form>
  <label data-field>
    Name
    <input type="text" placeholder="Full name" />
  </label>

  <label data-field>
    Email
    <input type="email" placeholder="you@example.com" />
  </label>

  <label data-field>
    Password
    <input type="password" placeholder="Password" />
    <small data-hint>Minimum 8 characters</small>
  </label>

  <label data-field>
    Message
    <textarea placeholder="Your message..."></textarea>
  </label>

  <label data-field>
    <input type="checkbox" /> I agree to the terms
  </label>

  <button type="submit">Submit</button>
</form>
```

## Focus States

Inputs get `border-color: var(--ring)` and `box-shadow: 0 0 0 2px` ring on focus. Invalid inputs get `border-color: var(--danger)` and danger-colored ring.

## Input Styling Details

- **Width**: 100% (full width)
- **Font**: `var(--font-sans)`, `var(--text-7)` (0.875rem)
- **Padding**: `var(--space-2)` vertical, `var(--space-3)` horizontal
- **Border**: `1px solid var(--input)`
- **Border radius**: `var(--radius-medium)` (0.375rem)
- **Background**: `var(--background)`
- **Placeholder**: `var(--muted-foreground)`
- **Disabled**: `var(--muted)` background
