# JSX Custom Components Reference

AntV Infographic provides a JSX-based rendering system for creating custom items, structures, and decorations. The JSX runtime maps to SVG elements and composites.

## Setup

### TypeScript Configuration

```jsonc
{
  "compilerOptions": {
    "jsx": "react-jsx",
    "jsxImportSource": "@antv/infographic"
  }
}
```

### Pragma (JSDoc)

```js
/** @jsxImportSource @antv/infographic */
```

### Imports

```ts
import {
  // Primitive nodes
  Rect, Text, Path, Circle, Ellipse, Polygon, Group, Defs, Fragment,

  // Built-in components
  BtnAdd, BtnRemove, BtnsGroup,
  Gap, Illus,
  ItemDesc, ItemIcon, ItemIconCircle, ItemLabel, ItemValue,
  ItemsGroup, ShapesGroup, Title,

  // Layout
  createLayout, cloneElement, getElementBounds, getElementsBounds, getCombinedBounds,

  // Rendering
  renderSVG,

  // Registration
  registerItem, registerStructure,
} from '@antv/infographic';
```

## Primitive Nodes

All primitives accept `x`, `y`, `width`, `height`, `transform`, plus standard SVG attributes (`fill`, `stroke`, `opacity`, `id`, `className`, `style`, `data-*`).

### Defs

Defines reusable references (gradients, filters, patterns). Referenced by `id` elsewhere.

```jsx
<Defs>
  <linearGradient id="gradient1" x1="0%" y1="0%" x2="100%" y2="0%">
    <stop offset="0%" stopColor="#ff0000" />
    <stop offset="100%" stopColor="#0000ff" />
  </linearGradient>
  <filter id="shadow">
    <feDropShadow dx="2" dy="2" stdDeviation="3" floodColor="#000000" />
  </filter>
</Defs>

<Rect fill="url(#gradient1)" width={100} height={50} />
<Rect filter="url(#shadow)" width={100} height={50} />
```

### Group

Behaves like SVG `<g>`. `x`/`y` auto-generate `transform="translate(x, y)"`. `width`/`height` are for bounds calculation only.

```jsx
<Group x={10} y={10} width={200} height={100} opacity={0.8}>
  {children}
</Group>
```

### Rect

Maps to SVG `<rect>`. Supports `rx`/`ry` for corner radii.

```jsx
<Rect x={0} y={0} width={100} height={50} fill="blue" rx={5} ry={5} />
```

### Ellipse

Draws an oval. Equal width and height creates a circle. `x`/`y` denote the top-left corner of the bounding box.

```jsx
<Ellipse x={0} y={0} width={100} height={60} fill="red" />
```

### Path

Corresponds to `<path>`. `x`/`y` auto-translate via `transform`.

```jsx
<Path d="M 0 0 L 100 100 L 100 0 Z" fill="green" width={100} height={100} />
```

### Polygon

Wraps `<polygon>`. `points` must be `{x, y}[]` (not a string).

```jsx
<Polygon
  points={[
    {x: 0, y: 0},
    {x: 100, y: 0},
    {x: 50, y: 100},
  ]}
  fill="purple"
/>
```

### Text

Renders text with alignment, background, and wrapping support.

```jsx
<Text
  x={0} y={0} width={200} height={100}
  fontSize={14} fontWeight="bold" fontFamily="Arial"
  alignHorizontal="center" alignVertical="middle"
  lineHeight={1.5} wordWrap={true}
  fill="#000000" backgroundColor="#ffff00"
>
  Multi-line text supported
</Text>
```

| Prop | Type | Default | Description |
|---|---|---|---|
| `alignHorizontal` | `'left'` \| `'center'` \| `'right'` | `left` | Horizontal alignment |
| `alignVertical` | `'top'` \| `'middle'` \| `'bottom'` | `top` | Vertical alignment |
| `fontSize` | number | 14 | Font size |
| `lineHeight` | number | — | Multiplier for baseline (>1) |
| `wordWrap` | boolean | — | Enable auto-wrapping |
| `backgroundColor` | string | `none` | Non-`none` emits background rect |
| `backgroundOpacity` | number | 1 | Background opacity |
| `backgroundRadius` | number | 0 | Background corner radius |

## Built-in Components

Components write identifiers like `data-element-type` and `data-indexes` for data binding, styling, and interaction.

### Buttons (Editor Mode)

Hidden in non-edit mode.

```tsx
<BtnAdd indexes={[0]} x={120} y={40} width={24} height={24} rx={4} />
<BtnRemove indexes={[1]} x={120} y={80} />
<BtnsGroup>
  <BtnAdd indexes={[0]} x={0} y={0} />
  <BtnRemove indexes={[0]} x={36} y={0} />
</BtnsGroup>
```

### Title

Renders main title and description text with vertical flex layout and auto-height.

