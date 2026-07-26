# embed Isolation

## Context Reset Mechanics

`embed` creates a fresh context by copying the current context and nulling internal properties:

```js
var context = mixin({}, this || {});
context.$$layoutStack = null;
context.$$layoutActions = null;
```

This means the embedded partial starts with clean internal state. Any `block` or `content` inside the embedded partial operates in its own scope, isolated from the parent page's layout.

## Why Isolation Matters

Without `embed`, block names would collide. Consider:

```handlebars
{{#extend "layout"}}
    {{#content "body"}}
        ! Without embed — "image" and "body" content would leak into the parent layout
        {{> media}}
            {{#content "image"}}<img src="x.jpg" />{{/content}}
            {{#content "body"}}Caption{{/content}}
        {{/media}}
    {{/content}}
{{/extend}}
```

With `embed`, the `media` partial's blocks are isolated:

```handlebars
{{#extend "layout"}}
    {{#content "body"}}
        {{#embed "media"}}
            {{#content "image"}}<img src="x.jpg" />{{/content}}
            {{#content "body"}}Caption{{/content}}
        {{/embed}}
    {{/content}}
{{/extend}}
```

The `{{#content "body"}}` inside `embed` targets the `media` partial's `{{#block "body"}}`, not the page layout's `{{#block "body"}}`.

## Nested Embeds

Embeds can be nested. Each level gets its own isolated scope:

```handlebars
{{#extend "layout"}}
    {{#content "body"}}
        {{#embed "outer-panel"}}
            {{#content "title"}}Outer{{/content}}
            {{#content "body"}}
                {{#embed "inner-widget"}}
                    {{#content "title"}}Inner{{/content}}
                    {{#content "body"}}Widget content{{/content}}
                {{/embed}}
            {{/content}}
        {{/embed}}
    {{/content}}
{{/extend}}
```

Each `embed` resets state independently. The `inner-widget`'s blocks are isolated from both `outer-panel` and the page layout.

## Embed Inside Loops

`embed` works correctly inside `{{#each}}` and other iteration helpers. Each iteration gets a fresh isolated context:

```handlebars
{{#extend "layout"}}
    {{#content "body"}}
        {{#each users}}
            {{#embed "user-card" name showBanner=isActive}}
                {{#content "body"}}
                    <p>{{first}} {{last}}</p>
                {{/content}}
            {{/embed}}
        {{/each}}
    {{/content}}
{{/extend}}
```

The `user-card` partial:

```handlebars
<div class="user">
    {{#if showBanner}}
        <p>User is {{status}}.</p>
    {{/if}}
    {{{block "body"}}}
</div>
```

Each user gets their own isolated `user-card` instance with its own block content.

## Hash Context in Embeds

`embed` accepts hash attributes just like `extend`. These merge into the embedded partial's context:

```handlebars
{{#embed "user" name showBanner=isActive status="active"}}
    {{#content "body"}}
        <p>{{first}} {{last}}</p>
    {{/content}}
{{/embed}}
```

Inside the `user` partial, `name`, `showBanner`, and `status` are available as context properties. Hash attributes override the copied context.

## Parent Context Access

Inside `embed`, use `../` depth references to access parent context:

```handlebars
{{#each users}}
    {{#embed "media"}}
        {{#content "image"}}
            <img src="{{../../picture}}" alt="" />
        {{/content}}
        {{#content "body"}}
            <p>{{../../name.first}} {{../../name.last}}</p>
        {{/content}}
    {{/embed}}
{{/each}}
```

The `../../` reference escapes both the `embed` context and the `{{#each}}` iteration to reach the root context.

## embed vs extend — Decision Guide

| Criteria | Use `extend` | Use `embed` |
|---|---|---|
| Page-level layout | Yes | No |
| Component with own blocks | No | Yes |
| Needs isolation from parent | No | Yes |
| Layout inheritance chain | Yes | No |
| Reusable widget/component | No | Yes |
| Inside loops | No | Yes |
| Context merging needed | Both | Both |

## Common Patterns

### Modal Component

```handlebars
! modal.hbs
<div class="modal">
    <div class="modal-hd">{{#block "title"}}Modal{{/block}}</div>
    <div class="modal-bd">{{{block "body"}}}</div>
    <div class="modal-ft">{{#block "footer"}}{{/block}}</div>
</div>

! page usage
{{#embed "modal" title="Settings"}}
    {{#content "title"}}Settings{{/content}}
    {{#content "body"}}
        <form>...</form>
    {{/content}}
    {{#content "footer"}}
        <button>Save</button>
        <button>Cancel</button>
    {{/content}}
{{/embed}}
```

### Media Object

```handlebars
! media.hbs
<div class="media">
    <div class="media-img">{{#block "image"}}{{/block}}</div>
    <div class="media-bd">{{{block "body"}}}</div>
</div>

! page usage
{{#embed "media"}}
    {{#content "image"}}<img src="photo.jpg" />{{/content}}
    {{#content "body"}}<p>Caption</p>{{/content}}
{{/embed}}
```

### Card Grid

```handlebars
! card.hbs
<div class="card">
    {{#block "header"}}{{/block}}
    <div class="card-body">{{{block "body"}}}</div>
    {{#block "footer"}}{{/block}}
</div>

! page usage
{{#each items}}
    {{#embed "card"}}
        {{#content "header"}}<h3>{{title}}</h3>{{/content}}
        {{#content "body"}}{{description}}{{/content}}
        {{#content "footer"}}<a href="{{url}}">Read more</a>{{/content}}
    {{/embed}}
{{/each}}
```
