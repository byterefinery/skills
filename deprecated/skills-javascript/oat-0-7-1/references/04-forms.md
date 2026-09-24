# Forms

All form elements are styled automatically. Wrap inputs in `<label>` for proper association and spacing.

## Basic form

```html
<form>
  <label data-field>
    Name
    <input type="text" placeholder="Enter your name" />
  </label>

  <label data-field>
    Email
    <input type="email" placeholder="you@example.com" />
  </label>

  <label data-field>
    Message
    <textarea placeholder="Your message..."></textarea>
  </label>

  <button type="submit">Submit</button>
</form>
```

## Input types

All standard input types are styled:

```html
<input type="text">
<input type="email">
<input type="password">
<input type="url">
<input type="number">
<input type="date">
<input type="datetime-local">
<input type="time">
<input type="file">
<input type="color">
<input type="range">
```

## Select

```html
<div data-field>
  <label>Select</label>
  <select aria-label="Choose an option">
    <option value="">Select an option</option>
    <option value="a">Option A</option>
    <option value="b">Option B</option>
  </select>
</div>
```

Custom chevron via inline SVG background image.

## Textarea

```html
<textarea placeholder="Your message..." rows="4"></textarea>
```

Auto-height with `min-height: 5rem`, vertical resize.

## Checkbox

```html
<label>
  <input type="checkbox" /> I agree to the terms
</label>
```

Custom-styled with checkmark mask image.

## Radio

```html
<fieldset class="hstack">
  <legend>Preference</legend>
  <label><input type="radio" name="pref"> Option A</label>
  <label><input type="radio" name="pref"> Option B</label>
  <label><input type="radio" name="pref"> Option C</label>
</fieldset>
```

Custom-styled with filled circle mask.

## Switch (toggle)

```html
<label>
  <input type="checkbox" role="switch"> Notifications
</label>
```

Pill-shaped toggle with sliding thumb. Uses `role="switch"` on a checkbox.

## Range slider

```html
<label data-field>
  Volume
  <input type="range" min="0" max="100" value="50" />
</label>
```

Custom track and thumb styling for WebKit and Firefox.

## Fieldset and legend

```html
<fieldset>
  <legend>Group label</legend>
  <label><input type="text" placeholder="Field 1"></label>
  <label><input type="text" placeholder="Field 2"></label>
</fieldset>
```

## Input group (inline combined)

Use `class="group"` on `<fieldset>` to join inputs with buttons or labels:

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

## Hint text

Use `[data-hint]` or `<small>` inside a `[data-field]` container:

```html
<label data-field>
  Password
  <input type="password" aria-describedby="pwd-hint" />
  <small id="pwd-hint" data-hint>Must be at least 8 characters</small>
</label>
```

## Validation errors

Set `aria-invalid="true"` on the field container to reveal error messages:

```html
<div data-field aria-invalid="true">
  <label for="email">Email</label>
  <input type="email" id="email" aria-invalid="true" aria-describedby="email-err" />
  <div id="email-err" class="error" role="status">Please enter a valid email</div>
</div>
```

The `.error` element is hidden by default and shown when the parent has `aria-invalid="true"` or contains an input with `aria-invalid="true"`.

## Disabled state

```html
<label data-field>
  Disabled
  <input type="text" disabled />
</label>
```

Muted background, `cursor: not-allowed`, reduced opacity.

## Focus ring

```css
:focus-visible {
  outline: 2px solid var(--ring);
  outline-offset: 2px;
}
```

Custom ring color on focus, only for keyboard navigation.
