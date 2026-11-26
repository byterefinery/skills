# daisyUI 5.7.47 Components

All 63 daisyUI 5 components, grouped by the official daisyUI site categories. Every class name, structure, and rule below is from the official daisyUI 5.7.47 docs and component CSS (https://daisyui.com/components/<name>/).

Class name categories (reference only — do not use in code): component (the component class), part (child part), style, behavior, color, size, placement, direction, modifier, variant.

## Actions

### Button
Use buttons to start actions.

[Button documentation](https://daisyui.com/components/button/)

#### Class names
- component: `btn`
- color: `btn-neutral`, `btn-primary`, `btn-secondary`, `btn-accent`, `btn-info`, `btn-success`, `btn-warning`, `btn-error`
- style: `btn-outline`, `btn-dash`, `btn-soft`, `btn-ghost`, `btn-link`
- behavior: `btn-active`, `btn-disabled`
- size: `btn-xs`, `btn-sm`, `btn-md`, `btn-lg`, `btn-xl`
- modifier: `btn-wide`, `btn-block`, `btn-square`, `btn-circle`

#### Syntax
```html
<button class="btn {MODIFIER}">Button</button>
```
#### Rules
- `{MODIFIER}` is optional. It can include one class name from each color, style, behavior, size, and modifier category.
- You can use `btn` on HTML elements such as `<button>`, `<a>`, and `<input>`.
- A `btn` element can have an icon before or after the text.
- If you use a class name to disable the button, set `tabindex="-1" role="button" aria-disabled="true"`.

### Dropdown
A dropdown can open a menu or another element when the user clicks the button.

[Dropdown documentation](https://daisyui.com/components/dropdown/)

#### Class names
- component: `dropdown`
- part: `dropdown-content`
- placement: `dropdown-start`, `dropdown-center`, `dropdown-end`, `dropdown-top`, `dropdown-bottom`, `dropdown-left`, `dropdown-right`
- modifier: `dropdown-hover`, `dropdown-open`, `dropdown-close`

#### Syntax

Popover API:
```html
<button popovertarget="{id}" style="anchor-name:--{anchor}">{button}</button>
<ul class="dropdown" popover id="{id}" style="position-anchor:--{anchor}">{CONTENT}</ul>
```

The `details` and `summary` elements open and close only when the user clicks them:
```html
<details class="dropdown">
  <summary>Button</summary>
  <ul class="dropdown-content">{CONTENT}</ul>
</details>
```

#### Rules
- `{MODIFIER}` is optional. It can include one modifier class name and one placement class name.
- Replace `{id}` and `{anchor}` with the same name. Do not use this name for another element.
- The content is not limited to `<ul>`. It can be a different HTML element.
- For the popover API method, use only a button and `dropdown`. Do not use `dropdown-content`.

### FAB
A FAB is a floating action button that stays in a bottom corner of the screen. It contains a focusable, accessible element with a button role. When the user clicks or focuses it, more speed-dial buttons appear. These buttons have a vertical or quarter-circle arrangement.

[FAB documentation](https://daisyui.com/components/fab/)

#### Class names
- component: `fab`
- part: `fab-close`, `fab-main-action`
- modifier: `fab-flower`

#### Syntax
One FAB in a screen corner:
```html
<div class="fab">
  <button class="btn btn-lg btn-circle">{IconOriginal}</button>
</div>
```
A FAB that opens three other buttons vertically in a page corner:
```html
<div class="fab">
  <div tabindex="0" role="button" class="btn btn-lg btn-circle btn-primary">{IconOriginal}</div>
  <button class="btn btn-lg btn-circle">{Icon1}</button>
  <button class="btn btn-lg btn-circle">{Icon2}</button>
  <button class="btn btn-lg btn-circle">{Icon3}</button>
</div>
```
A FAB that opens three other buttons vertically in a page corner. Each button has label text:
```html
<div class="fab">
  <div tabindex="0" role="button" class="btn btn-lg btn-circle btn-primary">{IconOriginal}</div>
  <div>{Label1}<button class="btn btn-lg btn-circle">{Icon1}</button></div>
  <div>{Label2}<button class="btn btn-lg btn-circle">{Icon2}</button></div>
  <div>{Label3}<button class="btn btn-lg btn-circle">{Icon3}</button></div>
</div>
```
A FAB with rectangular buttons. These buttons can contain more content than circular buttons:
```html
<div class="fab">
  <div tabindex="0" role="button" class="btn btn-lg btn-circle btn-primary">{IconOriginal}</div>
  <button class="btn btn-lg">{Label1}</button>
  <button class="btn btn-lg">{Label2}</button>
  <button class="btn btn-lg">{Label3}</button>
</div>
```
A FAB with a close button. When the FAB is open, the close button replaces the original button:
```html
<div class="fab">
  <div tabindex="0" role="button" class="btn btn-lg btn-circle btn-primary">{IconOriginal}</div>
  <div class="fab-close">Close <span class="btn btn-circle btn-lg btn-error">×</span></div>
  <div>{Label1}<button class="btn btn-lg btn-circle">{Icon1}</button></div>
  <div>{Label2}<button class="btn btn-lg btn-circle">{Icon2}</button></div>
  <div>{Label3}<button class="btn btn-lg btn-circle">{Icon3}</button></div>
</div>
```
A FAB with a main-action button. When the FAB is open, the main-action button replaces the original button:
```html
<div class="fab">
  <div tabindex="0" role="button" class="btn btn-lg btn-circle btn-primary">{IconOriginal}</div>
  <div class="fab-main-action">
    {LabelMainAction}<button class="btn btn-circle btn-secondary btn-lg">{IconMainAction}</button>
  </div>
  <div>{Label1}<button class="btn btn-lg btn-circle">{Icon1}</button></div>
  <div>{Label2}<button class="btn btn-lg btn-circle">{Icon2}</button></div>
  <div>{Label3}<button class="btn btn-lg btn-circle">{Icon3}</button></div>
</div>
```
A flower FAB. It opens the buttons in a quarter-circle arrangement instead of a vertical arrangement:
```html
<div class="fab fab-flower">
  <div tabindex="0" role="button" class="btn btn-lg btn-circle btn-primary">{IconOriginal}</div>
  <button class="fab-main-action btn btn-circle btn-lg">{IconMainAction}</button>
  <button class="btn btn-lg btn-circle">{Icon1}</button>
  <button class="btn btn-lg btn-circle">{Icon2}</button>
  <button class="btn btn-lg btn-circle">{Icon3}</button>
</div>
```
A flower FAB with tooltips. A quarter circle has no space for a text label. Thus, each tooltip identifies the button function:
```html
<div class="fab fab-flower">
  <div tabindex="0" role="button" class="btn btn-lg btn-circle btn-primary">{IconOriginal}</div>
  <button class="fab-main-action btn btn-circle btn-lg">{IconMainAction}</button>
  <div class="tooltip tooltip-left" data-tip="{Label1}">
    <button class="btn btn-lg btn-circle">{Icon1}</button>
  </div>
  <div class="tooltip tooltip-left" data-tip="{Label2}">
    <button class="btn btn-lg btn-circle">{Icon2}</button>
  </div>
  <div class="tooltip tooltip-left" data-tip="{Label3}">
    <button class="btn btn-lg btn-circle">{Icon3}</button>
  </div>
</div>
```
#### Rules
- Replace `{Icon*}` with the applicable icon for each button. If possible, use SVG icons.
- Use `{IconOriginal}` for the icon that appears before the FAB opens.
- Use `{IconMainAction}` for the icon that appears after the FAB opens.
- Use `{Icon1}`, `{Icon2}`, and `{Icon3}` for the other button icons.
- Replace `{Label*}` with the label text for each button.

### Modal
A modal shows a dialog or box when the user clicks a button.

[Modal documentation](https://daisyui.com/components/modal/)

#### Class names
- component: `modal`
- part: `modal-box`, `modal-action`, `modal-backdrop`, `modal-toggle`
- modifier: `modal-open`
- placement: `modal-top`, `modal-middle`, `modal-bottom`, `modal-start`, `modal-end`

#### Syntax
If possible, use the HTML `dialog` element:
```html
<button onclick="my_modal.showModal()">Open modal</button>
<dialog id="my_modal" class="modal">
  <div class="modal-box">{CONTENT}</div>
  <form method="dialog" class="modal-backdrop"><button>close</button></form>
</dialog>
```
To close the modal when the user clicks outside it:
```html
<button class="btn" onclick="my_modal.showModal()">open modal</button>
<dialog id="my_modal" class="modal">
  <div class="modal-box">
    <h3 class="text-lg font-bold">Hello!</h3>
    <p class="py-4">Press ESC key or click outside to close</p>
  </div>
  <form method="dialog" class="modal-backdrop">
    <button>close</button>
  </form>
</dialog>
```


If the modal must not keep keyboard navigation inside it, use the popover API:
```html
<button popovertarget="my_modal" class="btn">Open modal</button>
<div class="modal" popover id="my_modal">
  <div class="modal-box">
    {CONTENT}
    <div class="modal-action">
      <button popovertarget="my_modal" popovertargetaction="hide">close</button>
    </div>
  </div>
</div>
```
To close the modal when the user clicks outside it:
```html
<button class="btn" popovertarget="my_modal">Open</button>

<div class="modal" id="my_modal" popover>
  <div class="modal-box">
    <h3 class="font-bold text-lg">Hello!</h3>
    <p class="py-4">Press ESC key or click the button below to close</p>
  </div>
  <div class="modal-backdrop">
    <button popovertarget="my_modal" popovertargetaction="hide">close</button>
  </div>
</div>
```

Checkbox. This method is legacy:
```html
<label for="my-modal" class="btn">Open modal</label>
<input type="checkbox" id="my-modal" class="modal-toggle" />
<div class="modal">
  <div class="modal-box">{CONTENT}</div>
  <label class="modal-backdrop" for="my-modal">Close</label>
</div>
```

Anchor links. This method is legacy:
```html
<a href="#my-modal" class="btn">Open modal</a>
<div class="modal" id="my-modal">
  <div class="modal-box">{CONTENT}</div>
</div>
```

#### Rules
- `{MODIFIER}` is optional. It can include one modifier class name and one placement class name.
- Use a unique HTML ID for each modal.
- For an HTML `dialog` element, add `<form method="dialog">`. This lets the submit action close the modal.

### Swap
Use the swap component to change the visibility of two elements. Control the swap with a checkbox or a class name.

[Swap documentation](https://daisyui.com/components/swap/)

#### Class names
- component: `swap`
- part: `swap-on`, `swap-off`, `swap-indeterminate`
- modifier: `swap-active`
- style: `swap-rotate`, `swap-flip`

#### Syntax
Checkbox:
```html
<label class="swap {MODIFIER}">
  <input type="checkbox" />
  <div class="swap-on">{content when active}</div>
  <div class="swap-off">{content when inactive}</div>
</label>
```

Class name:
```html
<div class="swap {MODIFIER}">
  <div class="swap-on">{content when active}</div>
  <div class="swap-off">{content when inactive}</div>
</div>
```

#### Rules
- `{MODIFIER}` is optional. It can include one modifier class name and one style class name.
- Use only a hidden checkbox to control the swap state. As an alternative, use JavaScript to add or remove the `swap-active` class.
- To show content when the checkbox is indeterminate, use the `swap-indeterminate` class.

### Theme controller
If a checked checkbox or radio input has the `theme-controller` class, the page uses the theme in the input value.

[Theme controller documentation](https://daisyui.com/components/theme-controller/)

#### Class names
- component: `theme-controller`

#### Syntax
```html
<input type="checkbox" value="{theme-name}" class="theme-controller" />
```

#### Rules
- The `value` attribute of the input element must contain a valid daisyUI theme name.


## Data display

### Accordion
Use the accordion to show and hide content. Only one item can be open at a time.

[Accordion documentation](https://daisyui.com/components/accordion/)

#### Class names
- component: `collapse`
- part: `collapse-title`, `collapse-content`
- modifier: `collapse-arrow`, `collapse-plus`, `collapse-open`, `collapse-close`

#### Syntax
```html
<div class="collapse {MODIFIER}">{CONTENT}</div>
```
The content has this structure:
```html
<input type="radio" name="{name}" checked="{checked}" />
<div class="collapse-title">{title}</div>
<div class="collapse-content">{CONTENT}</div>
```

#### Rules
- `{MODIFIER}` is optional. It can be one of the modifier class names.
- The accordion uses radio inputs. Radio inputs that have the same name operate as one group. Only one input in the group can be open at a time.
- If a page has more than one accordion group, use a different radio-input name for each group.
- Replace `{name}` with a unique name for the accordion group.
- To open an accordion item by default, replace `{checked}` with `checked="checked"`.

### Avatar
Use an avatar to show a thumbnail image.

[Avatar documentation](https://daisyui.com/components/avatar/)

#### Class names
- component: `avatar`, `avatar-group`
- modifier: `avatar-online`, `avatar-offline`, `avatar-placeholder`

#### Syntax
```html
<div class="avatar {MODIFIER}">
  <div>
    <img src="{image-url}" />
  </div>
</div>
```

#### Rules
- `{MODIFIER}` is optional. It can be one of the modifier class names.
- Use `avatar-group` as a container for more than one avatar.
- To set a custom size, use `w-*` and `h-*`.
- To change the avatar shape, use mask classes such as `mask-squircle`, `mask-hexagon`, and `mask-triangle`.

### Aura
An aura adds a light effect around the border of a component. Use it to make an important button, card, or div easy to see.
[Aura documentation](https://daisyui.com/components/aura/)

#### Class names
- component: `aura`
- style: `aura-dual`, `aura-rainbow`, `aura-holo`, `aura-gold`, `aura-silver`, `aura-glow`
- size: `aura-xs`, `aura-sm`, `aura-md`, `aura-lg`, `aura-xl`

#### Syntax
```html
<div class="aura {MODIFIER}">{CONTENT}</div>
```

#### Rules
- `{MODIFIER}` is optional. It can include one class name from each style and size category.
- To set a custom color, use a `text-*` color class. For example, `text-primary` sets the aura to the primary color.
- To set a custom background color, use a `bg-*` color class. For example, `bg-secondary` sets a secondary-color background.
- To set a custom animation time, use a `duration-*` class. For example, `duration-1000` sets the animation time to one second.
- An aura must have one direct child element.
- Use an aura for an important button, card, or div.
- Do not use an aura for more than one element on the same page. More than one aura can make the page difficult to view.

### Badge
Use a badge to show the status of data.

[Badge documentation](https://daisyui.com/components/badge/)

#### Class names
- component: `badge`
- style: `badge-outline`, `badge-dash`, `badge-soft`, `badge-ghost`
- color: `badge-neutral`, `badge-primary`, `badge-secondary`, `badge-accent`, `badge-info`, `badge-success`, `badge-warning`, `badge-error`
- size: `badge-xs`, `badge-sm`, `badge-md`, `badge-lg`, `badge-xl`

#### Syntax
```html
<span class="badge {MODIFIER}">Badge</span>
```

#### Rules
- `{MODIFIER}` is optional. It can include one class name from each style, color, and size category.
- You can use a badge in text or buttons.
- To make an empty badge, remove the text between the span tags.

### Card
Use cards to group and show content.

[Card documentation](https://daisyui.com/components/card/)

#### Class names
- component: `card`
- part: `card-title`, `card-body`, `card-actions`
- style: `card-border`, `card-dash`
- modifier: `card-side`, `image-full`
- size: `card-xs`, `card-sm`, `card-md`, `card-lg`, `card-xl`

#### Syntax
```html
<div class="card {MODIFIER}">
  <figure><img src="{image-url}" alt="{alt-text}" /></figure>
  <div class="card-body">
    <h2 class="card-title">{title}</h2>
    <p>{CONTENT}</p>
    <div class="card-actions">{actions}</div>
  </div>
</div>
```

#### Rules
- `{MODIFIER}` is optional. It can include one modifier class name and one size class name.
- `<figure>` and `<div class="card-body">` are optional.
- For responsive layouts, use `sm:card-side`.
- If the image is after `card-body`, it is at the bottom of the card.

### Carousel
Use a carousel to show images or content in a scrollable area.

[Carousel documentation](https://daisyui.com/components/carousel/)

#### Class names
- component: `carousel`
- part: `carousel-item`
- modifier: `carousel-start`, `carousel-center`, `carousel-end`
- direction: `carousel-horizontal`, `carousel-vertical`

#### Syntax
```html
<div class="carousel {MODIFIER}">{CONTENT}</div>
```

#### Rules
- `{MODIFIER}` is optional. It can include one modifier class name and one direction class name.
- The content is a list of `carousel-item` divs: `<div class="carousel-item"></div>`.
- To make a full-width carousel, add `w-full` to each carousel item.

### Chat
A chat bubble shows one line of a conversation and its related data. This data can include the author image, name, and time.

[Chat documentation](https://daisyui.com/components/chat/)

#### Class names
- component: `chat`
- part: `chat-image`, `chat-header`, `chat-footer`, `chat-bubble`
- placement: `chat-start`, `chat-end`
- color: `chat-bubble-neutral`, `chat-bubble-primary`, `chat-bubble-secondary`, `chat-bubble-accent`, `chat-bubble-info`, `chat-bubble-success`, `chat-bubble-warning`, `chat-bubble-error`

#### Syntax
```html
<div class="chat {PLACEMENT}">
  <div class="chat-image"></div>
  <div class="chat-header"></div>
  <div class="chat-bubble {COLOR}">Message text</div>
  <div class="chat-footer"></div>
</div>
```

#### Rules
- You must specify `{PLACEMENT}` as `chat-start` or `chat-end`.
- `{COLOR}` is optional. It can be one of the color class names.
- To add an avatar, use `<div class="chat-image avatar">`. Put the avatar content in this element.

### Collapse
Use the collapse component to show and hide content.

[Collapse documentation](https://daisyui.com/components/collapse/)

#### Class names
- component: `collapse`
- part: `collapse-title`, `collapse-content`
- modifier: `collapse-arrow`, `collapse-plus`, `collapse-open`, `collapse-close`

#### Syntax
```html
<div tabindex="0" class="collapse {MODIFIER}">
  <div class="collapse-title">{title}</div>
  <div class="collapse-content">{CONTENT}</div>
</div>
```

#### Rules
- `{MODIFIER}` is optional. It can be one of the modifier class names.
- As an alternative to `tabindex="0"`, use `<input type="checkbox">` as the first child.
- You can also use `details` and `summary` tags.

### Countdown
A countdown gives a transition effect when a number changes from 0 through 999.

[Countdown documentation](https://daisyui.com/components/countdown/)

#### Class names
- component: `countdown`

#### Syntax
```html
<span class="countdown">
  <span style="--value:{number};">number</span>
</span>
```

#### Rules
- The `--value` CSS variable and the text must contain a number from 0 through 999.
- Use JavaScript to change the span text and the `--value` CSS variable.
- Add `aria-live="polite"` and `aria-label="{number}"`. These attributes let screen readers read changes correctly.

### Diff
Use the diff component to show a side-by-side comparison of two items.

[Diff documentation](https://daisyui.com/components/diff/)

#### Class names
- component: `diff`
- part: `diff-item-1`, `diff-item-2`, `diff-resizer`

#### Syntax
```html
<figure class="diff">
  <div class="diff-item-1">{item1}</div>
  <div class="diff-item-2">{item2}</div>
  <div class="diff-resizer"></div>
</figure>
```

#### Rules
- To keep the aspect ratio, add `aspect-16/9` or another aspect-ratio class to the `<figure class="diff">` element.

### Hover 3D
The hover 3D component is a wrapper that adds a 3D effect to its content. When the pointer is on the component, the component tilts and turns in relation to the pointer position.

The `hover-3d` component puts eight hover zones above the content. Each zone detects pointer movement and turns the content by a small angle. The angle changes with the pointer position in the zone. Together, the eight zones make a continuous 3D tilt effect.

Use only noninteractive content in the `hover-3d` wrapper. To make the complete card clickable, use a link for the complete `hover-3d` component. Do not put interactive elements in the wrapper.

[Hover 3D documentation](https://daisyui.com/components/hover-3d/)

#### Class names
- component: `hover-3d`

#### Syntax
```html
<div class="hover-3d my-12 mx-2">
  <figure class="max-w-100 rounded-2xl">
    <img src="https://img.daisyui.com/images/stock/creditcard.webp" alt="Tailwind CSS 3D card" />
  </figure>
  <div></div>
  <div></div>
  <div></div>
  <div></div>
  <div></div>
  <div></div>
  <div></div>
  <div></div>
</div>
```

#### Rules
- The hover 3D component can be a `<div>` or an `<a>` element.
- The hover 3D component must have exactly nine direct children. The first child is the main content. The other eight children are empty `<div>` elements for the hover zones.
- Do not put interactive content in the hover 3D component. Interactive content includes buttons, links, and inputs.

### Hover gallery
A hover gallery is a container for images. The first image is visible by default. When the pointer moves horizontally on it, the other images appear. Use a hover gallery for product cards, e-commerce sites, portfolios, or image galleries. A hover gallery can contain a maximum of 10 images.

[Hover gallery documentation](https://daisyui.com/components/hover-gallery/)

#### Class names
- component: `hover-gallery`

#### Syntax
```html
<figure class="hover-gallery max-w-60">
  <img src="https://img.daisyui.com/images/stock/daisyui-hat-1.webp" />
  <img src="https://img.daisyui.com/images/stock/daisyui-hat-2.webp" />
  <img src="https://img.daisyui.com/images/stock/daisyui-hat-3.webp" />
  <img src="https://img.daisyui.com/images/stock/daisyui-hat-4.webp" />
</figure>
```

#### Rules
- The hover gallery can be a `<div>` or a `<figure>` element.
- The hover gallery can contain a maximum of 10 images.
- Set a maximum width for the hover gallery. If you do not set it, the hover gallery fills the container width.
- All images must have the same dimensions. This gives correct alignment.

### Kbd
Use the kbd component to show keyboard shortcuts.

[Kbd documentation](https://daisyui.com/components/kbd/)

#### Class names
- component: `kbd`
- size: `kbd-xs`, `kbd-sm`, `kbd-md`, `kbd-lg`, `kbd-xl`

#### Syntax
```html
<kbd class="kbd {MODIFIER}">K</kbd>
```

#### Rules
- `{MODIFIER}` is optional. It can be one of the size class names.

### List
Use a list to show information in rows in a vertical layout.

[List documentation](https://daisyui.com/components/list/)

#### Class names
- component: `list`, `list-row`
- modifier: `list-col-wrap`, `list-col-grow`

#### Syntax
```html
<ul class="list">
  <li class="list-row">{CONTENT}</li>
</ul>
```

#### Rules
- Use `list-row` for each item in the list.
- By default, the second child of `list-row` fills the space that remains. To use a different child, add `list-col-grow` to that child.
- Use `list-col-wrap` to move an item to the next line.

### Stat
Use a stat component to show numbers and data in a block.

[Stat documentation](https://daisyui.com/components/stat/)

#### Class names
- component: `stats`
- part: `stat`, `stat-title`, `stat-value`, `stat-desc`, `stat-figure`, `stat-actions`
- direction: `stats-horizontal`, `stats-vertical`

#### Syntax
```html
<div class="stats {MODIFIER}">
  <div class="stat">{CONTENT}</div>
</div>
```

#### Rules
- `{MODIFIER}` is optional. It can be one of the direction class names.
- The default layout is horizontal. To make it vertical, use the `stats-vertical` class.
- Put `stat-title`, `stat-value`, and `stat-desc` in a `stat` element.

### Status
A status is a small icon that shows the current state of an element. Example states are online, offline, and error.

[Status documentation](https://daisyui.com/components/status/)

#### Class names
- component: `status`
- color: `status-neutral`, `status-primary`, `status-secondary`, `status-accent`, `status-info`, `status-success`, `status-warning`, `status-error`
- size: `status-xs`, `status-sm`, `status-md`, `status-lg`, `status-xl`

#### Syntax
```html
<span class="status {MODIFIER}"></span>
```

#### Rules
- `{MODIFIER}` is optional. It can include one color class name and one size class name.
- The user can easily see this small visual indicator.

### Table
Use a table to show data in rows and columns.

[Table documentation](https://daisyui.com/components/table/)

#### Class names
- component: `table`
- modifier: `table-zebra`, `table-pin-rows`, `table-pin-cols`
- size: `table-xs`, `table-sm`, `table-md`, `table-lg`, `table-xl`

#### Syntax
```html
<div class="overflow-x-auto">
  <table class="table {MODIFIER}">
    <thead>
      <tr>
        <th></th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <th></th>
      </tr>
    </tbody>
  </table>
</div>
```

#### Rules
- `{MODIFIER}` is optional. It can include one modifier class name and one size class name.
- To make the table scroll horizontally on small screens, add `overflow-x-auto` to the wrapper `<div>`.

### Text rotate
Text rotate can show a maximum of six text lines, one line at a time. It uses a continuous loop animation. The default animation time is 10 seconds. The animation pauses when the pointer is on the text.

[Text rotate documentation](https://daisyui.com/components/text-rotate/)

#### Class names
- component: `text-rotate`

#### Syntax
```html
<span class="text-rotate">
  <span>
    <span>Word 1</span>
    <span>Word 2</span>
    <span>Word 3</span>
    <span>Word 4</span>
    <span>Word 5</span>
    <span>Word 6</span>
  </span>
</span>
```
Example with a large font that is horizontally centered:
```html
<span class="text-rotate max-md:text-3xl text-7xl font-title">
  <span class="justify-items-center">
    <span>DESIGN</span>
    <span>DEVELOP</span>
    <span>DEPLOY</span>
    <span>SCALE</span>
    <span>MAINTAIN</span>
    <span>REPEAT</span>
  </span>
</span>
```
Words that change in a sentence, with a different color for each word:
```html
<span>
  Providing AI Agents for 
  <span class="text-rotate">
    <span>
      <span class="bg-teal-400 text-teal-800 px-2">Designers</span>
      <span class="bg-red-400 text-red-800 px-2">Developers</span>
      <span class="bg-blue-400 text-blue-800 px-2">Managers</span>
    </span>
  </span>
</span>
```
Custom line height for a tall font or more vertical space between lines:
```html
<span class="text-rotate max-md:text-3xl text-7xl font-title leading-[2]">
  <span class="justify-items-center">
    <span>DESIGN</span>
    <span>DEVELOP</span>
    <span>DEPLOY</span>
    <span>SCALE</span>
    <span>MAINTAIN</span>
    <span>REPEAT</span>
  </span>
</span>
```

#### Rules
- `text-rotate` must contain one `<span>` or `<div>`. This child must contain two to six `<span>` or `<div>` elements, one for each text line.
- The default total loop time is 10000 milliseconds.
- To set a custom time, use the `duration-{value}` utility class. The value is in milliseconds. For example, use `duration-12000` for 12 seconds.

### Timeline
Use a timeline to show a list of events in chronological order.

[Timeline documentation](https://daisyui.com/components/timeline/)

#### Class names
- component: `timeline`
- part: `timeline-start`, `timeline-middle`, `timeline-end`
- modifier: `timeline-snap-icon`, `timeline-box`, `timeline-compact`
- direction: `timeline-vertical`, `timeline-horizontal`

#### Syntax
```html
<ul class="timeline {MODIFIER}">
  <li>
    <div class="timeline-start">{start}</div>
    <div class="timeline-middle">{icon}</div>
    <div class="timeline-end">{end}</div>
  </li>
</ul>
```

#### Rules
- `{MODIFIER}` is optional. It can include one modifier class name and one direction class name.
- The default timeline is vertical. You can also add the `timeline-vertical` class to the `ul` element.
- Add `timeline-snap-icon` to put the icon at the start instead of the middle.
- Add the `timeline-compact` class to put all items on one side.


## Navigation

### Breadcrumbs
Use breadcrumbs to help users navigate.

[Breadcrumbs documentation](https://daisyui.com/components/breadcrumbs/)

#### Class names
- component: `breadcrumbs`

#### Syntax
```html
<div class="breadcrumbs">
  <ul><li><a>Link</a></li></ul>
</div>
```

#### Rules
- The breadcrumbs component has one main class name.
- You can put icons in the links.
- If you set `max-width` or the list becomes wider than its container, the breadcrumbs list scrolls.

### Dock
A dock is also called bottom navigation or a bottom bar. It gives navigation options and stays at the bottom of the screen.

[Dock documentation](https://daisyui.com/components/dock/)

#### Class names
- component: `dock`
- part: `dock-label`
- modifier: `dock-active`
- size: `dock-xs`, `dock-sm`, `dock-md`, `dock-lg`, `dock-xl`

#### Syntax
```html
<div class="dock {MODIFIER}">{CONTENT}</div>
```
The content is a list of buttons:
```html
<button>
    <svg>{icon}</svg>
    <span class="dock-label">Text</span>
</button>
```

#### Rules
- `{MODIFIER}` is optional. It can be one of the size class names.
- To make a button active, add the `dock-active` class to the button.
- For a responsive dock in iOS, add `<meta name="viewport" content="viewport-fit=cover">`.

### Link
The link component adds an underline to links.

[Link documentation](https://daisyui.com/components/link/)

#### Class names
- component: `link`
- style: `link-hover`
- color: `link-neutral`, `link-primary`, `link-secondary`, `link-accent`, `link-success`, `link-info`, `link-warning`, `link-error`

#### Syntax
```html
<a class="link {MODIFIER}">Click me</a>
```

#### Rules
- `{MODIFIER}` is optional. It can be one of the listed class names.

### Megamenu
A megamenu is a large horizontal menu. Each item opens a popover that shows a large group of navigation links. Use one megamenu at the top of the page. Each popover can contain a daisyUI menu or custom content. Use a megamenu on large screens. On small screens, hide it and show its content in a dropdown or drawer.

[Megamenu documentation](https://daisyui.com/components/megamenu/)

#### Class names
- component: `megamenu`
- part: `megamenu-active`
- modifier: `megamenu-wide`, `megamenu-full`
- direction: `megamenu-vertical`
- size: `megamenu-xs`, `megamenu-sm`, `megamenu-md`, `megamenu-lg`, `megamenu-xl`

#### Syntax
```html
<button class="btn sm:hidden" popovertarget="my-megamenu-1">Menu</button>
<div class="megamenu max-sm:megamenu-vertical {MODIFIER} p-2 border border-base-300" id="my-megamenu-1" popover>
  <span class="megamenu-active"></span>

  <button popovertarget="item-1">button 1</button>
  <div id="item-1" popover>
    {CONTENT}
  </div>

  <button popovertarget="item-2">button 2</button>
  <div id="item-2" popover>
    {CONTENT}
  </div>

</div>
```
Example of `megamenu-wide` with many menu items:
```html
<button class="btn sm:hidden" popovertarget="my-megamenu-2">Menu</button>
<div class="megamenu max-sm:megamenu-vertical megamenu-wide w-full p-2 border border-base-300" id="my-megamenu-2" popover>
  <span class="megamenu-active"></span>
  <button popovertarget="c1">One</button>
  <div id="c1" popover>
    <div class="flex max-sm:flex-col items-start">
      <ul class="menu w-full md:menu-horizontal">
        <li>
          <a>first column menu item</a>
          <ul><li><a>sub menu item</a></li></ul>
        </li>
        <li>
          <a>second column menu item</a>
          <ul><li><a>sub menu item</a></li></ul>
        </li>
        <li>
          <a>third column menu item</a>
          <ul><li><a>sub menu item</a></li></ul>
        </li>
      </ul>
      <img src="{image-url}" class="md:max-w-sm max-md:w-auto" alt="sample image at the end of the megamenu">
    </div>
  </div>
</div>
```


#### Rules
- `{MODIFIER}` is optional. It can include one modifier class name and one size class name.
- You must include the `megamenu-active` span. It is the indicator that moves below the active item.
- Each button must have a related popover. Its ID must be the same as the `popovertarget` value. Do not use an HTML ID more than once.
- `{CONTENT}` can include a daisyUI menu, such as `<ul class="menu"><li><a>List item 1</a></li></ul>`. It can also include custom content.
- You can put a horizontal menu in the popover. For example, use `<ul class="menu menu-horizontal"><li><a>List item 1</a></li></ul>`. You can also use a different daisyUI `menu` variation.
- On small screens, use `max-sm:megamenu-vertical` to hide the megamenu. When it is visible, it has a vertical layout. The button with `popovertarget="my-megamenu-1"` opens the megamenu with `id="my-megamenu-1" popover`.
- On large screens, use `sm:hidden` to hide the button. The megamenu has a horizontal layout. Each button in the megamenu opens its related popover.
- A megamenu can contain a maximum of 10 popovers.
- To hide the arrow on each button, add `after:content-none` to the buttons.

### Menu
Use a menu to show a list of links vertically or horizontally.

[Menu documentation](https://daisyui.com/components/menu/)

#### Class names
- component: `menu`
- part: `menu-title`, `menu-dropdown`, `menu-dropdown-toggle`
- modifier: `menu-disabled`, `menu-active`, `menu-focus`, `menu-dropdown-show`, `menu-paged`
- size: `menu-xs`, `menu-sm`, `menu-md`, `menu-lg`, `menu-xl`
- direction: `menu-vertical`, `menu-horizontal`

#### Syntax
Vertical menu:
```html
<ul class="menu">
  <li><button>Item</button></li>
</ul>
```
Horizontal menu:
```html
<ul class="menu menu-horizontal">
  <li><button>Item</button></li>
</ul>
```

#### Rules
- `{MODIFIER}` is optional. It can include one modifier class name, one size class name, and one direction class name.
- For responsive layouts, use `lg:menu-horizontal`.
- Use `menu-title` for the list-item title.
- Use the `<details>` tag to make submenus collapsible.
- Use `menu-paged` to show one submenu level at a time. The open `<summary>` becomes the back button.
- Use `menu-dropdown` and `menu-dropdown-toggle` to control the dropdown with JavaScript.

### Navbar
Use a navbar to show navigation at the top of the page.

[Navbar documentation](https://daisyui.com/components/navbar/)

#### Class names
- component: `navbar`
- part: `navbar-start`, `navbar-center`, `navbar-end`

#### Syntax
```html
<div class="navbar">{CONTENT}</div>
```

#### Rules
- Use `navbar-start`, `navbar-center`, and `navbar-end` to put content in horizontal positions.
- Put the applicable content in each section.
- You can use `base-200` for the background color.

### Pagination
Pagination is a group of buttons.

[Pagination documentation](https://daisyui.com/components/pagination/)

#### Class names
- component: `join`
- part: `join-item`
- direction: `join-vertical`, `join-horizontal`

#### Syntax
```html
<div class="join">{CONTENT}</div>
```

#### Rules
- Use `join-item` for each button or link in the pagination.
- Use the `btn` class to style pagination items.

### Steps
Use the steps component to show a sequence in a process.

[Steps documentation](https://daisyui.com/components/steps/)

#### Class names
- component: `steps`
- part: `step`, `step-icon`
- color: `step-neutral`, `step-primary`, `step-secondary`, `step-accent`, `step-info`, `step-success`, `step-warning`, `step-error`
- direction: `steps-vertical`, `steps-horizontal`

#### Syntax
```html
<ul class="steps {DIRECTION}">
  <li class="step step-primary">{completed step}</li>
  <li class="step">{upcoming step}</li>
</ul>
```

#### Rules
- The default steps layout is horizontal. For a vertical layout, add `steps-vertical` to the `ul`.
- Add direction classes to `steps`. Add `step-*` color classes to each applicable `step` item.
- To mark a step with the primary color, add `step-primary` to its `li`.
- To add an icon to a step, use the `step-icon` class.
- To show custom data, add `data-content="{value}"` to the `<li>`.

### Tab
Use tabs to show a list of links in a tabbed format.

[Tab documentation](https://daisyui.com/components/tab/)

#### Class names
- component: `tabs`
- part: `tab`, `tab-content`
- style: `tabs-box`, `tabs-border`, `tabs-lift`
- size: `tabs-xs`, `tabs-sm`, `tabs-md`, `tabs-lg`, `tabs-xl`
- modifier: `tab-active`, `tab-disabled`
- placement: `tabs-top`, `tabs-bottom`

#### Syntax
Buttons:
```html
<div role="tablist" class="tabs {MODIFIER}">
  <button role="tab" class="tab">Tab</button>
</div>
```

Radio inputs:
```html
<div role="tablist" class="tabs tabs-box">
  <input type="radio" name="my_tabs" class="tab" aria-label="Tab" />
</div>
```

#### Rules
- `{MODIFIER}` is optional. It can include one style class name and one size class name.
- To change the tab content after the user clicks a tab, use radio inputs.
- If you add a background to `tabs`, the two top corners of each tab become rounded.


## Feedback

### Alert
Use an alert to give users information about an important event.

[Alert documentation](https://daisyui.com/components/alert/)

#### Class names
- component: `alert`
- style: `alert-outline`, `alert-dash`, `alert-soft`
- color: `alert-info`, `alert-success`, `alert-warning`, `alert-error`
- direction: `alert-vertical`, `alert-horizontal`

#### Syntax
```html
<div role="alert" class="alert {MODIFIER}">{CONTENT}</div>
```

#### Rules
- `{MODIFIER}` is optional. It can include one class name from each style, color, and direction category.
- For responsive layouts, add `sm:alert-horizontal`.

### Loading
Use the loading component to show an animation while a process runs.

[Loading documentation](https://daisyui.com/components/loading/)

#### Class names
- component: `loading`
- style: `loading-spinner`, `loading-dots`, `loading-ring`, `loading-ball`, `loading-bars`, `loading-infinity`
- size: `loading-xs`, `loading-sm`, `loading-md`, `loading-lg`, `loading-xl`

#### Syntax
```html
<span class="loading {MODIFIER}"></span>
```

#### Rules
- `{MODIFIER}` is optional. It can include one style class name and one size class name.

### Progress
Use a progress bar to show task progress or the passage of time.

[Progress documentation](https://daisyui.com/components/progress/)

#### Class names
- component: `progress`
- color: `progress-neutral`, `progress-primary`, `progress-secondary`, `progress-accent`, `progress-info`, `progress-success`, `progress-warning`, `progress-error`

#### Syntax
```html
<progress class="progress {MODIFIER}" value="50" max="100"></progress>
```

#### Rules
- `{MODIFIER}` is optional. It can be one of the color class names.
- You must specify the `value` and `max` attributes.

### Radial progress
Use the radial progress component to show task progress or the passage of time.

[Radial progress documentation](https://daisyui.com/components/radial-progress/)

#### Class names
- component: `radial-progress`

#### Syntax
```html
<div class="radial-progress" style="--value:70;" aria-valuenow="70" role="progressbar">70%</div>
```

#### Rules
- The `--value` CSS variable and the text must contain a number from 0 through 100.
- Add `aria-valuenow={value}` and `role="progressbar"`. These attributes let screen readers identify the progress element and read its value.
- Use a `div` instead of a progress tag. Browsers cannot show text in a progress tag.
- Use `--size` to set the size. The default is 5rem. Use `--thickness` to set the indicator thickness.

### Skeleton
Use a skeleton component to show a loading state.

[Skeleton documentation](https://daisyui.com/components/skeleton/)

#### Class names
- component: `skeleton`
- modifier: `skeleton-text`

#### Syntax
```html
<div class="skeleton"></div>
```
Example with a text skeleton:
```html
<div class="skeleton skeleton-text">Loading data...</div>
```

#### Rules
- Add the `h-*` and `w-*` utility classes to set the height and width.

### Toast
A toast is a wrapper that stacks elements in a corner of the page.

[Toast documentation](https://daisyui.com/components/toast/)

#### Class names
- component: `toast`
- placement: `toast-start`, `toast-center`, `toast-end`, `toast-top`, `toast-middle`, `toast-bottom`

#### Syntax
```html
<div class="toast {MODIFIER}">{CONTENT}</div>
```

#### Rules
- `{MODIFIER}` is optional. It can be one of the placement class names.

### Tooltip
A tooltip shows a message when the pointer is on an element.

[Tooltip documentation](https://daisyui.com/components/tooltip/)

#### Class names
- component: `tooltip`
- part: `tooltip-content`
- modifier: `tooltip-open`
- placement: `tooltip-top`, `tooltip-bottom`, `tooltip-left`, `tooltip-right`
- alignment: `tooltip-start`, `tooltip-center`, `tooltip-end`
- color: `tooltip-primary`, `tooltip-secondary`, `tooltip-accent`, `tooltip-info`, `tooltip-success`, `tooltip-warning`, `tooltip-error`

#### Syntax
```html
<div class="tooltip {MODIFIER}" data-tip="Tooltip text">
  <button class="btn">Hover me</button>
</div>
```

#### Rules
- `{MODIFIER}` is optional. It can include one class name from each modifier, placement, and color category.


## Data input

### Calendar
The calendar component includes styles for different calendar libraries.

[Calendar documentation](https://daisyui.com/components/calendar/)

#### Class names

- component
  - `cally (for Cally web component)`
  - `react-day-picker (for the DayPicker component)`
  - `vc (for Vanilla Calendar Pro)`

#### Syntax

Cally:

```html
<calendar-date class="cally">{CONTENT}</calendar-date>
```

React Day Picker:

```html
<DayPicker className="react-day-picker"></DayPicker>
```

Vanilla Calendar Pro:

```html
<div id="calendar" class="vc"></div>
```

```js
import { Calendar } from "vanilla-calendar-pro"

const calendar = new Calendar("#calendar")
calendar.init()
```

CDN alternative:

```html
<script src="https://cdn.jsdelivr.net/npm/vanilla-calendar-pro/index.js" defer></script>
<div id="calendar" class="vc"></div>
<script>
  document.addEventListener("DOMContentLoaded", () => {
    const { Calendar } = window.VanillaCalendarPro
    const calendar = new Calendar("#calendar")
    calendar.init()
  })
</script>
```

#### Rules

- daisyUI supports Cally, React Day Picker, and Vanilla Calendar Pro.

### Checkbox
Use a checkbox to select or deselect a value.

[Checkbox documentation](https://daisyui.com/components/checkbox/)

#### Class names
- component: `checkbox`
- color: `checkbox-primary`, `checkbox-secondary`, `checkbox-accent`, `checkbox-neutral`, `checkbox-success`, `checkbox-warning`, `checkbox-info`, `checkbox-error`
- size: `checkbox-xs`, `checkbox-sm`, `checkbox-md`, `checkbox-lg`, `checkbox-xl`

#### Syntax
```html
<input type="checkbox" class="checkbox {MODIFIER}" />
```

#### Rules
- `{MODIFIER}` is optional. It can include one color class name and one size class name.

### Fieldset
Use a fieldset as a container for related form elements. Use `fieldset-legend` as the title. Use `label` as the description.

[Fieldset documentation](https://daisyui.com/components/fieldset/)

#### Class names
- component: `fieldset`, `label`
- part: `fieldset-legend`

#### Syntax
```html
<fieldset class="fieldset">
  <legend class="fieldset-legend">{title}</legend>
  {CONTENT}
  <p class="label">{description}</p>
</fieldset>
```

#### Rules
- The fieldset can have all types of elements as direct children.

### File input
Use a file input to upload files.

[File input documentation](https://daisyui.com/components/file-input/)

#### Class names
- component: `file-input`
- style: `file-input-ghost`
- color: `file-input-neutral`, `file-input-primary`, `file-input-secondary`, `file-input-accent`, `file-input-info`, `file-input-success`, `file-input-warning`, `file-input-error`
- size: `file-input-xs`, `file-input-sm`, `file-input-md`, `file-input-lg`, `file-input-xl`

#### Syntax
```html
<input type="file" class="file-input {MODIFIER}" />
```

#### Rules
- `{MODIFIER}` is optional. It can include one class name from each style, color, and size category.

### Filter
A filter is a group of radio buttons. When the user selects an option, the filter hides the other options. It also shows a reset button next to the selected option.

[Filter documentation](https://daisyui.com/components/filter/)

#### Class names
- component: `filter`
- part: `filter-reset`

#### Syntax
HTML form:
```html
<form class="filter">
  <input class="btn btn-square" type="reset" value="×"/>
  <input class="btn" type="radio" name="{NAME}" aria-label="Tab 1 title"/>
  <input class="btn" type="radio" name="{NAME}" aria-label="Tab 2 title"/>
</form>
```
No HTML form:
```html
<div class="filter">
  <input class="btn filter-reset" type="radio" name="{NAME}" aria-label="×"/>
  <input class="btn" type="radio" name="{NAME}" aria-label="Tab 1 title"/>
  <input class="btn" type="radio" name="{NAME}" aria-label="Tab 2 title"/>
</div>
```

#### Rules
- Replace `{NAME}` with a value that identifies the filter.
- Use a different `name` attribute for each set of radio inputs. This prevents conflicts.
- If the context permits, use the `<form>` tag. If you cannot use an HTML form, use `<div>`.
- Use the `filter-reset` class for the reset button.
- Do not select a radio input by default.

### Input
Use a text input as a simple input field.

[Input documentation](https://daisyui.com/components/input/)

#### Class names
- component: `input`
- style: `input-ghost`
- color: `input-neutral`, `input-primary`, `input-secondary`, `input-accent`, `input-info`, `input-success`, `input-warning`, `input-error`
- size: `input-xs`, `input-sm`, `input-md`, `input-lg`, `input-xl`

#### Syntax
```html
<input type="{type}" placeholder="Type here" class="input {MODIFIER}" />
```

#### Rules
- `{MODIFIER}` is optional. It can include one class name from each style, color, and size category.
- You can use it with all input field types, such as text, password, or email.
- If the input contains more than one element, use the `input` class on the parent element.

### Label
Use a label to give a name or title to an input field. Put the label before or after the field.

[Label documentation](https://daisyui.com/components/label/)

#### Class names
- component: `label`, `floating-label`

#### Syntax
Regular label:
```html
<label class="input">
  <span class="label">{label text}</span>
  <input type="text" placeholder="Type here" />
</label>
```
Floating label:
```html
<label class="floating-label">
  <input type="text" placeholder="Type here" class="input" />
  <span>{label text}</span>
</label>
```

#### Rules
- The `input` class styles the parent element that contains the input field and label. Do not add the `input` class to the label.
- Add `floating-label` to the parent element. This parent must contain an input field and a span. When the field has focus, the span moves above it.

### OTP
An OTP is a one-time password component that lets a user enter a verification code. The code usually contains four to six digits. Use it for two-factor authentication (2FA) or passwordless login.

[OTP documentation](https://daisyui.com/components/otp/)

#### Class names
- component: `otp`
- size: `otp-xs`, `otp-sm`, `otp-md`, `otp-lg`, `otp-xl`
- modifier: `otp-joined`
- color: `otp-neutral`, `otp-primary`, `otp-secondary`, `otp-accent`, `otp-info`, `otp-success`, `otp-warning`, `otp-error`

#### Syntax
```html
<label class="otp {MODIFIER}">
  <span></span>
  <span></span>
  <span></span>
  <span></span>
  <input type="text" autocomplete="one-time-code" inputmode="numeric" maxlength="4" pattern="[0-9]{4}" required />
</label>
```

#### Rules
- `{MODIFIER}` is optional. It can include one size class name and one color class name.
- The `otp-joined` modifier connects the character boxes.
- The `otp` class is for a label. The label must have four to six empty `<span>` elements that show the digits. It must also have an input field for the code.
- The number of `<span>` elements must agree with the `maxlength` attribute and the input pattern. For six `<span>` elements, use `maxlength="6"` and `pattern="\d{6}"`.
- On mobile devices, add `autocomplete="one-time-code"` and `inputmode="numeric"`. These attributes show the applicable keyboard and permit OTP autofill.

### Radio
Use radio buttons to let the user select one option.

[Radio documentation](https://daisyui.com/components/radio/)

#### Class names
- component: `radio`
- color: `radio-neutral`, `radio-primary`, `radio-secondary`, `radio-accent`, `radio-success`, `radio-warning`, `radio-info`, `radio-error`
- size: `radio-xs`, `radio-sm`, `radio-md`, `radio-lg`, `radio-xl`

#### Syntax
```html
<input type="radio" name="{name}" class="radio {MODIFIER}" />
```

#### Rules
- `{MODIFIER}` is optional. It can include one size class name and one color class name.
- Replace `{name}` with a name for the radio group.
- Recommendation: Use a unique `name` attribute for each radio-input group. This prevents conflicts with other groups on the same page.

### Range
Move a range-slider handle to select a value.

[Range documentation](https://daisyui.com/components/range/)

#### Class names
- component: `range`
- color: `range-neutral`, `range-primary`, `range-secondary`, `range-accent`, `range-success`, `range-warning`, `range-info`, `range-error`
- size: `range-xs`, `range-sm`, `range-md`, `range-lg`, `range-xl`
- direction: `range-vertical` (vertical slider)

#### Syntax
```html
<input type="range" min="0" max="100" value="40" class="range {MODIFIER}" />
```

#### Rules
- `{MODIFIER}` is optional. It can include one color class name and one size class name.
- For a vertical slider, use `range-vertical`.
- You must specify the `min` and `max` attributes.

### Rating
A rating is a set of radio buttons that lets the user give a rating.

[Rating documentation](https://daisyui.com/components/rating/)

#### Class names
- component: `rating`
- modifier: `rating-half`, `rating-hidden`
- size: `rating-xs`, `rating-sm`, `rating-md`, `rating-lg`, `rating-xl`

#### Syntax
```html
<div class="rating {MODIFIER}">
  <input type="radio" name="rating-1" class="mask mask-star" />
</div>
```

For a read-only, noninteractive rating, use `<div>` elements instead of radio inputs. Add `aria-current="true"` to the selected element:
```html
<div class="rating">
  <div class="mask mask-star" aria-label="1 star"></div>
  <div class="mask mask-star" aria-label="2 star" aria-current="true"></div>
  <div class="mask mask-star" aria-label="3 star"></div>
</div>
```

#### Rules
- `{MODIFIER}` is optional. It can include one modifier class name and one size class name.
- Recommendation: Use a unique `name` attribute for each rating-input group. This prevents conflicts with other ratings on the same page.
- Add `rating-hidden` to the first radio input to hide it. This lets the user clear the rating.
- For a read-only, noninteractive rating, use `<div>` elements instead of radio inputs. Add `aria-current="true"` to the selected element.

### Select
Use a select component to select a value from a list of options.

[Select documentation](https://daisyui.com/components/select/)

#### Class names
- component: `select`
- style: `select-ghost`
- color: `select-neutral`, `select-primary`, `select-secondary`, `select-accent`, `select-info`, `select-success`, `select-warning`, `select-error`
- size: `select-xs`, `select-sm`, `select-md`, `select-lg`, `select-xl`

#### Syntax
```html
<select class="select {MODIFIER}">
  <option>Option</option>
</select>
```

#### Rules
- `{MODIFIER}` is optional. It can include one class name from each style, color, and size category.

### Textarea
A textarea lets users enter text on more than one line.

[Textarea documentation](https://daisyui.com/components/textarea/)

#### Class names
- component: `textarea`
- style: `textarea-ghost`
- color: `textarea-neutral`, `textarea-primary`, `textarea-secondary`, `textarea-accent`, `textarea-info`, `textarea-success`, `textarea-warning`, `textarea-error`
- size: `textarea-xs`, `textarea-sm`, `textarea-md`, `textarea-lg`, `textarea-xl`

#### Syntax
```html
<textarea class="textarea {MODIFIER}" placeholder="Bio"></textarea>
```

#### Rules
- `{MODIFIER}` is optional. It can include one class name from each style, color, and size category.

### Toggle
A toggle is a checkbox with the style of a switch button.

[Toggle documentation](https://daisyui.com/components/toggle/)

#### Class names
- component: `toggle`
- color: `toggle-primary`, `toggle-secondary`, `toggle-accent`, `toggle-neutral`, `toggle-success`, `toggle-warning`, `toggle-info`, `toggle-error`
- size: `toggle-xs`, `toggle-sm`, `toggle-md`, `toggle-lg`, `toggle-xl`

#### Syntax
```html
<input type="checkbox" class="toggle {MODIFIER}" />
```

#### Rules
- `{MODIFIER}` is optional. It can include one color class name and one size class name.

### Validator
The validator class sets an error color or a success color on a form element. The input validation rules control the color.

[Validator documentation](https://daisyui.com/components/validator/)

#### Class names
- component: `validator`
- part: `validator-hint`

#### Syntax
```html
<input type="{type}" class="input validator" required />
<p class="validator-hint">Error message</p>
```

#### Rules
- Use the validator with `input`, `select`, and `textarea`.


## Layout

### Divider
Use a divider to separate content vertically or horizontally.

[Divider documentation](https://daisyui.com/components/divider/)

#### Class names
- component: `divider`
- color: `divider-neutral`, `divider-primary`, `divider-secondary`, `divider-accent`, `divider-success`, `divider-warning`, `divider-info`, `divider-error`
- direction: `divider-vertical`, `divider-horizontal`
- placement: `divider-start`, `divider-end`

#### Syntax
```html
<div class="divider {MODIFIER}">{text}</div>
```

#### Rules
- `{MODIFIER}` is optional. It can include one class name from each direction, color, and placement category.
- For a blank divider, do not add text.

### Drawer
A drawer is a grid layout that can show and hide a sidebar. The sidebar can be on either side of the page.

[Drawer documentation](https://daisyui.com/components/drawer/)

#### Class names
- component: `drawer`
- part: `drawer-toggle`, `drawer-content`, `drawer-side`, `drawer-overlay`, `drawer-button`
- placement: `drawer-end`
- modifier: `drawer-open`
- variant: `is-drawer-open:`, `is-drawer-close:`

#### Syntax
```html
<div class="drawer {MODIFIER}">
  <input id="my-drawer" type="checkbox" class="drawer-toggle" />
  <div class="drawer-content">{CONTENT}</div>
  <div class="drawer-side">{SIDEBAR}</div>
</div>
```
The `{CONTENT}` can contain a navbar, the site content, or a footer.
The `{SIDEBAR}` can contain a menu:
```html
<ul class="menu p-4 w-80 min-h-full bg-base-100 text-base-content">
  <li><a>Item 1</a></li>
  <li><a>Item 2</a></li>
</ul>
```
To open and close the drawer, use a label whose `for` attribute matches the `drawer-toggle` input ID:
```html
<label for="my-drawer" class="btn drawer-button">Open/close drawer</label>
```
Example: This sidebar is always visible on large screens. The user can toggle it on small screens:
```html
<div class="drawer lg:drawer-open">
  <input id="my-drawer-3" type="checkbox" class="drawer-toggle" />
  <div class="drawer-content flex flex-col items-center justify-center">
    <!-- Page content here -->
    <label for="my-drawer-3" class="btn drawer-button lg:hidden">
      Open drawer
    </label>
  </div>
  <div class="drawer-side">
    <label for="my-drawer-3" aria-label="close sidebar" class="drawer-overlay"></label>
    <ul class="menu bg-base-200 min-h-full w-80 p-4">
      <!-- Sidebar content here -->
      <li><button>Sidebar Item 1</button></li>
      <li><button>Sidebar Item 2</button></li>
    </ul>
  </div>
</div>
```

Example: This sidebar is always visible. In the closed state, it shows only icons. In the open state, it shows icons and text:
```html
<div class="drawer lg:drawer-open">
  <input id="my-drawer-4" type="checkbox" class="drawer-toggle" />
  <div class="drawer-content">
    <!-- Page content here -->
  </div>
  <div class="drawer-side is-drawer-close:overflow-visible">
    <label for="my-drawer-4" aria-label="close sidebar" class="drawer-overlay"></label>
    <div class="is-drawer-close:w-14 is-drawer-open:w-64 bg-base-200 flex flex-col items-start min-h-full">
      <!-- Sidebar content here -->
      <ul class="menu w-full grow">
        <!-- list item -->
        <li>
          <button class="is-drawer-close:tooltip is-drawer-close:tooltip-right" data-tip="Homepage">
            {ICON_HERE}
            <span class="is-drawer-close:hidden">Homepage</span>
          </button>
        </li>
        <!-- list item -->
        <li>
          <button class="is-drawer-close:tooltip is-drawer-close:tooltip-right" data-tip="Settings">
            {ICON_HERE}
            <span class="is-drawer-close:hidden">Settings</span>
          </button>
        </li>
      </ul>
      <!-- button to open/close drawer -->
      <div class="m-2 is-drawer-close:tooltip is-drawer-close:tooltip-right" data-tip="Open">
        <label for="my-drawer-4" class="btn btn-ghost btn-circle drawer-button is-drawer-open:rotate-y-180">
          {ICON_HERE}
        </label>
      </div>
    </div>
  </div>
</div>
```

#### Rules
- `{MODIFIER}` is optional. It can include one modifier class name and one placement class name.
- You must add an `id` to the `drawer-toggle` input. Change `my-drawer` to a unique HTML ID.
- To make the sidebar visible on larger screens, use `lg:drawer-open`.
- The `drawer-toggle` is a hidden checkbox. Use a label with a `for` attribute to change the checkbox state.
- To open the drawer with a button, use `<label for="my-drawer" class="btn drawer-button">Open drawer</label>`. The `my-drawer` value is the ID of the `drawer-toggle` input.
- When you use a drawer, put all page content in the `drawer-content` element. Put the navbar and footer inside the `drawer`.

### Footer
A footer can contain a logo, a copyright notice, and links to other pages.

[Footer documentation](https://daisyui.com/components/footer/)

#### Class names
- component: `footer`
- part: `footer-title`
- placement: `footer-center`
- direction: `footer-horizontal`, `footer-vertical`

#### Syntax
```html
<footer class="footer {MODIFIER}">{CONTENT}</footer>
```
The content can contain more than one `<nav>` tag. Each tag can contain `footer-title` and links.

#### Rules
- `{MODIFIER}` is optional. It can include one placement class name and one direction class name.
- To make the footer responsive, use `sm:footer-horizontal`.
- You can use `base-200` for the background color.

### Hero
Use a hero to show a large box or image with a title and description.

[Hero documentation](https://daisyui.com/components/hero/)

#### Class names
- component: `hero`
- part: `hero-content`, `hero-overlay`

#### Syntax
```html
<div class="hero {MODIFIER}">{CONTENT}</div>
```

#### Rules
- `{MODIFIER}` is optional.
- Use `hero-content` for the text content.
- Put `hero-overlay` in the hero. It adds a color layer above the background image.
- The content can contain a figure.

### Indicator
Use an indicator to put an element at the corner of another element.

[Indicator documentation](https://daisyui.com/components/indicator/)

#### Class names
- component: `indicator`
- part: `indicator-item`
- placement: `indicator-start`, `indicator-center`, `indicator-end`, `indicator-top`, `indicator-middle`, `indicator-bottom`

#### Syntax
```html
<div class="indicator">
  <span class="indicator-item">{indicator content}</span>
  <div>{main content}</div>
</div>
```

#### Rules
- Put all indicator elements with the `indicator-item` class before the main content.
- `{placement}` is optional. It can include one horizontal class name and one vertical class name. The default is `indicator-end indicator-top`.

### Join
A join is a container that groups more than one item. Use it to group buttons, inputs, or other elements. The join applies a border radius to the first and last items. It can make a horizontal or vertical list of items.

[Join documentation](https://daisyui.com/components/join/)

#### Class names
- component: `join`, `join-item`
- direction: `join-vertical`, `join-horizontal`

#### Syntax
```html
<div class="join {MODIFIER}">{CONTENT}</div>
```

#### Rules
- `{MODIFIER}` is optional. It can be one of the direction class names.
- The join element joins all its direct children.
- The join element affects all elements that have `join-item`.
- For responsive layouts, use `lg:join-horizontal`.

### Mask
A mask crops the content of an element to a common shape.

[Mask documentation](https://daisyui.com/components/mask/)

#### Class names
- component: `mask`
- style: `mask-squircle`, `mask-heart`, `mask-hexagon`, `mask-hexagon-2`, `mask-decagon`, `mask-pentagon`, `mask-diamond`, `mask-circle`, `mask-star`, `mask-star-2`, `mask-triangle`, `mask-triangle-2`, `mask-triangle-3`, `mask-triangle-4`
- modifier: `mask-half-1`, `mask-half-2`

#### Syntax
```html
<img class="mask {MODIFIER}" src="{image-url}" />
```

#### Rules
- You must specify `{MODIFIER}`. It can be one of the style or modifier class names.
- To change the shape of an element, use the `mask` class names.
- To set a custom size, use `w-*` and `h-*`.

### Stack
A stack puts elements on top of each other.

[Stack documentation](https://daisyui.com/components/stack/)

#### Class names
- component: `stack`
- modifier: `stack-top`, `stack-bottom`, `stack-start`, `stack-end`

#### Syntax
```html
<div class="stack {MODIFIER}">{CONTENT}</div>
```

#### Rules
- `{MODIFIER}` is optional. It can be one of the modifier class names.
- Use the `w-*` and `h-*` classes to set the stack width and height. These classes make all items the same size.


## Mockup

### Mockup browser
A browser mockup is a box in the form of a browser window.

[Browser mockup documentation](https://daisyui.com/components/mockup-browser/)

#### Class names
- component: `mockup-browser`
- part: `mockup-browser-toolbar`

#### Syntax
```html
<div class="mockup-browser">
  <div class="mockup-browser-toolbar">
    {toolbar content}
  </div>
  <div>{CONTENT}</div>
</div>
```

#### Rules
- For a default mockup, use only the `mockup-browser` class name.
- To set a URL in the toolbar, add a `<div>` with the `input` class.

### Mockup code
Use a code mockup to show code in a box with the style of a code editor.

[Code mockup documentation](https://daisyui.com/components/mockup-code/)

#### Class names
- component: `mockup-code`

#### Syntax
```html
<div class="mockup-code">
  <pre data-prefix="$"><code>npm i daisyui</code></pre>
</div>
```

#### Rules
- Use `<pre data-prefix="{prefix}">` to show a prefix before each line.
- Use the `<code>` tag to add code syntax highlighting. Another library is necessary for this feature.
- To make a line easy to see, add a background color or text color.

### Mockup phone
A phone mockup shows an iPhone mockup.

[Phone mockup documentation](https://daisyui.com/components/mockup-phone/)

#### Class names
- component: `mockup-phone`
- part: `mockup-phone-camera`, `mockup-phone-display`

#### Syntax
```html
<div class="mockup-phone">
  <div class="mockup-phone-camera"></div>
  <div class="mockup-phone-display">{CONTENT}</div>
</div>
```

#### Rules
- You can put content in `mockup-phone-display`.

### Mockup window
A window mockup is a box in the form of an operating-system window.

[Window mockup documentation](https://daisyui.com/components/mockup-window/)

#### Class names
- component: `mockup-window`

#### Syntax
```html
<div class="mockup-window">
  <div>{CONTENT}</div>
</div>
```

