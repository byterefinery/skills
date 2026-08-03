# Themes

Themes are JSON files that define colors for the TUI.

## Locations

Pi loads themes from:

- Built-in: `dark`, `light`
- Global: `~/.pi/agent/themes/*.json`
- Project: `.pi/themes/*.json` (only after the project is trusted)
- Packages: `themes/` directories or `pi.themes` entries in `package.json`
- Settings: `themes` array with files or directories
- CLI: `--theme <path>` (repeatable)

Disable discovery with `--no-themes`.

## Selecting a Theme

Select via `/settings` or in `settings.json`:

```json
{ "theme": "my-theme" }
```

On first run, pi detects terminal background and defaults to `dark` or `light`.

## Creating a Custom Theme

1. Create `~/.pi/agent/themes/my-theme.json`
2. Define the theme with all required colors
3. Select via `/settings`

Hot reload: when you edit the currently active custom theme file, pi reloads it automatically.

## Theme Format

```json
{
  "$schema": "https://raw.githubusercontent.com/earendil-works/pi/main/packages/coding-agent/src/modes/interactive/theme/theme-schema.json",
  "name": "my-theme",
  "vars": {
    "blue": "#0066cc",
    "gray": 242
  },
  "colors": {
    "accent": "blue",
    "muted": "gray",
    "text": "",
    /* ... all 51 required tokens ... */
  }
}
```

- `name` is required, must be unique, must not contain `/`
- `vars` is optional — define reusable colors, reference in `colors`
- `colors` must define all 51 required tokens. `thinkingMax` is optional, falls back to `thinkingXhigh`

## Color Tokens

### Core UI (11 colors)

`accent`, `border`, `borderAccent`, `borderMuted`, `success`, `error`, `warning`, `muted`, `dim`, `text`, `thinkingText`

### Backgrounds & Content (11 colors)

`selectedBg`, `userMessageBg`, `userMessageText`, `customMessageBg`, `customMessageText`, `customMessageLabel`, `toolPendingBg`, `toolSuccessBg`, `toolErrorBg`, `toolTitle`, `toolOutput`

### Markdown (10 colors)

`mdHeading`, `mdLink`, `mdLinkUrl`, `mdCode`, `mdCodeBlock`, `mdCodeBlockBorder`, `mdQuote`, `mdQuoteBorder`, `mdHr`, `mdListBullet`

### Tool Diffs (3 colors)

`toolDiffAdded`, `toolDiffRemoved`, `toolDiffContext`

### Syntax Highlighting (9 colors)

`syntaxComment`, `syntaxKeyword`, `syntaxFunction`, `syntaxVariable`, `syntaxString`, `syntaxNumber`, `syntaxType`, `syntaxOperator`, `syntaxPunctuation`

### Thinking Level Borders (6 required, 1 optional)

`thinkingOff`, `thinkingMinimal`, `thinkingLow`, `thinkingMedium`, `thinkingHigh`, `thinkingXhigh`, `thinkingMax` (optional, falls back to `thinkingXhigh`)

### Bash Mode (1 color)

`bashMode`

### HTML Export (optional)

```json
{
  "export": {
    "pageBg": "#18181e",
    "cardBg": "#1e1e24",
    "infoBg": "#3c3728"
  }
}
```

## Color Values

| Format | Example | Description |
|--------|---------|-------------|
| Hex | `"#ff0000"` | 6-digit hex RGB |
| 256-color | `39` | xterm 256-color palette index (0-255) |
| Variable | `"primary"` | Reference to a `vars` entry |
| Default | `""` | Terminal's default color |

## Tips

- **Dark terminals:** Use bright, saturated colors with higher contrast
- **Light terminals:** Use darker, muted colors with lower contrast
- **Color harmony:** Start with a base palette, define in `vars`, reference consistently
- **Testing:** Check with different message types, tool states, markdown content, and long wrapped text
- **VS Code:** Set `terminal.integrated.minimumContrastRatio` to `1` for accurate colors

Check truecolor support: `echo $COLORTERM` (should output `truecolor` or `24bit`).
