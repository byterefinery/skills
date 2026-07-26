# CLI Tool

mustache.js ships with a Node.js command-line tool for rendering templates from the terminal.

## Installation

```bash
npm install -g mustache       # global
npm install mustache --save-dev  # project dependency
```

## Usage

```bash
mustache <view> <template> [output]
```

- `view` — JSON file, JS module file, or `-` for stdin
- `template` — `.mustache` template file
- `output` — optional output file (defaults to stdout)

### Basic

```bash
mustache data.json template.mustache > output.html
```

### With partials

```bash
mustache -p partials/header.mustache -p partials/footer.mustache data.json template.mustache
```

Partial names are derived from the filename (without `.mustache` extension).

### From stdin

```bash
cat data.json | mustache - template.mustache
```

The `-` tells mustache to read the view from stdin.

### JS view files

View files with `.js` or `.cjs` extension are loaded via `require()` and support functions:

```js
// view.js
module.exports = {
  name: 'Alice',
  greeting: function () {
    return 'Hello, ' + this.name + '!';
  }
};
```

```bash
mustache view.js template.mustache
```

JSON views do not support functions.

### Version

```bash
mustache --version
mustache -v
```

## Build integration

Use in `package.json` scripts:

```json
{
  "scripts": {
    "build": "mustache src/data.json src/template.mustache > dist/output.html"
  }
}
```

## Limitations

- CLI views must be files or stdin — no inline data
- JSON views cannot contain functions
- Partial paths are resolved relative to the current working directory
- No built-in template auto-reload or watch mode
