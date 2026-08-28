# Alpine.js 3.16.3 — `@alpinejs/ui` Headless Components

`@alpinejs/ui` (3.16.3) adds headless, accessible UI behaviors to Alpine — interaction logic, keyboard handling, and ARIA wiring, **no styling of its own** (you supply all CSS/classes). Components are directive-based: each has a root directive and sub-part directives.

```js
import Alpine from 'alpinejs'
import ui from '@alpinejs/ui'
Alpine.plugin(ui)
Alpine.start()
```

```html
<!-- CDN: before the core, deferred -->
<script defer src="https://cdn.jsdelivr.net/npm/@alpinejs/ui@3.16.3/dist/cdn.min.js"></script>
```

- [combobox](#combobox)
- [dialog](#dialog)
- [disclosure](#disclosure)
- [listbox](#listbox)
- [menu](#menu)
- [popover](#popover)
- [radio](#radio)
- [switch](#switch)
- [tabs](#tabs)

## combobox

Searchable select. Root `x-combobox` (bind with `x-model`), parts: `x-combobox:input`, `:button`, `:label`, `:options`, `:option`.

```html
<div x-data="{
    query: '',
    selected: null,
    people: [ { id: 1, name: 'Wade Cooper' }, { id: 2, name: 'Arlene Mccoy' } ],
    get filteredPeople() {
        return this.query === ''
            ? this.people
            : this.people.filter(p => p.name.toLowerCase().includes(this.query.toLowerCase()))
    },
}">
    <div x-combobox x-model="selected">
        <label x-combobox:label>Select person</label>

        <div>
            <input
                x-combobox:input
                :display-value="person => person.name"
                @change="query = $event.target.value"
                placeholder="Search..."
            />
            <button x-combobox:button>Toggle</button>
        </div>

        <div x-combobox:options>
            <template x-for="person in filteredPeople" :key="person.id">
                <li
                    x-combobox:option
                    :option="person.id"
                    :value="person"
                    :disabled="person.disabled"
                ><span x-text="person.name"></span></li>
            </template>
        </div>
    </div>
</div>
```

- `:display-value` is a function mapping the selected model value to the input text.
- Options carry `:option` (unique key, used for matching/keyboard nav) and `:value` (the payload stored into the model); `:disabled` per option.
- Filtering is yours: keep a `query` state and a `filtered` getter; feed filtered items to `:options`.

## dialog

Modal dialog. `x-dialog` on the container, bound by `x-model="open"` (boolean) or `:open="open"` with a `@close` handler. Parts: `x-dialog:overlay`, `:panel`, `:title`, `:description`.

```html
<div x-data="{ open: false }">
    <button @click="open = ! open">Open</button>

    <article x-dialog x-model="open">
        <div x-dialog:overlay @click="open = false"></div>

        <div x-dialog:panel>
            <h2 x-dialog:title>Dialog title</h2>
            <p x-dialog:description>What this dialog is about.</p>
            Dialog contents...
            <button @click="$dialog.close()">Close</button>
        </div>
    </article>
</div>
```

- Sets `role="dialog"`, `aria-modal="true"`, wires `aria-labelledby`/`aria-describedby` between the `:title`/`:description` parts and the panel.
- `$dialog.close()` magic closes programmatically; the `close` event fires for external handlers.
- Focus is managed while open (escapes to the panel).

## disclosure

Expand/collapse. Root `x-disclosure`, parts `x-disclosure:button` and `x-disclosure:panel`. Model via `x-model` on the root (it exposes `x-modelable`) or the `default-open` attribute.

```html
<div x-data x-disclosure>
    <button x-disclosure:button>Trigger</button>

    <div x-disclosure:panel>
        Content
        <button type="button" @click="$disclosure.close()">Close</button>
    </div>
</div>

<!-- controlled from outside -->
<div x-data="{ open: false }">
    <button @click="open = ! open">Toggle</button>
    <div x-disclosure x-model="open">
        <button x-disclosure:button>Trigger</button>
        <div x-disclosure:panel>Content</div>
    </div>
</div>
```

- `x-disclosure:button` auto-sets `aria-expanded`/`aria-controls` and toggles on click; non-`<button>` triggers still work, `<button>` gets `type="button"` automatically.
- `$disclosure.isOpen` (boolean) and `$disclosure.close()` magic.
- The panel's visibility is yours to apply (e.g. `:class="$disclosure.isOpen && 'block'"` or `x-show`).

## listbox

Single/multi select. Root `x-listbox` with `x-model`, parts: `:label`, `:button`, `:options`, `:option`.

```html
<div
    x-data="{ active: null, people: [ { id: 1, name: 'Wade Cooper' }, { id: 2, name: 'Arlene Mccoy', disabled: true } ] }"
    x-listbox
    x-model="active"
>
    <label x-listbox:label>Assigned to</label>

    <button x-listbox:button x-text="active ? active.name : 'Select Person'"></button>

    <ul x-listbox:options>
        <template x-for="person in people" :key="person.id">
            <li :option="person.id" x-listbox:option :value="person" :disabled="person.disabled">
                <span x-text="person.name"></span>
            </li>
        </template>
    </ul>
</div>
```

- Same `:option` (key) / `:value` (payload) pattern as combobox.
- Keyboard: arrow keys navigate, Enter selects, Esc closes.
- `$listbox` and `$listboxOption` magics expose selection state to option markup.

## menu

Dropdown menu. Root `x-menu`, parts: `x-menu:button` (trigger), `x-menu:items` (container), `x-menu:item` (each entry).

```html
<div x-data x-menu>
    <button x-menu:button>Options</button>

    <div x-menu:items>
        <p>Signed in as tom@example.com</p>
        <a x-menu:item href="#account">Account settings</a>
        <a x-menu:item disabled href="#soon">New feature (soon)</a>
        <a x-menu:item href="#sign-out">Sign out</a>
    </div>
</div>
```

- `$menuItem` magic on items; `disabled` attribute on an item disables selection and hover/focus.
- Items close the menu on activation; keyboard navigation is built in.

## popover

Floating panel anchored near a button. Root `x-popover`, parts: `:overlay`, `:button`, `:panel`, `:group` (groups multiple popovers so opening one closes the others).

```html
<div x-data x-popover>
    <button x-popover:button>Toggle</button>

    <ul x-popover:panel>
        <li>Contents...</li>
    </ul>
</div>

<!-- static panel (always in DOM, hidden via classes) -->
<ul x-popover:panel static>...</ul>
```

- `static` keeps the panel rendered at all times (visibility toggled instead of insert/remove).
- `$popover` magic exposes open state; close on outside click / Esc is built in.

## radio

Radio group. Root `x-radio` with `x-model`, parts: `:label` (group label), `:description` (group description), `:option` (each choice, with `:option` key, `:value` payload, `:disabled`).

```html
<main x-data="{
    active: null,
    access: [
        { id: 'access-1', name: 'Public access', description: 'Anyone with the link' },
        { id: 'access-2', name: 'Private to members', description: 'Only members', disabled: true },
    ]
}">
    <div x-radio x-model="active">
        <fieldset>
            <h2 x-radio:label>Privacy setting</h2>

            <template x-for="item in access" :key="item.id">
                <div :option="item.id" x-radio:option :value="item.id" :disabled="item.disabled">
                    <span x-radio:label x-text="item.name"></span>
                    <span x-radio:description x-text="item.description"></span>
                </div>
            </template>
        </fieldset>
    </div>
</main>
```

- Full ARIA radiogroup wiring (roles, labelledby/describedby, roving tabindex) is automatic.

## switch

Toggle switch. The switch control is `x-switch` itself (bound with `x-model`); optional wrapper parts: `x-switch:group`, `:label`, `:description`.

```html
<div x-data="{ checked: false }">
    <article x-switch:group>
        <label x-switch:label>Enable notifications</label>
        <span x-switch:description>Receives push alerts.</span>

        <button x-switch x-model="checked">Enable Notifications</button>
    </article>
</div>
```

- `x-switch` renders as `role="switch"` with `aria-checked`, `aria-labelledby`, `aria-describedby` (from the `:label`/`:description` parts), `tabindex="0"`, and auto `type="button"` on `<button>` elements.
- `$switch` magic reads/writes the checked state.

## tabs

Tab list with roving focus. Root `x-tabs`, parts: `x-tabs:list` (container of tabs), `x-tabs:tab` (each tab trigger), `x-tabs:panels`, `x-tabs:panel` (each panel).

```html
<div x-data x-tabs>
    <div x-tabs:list>
        <button x-tabs:tab>First</button>
        <button x-tabs:tab>Second</button>
    </div>

    <div x-tabs:panels>
        <div x-tabs:panel>First Panel</div>
        <div x-tabs:panel>Second Panel</div>
    </div>
</div>
```

- First tab/panel pair is active by default; arrows cycle focus+selection; Home/End jump.
- Panel visibility is yours to control (the plugin tracks active state; style hidden panels with `hidden`/`x-show` or CSS based on the active tab).

## Cross-component conventions

- **Binding**: stateful components take `x-model` on the root; disclosure/dialog also accept `:open`-style props.
- **Option pattern**: `:option` = stable unique key, `:value` = the data payload stored on selection (works with objects).
- **ARIA is automatic**: roles, `aria-expanded`, `aria-controls`, `aria-labelledby`, `aria-describedby`, `aria-checked`, roving tabindex — don't duplicate these attributes.
- **Styling is on you**: every part is plain HTML; add `x-show`/classes for visibility states where the component doesn't manage them.
- **Magics**: each component exposes a matching `$` magic (`$disclosure`, `$dialog`, `$listbox`, `$popover`, `$switch`, `$tab`, `$menuItem`, `$combobox`, ...) with state getters and action methods.
