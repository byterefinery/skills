# Express Integration

## Basic Setup

```js
const express = require('express');
const consolidate = require('consolidate');
const handlebars = require('handlebars');
const layouts = require('handlebars-layouts');
const fs = require('fs');
const path = require('path');

// Register layout helpers
layouts.register(handlebars);

// Register layout partials
handlebars.registerPartial({
  layout: fs.readFileSync(path.join(__dirname, 'partials/layout.hbs'), 'utf8'),
  admin: fs.readFileSync(path.join(__dirname, 'partials/admin.hbs'), 'utf8'),
});

const app = express();

app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'html');
app.engine('html', consolidate.handlebars);

app.listen(3000);
```

## consolidate.handlebars

`consolidate` is a wrapper that adapts various template engines for Express. It reads the template file, compiles it with Handlebars, and renders with the provided data.

When using `consolidate.handlebars`, the global `handlebars` instance (with registered helpers and partials) is used for compilation. This means `layouts.register(handlebars)` on the global instance works seamlessly.

## Per-Route Layouts

Different routes can use different layouts by having page templates extend different partials:

```handlebars
! views/home.html
{{#extend "layout"}}
    {{#content "body"}}
        <h1>Home Page</h1>
    {{/content}}
{{/extend}}

! views/admin/dashboard.html
{{#extend "admin"}}
    {{#content "content"}}
        <h1>Dashboard</h1>
    {{/content}}
{{/extend}}
```

```js
app.get('/', (req, res) => res.render('home', { title: 'Home' }));
app.get('/admin', (req, res) => res.render('admin/dashboard', { user: req.user }));
```

## Dynamic Partial Registration

For larger projects, automate partial registration:

```js
const fs = require('fs');
const path = require('path');

function registerPartials(dir) {
  const files = fs.readdirSync(dir);
  const partials = {};

  files.forEach(file => {
    if (path.extname(file) === '.hbs') {
      const name = path.basename(file, '.hbs');
      partials[name] = fs.readFileSync(path.join(dir, file), 'utf8');
    }
  });

  handlebars.registerPartial(partials);
}

registerPartials(path.join(__dirname, 'partials'));
```

## Error Handling

Missing partials throw during rendering:

```js
app.get('/page', (req, res) => {
  try {
    res.render('page', data);
  } catch (err) {
    if (err.message && err.message.indexOf('Missing partial') !== -1) {
      return res.status(500).send('Layout partial not registered');
    }
    throw err;
  }
});
```

## Express Test Server

The library includes a test server at `test/express.js` that demonstrates the pattern:

```js
const express = require('express');
const consolidate = require('consolidate');
const handlebars = require('handlebars');
const layouts = require('handlebars-layouts');

layouts.register(handlebars);

handlebars.registerPartial({
  layout: fs.readFileSync('partials/layout.hbs', 'utf8'),
  layout2col: fs.readFileSync('partials/layout2col.hbs', 'utf8'),
  media: fs.readFileSync('partials/media.hbs', 'utf8'),
  user: fs.readFileSync('partials/user.hbs', 'utf8'),
});

express()
  .set('views', 'fixtures/templates')
  .set('view engine', 'html')
  .engine('html', consolidate.handlebars)
  .get('/:id', (req, res) => res.render(req.params.id, data))
  .listen(3000);
```

Access `http://localhost:3000/extend` to render `extend.html`, `http://localhost:3000/embed` for `embed.html`, etc.

## Alternative: express-hbs

For production projects, consider `express-hbs` which provides built-in layout support:

```js
const exphbs = require('express-handlebars');

const hbs = exphbs.create({
  defaultLayout: 'main',
  helpers: layouts(require('handlebars')),
});

app.engine('hbs', hbs.engine);
app.set('view engine', 'hbs');
```

This handles partial discovery automatically from `views/partials/`.

## Middleware Pattern

Register helpers in a middleware or setup module:

```js
! setup-hbs.js
module.exports = function setupHandlebars(handlebars) {
  const layouts = require('handlebars-layouts');
  layouts.register(handlebars);

  ! Add custom helpers
  handlebars.registerHelper('json', function(context) {
    return JSON.stringify(context);
  });

  return handlebars;
};

! app.js
const handlebars = require('handlebars');
require('./setup-hbs')(handlebars);
```
