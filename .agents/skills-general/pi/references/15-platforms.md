# Platform Setup

## Windows

Pi requires a bash shell on Windows. Checked locations (in order):

1. Custom path from `~/.pi/agent/settings.json`
2. Git Bash (`C:\Program Files\Git\bin\bash.exe`)
3. `bash.exe` on PATH (Cygwin, MSYS2, WSL)

For most users, [Git for Windows](https://git-scm.com/download/win) is sufficient.

Custom shell path:

```json
{ "shellPath": "C:\\cygwin64\\bin\\bash.exe" }
```

`app.suspend` has no default binding on native Windows (no Unix job control). Pi shows a status message instead.

## Termux on Android

Pi runs on Android via [Termux](https://termux.dev/).

### Installation

```bash
pkg update && pkg upgrade
pkg install nodejs termux-api git
npm install -g --ignore-scripts @earendil-works/pi-coding-agent
mkdir -p ~/.pi/agent
pi
```

Install [Termux:API](https://github.com/termux/termux-api#installation) from GitHub or F-Droid for clipboard and device integrations.

### Termux Commands

```bash
termux-open-url "https://example.com"     # Open URL
termux-open file.pdf                       # Open file with default app
termux-clipboard-set "text"               # Copy
termux-clipboard-get                       # Paste
termux-notification -t "Title" -c "Content"
termux-battery-status
termux-wifi-connectioninfo
termux-toast "message"
termux-camera-photo out.jpg
```

### Limitations

- No image clipboard — Termux clipboard API only supports text
- No native binaries — some optional native dependencies unavailable on Android ARM64
- Run `termux-setup-storage` once for `/storage/emulated/0` access

## tmux

Pi works inside tmux, but tmux strips modifier information from certain keys by default.

### Recommended Configuration

Add to `~/.tmux.conf`:

```tmux
set -g extended-keys on
set -g extended-keys-format csi-u
```

Then restart tmux: `tmux kill-server && tmux`.

Requires tmux 3.5+ for `extended-keys-format csi-u`. With tmux 3.2-3.4, omit that line; pi still supports the default xterm `modifyOtherKeys` format.

## Terminal Setup

Pi uses the [Kitty keyboard protocol](https://sw.kovidgoyal.net/kitty/keyboard-protocol/) for reliable modifier key detection.

### Works Out of Box

Kitty, iTerm2, VS Code (1.109.5+).

### Apple Terminal

Pi enables enhanced key reporting when available. Local macOS modifier fallback treats plain Return as `Shift+Enter` when running locally (not over SSH).

### Ghostty

Add to config:

```
keybind = alt+backspace=text:\x1b\x7f
```

Remove any older `shift+enter=text:\n` mapping — it sends a raw linefeed indistinguishable from `Ctrl+J`.

### WezTerm

For Kitty keyboard protocol explicitly:

```lua
config.enable_kitty_keyboard = true
```

On macOS, bind `Option+Enter` to fullscreen by default. Override for pi follow-up queueing:

```lua
config.keys = {
  { key = 'Enter', mods = 'ALT', action = wezterm.action.SendString('\x1b[13;3u') },
}
```

### Alacritty

For `Option+Enter` follow-up queueing on macOS, add to `~/.config/alacritty/alacritty.toml`:

```toml
[[keyboard.bindings]]
key = "Enter"
mods = "Alt"
chars = "\u001b[13;3u"
```

### VS Code (older than 1.109.5)

Add to `keybindings.json`:

```json
{
  "key": "shift+enter",
  "command": "workbench.action.terminal.sendSequence",
  "args": { "text": "\u001b[13;2u" },
  "when": "terminalFocus"
}
```

### Windows Terminal

Add to `settings.json` `actions`:

```json
{
  "actions": [
    { "command": { "action": "sendInput", "input": "\u001b[13;2u" }, "keys": "shift+enter" },
    { "command": { "action": "sendInput", "input": "\u001b[13;3u" }, "keys": "alt+enter" }
  ]
}
```

Windows Terminal binds `Alt+Enter` to fullscreen by default — remap it for pi follow-up queueing.

### Limited Support Terminals

xfce4-terminal, terminator, and IntelliJ IDEA's built-in terminal have limited escape sequence support. Modified Enter keys cannot be distinguished from plain Enter. Use a terminal that supports the Kitty keyboard protocol for the best experience.

## Shell Aliases

Pi runs bash in non-interactive mode (`bash -c`), which doesn't expand aliases by default.

To enable aliases, add to `~/.pi/agent/settings.json`:

```json
{
  "shellCommandPrefix": "shopt -s expand_aliases\neval \"$(grep '^alias ' ~/.zshrc)\""
}
```

Adjust the path to match your shell config.
