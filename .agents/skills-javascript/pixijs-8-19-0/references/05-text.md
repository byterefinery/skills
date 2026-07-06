# Text

## Text (Canvas)

Canvas-based text rendering. Best balance of quality and performance for most use cases.

### Creation

```ts
import { Text } from 'pixi.js';

// Basic
const text = new Text({
    text: 'Hello Pixi!',
    style: {
        fontFamily: 'Arial',
        fontSize: 24,
        fill: 0xff1010,
        align: 'center',
    }
});

// Multi-line
const text = new Text({
    text: 'Line 1\nLine 2\nLine 3',
    style: {
        fontSize: 20,
        fill: 0xffffff,
        lineHeight: 30,
    }
});

// Word-wrapped
const text = new Text({
    text: 'This is a long piece of text that will automatically wrap',
    style: {
        fontSize: 20,
        wordWrap: true,
        wordWrapWidth: 200,
        lineHeight: 28,
    }
});
```

### TextStyle

```ts
interface TextStyle {
    // Font
    fontFamily?: string | string[];    // ['Arial', 'Helvetica', 'sans-serif']
    fontSize?: number | string;        // 24 or '24px'
    fontStyle?: 'normal' | 'italic' | 'oblique';
    fontVariant?: 'normal' | 'small-caps';
    fontWeight?: 'normal' | 'bold' | 'bolder' | 'lighter' | number; // 100-900

    // Color
    fill?: TextStyleFill | TextStyleFill[]; // Color, gradient, pattern
    fillWidth?: number; // Width of gradient fill

    // Stroke
    stroke?: StrokeInput;
    strokeAlignment?: number; // 0 = inside, 0.5 = center, 1 = outside
    strokeThickness?: number; // Deprecated, use stroke.width

    // Layout
    align?: 'left' | 'center' | 'right' | 'justify';
    letterSpacing?: number;
    lineHeight?: number;
    lineJoin?: 'miter' | 'round' | 'bevel';
    miterLimit?: number;
    padding?: number;
    trim?: boolean;
    wordWrap?: boolean;
    wordWrapWidth?: number; // Default: 100

    // Effects
    dropShadow?: DropShadow;
    textShadow?: TextShadow; // Deprecated, use dropShadow

    // Advanced
    whiteSpace?: 'pre' | 'pre-wrap'; // Default: 'pre-wrap'
    fontFragments?: string[]; // Force specific font loading
}
```

### Fill Options

```ts
// Single color
style.fill = 0xff0000;
style.fill = 'red';
style.fill = '#ff0000';

// Multiple colors (gradient effect per character)
style.fill = ['#ff0000', '#00ff00', '#0000ff'];

// Gradient fill
style.fill = new FillGradient({
    start: { x: 0, y: 0 },
    end: { x: 1, y: 1 },
    stops: [
        { color: 0xff0000, offset: 0 },
        { color: 0x0000ff, offset: 1 },
    ]
});

// Pattern/texture fill
style.fill = new FillPattern(texture);
```

### Stroke

```ts
style.stroke = {
    color: 0x000000,
    width: 4,
};

// Or shorthand
style.strokeThickness = 4;
style.stroke = '#000000';
```

### Drop Shadow

```ts
style.dropShadow = {
    alpha: 0.5,
    angle: Math.PI / 6,
    blur: 4,
    color: 0x000000,
    distance: 6,
};
```

### Dynamic Updates

```ts
// Update text content
text.text = 'New text';

// Update style (creates new texture)
text.style = { ...text.style, fontSize: 32 };

// Modify individual style properties
text.style.fontSize = 32;
text.dirty = true; // Mark for rebuild
```

## BitmapText

Pre-rendered bitmap font text. Faster rendering, lower memory for repeated characters.

### Creation

```ts
import { BitmapText } from 'pixi.js';

// Dynamic font (generated from system font)
const text = new BitmapText({
    text: 'Hello Pixi!',
    style: {
        fontFamily: 'Arial',
        fontSize: 24,
        fill: 0xff1010,
        align: 'center',
    }
});

// Pre-installed font
import { BitmapFont } from 'pixi.js';
BitmapFont.install({
    name: 'myFont',
    style: { fontFamily: 'Arial', fontSize: 24 },
});

const text = new BitmapText({
    text: 'Hello!',
    style: { fontFamily: 'myFont', fontSize: 24 },
});

// Loaded bitmap font (XML/FNT)
const font = await Assets.load('fonts/myFont.fnt');
const text = new BitmapText({
    text: 'Hello!',
    style: { fontFamily: 'myLoadedFont' }, // Name from .fnt file
});
```

