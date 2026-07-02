---
name: jump
description: Conditional branching — jump forward or backward to a named label and resume processing from that point. Conditions can be mathematical, logical, or free-form natural language descriptions.
metadata:
  tags:
    - meta
---

# jump

## Overview

Jump is a conditional branching meta skill. It evaluates a condition and, when satisfied, redirects processing to a named label created by the `label` skill. Think of it as a natural-language `goto` with a guard clause — like `if (condition) goto label` in C/C++.

Jump works alongside `label` which places named markers in the conversation. Jump evaluates whether to reach them.

## Usage

### Syntax

```
jump <label-name> if <condition>
```

### Condition Types

**Mathematical** — numeric comparisons, arithmetic expressions:

```
jump label-retry if attempts < 3
jump label-done if score >= 90
jump label-overflow if count > max + 10
```

**Logical** — boolean operators, equality, membership:

```
jump label-error-handling if status == "failed"
jump label-next-step if ready && connected
jump label-skip if not in_whitelist
jump label-fallback if method == "a" || method == "b"
```

**Free-form** — natural language descriptions evaluated by the agent:

```
jump label-rewrite if the output is too verbose
jump label-clarify if the user seems confused
jump label-optimize if performance is a concern
jump label-summary if we have covered enough ground
```

### Execution Flow

1. Evaluate the condition against current context (conversation state, variables, outputs, user intent)
2. If condition is true → jump to the named label, resume processing from that point
3. If condition is false → continue linearly, skip the jump

### Examples

Pseudo-code example:

```
# Place labels first (via label skill)
/label start
/label retry
/label done

# Basic conditional jump
/jump retry if error_count > 0
/jump done if all_tasks_complete

# Chained jumps (evaluated in order, first match wins)
/jump critical if severity == "P0"
/jump warning if severity == "P1"
/jump info if severity == "P2"

# Free-form intent-based jump
/jump deep-dive if the user wants more detail
/jump high-level if the user needs a summary
```

### Combining with Label

Pseudo-code example, labels define destinations; jumps define the path. Use them together:

```
/label loop-top
... do work ...
/jump loop-top if more_items
/jump finished otherwise

/label finished
... wrap up ...
```

## Gotchas

- **Label must exist** — jumping to a label that was never placed has no effect. Verify the label was created before jumping to it.
- **No nested jumps** — a jump targets a single label. For complex branching, chain multiple jump statements rather than nesting.
- **First-match semantics** — when multiple jumps appear in sequence, evaluate them in order and stop at the first true condition. Later jumps are not evaluated.
- **Free-form conditions are subjective** — the agent interprets natural language conditions. Be specific: "if output exceeds 200 words" is better than "if output is long".
- **Backward jumps create loops** — jumping to an earlier label can repeat processing. Always pair backward jumps with a termination condition to avoid infinite loops.
- **Condition scope is current context** — conditions evaluate against the conversation state at the moment the jump is reached, not when it was written. Variables or state may have changed.
- **No variable assignment in conditions** — conditions are read-only evaluations. Use `if x > 5`, not `if x = 5`.
- **Label skill dependency** — this skill requires `label` to define destinations. Load `label` skill alongside `jump` when setting up branching workflows.
