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

In v8, `dropShadow` is an object. Update properties directly on the object:

```ts
style.dropShadow = {
    alpha: 0.5,
    angle: Math.PI / 6,
    blur: 4,
    color: 0x000000,
    distance: 6,
};

// Update individual properties
style.dropShadow.color = '#ff0000';
style.dropShadow.blur = 8;
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
// MSDF/SDF font generation: https://msdf-bmfont.donmccurdy.com/
// AssetPack can also generate MSDF/SDF fonts from .ttf/.otf

// Load MSDF/SDF font
const font = await Assets.load('fonts/myFont.fnt');

// Automatically uses MSDF/SDF rendering if the font supports it
const text = new BitmapText({
    text: 'MSDF Text',
    style: { fontFamily: 'myFont' },
});
```

### MSDF/SDF Benefits

- Crisp, resolution-independent text at any size and scale
- No blurring when scaled up
- Supports rotation without quality loss
- Generated via [AssetPack](https://pixijs.io/assetpack/) or [msdf-bmfont](https://msdf-bmfont.donmccurdy.com/)

### Limitations

- `BitmapText.resolution` is not mutable after creation
- Large character sets (CJK, emoji) are impractical due to texture size limits
- Use `Text` or `HTMLText` for dynamic internationalization or emoji support

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

// Custom tags with tagStyles
const text = new HTMLText({
    text: '<red>Red</red>, <blue>Blue</blue>',
    style: {
        fontFamily: 'DM Sans',
        fontSize: 32,
        fill: '#ffffff',
        tagStyles: {
            red: { fill: 'red' },
            blue: { fill: 'blue' },
        },
    }
});

// CSS overrides
const fancy = new HTMLText({
    text: '<b>Styled</b> text',
    style: {
        fontFamily: 'Arial',
        fontSize: 24,
        fill: '#ffffff',
    }
});
fancy.style.addOverride('text-shadow: 2px 2px 4px rgba(0,0,0,0.5)');
```

### Async Rendering

HTMLText renders asynchronously (after the next frame). Text content is not immediately visible after instantiation.

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
    cssOverrides?: string[]; // CSS override strings
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

## SplitText & SplitBitmapText

Break text into individual lines, words, and characters — each as its own display object. Enables per-segment animations and advanced text layout effects.

:::warning Experimental — may evolve in future versions

```ts
import { SplitText, SplitBitmapText } from 'pixi.js';

// SplitText (based on Text)
const text = new SplitText({
    text: 'Hello World',
    style: { fontSize: 32, fill: 0xffffff },
    lineAnchor: 0.5,            // Center lines
    wordAnchor: { x: 0, y: 0.5 }, // Left-center words
    charAnchor: { x: 0.5, y: 1 }, // Bottom-center characters
    autoSplit: true,            // Auto-update on text/style change
});

// SplitBitmapText (based on BitmapText, high-performance)
const bitmap = new SplitBitmapText({
    text: 'High Performance',
    style: { fontFamily: 'GameFont', fontSize: 32 },
    autoSplit: true,
});

// Access segments
console.log(text.lines);  // Array of line containers
console.log(text.words);  // Array of word containers
console.log(text.chars);  // Array of character display objects

// Convert existing text to split version
const split = SplitText.from(existingText);
const splitBitmap = SplitBitmapText.from(existingBitmapText);

// Animation example (with GSAP)
text.chars.forEach((char, i) => {
    gsap.from(char, { alpha: 0, delay: i * 0.05 });
});

text.words.forEach((word, i) => {
    gsap.to(word.scale, { x: 1.2, y: 1.2, yoyo: true, repeat: -1, delay: i * 0.2 });
});
```

### Global Defaults

```ts
SplitText.defaultOptions = {
    lineAnchor: 0.5,
    wordAnchor: { x: 0, y: 0.5 },
    charAnchor: { x: 0.5, y: 1 },
};
```

### Limitations

- Creates additional display objects — less efficient than plain Text
- Character spacing differs slightly from standard Text (no browser kerning)
- Use only when per-segment animations or interactive text effects are needed

## Text Performance Tips

- **Use BitmapText** for frequently updated text (scores, HUD values)
- **Use Text** for static or rarely changing text with good quality
- **Use HTMLText** for rich formatted text (dialogs, descriptions)
- **Use SplitText/SplitBitmapText** for per-character/word animations
- **Reuse TextStyle objects** — cloning is cheaper than creating new ones
- **Set `wordWrapWidth`** to prevent unbounded text growth
- **Use `padding: 0`** on TextStyle to reduce texture size
- **Prefer BitmapText** for games with lots of text elements
- **Avoid creating Text objects in render loop** — reuse and update `.text` property
- **BitmapText.resolution is not mutable** — must be set by the BitmapFont
- **BitmapText large character sets** — CJK or emoji-rich sets impractical (too much memory). Use Text or HTMLText instead
