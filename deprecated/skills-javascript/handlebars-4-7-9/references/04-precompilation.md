# Precompilation

## Why precompile

Precompiling templates converts Handlebars source to JavaScript at build time, eliminating the compiler dependency at runtime. Benefits:

- **Smaller runtime** — `handlebars.runtime` is smaller than full `handlebars`
- **Faster startup** — no parse + compile step on first render
- **Early error detection** — syntax errors caught at build time
- **Security** — no template compilation in production environments

## CLI precompilation

The `handlebars` CLI command (from `bin/handlebars`) precompiles templates:

```bash
! Compile a single file
handlebars template.hbs -f dist/template.js

! Compile a directory
handlebars src/templates/ -f dist/templates.js

! Minimize output (requires uglify-js)
handlebars template.hbs -f dist/template.js -m

! AMD output
handlebars template.hbs -f dist/template.js -a

! CommonJS with custom module path
handlebars template.hbs -f dist/template.js -c node_modules/handlebars

! Simple mode (template function only, no wrapper)
handlebars template.hbs -f dist/template.js -s

! With source name for errors
echo '{{name}}' | handlebars -i "-" -N greeting -f dist/greeting.js -s

! Custom template extension
handlebars src/ -f dist/templates.js -e html

! Known helpers optimization
handlebars template.hbs -f dist/template.js -k "if each with"

! Known helpers only (throw on unknown)
handlebars template.hbs -f dist/template.js -k "if each" -o

! Custom namespace
handlebars template.hbs -f dist/template.js -n MyApp.templates

! Remove BOM
handlebars template.hbs -f dist/template.js -b

! Print version
handlebars -v
```

### CLI flags

| Flag | Alias | Description |
|---|---|---|
| `-f` | `--output` | Output file path |
| `-m` | `--min` | Minimize output (requires uglify-js) |
| `-a` | `--amd` | AMD-style exports (require.js) |
| `-c` | `--commonjs` | CommonJS exports, path to Handlebars module |
| `-h` | `--handlebarPath` | Path to handlebars.js (AMD mode only) |
| `-k` | `--known` | Known helpers (space-separated) |
| `-o` | `--knownOnly` | Known helpers only |
| `-n` | `--namespace` | Template namespace (default: `Handlebars.templates`) |
| `-s` | `--simple` | Output template function only (no wrapper) |
| `-N` | `--name` | Name for stdin/string templates |
| `-i` | `--string` | Template from string arg (`-` for stdin) |
| `-r` | `--root` | Template root (stripped from template names) |
| `-p` | `--partial` | Compiling a partial template |
| `-d` | `--data` | Include data when compiling |
| `-e` | `--extension` | Template extension (default: `handlebars`) |
| `-b` | `--bom` | Remove BOM from templates |
| `-v` | `--version` | Print compiler version |
| `-map` | `--source-map` | Source map file path |

## Programmatic precompilation

```js
const Handlebars = require('handlebars');
const fs = require('fs');

const source = fs.readFileSync('template.hbs', 'utf8');
const compiled = Handlebars.precompile(source, {
  srcName: 'template.hbs',
  knownHelpers: { if: true, each: true },
  trackIds: true,
});

! compiled is a string of JavaScript source
fs.writeFileSync('template-compiled.js', compiled);
```

`Handlebars.precompile()` accepts either a template string or a pre-parsed AST.

## Using precompiled templates

### With full Handlebars

```js
const Handlebars = require('handlebars');

! Register from precompiled module
const tplModule = require('./template-compiled');
! The module exports a function that registers into Handlebars.templates
tplModule();

! Use from registry
const html = Handlebars.templates['template'](context);
```

### With runtime-only

```js
const Handlebars = require('handlebars.runtime');

! Precompiled templates self-register
require('./template-compiled');

const html = Handlebars.templates['template'](context);
```

### Manual wrapping

```js
const spec = require('./template-spec'); ! exports the template spec object
const tpl = Handlebars.template(spec);
const html = tpl(context);
```

## Build tool integration

### Webpack

Use `handlebars-loader`:

```js
! webpack.config.js
module.exports = {
  module: {
    rules: [
      {
        test: /\.hbs$/,
        loader: 'handlebars-loader',
        options: {
          knownHelpers: true,
          strict: true,
        },
      },
    ],
  },
};
```

```js
import template from './template.hbs';
const html = template(context);
```

### Vite

Use `@cybo/vite-plugin-handlebars` or `rollup-plugin-handlebars`:

```js
! vite.config.js
import handlebars from '@cybo/vite-plugin-handlebars';

export default {
  plugins: [
    handlebars({
      strict: true,
    }),
  ],
};
```

### Gulp

```js
const gulp = require('gulp');
const handlebars = require('gulp-handlebars');
const wrap = require('gulp-wrap');
const declare = require('gulp-declare');

gulp.task('templates', function() {
  return gulp.src('src/templates/**/*.hbs')
    .pipe(handlebars())
    .pipe(wrap('Handlebars.template(<%= contents %>)'))
    .pipe(declare({
      namespace: 'Templates',
      noRedeclare: true,
    }))
    .pipe(gulp.dest('dist'));
});
```

## Template registry

Precompiled templates register themselves into `Handlebars.templates`:

```js
Handlebars.templates['my-template']  ! the compiled template function
```

With custom namespace:

```bash
handlebars template.hbs -f out.js -n MyApp.templates
```

```js
MyApp.templates['template'](context);
```

## Precompilation options

Same compile-time options apply:

```js
Handlebars.precompile(source, {
  strict: true,
  assumeExternal: true,
  knownHelpers: { if: true, each: true },
  knownHelpersOnly: true,
  trackIds: true,
  stringParams: true,
  compat: true,
  noEscape: false,
  srcName: 'template.hbs',
  destName: 'template-compiled.js',
});
```

## Runtime-only mode

The `handlebars.runtime` package provides only the runtime — no compiler:

```js
const Handlebars = require('handlebars.runtime');
! Handlebars.compile — NOT available
! Handlebars.precompile — NOT available
! Handlebars.template — available
! Handlebars.registerPartial — available
! Handlebars.registerHelper — available
```

In runtime-only mode, partials passed as strings are compiled on first use **only if** the full compiler is available. With pure runtime, all partials must be precompiled or passed as compiled functions.

## Compiler revisions

| Revision | Version range |
|---|---|
| 7 | >= 4.0.0 < 4.3.0 |
| 8 | >= 4.3.0 |

Runtime rev 8 is backward compatible with templates compiled by rev 7. Templates compiled by rev 8 require runtime rev 8. Mismatch throws a descriptive exception.

The template spec includes `compiler: [8, ">= 4.3.0"]` which is checked by `checkRevision()` at template setup.
