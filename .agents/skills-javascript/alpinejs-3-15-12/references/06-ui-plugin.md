# UI Plugin (`@alpinejs/ui`)

The UI plugin provides accessible, composable UI components built on Alpine's directive system. Components use `Alpine.bind()` internally to compose directives programmatically.

**Note:** This plugin is in active development. APIs may change.

## Installation

```js
import Alpine from 'alpinejs'
import ui from '@alpinejs/ui'
Alpine.plugin(ui)
Alpine.start()
```

---

## Dialog (`x-dialog`)

Accessible modal dialog with focus trapping, escape-to-close, and aria attributes.

```html
<div x-dialog x-model="open">
  <div x-dialog:overlay></div>
  <div x-dialog:panel>
    <h2 x-dialog:title>Title</h2>
    <p x-dialog:description>Description</p>
    <button @click="open = false">Close</button>
  </div>
</div>
```

### Directives

| Directive | Role |
|---|---|
| `x-dialog` | Root — manages open state, focus trap, escape key |
| `x-dialog:overlay` | Background overlay, closes on click |
| `x-dialog:panel` | Content panel, closes on outside click |
| `x-dialog:title` | Dialog title (linked via `aria-labelledby`) |
| `x-dialog:description` | Dialog description (linked via `aria-describedby`) |

### Magic

`$dialog` — `{ get isOpen, close() }`

### Features

- `x-model` binding for open state
- `:open` attribute as alternative to `x-model`
- `:initial-focus` attribute to set initial focused element
- `@close` event dispatch when using `:open` binding
- `x-trap.inert.noscroll` for accessibility
- Auto `x-id` for title and description references

---

## Menu (`x-menu`)

Accessible dropdown menu with keyboard navigation.

```html
<div x-menu>
  <button x-menu:button>Menu</button>
  <div x-menu:items>
    <button x-menu:item>Action 1</button>
    <button x-menu:item disabled>Action 2</button>
    <button x-menu:item>Action 3</button>
  </div>
</div>
```

### Directives

| Directive | Role |
|---|---|
| `x-menu` | Root — manages open state, focus management |
| `x-menu:button` | Trigger button with aria attributes |
| `x-menu:items` | Menu items container |
| `x-menu:item` | Individual menu item |

### Magic

`$menuItem` — `{ get isActive, get isDisabled }`

### Features

- Keyboard navigation (arrow keys, escape, enter, space)
- `x-modelable` for open state binding
- Auto `x-id` for button and items references
- Closes on outside focus

---

## Tabs (`x-tabs`)

Accessible tab panel component.

```html
<div x-tabs x-model="selectedIndex">
  <div x-tabs:list>
    <button x-tabs:tab>Tab 1</button>
    <button x-tabs:tab disabled>Tab 2</button>
    <button x-tabs:tab>Tab 3</button>
  </div>
  <div x-tabs:panels>
    <div x-tabs:panel>Content 1</div>
    <div x-tabs:panel>Content 2</div>
    <div x-tabs:panel>Content 3</div>
  </div>
</div>
```

### Directives

| Directive | Role |
|---|---|
| `x-tabs` | Root — manages selected index |
| `x-tabs:list` | Tab list container |
| `x-tabs:tab` | Individual tab button |
| `x-tabs:panels` | Panels container |
| `x-tabs:panel` | Individual panel |

### Magics

- `$tab` — `{ get isSelected, get isDisabled }`
- `$panel` — `{ get isSelected }`

### Features

- `x-model` binding for selected index
- `:default-index` attribute for initial selection
- `:manual` attribute for manual activation mode
- `x-modelable` for parent binding
- Disabled tab support

---

## Listbox (`x-listbox`)

Accessible single-select dropdown listbox.

```html
<div x-listbox x-model="selected">
  <button x-listbox:button>Select...</button>
  <div x-listbox:options>
    <div x-listbox:option :value="'option1'">Option 1</div>
    <div x-listbox:option :value="'option2'">Option 2</div>
  </div>
</div>
```

### Directives

| Directive | Role |
|---|---|
| `x-listbox` | Root — manages selected value |
| `x-listbox:button` | Trigger button showing current selection |
| `x-listbox:options` | Options container |
| `x-listbox:option` | Individual option |

### Magic

`$listboxOption` — `{ get isSelected, get isDisabled }`

---

## Combobox (`x-combobox`)

Accessible search-enabled select component.

```html
<div x-combobox x-model="selected">
  <input x-combobox:input placeholder="Search...">
  <div x-combobox:options>
    <div x-combobox:option :value="'option1'">Option 1</div>
    <div x-combobox:option :value="'option2'">Option 2</div>
  </div>
</div>
```

### Directives

| Directive | Role |
|---|---|
| `x-combobox` | Root — manages selected value and search |
| `x-combobox:input` | Search input |
| `x-combobox:options` | Options container |
| `x-combobox:option` | Individual option |

---

## Popover (`x-popover`)

Accessible popover component.

```html
<div x-popover>
  <button x-popover:button>Trigger</button>
  <div x-popover:panel>
    Popover content
  </div>
</div>
```

### Directives

| Directive | Role |
|---|---|
| `x-popover` | Root — manages open state |
| `x-popover:button` | Trigger button |
| `x-popover:panel` | Popover content panel |

---

## Switch (`x-switch`)

Accessible toggle switch.

```html
<div x-switch x-model="enabled">
  <button x-switch:toggle>
    <span x-switch:knob></span>
  </button>
</div>
```

### Directives

| Directive | Role |
|---|---|
| `x-switch` | Root — manages checked state |
| `x-switch:toggle` | Toggle track |
| `x-switch:knob` | Toggle knob/thumb |

### Magic

`$switch` — `{ get isChecked }`

---

## Radio (`x-radio`)

Accessible radio group.

```html
<div x-radio x-model="selected">
  <div x-radio:option :value="'option1'">
    <div x-radio:circle></div>
    <span>Option 1</span>
  </div>
  <div x-radio:option :value="'option2'">
    <div x-radio:circle></div>
    <span>Option 2</span>
  </div>
</div>
```

### Directives

| Directive | Role |
|---|---|
| `x-radio` | Root — manages selected value |
| `x-radio:option` | Individual radio option |
| `x-radio:circle` | Radio circle indicator |

---

## Disclosure (`x-disclosure`)

Accessible expandable content section.

```html
<div x-disclosure>
  <button x-disclosure:button>Toggle</button>
  <div x-disclosure:panel>
    Expandable content
  </div>
</div>
```

### Directives

| Directive | Role |
|---|---|
| `x-disclosure` | Root — manages open state |
| `x-disclosure:button` | Toggle button |
| `x-disclosure:panel` | Expandable content panel |

---

## Common Patterns

### x-modelable

All UI components support `x-modelable`, enabling parent components to control state:

```html
<div x-data="{ open: false }">
  <div x-dialog x-model="open">
    <!-- dialog content -->
  </div>
</div>
```

### Composing with x-bind

UI components use `Alpine.bind()` internally. You can add additional directives alongside:

```html
<div x-dialog x-model="open" @close="onClose">
```

### Accessibility

All UI components include proper ARIA attributes, keyboard navigation, and screen reader support out of the box. The directives auto-manage `aria-expanded`, `aria-labelledby`, `aria-controls`, `role`, and related attributes.