```tsx
<Title
  x={40} y={24} width={640}
  alignHorizontal="left"
  title="Market Overview"
  desc="Auto-wrap and calculate height according to descLineNumber"
  descLineNumber={2}
  themeColors={themeColors}
/>
```

### Gap

Placeholder component — creates spacing without rendering graphics. Must be written directly as `<Gap />`.

```tsx
<FlexLayout flexDirection="row" gap={12}>
  <ItemLabel indexes={[0]}>Title</ItemLabel>
  <Gap width={8} />
  <ItemValue indexes={[0]} value={32} />
</FlexLayout>
```

### Illustration

Replaces SVG area with illustration resources from data.

```tsx
<Illus x={40} y={20} width={200} height={120} rx={12} />
<Illus indexes={[1]} x={0} y={0} width={96} height={96} />
```

### Item Label

Data item label text. Default width 100, font size 18, bold, line height 1.4. Must pass `indexes`.

```tsx
<ItemLabel indexes={[index]} width={160} fill="#222">
  {datum.label}
</ItemLabel>
```

### Item Description

Data item description text. Default width 100, font size 14, `#666`, `wordWrap` enabled. Controls max lines via `lineNumber` (default 2).

```tsx
<ItemDesc indexes={[index]} width={220} lineNumber={3}>
  {datum.desc}
</ItemDesc>
```

### Item Icon / ItemIconCircle

Square icon placeholder (default 32×32). Circle variant adds circular background.

```tsx
<ItemIconCircle
  indexes={[index]} x={0} y={0} size={48}
  fill={themeColors.colorPrimary}
  colorBg="#fff8e6"
/>
```

### Item Value

Numeric text. Requires `value: number`. Use `formatter` for display format.

```tsx
<ItemValue
  indexes={[index]} value={datum.value}
  formatter={(v) => `${v}%`}
  fontSize={20} fontWeight="bold"
/>
```

### ItemsGroup / ShapesGroup

Container groups with `data-element-type` markers for layout calculations and theme styling.

## Layout System

### createLayout

Create reusable layout components that position children before rendering.

```tsx
import { createLayout, cloneElement, getElementBounds, Group } from '@antv/infographic/jsx';

// Simple vertical stacking layout
export const Stack = createLayout<{gap?: number}>(
  (children, {gap = 8, ...props}) => {
    let offsetY = 0;
    const placed = children.map((child) => {
      const bounds = getElementBounds(child);
      const next = cloneElement(child, {x: 0, y: offsetY});
      offsetY += bounds.height + gap;
      return next;
    });
    return <Group {...props}>{placed}</Group>;
  }
);

// Usage
const Card = () => (
  <Stack x={20} y={20} gap={12}>
    <Rect width={200} height={80} fill="#EEF3FF" rx={12} />
    <Text width={200} height={24}>Title</Text>
    <Text width={200} height={40} alignVertical="middle">Description</Text>
  </Stack>
);
```

### Built-in Layouts

- **AlignLayout**: Aligns elements left/center/right, top/middle/bottom within a container.
  ```jsx
  <AlignLayout horizontal="center" vertical="middle">
    <Rect width={120} height={60} />
    <Text width={120} height={24} alignHorizontal="center">Centered</Text>
  </AlignLayout>
  ```

- **FlexLayout**: Flex-like layout with `flexDirection`, `justifyContent`, `alignItems`, `flexWrap`, `gap`.
  ```jsx
  <FlexLayout width={320} height={200} gap={12} justifyContent="space-between">
    <Rect width={80} height={80} />
    <Rect width={80} height={80} />
    <Rect width={80} height={80} />
  </FlexLayout>
  ```

### Utility Functions

| Function | Description |
|---|---|
| `cloneElement(element, props)` | Shallow clone a JSX node with merged props |
| `getElementBounds(node)` | Compute bounds of a single JSX node |
| `getElementsBounds(elements)` | Combined bounds of multiple nodes |
| `getCombinedBounds(bounds[])` | Pure geometry merge of bounds objects |
| `renderSVG(node, options?)` | Render JSX to SVG string |

### Layout Execution Flow

1. Renderer detects the layout symbol on the component.
2. Collects children.
3. Executes the layout function with `children` and props.
4. Receives the position-adjusted children.
5. Continues rendering the new array.

## Creating Custom Items

An item is a JSX component that renders a single data point.

```tsx
import { Rect, Text, Group, registerItem } from '@antv/infographic';

function CustomCard(props) {
  const { datum, x, y, indexes, themeColors, positionH } = props;
  const { label, desc, value, icon } = datum;
  const isFlipped = positionH === 'flipped';

  return (
    <Group x={x} y={y}>
      <Rect
        x={0} y={0} width={200} height={80} rx={8}
        fill={themeColors.colorBgElevated}
        stroke={themeColors.colorPrimary} strokeWidth={1}
      />
      {icon && (
        <ItemIcon indexes={indexes} x={12} y={12} width={24} height={24} />
      )}
      <ItemLabel indexes={indexes} x={44} y={16} width={148} fontWeight="bold">
        {label}
      </ItemLabel>
      {desc && (
        <ItemDesc indexes={indexes} x={44} y={40} width={148} lineNumber={2}>
          {desc}
        </ItemDesc>
      )}
    </Group>
  );
}

registerItem('custom-card', {
  component: CustomCard,
  composites: ['Text', 'Icon', 'Shape'],
  options: { /* default item options */ },
});
```

