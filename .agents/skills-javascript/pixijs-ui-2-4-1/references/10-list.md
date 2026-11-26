# List — Auto-Layout Container

Arranges child containers one after another based on their sizes. Used standalone for simple layouts and internally by `ScrollBox`, `RadioGroup`, and `Select` (button rows).

## Options (`ListOptions<C>`)

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `type` | `ListType` | `'bidirectional'` | `vertical` \| `horizontal` \| `bidirectional` |
| `elementsMargin` | `number` | `0` | Gap between arranged elements |
| `items` / `children` | `C[]` | — | Initial children (`items` added one by one via `addChild`) |
| `padding` | `number` | `0` | All four paddings at once |
| `vertPadding` | `number` | — | Top + bottom padding |
| `horPadding` | `number` | — | Left + right padding |
| `topPadding` / `bottomPadding` / `leftPadding` / `rightPadding` | `number` | — | Individual paddings (fallback chain: side → vert/hor → padding → 0) |
| `maxWidth` | `number` | `0` | Width to fit elements into for bidirectional wrap (0 ⇒ parent width, then Infinity) |
| `maxHeight` | `number` | — | Reserved for height constraints |
| + `ContainerOptions` | | | Passed through to the container |

## API

| Member | Description |
|--------|-------------|
| `children` | `C[]` — all arranged elements |
| `type` | Get/set arrange direction (re-arranges on set) |
| `elementsMargin` | Get/set gap (re-arranges) |
| `padding` / `vertPadding` / `horPadding` / `topPadding` / `bottomPadding` / `leftPadding` / `rightPadding` | Get/set paddings (re-arrange) |
| `maxWidth` | Get/set wrap width (re-arranges) |
| `addItems(items)` | Batch add; arranging is suspended and runs once at the end |
| `removeItem(itemID)` | Remove by index (does not destroy) and re-arrange |
| `arrangeChildren()` | Public manual re-layout |
| `init(options)` | Re-initialise options |

Setting any option before `init` has run (e.g., `elementsMargin` on a bare `new List()`) throws `List has not been initiated!`.

## Arrangement Rules

- **vertical** — children stack top to bottom at `x = leftPadding`, each below the previous (`y += margin + height`).
- **horizontal** — children stack left to right at `y = topPadding` (`x += margin + width`).
- **bidirectional** (default) — like CSS `inline-block`: flow left to right, wrap to a new row when `x + child.width > maxWidth`. `maxWidth` defaults to `this.maxWidth || parent.width || Infinity`. Row height is the max child height in that row.
- **Anchor/pivot aware** — each child's offset is computed from its local bounds and pivot, so anchored `Sprite`s and pivoted containers align by their visual bounds, not their origin point.
- Adding a child (`addChild`) arranges automatically; batch `addItems` arranges once at the end (avoids quadratic re-layout for large fills).

## Example

```ts
const list = new List({
    type: 'bidirectional',
    elementsMargin: 10,
    padding: 10,
    maxWidth: 400,
});

list.addChild(new Graphics().rect(0, 0, 50, 50).fill(0x000000));
list.addItems([a, b, c]); // one arrange at the end
list.removeItem(0);
list.arrangeChildren(); // after external size changes
```
