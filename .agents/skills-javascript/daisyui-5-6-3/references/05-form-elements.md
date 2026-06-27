# 05 — Form Elements

## input

Text input field. Works with any `type` (text, password, email, etc.).

**Class names:**
- component: `input`
- style: `input-ghost`
- color: `input-neutral`, `input-primary`, `input-secondary`, `input-accent`, `input-info`, `input-success`, `input-warning`, `input-error`
- size: `input-xs`, `input-sm`, `input-md`, `input-lg`, `input-xl`

```html
<input type="text" placeholder="Type here" class="input {MODIFIER}" />
```

Use `input` class on the parent when multiple elements sit inside (e.g., with a label).

## textarea

Multi-line text input.

**Class names:**
- component: `textarea`
- style: `textarea-ghost`
- color: `textarea-neutral`, `textarea-primary`, `textarea-secondary`, `textarea-accent`, `textarea-info`, `textarea-success`, `textarea-warning`, `textarea-error`
- size: `textarea-xs`, `textarea-sm`, `textarea-md`, `textarea-lg`, `textarea-xl`

```html
<textarea class="textarea {MODIFIER}" placeholder="Bio"></textarea>
```

## select

Dropdown to pick from a list of options.

**Class names:**
- component: `select`
- style: `select-ghost`
- color: `select-neutral`, `select-primary`, `select-secondary`, `select-accent`, `select-info`, `select-success`, `select-warning`, `select-error`
- size: `select-xs`, `select-sm`, `select-md`, `select-lg`, `select-xl`

```html
<select class="select {MODIFIER}">
  <option>Option</option>
</select>
```

## checkbox

Select or deselect a value.

**Class names:**
- component: `checkbox`
- color: `checkbox-primary`, `checkbox-secondary`, `checkbox-accent`, `checkbox-neutral`, `checkbox-success`, `checkbox-warning`, `checkbox-info`, `checkbox-error`
- size: `checkbox-xs`, `checkbox-sm`, `checkbox-md`, `checkbox-lg`, `checkbox-xl`

```html
<input type="checkbox" class="checkbox {MODIFIER}" />
```

## radio

Select one option from a group.

**Class names:**
- component: `radio`
- color: `radio-primary`, `radio-secondary`, `radio-accent`, `radio-neutral`, `radio-success`, `radio-warning`, `radio-info`, `radio-error`
- size: `radio-xs`, `radio-sm`, `radio-md`, `radio-lg`, `radio-xl`

```html
<input type="radio" name="{group}" class="radio {MODIFIER}" />
```

Each radio group must have a unique `name`. Use different names for separate groups on the same page.

## toggle

Checkbox styled as a switch.

**Class names:**
- component: `toggle`
- color: `toggle-primary`, `toggle-secondary`, `toggle-accent`, `toggle-neutral`, `toggle-success`, `toggle-warning`, `toggle-info`, `toggle-error`
- size: `toggle-xs`, `toggle-sm`, `toggle-md`, `toggle-lg`, `toggle-xl`

```html
<input type="checkbox" class="toggle {MODIFIER}" />
```

## range

Slider to select a value.

**Class names:**
- component: `range`
- color: `range-primary`, `range-secondary`, `range-accent`, `range-neutral`, `range-success`, `range-warning`, `range-info`, `range-error`
- size: `range-xs`, `range-sm`, `range-md`, `range-lg`, `range-xl`
- direction: `range-vertical`

```html
<input type="range" min="0" max="100" value="40" class="range {MODIFIER}" />
```

Must specify `min` and `max` attributes. Use `range-vertical` for vertical slider.

## file-input

File upload input.

**Class names:**
- component: `file-input`
- style: `file-input-ghost`
- color: `file-input-primary`, `file-input-secondary`, `file-input-accent`, `file-input-neutral`, `file-input-info`, `file-input-success`, `file-input-warning`, `file-input-error`
- size: `file-input-xs`, `file-input-sm`, `file-input-md`, `file-input-lg`, `file-input-xl`

```html
<input type="file" class="file-input {MODIFIER}" />
```

## label

Label for input fields. Supports regular and floating variants.

**Class names:**
- component: `label`, `floating-label`

Regular:
```html
<label class="input">
  <span class="label">{label text}</span>
  <input type="text" placeholder="Type here" />
</label>
```

Floating:
```html
<label class="floating-label">
  <input type="text" placeholder="Type here" class="input" />
  <span>{label text}</span>
</label>
```

## fieldset

Groups related form elements with a title and description.

**Class names:**
- component: `fieldset`, `label`
- part: `fieldset-legend`

```html
<fieldset class="fieldset">
  <legend class="fieldset-legend">{title}</legend>
  {form elements}
  <p class="label">{description}</p>
</fieldset>
```

## otp

One-Time Password input for 2FA or passwordless login.

**Class names:**
- component: `otp`
- size: `otp-xs`, `otp-sm`, `otp-md`, `otp-lg`, `otp-xl`
- modifier: `otp-joined`
- color: `otp-primary`, `otp-secondary`, `otp-accent`, `otp-neutral`, `otp-info`, `otp-success`, `otp-warning`, `otp-error`

```html
<label class="otp {MODIFIER}">
  <span></span>
  <span></span>
  <span></span>
  <span></span>
  <input type="text" autocomplete="one-time-code" inputmode="numeric" maxlength="4" pattern="[0-9]{4}" required />
</label>
```

The number of `<span>` elements must match `maxlength` and `pattern`. Always include `autocomplete="one-time-code"` and `inputmode="numeric"` for mobile autofill.

## validator

Changes form element colors to error/success based on validation rules.

**Class names:**
- component: `validator`
- part: `validator-hint`

```html
<input type="email" class="input validator" required />
<p class="validator-hint">Please enter a valid email</p>
```

Use with `input`, `select`, `textarea`.
