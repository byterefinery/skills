# Themes Reference

## Built-in Themes

All themes are CSS-only. Swap by changing the `<link>` with `id="theme"`:

| Theme | File | Description |
|---|---|---|
| Black | `dist/theme/black.css` | Black background, light text (default) |
| White | `dist/theme/white.css` | White background, dark text |
| League | `dist/theme/league.css` | Dark background with accent colors |
| Beige | `dist/theme/beige.css` | Beige background with dark text |
| Sky | `dist/theme/sky.css` | Light blue gradient background |
| Simple | `dist/theme/simple.css` | Minimal, clean white theme |
| Serif | `dist/theme/serif.css` | Serif fonts, classic look |
| Blood | `dist/theme/blood.css` | Dark background with red accents |
| Night | `dist/theme/night.css` | Pure black background |
| Moon | `dist/theme/moon.css` | Dark blue-gray background |
| Solarized | `dist/theme/solarized.css` | Solarized color palette |
| Dracula | `dist/theme/dracula.css` | Dracula theme colors |
| Black Contrast | `dist/theme/black-contrast.css` | Black with higher contrast text |
| White Contrast | `dist/theme/white-contrast.css` | White with higher contrast text |

### Usage

```html
<link rel="stylesheet" href="dist/theme/black.css" id="theme" />
```

### Runtime Theme Switching

```js
document.getElementById('theme').setAttribute('href', 'dist/theme/white.css');
```

No reinitialization needed — themes are pure CSS.

## Custom Themes

### Method 1: Extend a Built-in Theme

Copy a theme SCSS file from `css/theme/` and modify variables:

```scss
@import '../template/mixins';
@import '../template/settings';

// Override settings
$backgroundColor: #1a1a2e;
$mainColor: #eee;
$headingColor: #e94560;
$headingTextShadow: none;
$linkColor: #e94560;
$linkColorHover: #ff6b81;

@import '../template/theme';
```

Compile with Sass:

```bash
sass my-theme.scss my-theme.css
```

### Method 2: CSS Override

Create a CSS file that overrides reveal.js defaults:

```css
.reveal {
  font-family: 'Georgia', serif;
  font-size: 40px;
  color: #ddd;
}

.reveal h1, .reveal h2, .reveal h3 {
  color: #e94560;
  text-shadow: none;
}

.reveal a {
  color: #e94560;
}

.reveal section {
  background-color: #1a1a2e;
}
```

Load after the theme:

```html
<link rel="stylesheet" href="dist/theme/black.css" />
<link rel="stylesheet" href="custom.css" />
```

### Method 3: SCSS Template Variables

The theme template (`css/theme/template/settings.scss`) exposes these variables:

| Variable | Description |
|---|---|
| `$mainFont` | Body font family |
| `$mainFontSize` | Body font size |
| `$mainColor` | Body text color |
| `$backgroundColor` | Slide background color |
| `$headingFont` | Heading font family |
| `$headingColor` | Heading text color |
| `$headingTextShadow` | Heading text shadow |
| `$headingLineHeight` | Heading line height |
| `$headingLetterSpacing` | Heading letter spacing |
| `$headingTextTransform` | Heading text transform |
| `$linkColor` | Link color |
| `$linkColorHover` | Link hover color |
| `$rulerColor` | Horizontal rule color |
| `$selectionBackgroundColor` | Text selection background |
| `$selectionTextColor` | Text selection text color |

### Font Themes

Themes can specify font imports:

```scss
@import url('https://fonts.googleapis.com/css?family=Montserrat');

$headingFont: 'Montserrat', sans-serif;
$mainFont: 'Helvetica', sans-serif;
```

## Per-Slide Styling

Use `data-state` for broader style changes:

```html
<section data-state="dark-mode">
  <h2>Dark content</h2>
</section>
```

```css
.reveal.dark-mode {
  background-color: #111;
}

.reveal.dark-mode .slides section {
  color: #fff;
}
```

## Dark/Light Background Detection

reveal.js adds classes based on background brightness:
- `.has-dark-background` — Dark background slide
- `.has-light-background` — Light background slide

Use these for conditional styling:

```css
.slides section.has-dark-background h2 {
  color: #fff;
}

.slides section.has-light-background h2 {
  color: #222;
}
```
