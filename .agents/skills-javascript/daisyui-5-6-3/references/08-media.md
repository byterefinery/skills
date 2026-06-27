# 08 — Media

## avatar

Thumbnail image with online/offline indicators.

**Class names:**
- component: `avatar`, `avatar-group`
- modifier: `avatar-online`, `avatar-offline`, `avatar-placeholder`

```html
<div class="avatar {MODIFIER}">
  <div>
    <img src="{url}" />
  </div>
</div>
```

Use `avatar-group` for multiple avatars. Set custom sizes with `w-*` and `h-*`. Use mask classes (`mask-squircle`, `mask-hexagon`) on the inner div.

## chat

Conversation bubbles with author info.

**Class names:**
- component: `chat`
- part: `chat-image`, `chat-header`, `chat-footer`, `chat-bubble`
- placement: `chat-start`, `chat-end`
- color: `chat-bubble-primary`, `chat-bubble-secondary`, `chat-bubble-accent`, `chat-bubble-neutral`, `chat-bubble-info`, `chat-bubble-success`, `chat-bubble-warning`, `chat-bubble-error`

```html
<div class="chat {PLACEMENT}">
  <div class="chat-image avatar">
    <div><img src="{url}" /></div>
  </div>
  <div class="chat-header">Name <time>12:00</time></div>
  <div class="chat-bubble {COLOR}">Message</div>
  <div class="chat-footer">Delivered</div>
</div>
```

`chat-start` for the other person, `chat-end` for the current user. `chat-image` is optional.

## carousel

Scrollable image or content gallery.

**Class names:**
- component: `carousel`
- part: `carousel-item`
- modifier: `carousel-start`, `carousel-center`, `carousel-end`
- direction: `carousel-horizontal`, `carousel-vertical`

```html
<div class="carousel {MODIFIER}">
  <div class="carousel-item"><img src="{url}" /></div>
  <div class="carousel-item"><img src="{url}" /></div>
</div>
```

Add `w-full` to each item for full-width carousel.

## mockup-browser

Browser window mockup with toolbar.

**Class names:**
- component: `mockup-browser`
- part: `mockup-browser-toolbar`

```html
<div class="mockup-browser">
  <div class="mockup-browser-toolbar">
    <div class="input">https://example.com</div>
  </div>
  <div>{content}</div>
</div>
```

## mockup-code

Code editor mockup with line prefixes.

**Class names:**
- component: `mockup-code`

```html
<div class="mockup-code">
  <pre data-prefix="$"><code>npm i daisyui</code></pre>
  <pre data-prefix=">"><code>Done!</code></pre>
</div>
```

Use `<pre data-prefix="{char}">` for line prefixes.

## mockup-phone

iPhone mockup frame.

**Class names:**
- component: `mockup-phone`
- part: `mockup-phone-camera`, `mockup-phone-display`

```html
<div class="mockup-phone">
  <div class="mockup-phone-camera"></div>
  <div class="mockup-phone-display">{content}</div>
</div>
```

## mockup-window

Desktop window mockup with traffic light buttons.

**Class names:**
- component: `mockup-window`

```html
<div class="mockup-window">
  <div>{content}</div>
</div>
```