### BitmapText Style

```ts
interface BitmapTextStyle {
    fontFamily?: string;    // Font name
    fontSize?: number;      // Font size
    fill?: ColorSource;     // Text color
    align?: TextStyleAlign; // Text alignment
    stroke?: StrokeInput;   // Stroke (limited support)
    letterSpacing?: number; // Letter spacing
    lineHeight?: number;    // Line height
    wordWrap?: boolean;     // Word wrapping
    wordWrapWidth?: number; // Wrap width
    anchor?: PointData | number; // Text anchor
    tint?: ColorSource;     // Tint color
    mipmap?: boolean;       // Use mipmaps
}
```

### Bitmap Font Types

1. **Dynamic** — generated at runtime from system fonts, automatic reuse
2. **Pre-loaded** — loaded via Assets (XML/FNT formats), supports MSDF/SDF
3. **Pre-installed** — registered via `BitmapFont.install()`

```ts
// MSDF font generation: https://msdf-bmfont.donmccurdy.com/
// Load MSDF font
const font = await Assets.load('fonts/myFont.fnt');

// The font will automatically use MSDF rendering if supported
const text = new BitmapText({
    text: 'MSDF Text',
    style: { fontFamily: 'myFont' },
});
```

## HTMLText

HTML/CSS text rendering via SVG foreignObject. Rich formatting with HTML tags.

### Creation

```ts
import { HTMLText } from 'pixi.js';

// Basic HTML
const text = new HTMLText({
    text: '<b>Bold</b> and <i>Italic</i> text',
    style: {
        fontSize: 24,
        fill: 0xff1010,
    }
});

// Rich HTML
const text = new HTMLText({
    text: `
        <h1>Title</h1>
        <p>This is <strong>bold</strong> and <em>italic</em> text.</p>
    `,
    style: {
        fontFamily: 'Arial',
        fontSize: 24,
        fill: 0xffffff,
        maxWidth: 300,
    }
});

// Custom tags
const text = new HTMLText({
    text: '<custom>Custom Tag</custom>',
    style: {
        fontFamily: 'Arial',
        fontSize: 32,
        fill: 0x4a4a4a,
        tagStyles: {
            custom: {
                fontSize: 32,
                fill: '#00ff00',
                fontStyle: 'italic',
            }
        }
    }
});
```

### HTMLTextStyle

```ts
interface HTMLTextStyle {
    // Font
    fontFamily?: string | string[];
    fontSize?: number | string;
    fontStyle?: 'normal' | 'italic' | 'oblique';
    fontWeight?: 'normal' | 'bold' | number;

    // Color
    fill?: ColorSource;

    // Layout
    align?: 'left' | 'center' | 'right' | 'justify';
    letterSpacing?: number;
    lineHeight?: number;
    padding?: number;
    wordWrap?: boolean;
    wordWrapWidth?: number;
    maxWidth?: number; // Max width for wrapping

    // Effects
    dropShadow?: DropShadow;
    textShadow?: TextShadow; // Deprecated

    // HTML-specific
    tagStyles?: Record<string, Partial<HTMLTextStyle>>; // Custom tag styles
    css?: string; // Additional CSS
}
```

## Text Comparison

| Feature | Text (Canvas) | BitmapText | HTMLText |
|---|---|---|---|
| **Performance** | Medium | High | Medium |
| **Quality** | High | Medium (pixelated when scaled) | High |
| **Rich formatting** | Limited (tags) | Limited | Full HTML/CSS |
| **Font support** | System fonts | Bitmap fonts + system | System fonts |
| **Scaling quality** | Good (re-renders) | Poor (pixelated) | Good (re-renders) |
| **Memory** | Medium | Low (shared glyphs) | Medium |
| **Dynamic updates** | Fast | Fast | Slower |
| **CJK languages** | Good | Poor (too many glyphs) | Good |
| **Emoji** | Yes | No | Yes |

## Text Performance Tips

- **Use BitmapText** for frequently updated text (scores, HUD values)
- **Use Text** for static or rarely changing text with good quality
- **Use HTMLText** for rich formatted text (dialogs, descriptions)
- **Reuse TextStyle objects** — cloning is cheaper than creating new ones
- **Set `wordWrapWidth`** to prevent unbounded text growth
- **Use `padding: 0`** on TextStyle to reduce texture size
- **Prefer BitmapText** for games with lots of text elements
- **Avoid creating Text objects in render loop** — reuse and update `.text` property
