# Security Reference

## Overview

`alpinejs-component` renders HTML content directly into Shadow DOM without sanitization. Security is the developer's responsibility. The plugin provides minimal safeguards (origin checks, protocol validation) but does not protect against malicious template content.

## What the plugin does

### URL validation

- Only `http:` and `https:` protocols are accepted
- Other protocols (`file:`, `data:`, `javascript:`, etc.) throw an error
- URLs are resolved via `new URL(input, window.location.href)` — invalid URLs throw

### Same-origin enforcement

- `x-component.url` only allows URLs on the same origin as the page
- Cross-origin URLs throw: `Cross-origin URL blocked for x-component.url: <url>`
- `x-component.url.external` opts out of origin checking

### No sanitization

- HTML content from templates or URLs is rendered as-is
- `<script>` tags inside templates are parsed as DOM but not executed (standard browser behavior for `innerHTML`/template parsing)
- Event handlers in HTML attributes (e.g., `onclick="..."`) are not processed — Alpine.js does not process raw HTML event attributes
- Shadow DOM provides some isolation but does not prevent all attacks

## What you must do

### Only load trusted templates

Never use user-supplied input directly as a template source:

```html
<!-- DANGEROUS — user controls the template id -->
<div x-component="userInput"></div>

<!-- DANGEROUS — user controls the URL -->
<div x-component.url="userProvidedUrl"></div>
```

Instead, validate against an allowlist:

```js
x-data="{
  allowedTemplates: ['card', 'summary', 'detail'],
  selectedView: 'card',
  get template() {
    return this.allowedTemplates.includes(this.selectedView)
      ? this.selectedView
      : ''
  }
}"
```

### Use CSP headers

Content Security Policy headers add a defense layer:

```
Content-Security-Policy: default-src 'self'; script-src 'self'
```

This restricts where resources can be loaded from, complementing the plugin's origin checks.

### Validate dynamic URLs

For dynamic URL sources, validate before passing to the directive:

```js
x-data="{
  baseUrl: '/components/',
  getViewUrl(name) {
    const allowed = ['card', 'summary', 'detail']
    return allowed.includes(name) ? `${this.baseUrl}${name}.html` : ''
  }
}"
```

### Server-side validation

When templates are selected server-side, ensure the server validates the template name/path before sending it to the client.

## Cross-origin considerations

### `x-component.url.external`

Use only with trusted remote sources. Cross-origin content has the same risks as same-origin content, plus:

- You cannot verify the content integrity without additional measures
- The remote server could change content without your knowledge
- CORS errors on stylesheet access may silently drop styles

### Subresource Integrity (SRI)

The plugin does not support SRI for remote templates. If loading from CDNs, consider:
- Using on-page templates instead of remote URLs
- Hosting templates on your own origin
- Implementing a proxy that validates content before serving

## Shadow DOM security notes

### Isolation benefits

Shadow DOM provides:
- CSS encapsulation — external styles cannot target shadow content
- DOM encapsulation — `querySelector` from light DOM does not penetrate shadow boundary
- Script isolation — `<script>` tags in shadow DOM content are not executed (they become inert nodes)

### Limitations

- Shadow DOM does not prevent XSS from event handlers or inline scripts that Alpine processes
- `x-on:` directives in templates are processed by Alpine and can execute arbitrary expressions
- Slot content from the light DOM is projected into the shadow root and is fully trusted

## Expression evaluation

Directive expressions are evaluated by Alpine's expression system. If an expression throws:

1. The error is logged to console
2. `x-component:error` event is dispatched with the error
3. Component content is cleared

Untrusted expressions should be guarded:

```html
<!-- Safe — expression is a static string literal -->
<div x-component="'card'"></div>

<!-- Guarded — reactive value validated -->
<div x-component="safeView"></div>
```

## Summary checklist

- [ ] Never pass user input directly to `x-component` or `x-component.url`
- [ ] Validate template ids against an allowlist
- [ ] Validate URLs before using with `.url` modifier
- [ ] Use CSP headers for additional protection
- [ ] Only load templates from your own trusted servers
- [ ] Avoid `x-component.url.external` unless the remote source is fully trusted
- [ ] Remember that Alpine processes `x-on:` directives in templates — malicious templates can execute code through Alpine bindings
