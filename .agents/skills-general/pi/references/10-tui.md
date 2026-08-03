# TUI Components

Extensions and custom tools can render custom TUI components for interactive user interfaces.

**Source:** [`@earendil-works/pi-tui`](https://github.com/earendil-works/pi-mono/tree/main/packages/tui)

## Component Interface

```typescript
interface Component {
  render(width: number): string[];
  handleInput?(data: string): void;
  wantsKeyRelease?: boolean;
  invalidate(): void;
}
```

- `render(width)` — return array of strings (one per line). Each line **must not exceed `width`**
- `handleInput(data)` — receive keyboard input when component has focus
- `wantsKeyRelease` — if true, component receives key release events (Kitty protocol). Default: false
- `invalidate()` — clear cached render state. Called on theme changes

Styles do not carry across lines. Reapply styles per line or use `wrapTextWithAnsi()`.

## Focusable Interface (IME Support)

Components displaying a text cursor should implement `Focusable`:

```typescript
import { CURSOR_MARKER, type Component, type Focusable } from "@earendil-works/pi-tui";

class MyInput implements Component, Focusable {
  focused: boolean = false;
  
  render(width: number): string[] {
    const marker = this.focused ? CURSOR_MARKER : "";
    return [`> ${beforeCursor}${marker}\x1b[7m${atCursor}\x1b[27m${afterCursor}`];
  }
}
```

Container components with embedded `Input` or `Editor` children must propagate focus state for IME cursor positioning.

## Using Components

In extensions via `ctx.ui.custom()`:

```typescript
pi.on("session_start", async (_event, ctx) => {
  const result = await ctx.ui.custom<string | null>((tui, theme, keybindings, done) =>
    new MyComponent({
      theme,
      keybindings,
      onChange: () => tui.requestRender(),
      onSelect: (value) => done(value),
      onCancel: () => done(null),
    })
  );
});
```

## Overlays

Render components on top of existing content without clearing the screen:

```typescript
const result = await ctx.ui.custom<string | null>(
  (tui, theme, keybindings, done) => new MyDialog({ onClose: done }),
  { overlay: true, overlayOptions: {
    width: "50%", minWidth: 40, maxHeight: "80%",
    anchor: "right-center", offsetX: -2, offsetY: 0,
    margin: 2,
    visible: (termWidth, termHeight) => termWidth >= 80,
  }, onHandle: (handle) => {
    handle.focus(); handle.unfocus(); handle.setHidden(true);
  }}
);
```

Overlay components are disposed when closed. Create fresh instances for each show.

## Built-in Components

Import from `@earendil-works/pi-tui`:

### Text

Multi-line text with word wrapping:

```typescript
const text = new Text("Hello World", 1, 1, (s) => bgGray(s));
text.setText("Updated");
```

### Box

Container with padding and background:

```typescript
const box = new Box(1, 1, (s) => bgGray(s));
box.addChild(new Text("Content", 0, 0));
```

### Container

Groups child components vertically:

```typescript
const container = new Container();
container.addChild(component1);
container.addChild(component2);
```

### Spacer

Empty vertical space: `new Spacer(2)`.

### Markdown

Renders markdown with syntax highlighting:

```typescript
const md = new Markdown("# Title\n\nSome **bold** text", 1, 1, theme);
md.setText("Updated markdown");
```

### Image

Renders images in supported terminals (Kitty, iTerm2, Ghostty, WezTerm, Warp):

```typescript
const image = new Image(base64Data, "image/png", theme, { maxWidthCells: 80, maxHeightCells: 24 });
```

## Keyboard Input

```typescript
import { matchesKey, Key } from "@earendil-works/pi-tui";

handleInput(data: string) {
  if (matchesKey(data, Key.up)) { this.selectedIndex--; }
  else if (matchesKey(data, Key.enter)) { this.onSelect?.(this.selectedIndex); }
  else if (matchesKey(data, Key.escape)) { this.onCancel?.(); }
  else if (matchesKey(data, Key.ctrl("c"))) { /* Ctrl+C */ }
}
```

Key identifiers: `Key.enter`, `Key.escape`, `Key.tab`, `Key.space`, `Key.backspace`, `Key.delete`, `Key.home`, `Key.end`, `Key.up`, `Key.down`, `Key.left`, `Key.right`, `Key.ctrl("c")`, `Key.shift("tab")`, `Key.alt("left")`, `Key.ctrlShift("p")`. String format also works: `"enter"`, `"ctrl+c"`, `"shift+tab"`.

## Line Width

Each line from `render()` must not exceed `width`:

```typescript
import { visibleWidth, truncateToWidth } from "@earendil-works/pi-tui";

render(width: number): string[] {
  return [truncateToWidth(this.text, width)];
}
```

Utilities: `visibleWidth(str)`, `truncateToWidth(str, width, ellipsis?)`, `wrapTextWithAnsi(str, width)`.

## Theming

Use `theme` from the callback. Never import theme directly.

```typescript
// Foreground colors
theme.fg("accent", text), theme.fg("success", text), theme.fg("error", text), theme.fg("muted", text)
theme.fg("border", text), theme.fg("mdHeading", text), theme.fg("syntaxKeyword", text)

// Background colors
theme.bg("selectedBg", text), theme.bg("toolPendingBg", text), theme.bg("userMessageBg", text)

// For Markdown
import { getMarkdownTheme } from "@earendil-works/pi-coding-agent";
const mdTheme = getMarkdownTheme();
```

## Common Patterns

### Pattern 1: Selection Dialog (SelectList)

```typescript
import { DynamicBorder } from "@earendil-works/pi-coding-agent";
import { Container, type SelectItem, SelectList, Text } from "@earendil-works/pi-tui";

const result = await ctx.ui.custom<string | null>((tui, theme, _kb, done) => {
  const container = new Container();
  container.addChild(new DynamicBorder((s: string) => theme.fg("accent", s)));
  container.addChild(new Text(theme.fg("accent", theme.bold("Pick an Option")), 1, 0));
  
  const selectList = new SelectList(items, Math.min(items.length, 10), {
    selectedPrefix: (t) => theme.fg("accent", t),
    selectedText: (t) => theme.fg("accent", t),
    description: (t) => theme.fg("muted", t),
  });
  selectList.onSelect = (item) => done(item.value);
  selectList.onCancel = () => done(null);
  container.addChild(selectList);
  container.addChild(new DynamicBorder((s: string) => theme.fg("accent", s)));

  return {
    render: (w) => container.render(w),
    invalidate: () => container.invalidate(),
    handleInput: (data) => { selectList.handleInput(data); tui.requestRender(); },
  };
});
```

### Pattern 2: Async Operation with Cancel (BorderedLoader)

```typescript
import { BorderedLoader } from "@earendil-works/pi-coding-agent";

const result = await ctx.ui.custom<string | null>((tui, theme, _kb, done) => {
  const loader = new BorderedLoader(tui, theme, "Fetching data...");
  loader.onAbort = () => done(null);
  fetchData(loader.signal).then((data) => done(data)).catch(() => done(null));
  return loader;
});
```

### Pattern 3: Settings/Toggles (SettingsList)

```typescript
import { getSettingsListTheme } from "@earendil-works/pi-coding-agent";
import { Container, type SettingItem, SettingsList, Text } from "@earendil-works/pi-tui";

await ctx.ui.custom((_tui, theme, _kb, done) => {
  const container = new Container();
  container.addChild(new Text(theme.fg("accent", theme.bold("Settings")), 1, 1));
  const settingsList = new SettingsList(items, 15, getSettingsListTheme(),
    (id, newValue) => ctx.ui.notify(`${id} = ${newValue}`, "info"),
    () => done(undefined), { enableSearch: true });
  container.addChild(settingsList);
  return { render: (w) => container.render(w), invalidate: () => container.invalidate(),
    handleInput: (data) => settingsList.handleInput?.(data) };
});
```

### Pattern 4: Persistent Status Indicator

```typescript
ctx.ui.setStatus("my-ext", ctx.ui.theme.fg("accent", "● active"));
ctx.ui.setStatus("my-ext", undefined); // clear
```

### Pattern 5: Widgets Above/Below Editor

```typescript
ctx.ui.setWidget("my-widget", ["Line 1", "Line 2"]);
ctx.ui.setWidget("my-widget", ["Line 1", "Line 2"], { placement: "belowEditor" });
ctx.ui.setWidget("my-widget", (_tui, theme) => ({
  render: () => items.map(item => item.done ? theme.fg("success", "✓ " + item.text) : theme.fg("dim", "○ " + item.text)),
  invalidate: () => {},
}));
ctx.ui.setWidget("my-widget", undefined); // clear
```

### Pattern 6: Custom Footer

```typescript
ctx.ui.setFooter((tui, theme, footerData) => ({
  invalidate() {},
  render(width: number): string[] {
    return [`${ctx.model?.id} (${footerData.getGitBranch() || "no git"})`];
  },
  dispose: footerData.onBranchChange(() => tui.requestRender()),
}));
ctx.ui.setFooter(undefined); // restore default
```

### Pattern 7: Custom Editor (vim mode, etc.)

```typescript
import { CustomEditor } from "@earendil-works/pi-coding-agent";
import { matchesKey, truncateToWidth } from "@earendil-works/pi-tui";

class VimEditor extends CustomEditor {
  private mode: "normal" | "insert" = "insert";

  handleInput(data: string): void {
    if (matchesKey(data, "escape")) {
      if (this.mode === "insert") { this.mode = "normal"; return; }
      super.handleInput(data); return;
    }
    if (this.mode === "insert") { super.handleInput(data); return; }
    // Normal mode: vim-style navigation
    switch (data) {
      case "i": this.mode = "insert"; return;
      case "h": super.handleInput("\x1b[D"); return;
      case "j": super.handleInput("\x1b[B"); return;
      case "k": super.handleInput("\x1b[A"); return;
      case "l": super.handleInput("\x1b[C"); return;
    }
    if (data.length === 1 && data.charCodeAt(0) >= 32) return;
    super.handleInput(data);
  }

  render(width: number): string[] {
    const lines = super.render(width);
    if (lines.length > 0) {
      const label = this.mode === "normal" ? " NORMAL " : " INSERT ";
      lines[lines.length - 1] = truncateToWidth(lines[lines.length - 1], width - label.length, "") + label;
    }
    return lines;
  }
}

ctx.ui.setEditorComponent((tui, theme, keybindings) => new VimEditor(tui, theme, keybindings));
ctx.ui.setEditorComponent(undefined); // restore default
```

## Key Rules

1. Always use `theme` from callback — don't import theme directly
2. Always type `DynamicBorder` color param: `(s: string) => theme.fg("accent", s)`
3. Call `tui.requestRender()` after state changes in `handleInput`
4. Return `{ render, invalidate, handleInput }` for custom components
5. Use existing components — `SelectList`, `SettingsList`, `BorderedLoader` cover 90% of cases

## Debug Logging

Set `PI_TUI_WRITE_LOG` to capture the raw ANSI stream written to stdout.
