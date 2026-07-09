# Styles and Text

## Text Styles

Styles are templates for drawing text labels. They conform to Pixi.js `TextStyle` properties.

### Using Styles

```js
// Get a style reference
var style = styles.get('StyleName');

// Get a copy (safe to modify)
var copy = styles.get('StyleName', true);
copy.wordWrap = true;
copy.wordWrapWidth = 320;

// Get a copy with modifications
var multiline = styles.get('StyleName', {
    wordWrap: true,
    wordWrapWidth = 320
});

// Apply to Text copy
this.textStyle = styles.get('StyleName');
```

### Creating Styles Programmatically

```js
styles.new('MyStyle', {
    fontSize: 24,
    fontFamily: 'Arial',
    fill: 0xffffff,
    align: 'center',
    wordWrap: true,
    wordWrapWidth: 300
});
```

## Text Base Class

Text copies derive from `PIXI.Text`. Properties:

| Property | Type | Description |
|---|---|---|
| `text` | `string` | Text content |
| `textStyle` | `PIXI.TextStyle` | Text style object |

```js
// Change text
this.text = 'New score: ' + score;

// Apply style
this.textStyle = styles.get('LabelStyle');
```

## TextBox Base Class

Input fields for text entry. Properties:

| Property | Type | Description |
|---|---|---|
| `text` | `string` | Current text value |
| `fieldType` | `string` | `'text'`, `'password'`, `'email'`, `'number'` |
| `maxLength` | `number` | Maximum characters |

```js
// Read input
var login = templates.list['LoginField'][0].text;
var password = templates.list['PasswordField'][0].text;
```

## Bitmap Fonts

Bitmap fonts are pre-rendered fonts for pixel-perfect text. Import .ttf files in ct.js IDE and enable bitmap font generation.

### Creating Bitmap Text

```js
this.label = new PIXI.BitmapText('Initial text', {
    font: {
        name: 'Void_400',
        size: 16
    },
    align: 'left'
});
this.addChild(this.label);
```

### Manipulating Bitmap Text

```js
this.label.text = 'Score: ' + this.score;
this.label.tint = 0xff0000;
this.label.rotation = 15;
this.label.scale.y = 1.25;

// Cleanup
this.label.destroy();
```

### Bitmap Font Settings

In ct.js IDE font editor:
- Font size (may differ from font's nominal size; pixel fonts often need 16px)
- Line height
- Character subsets (digits, punctuation, specific ranges)
- "Draw everything the font supports" for full character set

## Canvas vs Bitmap Text

| Feature | Canvas Text | Bitmap Text |
|---|---|---|
| Rendering | Canvas API | Pre-rendered sprites |
| Best for | Static/large text | Dynamic/moving text |
| Pixel art | May smear | Pixel-perfect |
| Performance | Good for static | Better for moving |
| Font format | System fonts | .ttf → bitmap |
| Text changes | Instant | Re-renders |

## Gotchas

- **`styles.get()` returns reference** — modifying it affects all users. Use `styles.get(name, true)` for a safe copy.
- **`styles.get(name, opts)` merges** — creates a copy extended with the options object.
- **`textStyle` assignment replaces** — `this.textStyle = styles.get('Name')` replaces the entire style.
- **Bitmap font size in IDE** — pixel fonts often need larger size (e.g., 16px) than their nominal size.
- **`'Digits and punctuation'` checkbox** — includes spaces, commas, periods. Enable unless you only need specific characters.
- **`PIXI.BitmapText` needs container** — add as child to a copy or room with `this.addChild()`.
- **Bitmap text can be transformed** — `tint`, `rotation`, `scale` work on bitmap text labels.
- **`fieldType` controls input** — `'number'` restricts to numeric input, `'password'` masks characters.
- **TextBox has two events** — text change events with `value` variable available.
- **`maxLength` enforces limit** — set on TextBox copies to restrict input length.
- **`styles.new()` creates globally** — the style is available to all copies and rooms.
