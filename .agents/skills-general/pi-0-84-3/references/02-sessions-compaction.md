# Sessions and compaction

## Storage

Sessions auto-save to `~/.pi/agent/sessions/`, organized by working directory. Each session is a JSONL file with a tree structure — every entry has `id` and `parentId`, so branching happens in-place without new files. Override with `--session-dir`, `PI_CODING_AGENT_SESSION_DIR`, or `sessionDir` in settings.

```bash
pi -c                  # Continue most recent session
pi -r                  # Browse and select past sessions
pi --no-session        # Ephemeral (not saved)
pi --name "my task"    # Display name at startup
pi --session <path|id> # Specific file or partial UUID
pi --fork <path|id>    # Fork into a new session file
```

`/session` shows the current session file, ID, message count, tokens, and cost.

### Resume picker keys

`/resume` (and `pi -r`) opens the picker: type to search, Ctrl+P toggle path display, Ctrl+S sort mode, Ctrl+N named-only filter, Ctrl+R rename, Ctrl+D delete (uses the `trash` CLI when available).

## Branching

### `/tree`

Navigate the session tree in-place. Select any previous point and continue from there; all history stays in one file.

| Key | Action |
|---|---|
| ↑/↓ | Navigate visible entries |
| ←/→ | Page up/down |
| Ctrl+←/Ctrl+→ or Alt+←/Alt+→ | Fold/unfold, jump between branch segments |
| Shift+L | Set/clear a label (bookmark) on the selected entry |
| Shift+T | Toggle label timestamps |
| Enter | Select |
| Escape / Ctrl+C | Cancel |
| Ctrl+O | Cycle filter: default → no-tools → user-only → labeled-only → all |
| Ctrl+X | Copy selected message |

Default filter: `treeFilterMode` setting.

**Selection behavior:**
- Selecting a **user/custom message**: leaf moves to that message's parent, its text goes into the editor for editing and resubmission → new branch.
- Selecting an **assistant/tool/other entry**: leaf moves there, editor empty, continue from that point.
- Selecting the **root user message**: resets to an empty conversation with the original prompt in the editor.

### `/fork` vs `/clone` vs `/tree`

| Feature | `/tree` | `/fork` | `/clone` |
|---|---|---|---|
| Output | Same file | New file | New file |
| View | Full tree | User-message selector | Current active branch |
| Use | Explore alternatives in place | New session from an earlier prompt | Duplicate current work before continuing |

`/fork` copies the active path up to the chosen user message and places that prompt in the editor for modification. `/clone` duplicates the current active branch at the current position with an empty editor.

### Branch summaries

When `/tree` switches to another branch, pi offers to summarize the abandoned branch and attach the summary at the new position (no summary / default / custom focus). This preserves context from the path you left without replaying it.

## Compaction

Auto-compaction (enabled by default) summarizes older messages while keeping recent ones. Manual: `/compact [custom instructions]`.

**Trigger:** `contextTokens > contextWindow - reserveTokens` (default reserve 16384). Also triggers on context overflow (recovers and retries the aborted turn) or proactively when approaching the limit.

**How it works:**
1. Find the cut point by walking backwards from newest until `keepRecentTokens` (default 20000) is reached. Valid cut points: user messages, assistant messages, bash execution messages, custom messages — never tool results (they stay with their call).
2. Extract messages from the previous kept boundary (or session start) up to the cut point.
3. Generate a structured summary via LLM, passing the previous summary as iterative context.
4. Append a `CompactionEntry` (summary, `firstKeptEntryId`, `tokensBefore`, file-op details) and rebuild context as: system prompt + summary + messages from `firstKeptEntryId` onward.

**Split turns:** when a single turn exceeds `keepRecentTokens`, the cut lands mid-turn; pi generates two summaries (history + turn prefix) and merges them.

**Repeated compaction** summarizes from the previous compaction's kept boundary, so surviving messages are re-summarized into the new summary. `tokensBefore` is recalculated from the rebuilt context before writing.

**File tracking:** read/modified file lists accumulate across compactions and branch summaries (from tool calls and previous entry `details`), so the final summary knows every file touched.

### Summary format (structured)

Sections: `## Goal`, `## Constraints & Preferences`, `## Progress` (Done / In Progress / Blocked), `## Key Decisions`, `## Next Steps`, `## Critical Context`, plus `<read-files>` and `<modified-files>` blocks.

Messages are serialized as `[User]:`, `[Assistant thinking]:`, `[Assistant]:`, `[Assistant tool calls]:`, `[Tool result]:` lines (tool results truncated to 2000 chars) so the model summarizes instead of continuing the conversation.

**Compaction is lossy.** The full history remains in the JSONL file; use `/tree` to revisit.

### Settings

```json
{
  "compaction": { "enabled": true, "reserveTokens": 16384, "keepRecentTokens": 20000 },
  "branchSummary": { "reserveTokens": 16384, "skipPrompt": false }
}
```

Disable auto-compaction with `enabled: false` (`/compact` still works).

### Extension hooks

- `session_before_compact` — fired before auto or manual compaction; can `{ cancel: true }` or return `{ compaction: { summary, firstKeptEntryId, tokensBefore, usage?, details? } }`. Event includes `preparation` (messagesToSummarize, turnPrefixMessages, previousSummary, fileOps, tokensBefore, firstKeptEntryId, settings), `reason` (`manual` | `threshold` | `overflow`), `willRetry`, `signal`.
- `session_compact` / `session_compact_failed` — success and failure/abort notifications (for pairing attempts with outcomes).
- `session_before_tree` / `session_tree` — cancel navigation or provide a custom branch summary.
- Helpers: `convertToLlm()` + `serializeConversation()` from `@earendil-works/pi-coding-agent` to build your own summaries.

## Session file format

Entries (all with `id` + `parentId`): session header, messages (user/assistant/toolResult), model changes, thinking-level changes, labels, compactions, branch summaries, custom entries (extension state, not sent to LLM), custom messages (extension, sent to LLM), session info. Context for the next LLM call is rebuilt from the header, active path, and the latest compaction summary. See `docs/session-format.md` in the pi repo for the full entry/type reference and the `SessionManager` API (`getBranch()`, `getEntries()`, `getLabel()`, in-memory vs file-backed).

## Export, share, import

- `/export [file]` — HTML (styled, theme-derived colors) or JSONL
- `/share` — private GitHub gist with a shareable HTML link (`PI_SHARE_VIEWER_URL` overrides base URL)
- `/import <file>` — import and resume a session from JSONL
- `pi --export <in> [out]` — CLI export
- For publishing OSS sessions to Hugging Face: `badlogic/pi-share-hf`
