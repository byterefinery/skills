# Themes, Palettes & Stylization Reference

## Theme System

Themes control colors, fonts, and visual style. Use `theme` for a named preset and `themeConfig` for deep customization.

### Built-in Themes

| Name | Description |
|---|---|
| `default` | Standard light theme with antv palette, clean and elegant |
| `light` | White background |
| `dark` | Dark background (#1F1F1F), white text |
| `hand-drawn` | Hand-drawn style with `851tegakizatsu` font + rough stylization |

### Theme Config Object

```ts
interface ThemeConfig {
  colorBg?: string;           // Canvas background
  colorPrimary?: string;      // Primary brand color
  palette?: Palette;          // Color palette
  base?: {                    // Global defaults
    global?: DynamicAttributes<BaseAttributes>;
    shape?: ShapeAttributes;
    text?: TextAttributes;
  };
  title?: TextAttributes;     // Title text style
  desc?: TextAttributes;      // Description text style
  shape?: ShapeAttributes;    // Global shape style
  item?: {                    // Per-element item overrides
    icon?: DynamicAttributes<IconAttributes>;
    label?: DynamicAttributes<TextAttributes>;
    desc?: DynamicAttributes<TextAttributes>;
    value?: DynamicAttributes<TextAttributes>;
    shape?: DynamicAttributes<ShapeAttributes>;
  };
  stylize?: StylizeConfig | null;  // Visual stylization
  elements?: Record<string, ShapeAttributes | TextAttributes>; // Per-element
}
```

### Specific Part Styles

| Config Path | Description |
|---|---|
| `base.global` | Global graphic styles |
| `base.text` | Global text styles |
| `base.shape` | Global shape styles |
| `title` | Infographic title styles |
| `desc` | Infographic description styles |
| `shape` | Shape graphic styles |
| `item.icon` | Data item icon styles |
| `item.label` | Data item label styles |
| `item.desc` | Data item description styles |
| `item.value` | Data item value styles |

> A `shape` refers to graphics that set `data-element-type="shape"` when defining custom structures or items.

### Dynamic Attributes

Theme attributes can be static values or functions that receive the current value and SVG node:

```ts
// Static
fill: '#1677ff'

// Dynamic — function form
fill: (value, node) => {
  const depth = node.getAttribute('data-depth');
  return depth === '0' ? '#1677ff' : '#69b1ff';
}
```

## Color Palettes

A palette provides colors for multi-item infographics (charts, progress indicators, categorized data).

### Palette Types

| Type | Example |
|---|---|
| Named string | `'antv'`, `'spectral'` |
| Color array | `['#1677ff', '#00C9C9', '#F0884D']` |
| Single color | `'#1677ff'` — auto-generates a series |
| Function | `(ratio, index, count) => color` |

> When the number of data items exceeds the palette length, colors are used **cyclically** (4th item uses 1st color, etc.).

### Built-in Palettes

| Name | Description |
|---|---|
| `antv` | AntV brand colors (11 colors) |
| `spectral` | Sequential diverging palette for continuous data |

### Palette API

```ts
import {
  getPalette,
  getPalettes,
  getPaletteColor,
  registerPalette,
} from '@antv/infographic';

// Get all palette names
const names = getPalettes();

// Get palette definition
const antv = getPalette('antv');

// Get a specific color from palette
const color = getPaletteColor('antv', [0], 3);

// Register custom palette (discrete array)
registerPalette('my-palette', ['#ff0000', '#00ff00', '#0000ff']);

// Register custom palette (continuous function)
registerPalette('rainbow', (ratio, index, count) => {
  const hue = (index / count) * 360;
  return `hsl(${hue}, 70%, 50%)`;
});
```

## Stylization

Stylization applies visual effects to shapes. Set via `themeConfig.stylize`.

### Rough (Hand-Drawn)

```ts
stylize: {
  type: 'rough',
  roughness: 2,    // 0-10, default ~1
  bowing: 1,       // Line waviness
  fillWeight: 1,   // Fill hatch weight
  hachureGap: 10,  // Hatch line gap
}
```

Uses `roughjs` internally. Works best with the `hand-drawn` theme.

### Pattern Fill

```ts
stylize: {
  type: 'pattern',
  pattern: 'dot',           // 'dot' | 'line' | 'square' | 'diamond' | 'hex' | 'mosaic'
  backgroundColor: '#f0f0f0',
  foregroundColor: '#1677ff',
  scale: 1,
}
```

#### Built-in Patterns

| Name | Description |
|---|---|
| `line` | Parallel lines, texture effect |
| `dot` | Evenly distributed dots, granular feel |
| `hex` | Hexagonal grids, structured effect |
| `diamond` | Diamond grids, geometric beauty |
| `mosaic` | Irregular shapes, diverse effect |
| `square` | Evenly distributed squares, modern feel |

### Linear Gradient

```ts
stylize: {
  type: 'linear-gradient',
  angle: 135,  // 0=right, 90=down, 180=left, 270=up
  colors: ['#667eea', '#764ba2'],
  // Or with explicit offsets:
  // colors: [
  //   { color: '#667eea', offset: '0%' },
  //   { color: '#764ba2', offset: '100%' },
  // ],
}
```

### Radial Gradient

```ts
stylize: {
  type: 'radial-gradient',
  colors: ['#f093fb', '#f5576c'],
}
```

## Fonts

### Built-in Fonts

| Font Family | Name | Weights |
|---|---|---|
| `Alibaba PuHuiTi` | 阿里巴巴普惠体 | regular, bold |
| `Source Han Sans` | 黑体 | regular |
| `Source Han Serif` | 宋体 | regular |
| `LXGW WenKai` | 楷体 | regular |
| `851tegakizatsu` | 手写体 | regular |

All fonts load from `https://assets.antv.antgroup.com`.

### Font API

```ts
import {
  getFont,
  getFonts,
  registerFont,
  setDefaultFont,
} from '@antv/infographic';

// Get all registered fonts
const fonts = getFonts();

// Get a specific font
const font = getFont('Alibaba PuHuiTi');

// Set default font
setDefaultFont('Source Han Sans');

// Register custom font
registerFont({
  fontFamily: 'MyFont',
  name: 'My Custom Font',
  baseUrl: 'https://cdn.example.com',
  fontWeight: {
    regular: 'myfont-regular/result.css',
    bold: 'myfont-bold/result.css',
  },
});
```

### Using Fonts in Theme

```ts
themeConfig: {
  base: {
    text: {
      'font-family': 'Alibaba PuHuiTi',
    },
  },
}
```

## Theme API

```ts
import {
  getTheme,
  getThemes,
  registerTheme,
  getThemeColors,
} from '@antv/infographic';

// List all themes
const themes = getThemes();

// Get theme config
const light = getTheme('light');

// Register custom theme
registerTheme('corporate', {
  colorPrimary: '#003366',
  colorBg: '#f5f7fa',
  palette: ['#003366', '#0066CC', '#0099FF', '#66B3FF'],
  base: {
    text: {
      'font-family': 'Source Han Sans',
      fill: '#333',
    },
  },
  item: {
    label: {
      'font-weight': 'bold',
    },
  },
});

// Generate derived colors
const colors = getThemeColors({ colorPrimary: '#1677ff', colorBg: '#fff' });
```

## Complete Theme Example

```ts
// JS object form
{
  theme: 'light',
  themeConfig: {
    colorPrimary: '#1677ff',
    palette: ['#1677ff', '#00C9C9', '#F0884D', '#D580FF', '#7863FF'],

    base: {
      text: {
        'font-family': 'Alibaba PuHuiTi',
        fill: '#333',
        'font-size': 14,
      },
      shape: {
        fill: '#ffffff',
        stroke: '#1677ff',
        'stroke-width': 1,
      },
    },

    title: {
      'font-size': 28,
      'font-weight': 'bold',
      fill: '#1677ff',
    },

    desc: {
      'font-size': 14,
      fill: '#666666',
    },

    item: {
      label: {
        'font-size': 16,
        'font-weight': 'bold',
      },
      desc: {
        'font-size': 12,
        fill: '#888888',
      },
      shape: {
        'fill-opacity': 0.9,
      },
    },

    stylize: {
      type: 'linear-gradient',
      angle: 135,
      colors: ['#667eea', '#764ba2'],
    },
  },
}
```

### Syntax Form

```
theme
  colorPrimary: '#1677ff'
  palette: ['#1677ff', '#00C9C9', '#F0884D']

  base
    text
      font-family: 'Alibaba PuHuiTi'
      fill: '#333'

  title
    font-size: 28
    fill: '#1677ff'

  stylize
    type: linear-gradient
    angle: 135
    colors: ['#667eea', '#764ba2']
```

## Theme Color Generation

When you set `colorPrimary`, the system auto-generates a full color set:

| Generated Property | Source |
|---|---|
| `colorPrimary` | Your input |
| `colorPrimaryBg` | Primary at 8% opacity on bg |
| `colorPrimaryText` | Contrasting text for primary bg |
| `colorText` | Dark (#333) or light (#fff) based on bg |
| `colorTextSecondary` | Muted version of text color |
| `colorWhite` | `#ffffff` |
| `colorBg` | From theme or `themeConfig.colorBg` |
| `colorBgElevated` | Slightly elevated from bg |
| `isDarkMode` | Derived from bg luminance |

## Gotchas

- **`stylize` applies to shapes, not text** — rough, pattern, and gradient stylization affects shape fills/strokes. Text elements are unaffected.
- **`hand-drawn` theme bundles `rough` stylization** — setting `theme: 'hand-drawn'` automatically enables rough mode. Override with `themeConfig.stylize: null` to disable.
- **Single-color palette generates a scale** — `palette: '#1677ff'` creates a light-to-dark series from that color. For exact colors, always use an array.
- **Font loading is network-dependent** — built-in fonts load from `assets.antv.antgroup.com`. In offline environments, use system fonts or self-host.
- **`elements` overrides are by ID** — the `elements` field in themeConfig targets specific SVG elements by their `id` attribute. IDs are auto-generated or set via data `attributes`.
- **Gradient `angle` uses CSS convention** — 0° = left-to-right, 90° = top-to-bottom, 180° = right-to-left, 270° = bottom-to-top.
