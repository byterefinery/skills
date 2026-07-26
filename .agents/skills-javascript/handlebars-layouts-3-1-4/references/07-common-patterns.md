# Common Patterns

## Two-Column Grid Layout

Layout with conditional column sizing based on whether right column content is provided:

```handlebars
! layout2col.hbs
{{#extend "layout"}}
    {{#content "header" mode="append"}}
        {{#block "subtitle"}}{{/block}}
    {{/content}}

    {{#content "body"}}
        <div class="grid">
            <div class="col 2of3">
                {{#block "left"}}<p>Default left</p>{{/block}}
            </div>
            <div class="col 1of3">
                {{#block "right"}}<p>Default right</p>{{/block}}
            </div>
        </div>
    {{/content}}
{{/extend}}
```

```handlebars
! page.hbs
{{#extend "layout2col"}}
    {{#content "subtitle" mode="append"}}
        <h2>Page Title</h2>
    {{/content}}

    {{#content "left" mode="prepend"}}
        <p>Custom left content</p>
    {{/content}}

    {{#content "right"}}
        <p>Custom right content</p>
    {{/content}}
{{/extend}}
```

## Media Object Component

Reusable media object with image and body blocks:

```handlebars
! media.hbs
<div class="media">
    <div class="media-img">
        {{#block "image"}}{{/block}}
    </div>
    <div class="media-bd">
        {{{block "body"}}}
    </div>
</div>
```

```handlebars
! usage
{{#embed "media"}}
    {{#content "image"}}
        <img src="photo.jpg" alt="Description" />
    {{/content}}
    {{#content "body"}}
        <p>Caption text for the media object.</p>
    {{/content}}
{{/embed}}
```

Inside loops with parent context access:

```handlebars
{{#each items}}
    {{#embed "media"}}
        {{#content "image"}}
            <img src="{{../../image}}" alt="" />
        {{/content}}
        {{#content "body"}}
            <p>{{../../title}}</p>
        {{/content}}
    {{/embed}}
{{/each}}
```

## User Card Component

Component with conditional banner and content block:

```handlebars
! user.hbs
<div class="user">
    {{#if showBanner}}
        <p>User is {{status}}.</p>
    {{/if}}
    {{{block "body"}}}
</div>
```

```handlebars
! usage with hash context
{{#embed "user" name showBanner=isActive status="active"}}
    {{#content "body"}}
        <p>{{first}} {{last}}</p>
    {{/content}}
{{/embed}}
```

## Modal / Dialog Component

```handlebars
! modal.hbs
<div class="modal" role="dialog">
    <div class="modal-header">
        {{#block "title"}}Modal{{/block}}
        <button class="close">&times;</button>
    </div>
    <div class="modal-body">
        {{{block "body"}}}
    </div>
    <div class="modal-footer">
        {{#block "footer"}}
            <button class="btn">Close</button>
        {{/block}}
    </div>
</div>
```

```handlebars
! usage
{{#embed "modal" title="Settings"}}
    {{#content "title"}}Settings{{/content}}
    {{#content "body"}}
        <form>
            <label>Option: <input type="checkbox" /></label>
        </form>
    {{/content}}
    {{#content "footer"}}
        <button class="btn btn-primary">Save</button>
        <button class="btn">Cancel</button>
    {{/content}}
{{/embed}}
```

## Admin Panel Layout

Multi-level admin layout hierarchy:

```handlebars
! admin.hbs — extends base layout
{{#extend "layout"}}
    {{#content "header"}}
        <nav class="admin-nav">
            <a href="/admin">Dashboard</a>
            <a href="/admin/settings">Settings</a>
        </nav>
    {{/content}}

    {{#content "body"}}
        <div class="admin-container">
            <aside class="sidebar">{{{block "sidebar"}}}</aside>
            <main class="content">{{{block "content"}}}</main>
        </div>
    {{/content}}
{{/extend}}
```

```handlebars
! admin/users.hbs — extends admin layout
{{#extend "admin"}}
    {{#content "sidebar"}}
        <ul>
            <li><a href="/admin/users">Users</a></li>
            <li><a href="/admin/roles">Roles</a></li>
        </ul>
    {{/content}}

    {{#content "content"}}
        <h1>User Management</h1>
        {{{block "users-content"}}}
    {{/content}}
{{/extend}}
```

```handlebars
! admin/users/list.hbs — extends admin/users
{{#extend "admin/users"}}
    {{#content "users-content"}}
        <table>
            {{#each users}}
                <tr>
                    <td>{{name}}</td>
                    <td>{{email}}</td>
                    <td>{{status}}</td>
                </tr>
            {{/each}}
        </table>
    {{/content}}
{{/extend}}
```

## Conditional Sections

Layout that conditionally shows sections based on content:

```handlebars
! layout.hbs
<!doctype html>
<html>
<head>
    {{#block "head"}}<title>{{title}}</title>{{/block}}
</head>
<body>
    {{#if (content "header")}}
        <header>{{{block "header"}}}</header>
    {{/if}}

    <main>{{{block "body"}}}</main>

    {{#if (content "footer")}}
        <footer>{{{block "footer"}}}</footer>
    {{/if}}

    {{#block "foot"}}{{/block}}
</body>
</html>
```

Pages that omit `header` or `footer` content get a cleaner layout without those sections.

## Head Script/CSS Accumulation

Append multiple scripts and styles to the head block:

```handlebars
{{#extend "layout"}}
    {{#content "head" mode="append"}}
        <link rel="stylesheet" href="page.css" />
    {{/content}}

    {{#content "head" mode="append"}}
        <link rel="stylesheet" href="component.css" />
    {{/content}}

    {{#content "foot" mode="prepend"}}
        <script src="analytics.js"></script>
    {{/content}}

    {{#content "foot" mode="append"}}
        <script src="page.js"></script>
    {{/content}}

    {{#content "body"}}
        <h1>Page Content</h1>
    {{/content}}
{{/extend}}
```

Result: styles accumulate in head, scripts order is `analytics.js` (prepend) → default scripts → `page.js` (append).

## Breadcrumb Pattern

```handlebars
! layout.hbs
<nav class="breadcrumbs">
    <a href="/">Home</a>
    {{#block "breadcrumbs"}}{{/block}}
</nav>

! page.hbs
{{#extend "layout"}}
    {{#content "breadcrumbs" mode="append"}}
        <span>/</span> <a href="/category">Category</a>
    {{/content}}

    {{#content "breadcrumbs" mode="append"}}
        <span>/</span> <span class="current">Page</span>
    {{/content}}
{{/extend}}
```

Multiple `append` calls build the breadcrumb trail incrementally.
