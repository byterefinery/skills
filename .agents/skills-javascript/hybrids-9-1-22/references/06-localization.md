# Localization

## Table of Contents

- [localize()](#localize)
- [msg Tagged Template](#msg-tagged-template)
- [msg.html and msg.svg](#msghtml-and-msgsvg)
- [Plural Forms](#plural-forms)
- [Remote Translation](#remote-translation)
- [Chrome.i18n Format](#chromei18n-format)
- [Automatic Template Translation](#automatic-template-translation)
- [Context Hints](#context-hints)
- [CLI: Message Extraction](#cli-message-extraction)
- [Language Detection](#language-detection)

---

## localize()

Register translation dictionaries:

```js
import { localize } from "hybrids";

localize("pl", {
  "Hello ${0}!": {
    message: "Witaj ${0}!",
  },
  "Submit": {
    message: "Wyślij",
    description: "Button label",
  },
});

localize("de", {
  "Hello ${0}!": {
    message: "Hallo ${0}!",
  },
});
```

### Dictionary Format

```js
{
  "Source text": {
    message: "Translated text",        // string or plural object
    description: "Optional context",   // for translators
  },
}
```

- Keys are the source (fallback) text
- `${0}`, `${1}`, etc. are placeholders for interpolated values
- Multiple languages can be registered; the first match wins

---

## msg Tagged Template

Create translatable strings with interpolation:

```js
import { msg } from "hybrids";

const greeting = msg`Hello ${name}!`;
// → "Witaj John!" (if Polish is active)

const count = msg`You have ${n} items`;
// → "Masz 3 elementy" (with plural support)
```

### How It Works

1. Template parts are joined into a key: `"Hello ${0}!"`
2. The key is looked up in the translation dictionary
3. Placeholders are replaced with actual values
4. If no translation is found, the source text is returned (with a console warning if any dictionary is registered)

---

## msg.html and msg.svg

Create translatable templates:

```js
import { msg } from "hybrids";

// HTML
msg.html`Hello ${name}!`
// Returns an UpdateFunction (like html`...`)

// SVG
msg.svg`Circle ${label}`
```

These work like `html`/`svg` but with translation applied to text content before template compilation.

---

## Plural Forms

Use ICU-style plural forms in translations:

```js
localize("en", {
  "You have ${0} items": {
    message: {
      zero: "No items",
      one: "You have 1 item",
      two: "You have 2 items",      // for languages with dual form
      few: "You have ${0} items",   // for Slavic languages
      many: "You have ${0} items",
      other: "You have ${0} items",
    },
  },
});
```

### Usage

```js
msg`You have ${count} items`
// Returns a function: (number) => plural form string

const pluralFn = msg`You have ${count} items`;
const result = pluralFn(5);  // "You have 5 items"
```

In templates with automatic translation, plural forms are resolved automatically based on the first interpolated value.

### Plural Rules

Uses `Intl.PluralRules` for language-specific plural selection. Supported categories: `zero`, `one`, `two`, `few`, `many`, `other`.

---

## Remote Translation

Integrate with external translation services by passing a function:

```js
import { localize } from "hybrids";

// Custom translation function
localize((key, context) => {
  return translationService.translate(key, context);
});
```

The function receives:
- `key` — the source text
- `context` — disambiguation context (from HTML comments)

Return a translated string or a plural function `(number) => string`.

---

## Chrome.i18n Format

Integrate with Chrome extension messaging:

```js
import { localize } from "hybrids";

localize(
  (key, context) => chrome.i18n.getMessage(key, context),
  { format: "chrome.i18n" }
);
```

Keys are automatically converted to Chrome's format:
- `"Hello ${0}!"` → `hello___0___`
- Special characters are replaced with `_`
- `$` is replaced with `@`

---

## Automatic Template Translation

When `localize()` is configured, text content in `html`/`svg` templates is automatically translated:

```js
localize("pl", {
  "Submit": { message: "Wyślij" },
  "Cancel": { message: "Anuluj" },
});

html`
  <button>Submit</button>
  <button>Cancel</button>
`
// → <button>Wyślij</button><button>Anuluj</button>
```

### Rules

- Text nodes are normalized (whitespace trimmed, multiple spaces collapsed)
- Text with only placeholders (e.g., `"${0} ${1}"`) is not translated
- Script and style elements are excluded
- Elements with `translate="no"` are excluded (and their children)

### Disabling Translation

```js
html`
  <div translate="no">
    <code>const x = 1;</code>
  </div>
`
```

---

## Context Hints

Disambiguate translations with HTML comments:

```html
<!-- | button label -->
Submit

<!-- | page title -->
Submit
```

The comment format is `<!-- | context text -->`. The context is used as a secondary lookup key: `"Submit | button label"`.

In `msg` templates, use `|` separator:

```js
msg`Submit | button label`
```

---

## CLI: Message Extraction

Extract translatable messages from source files:

```bash
# Extract from a file
npx hybrids extract ./src/components

# Extract from a directory
npx hybrids extract ./src --output messages.json

# Options
npx hybrids extract ./src --format csv --output messages.csv
```

### Output Formats

- `json` — JSON array of message objects
- `csv` — CSV with columns: key, context, description

### Example JSON Output

```json
[
  {
    "key": "Hello ${0}!",
    "context": "",
    "description": ""
  },
  {
    "key": "Submit",
    "context": "button label",
    "description": ""
  }
]
```

---

## Language Detection

Hybrids automatically detects the browser's language preference:

```js
import { localize } from "hybrids";

// Check active languages
console.log(localize.languages);
// → ["pl-PL", "pl", "en-US", "en"]

// Languages are derived from navigator.languages
// Both full codes (pl-PL) and base codes (pl) are registered
```

### Default Fallback

Use `"default"` as a language code for fallback translations:

```js
localize("default", {
  "Hello ${0}!": { message: "¡Hola ${0}!" },
});
```

The default language is checked last, after all browser languages.

### Lookup Order

1. Full browser language codes (e.g., `pl-PL`)
2. Base language codes (e.g., `pl`)
3. `"default"` (if registered)
4. Source text (fallback)
