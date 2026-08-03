# Compaction & Branch Summarization

Pi has two summarization mechanisms:

| Mechanism | Trigger | Purpose |
|-----------|---------|---------|
| Compaction | Context exceeds threshold, or `/compact` | Summarize old messages to free context |
| Branch summarization | `/tree` navigation | Preserve context when switching branches |

## Compaction

### When It Triggers

Auto-compaction triggers when: `contextTokens > contextWindow - reserveTokens`

Default `reserveTokens` is 16384. Manual trigger with `/compact [instructions]`.

### How It Works

1. **Find cut point**: Walk backwards from newest message until `keepRecentTokens` (default 20k) is reached
2. **Extract messages**: Collect messages from previous kept boundary up to cut point
3. **Generate summary**: Call LLM with structured format, passing previous summary as iterative context
4. **Append entry**: Save `CompactionEntry` with summary and `firstKeptEntryId`
5. **Reload**: Session reloads using summary + messages from `firstKeptEntryId` onwards

### Split Turns

When a single turn exceeds `keepRecentTokens`, the cut point lands mid-turn. Pi generates two summaries (history + turn prefix) and merges them.

### Cut Point Rules

Valid cut points: user messages, assistant messages, BashExecution messages, custom messages. Never cut at tool results.

### CompactionEntry Structure

```typescript
interface CompactionEntry {
  type: "compaction";
  summary: string;
  firstKeptEntryId: string;
  tokensBefore: number;
  usage?: Usage;
  details?: { readFiles: string[]; modifiedFiles: string[] };
}
```

## Branch Summarization

When `/tree` navigates away from a branch, pi offers to summarize the abandoned branch. It finds the common ancestor, collects entries from old leaf back to ancestor, generates a summary, and appends a `BranchSummaryEntry`.

```typescript
interface BranchSummaryEntry {
  type: "branch_summary";
  fromId: string;
  summary: string;
  usage?: Usage;
  details?: { readFiles: string[]; modifiedFiles: string[] };
}
```

## Summary Format

Both use the same structured format:

```markdown
## Goal
## Constraints & Preferences
## Progress
### Done
### In Progress
### Blocked
## Key Decisions
## Next Steps
## Critical Context

<read-files>
path/to/file1.ts
</read-files>

<modified-files>
path/to/changed.ts
</modified-files>
```

Tool results are truncated to 2000 characters during serialization.

## Custom Summarization via Extensions

### session_before_compact

```typescript
pi.on("session_before_compact", async (event, ctx) => {
  const { preparation, branchEntries, customInstructions, reason, willRetry, signal } = event;
  
  // Cancel:
  return { cancel: true };
  
  // Custom summary:
  return {
    compaction: {
      summary: "Your summary...",
      firstKeptEntryId: preparation.firstKeptEntryId,
      tokensBefore: preparation.tokensBefore,
    }
  };
});
```

### session_before_tree

```typescript
pi.on("session_before_tree", async (event, ctx) => {
  const { preparation, signal } = event;
  return { cancel: true };
  // OR custom summary (only used if userWantsSummary is true):
  if (preparation.userWantsSummary) {
    return { summary: { summary: "Your summary..." } };
  }
});
```

## Settings

```json
{
  "compaction": {
    "enabled": true,
    "reserveTokens": 16384,
    "keepRecentTokens": 20000
  },
  "branchSummary": {
    "reserveTokens": 16384,
    "skipPrompt": false
  }
}
```