### Item Props

| Prop | Type | Description |
|---|---|---|
| `x` | number | X position |
| `y` | number | Y position |
| `id` | string | Element ID |
| `indexes` | number[] | Index path in data array |
| `data` | ParsedData | Full parsed data object |
| `datum` | ItemDatum | Current data item |
| `themeColors` | ThemeColors | Computed theme colors |
| `positionH` | `normal` \| `center` \| `flipped` | Horizontal position mode |
| `positionV` | `normal` \| `middle` \| `flipped` | Vertical position mode |
| `valueFormatter` | function | Value formatter function |

### ThemeColors

| Property | Description |
|---|---|
| `colorPrimary` | Primary brand color |
| `colorPrimaryBg` | Light primary background |
| `colorPrimaryText` | Text on primary background |
| `colorText` | Main text color |
| `colorTextSecondary` | Secondary text color |
| `colorWhite` | Pure white |
| `colorBg` | Canvas background |
| `colorBgElevated` | Card/elevated background |
| `isDarkMode` | Dark mode flag |

## Creating Custom Structures

A structure is a JSX component that lays out multiple items.

```tsx
import { Group, registerStructure } from '@antv/infographic';

function CustomLayout(props) {
  const { Item, Items, data, options, Title } = props;
  const items = data.items || [];
  const itemWidth = 200;
  const itemHeight = 80;
  const gap = 20;

  return (
    <Group>
      {Title && <Title title={data.title} desc={data.desc} />}
      {items.map((datum, index) => {
        const x = index % 4 * (itemWidth + gap);
        const y = Math.floor(index / 4) * (itemHeight + gap);
        return (
          <Item
            key={datum.id ?? index}
            x={x} y={y}
            indexes={[index]}
            data={data}
            datum={datum}
          />
        );
      })}
    </Group>
  );
}

registerStructure('custom-grid', {
  component: CustomLayout,
  composites: ['Text', 'Shape', 'Icon'],
});
```

### Structure Props

| Prop | Type | Description |
|---|---|---|
| `Title` | ComponentType | Title component (may be null) |
| `Item` | ComponentType | Item component for rendering |
| `Items` | ComponentType[] | Array of item components (multi-level) |
| `data` | ParsedData | Parsed data object |
| `options` | ParsedInfographicOptions | Full parsed options |

## Registering Custom Components

```ts
// Register a custom item
registerItem('my-item', {
  component: MyItemComponent,
  composites: ['Text', 'Shape'],
  options: { width: 200 },
});

// Register a custom structure
registerStructure('my-structure', {
  component: MyStructureComponent,
  composites: ['Text', 'Shape', 'Icon'],
});

// Register a custom template
import { registerTemplate } from '@antv/infographic';

registerTemplate('my-template', {
  design: {
    structure: { type: 'my-structure' },
    items: [{ type: 'my-item' }],
  },
  themeConfig: {
    colorPrimary: '#1677ff',
  },
});
```

## Using Custom Components in Syntax

After registration, custom items and structures are available in the infographic syntax:

```
infographic my-template
data
  items
    - label Item 1
      desc Description 1
    - label Item 2
      desc Description 2
```

Or with inline design:

```
template list-row
design
  item
    type my-item
    width 240
data
  lists
    - label Custom Item
      desc Using my custom item component
```

## Gotchas

- **Composites must be declared** — every composite used in your JSX component (Text, Shape, Icon, etc.) must be listed in the `composites` array. The renderer uses this to know which sub-renderers to initialize.
- **Items receive positions from structures** — don't hardcode absolute positions in items. Use the `x`/`y` props passed by the structure, and layout relative to them.
- **ThemeColors may not be passed** — in some structure contexts, `themeColors` is optional on item props. Check before accessing.
- **JSX runtime differs from React** — `@antv/infographic` has its own JSX runtime. Don't import `react` or `react/jsx-runtime`. Use `'@antv/infographic/jsx-runtime'`.
- **Text measurement is async with custom fonts** — if using non-default fonts, text bounds may not be accurate on first render. Use the `loaded` event.
- **`Gap` must be used directly** — write `<Gap />` directly, not assigned to a variable first.
- **Layout runs during processing** — layout functions execute before rendering, so they can modify positions and sizes that affect the final SVG.
- **Nested layouts are supported** — you can nest `createLayout` components inside each other.
