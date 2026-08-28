# Security

## Trust model

The plugin renders template HTML directly, with **no sanitization**, and performs minimal URL validation. It is designed for developer-controlled content.

- Don't use user input directly in `x-component` or `x-component.url`
- Only load templates from your own trusted servers
- Validate/sanitize any dynamic template selection
- Use CSP headers for additional protection

Sanitizing inside the plugin is not an option: `setHTML()` and the Sanitizer API strip unknown attributes, which removes `x-text`, `x-for`, `@click`, and every other Alpine directive, leaving inert markup.

## URL validation

`x-component.url` accepts only `http:` and `https:` URLs (anything else throws) and blocks cross-origin URLs by default. `x-component.url.external` opts in to cross-origin `http(s)` requests.

## Content Security Policy

**Alpine's default build needs `'unsafe-eval'`.** It compiles every directive expression with `new Function`, so this is about Alpine itself, not this plugin. If your CSP can't allow `'unsafe-eval'`, use Alpine's [CSP build](https://alpinejs.dev/advanced/csp) (`@alpinejs/csp`). The plugin works with it — `x-component`, `.url`, slots, and dynamic expressions all behave the same.

**Trusted Types needs both pieces.** Templates are parsed by assigning to `innerHTML`, which is a Trusted Types sink, so under `require-trusted-types-for 'script'` the plugin registers a pass-through policy named `alpinejs-component`. Allow that name:

```http
Content-Security-Policy: trusted-types alpinejs-component; require-trusted-types-for 'script'
```

If the name isn't allowed, the plugin logs a warning and rendering fails on that page. The header alone is not enough, though: `require-trusted-types-for 'script'` also blocks `new Function`, so Alpine's default build can't evaluate any expression and nothing renders. Trusted Types therefore requires the CSP build **and** the policy name together.

The policy is pass-through — it does not sanitize and does not make untrusted templates safe; the trust model above still applies.

## Browser support

The plugin targets modern browsers with support for `template.content` and `Element.replaceChildren`. The test suite runs against Chromium, Firefox, and WebKit, so that support is tested rather than assumed.
