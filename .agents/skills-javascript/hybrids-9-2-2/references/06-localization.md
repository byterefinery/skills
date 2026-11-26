# Localization

Seamless, fully featured localization. Template text content is translated **automatically at compile time**; the `msg` helper covers plural forms, HTML content, and non-template contexts. The process is global — every component using the template engine picks up messages initialized with `localize`.

## Table of Contents

- [Template translation](#template-translation)
- [Keys, descriptions & context](#keys-descriptions--context)
- [Disabling translation](#disabling-translation)
- [msg helper](#msg-helper)
- [Plural forms](#plural-forms)
- [msg.html & msg.svg](#msghtml--msgsvg)
- [localize](#localize)
- [Async sources](#async-sources)
- [Custom translation functions](#custom-translation-functions)
- [CLI extraction](#cli-extraction)

---

## Template translation

Text content is translated once, when the first instance of a component using the template renders. After compilation the template body stores the target messages — template translation does **not** support dynamic language switching, plural forms, or HTML content (use `msg` for those).

Adding translation usually requires zero source changes:

```js
import { define, html, localize } from "hybrids";

export default define({
  tag: "my-element",
  name: "",
  render: ({ name }) => html`
    <div>Hello ${name}!</div>
  `,
});

localize("pl", {
  "Hello ${0}!": { message: "Witaj ${0}!" },
});
```

## Keys, descriptions & context

- The key is the trimmed text content; expressions become `${0}`, `${1}`, … placeholders (ascending from zero, stable when expressions are added). Expression order may change in translations (`Values: ${1}, ${0}` is valid)
- An HTML comment immediately before the text content adds metadata: `<!-- description | context -->`
- With a context, the key is `text | context`; the context is never added to missing translations — the plain key is the fallback
- `<script>` and `<style>` elements are omitted automatically

## Disabling translation

`translate="no"` skips the element's text content and its descendants:

```js
render: () => html`
  <div>
    <div>Translated text</div>
    <div translate="no">MyCompany © 2022</div>
  </div>
`;
```

## msg helper

Manual translation for complex scenarios; usable outside templates. The key string uses the same expression rules; `|` splits description/context (escape as `&#124;` when literal):

```js
msg`This is a message with ${value} | description | context`: string
```

- For attribute content: `html`<my-button name="${msg`Submit`}">`
- **Avoid `msg` for static template text** — it creates a dynamic expression translated on every update; automatic template translation is cheaper

## Plural forms

If the dictionary value is a plural-forms object, `msg` uses the first dynamic expression value (a cardinal number) to pick the form via `Intl.PluralRules`. Forms: `zero`, `one`, `two`, `few`, `many`, `other`; missing types fall back to `other`. Define only the types that differ (plus `other`). A custom translation function receives the argument list and can implement pluralization manually.

```js
render: ({ count }) => html`<div>${msg`There are ${count} items`}</div>`;
```

Even when the language has no `zero` category, `count === 0` can be mapped to a custom message (e.g., "There are no items").

## msg.html & msg.svg

Generate a nested template function from a message containing HTML/SVG content. The **whole body** of the message is the key — use expressions to keep dynamic parts (like URLs) out of the key. The returned function is used like `html`/`svg`. **Not sanitized** — malicious message content is an XSS vector; avoid when not required.

```js
const url = "https://some-domain.com/";

render: () => html`
  <p>${msg.html`Click <a href="${url}">here</a> to accept terms and conditions`}</p>
`;
```

## localize

Must be called **before templates compile** (before the first render) and before any `msg` invocation. Two forms:

### Built-in messages format

```js
localize(lang: string, messages: object): void
```

- `lang` — language code (with or without region) or `"default"` for the fallback locale
- `messages` — object keyed by message (or `message | context`):

```js
{
  "This is a message | context": {
    message: "To jest wiadomość",
    description: "This is description", // optional, not used in translation
  },
  "You have ${0} messages": {
    message: { one: "Masz jedną wiadomość", other: "Masz ${0} wiadomości" },
  },
}
```

Format is similar to `chrome.i18n` files with custom placeholder/plural support. Language resolution uses `navigator.languages` + `navigator.language` (region-less locales appended); messages are looked up in that order, so incomplete translations may mix languages. Use the origin-language message as the key for seamless integration; structured keys (`home.header.title`) work with a `"default"` locale as last fallback.

### Async sources

`localize` is synchronous only. Delay rendering until translations load — the loader component must not contain messages:

```js
const lang = localize.languages.find((lng) => supportedLangs.includes(lng));
const promise = fetch(`/locales/${lang}/messages.json`)
  .then((r) => r.json())
  .then((msgs) => localize(lang, msgs));

define({
  tag: "app-wrapper",
  render: () => html.resolve(
    promise.then(() => html`<app-root></app-root>`),
    html`<app-loader></app-loader>`,
  ),
});
```

`localize.languages` holds the current preferred language list.

### Custom translation functions

```js
localize(translate: (key: string, context: string) => string | ((number) => string), options?: object): void
```

Bypasses dictionary/language detection (do language detection manually). Only one custom function at a time (can be overwritten); called when a message is not found in the dictionary, so it can be mixed with the built-in format. Returning a function enables pluralization by count.

**`options.format: "chrome.i18n"`** — transforms key+context into the chrome.i18n key format, e.g., `localize(chrome.i18n.getMessage, { format: "chrome.i18n" })`. Generate matching files with the CLI `--format=chrome.i18n` option.

## CLI extraction

Extracts messages from JS/TS source into the built-in format:

```bash
npx hybrids extract ./src
# or as a package.json script: "extract": "hybrids extract ./src"
```

```text
hybrids extract [options] <file or directory> [<output file>]

Options:
-e, --empty-message   Set default message body to empty string
-f, --force           Overwrite output file instead of merging with existing messages
-p, --include-path    Include path in message description
-h, --help            Show this help
--format=type         Transform messages; supported: chrome.i18n
```

Without an output file, messages go to stdout. Uses a simplified in-house parser — report unsupported edge cases upstream.
