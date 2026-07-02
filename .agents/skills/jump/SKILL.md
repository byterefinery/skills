---
name: jump
description: Conditional branching — jump forward or backward to a named label and resume processing from that point. Deterministic conditions (math, logic) are evaluated via on-the-fly scripts. Only vague natural-language conditions fall back to LLM judgment.
metadata:
  tags:
    - meta
---

# jump

## Overview

Jump is a conditional branching meta skill. It evaluates a condition and, when satisfied, redirects processing to a named label created by the `label` skill. Think of it as a natural-language `goto` with a guard clause — like `if (condition) goto label` in C/C++.

Jump works alongside `label` which places named markers in the conversation. Jump evaluates whether to reach them.

## Core Principle: Deterministic by Default

**Mathematical and logical conditions are NEVER evaluated by the LLM.** They are compiled into a small script, executed, and the exit code determines the jump. This guarantees deterministic, reproducible results.

Only **free-form natural language conditions** (vague, subjective, intent-based) fall back to LLM judgment.

## Usage

### Activation

When the jump skill is loaded without any prompt or condition to evaluate, it outputs:

```
jump activated
```

This signals the skill is ready. No action is taken until a condition is encountered.

### Syntax

```
jump <label-name> [if <condition>]
```

### Condition Types

#### 1. Mathematical — evaluated via script

Numeric comparisons and arithmetic expressions. The agent extracts variable values from context, writes a script, and runs it.

```
jump label-retry if attempts < 3
jump label-done if score >= 90
jump label-overflow if count > max + 10
```

#### 2. Logical — evaluated via script

Boolean operators, equality, membership, string comparisons. Same script mechanism.

```
jump label-error-handling if status == "failed"
jump label-next-step if ready && connected
jump label-skip if not in_whitelist
jump label-fallback if method == "a" || method == "b"
```

#### 3. Free-form — evaluated by LLM (fallback only)

Natural language descriptions that are inherently subjective or context-dependent. These are the ONLY conditions the LLM evaluates directly.

```
jump label-rewrite if the output is too verbose
jump label-clarify if the user seems confused
jump label-optimize if performance is a concern
jump label-summary if we have covered enough ground
```

### Execution Flow

1. **Classify the condition**: Is it deterministic (math/logic) or free-form (natural language)?
2. **For deterministic conditions**:
   a. Extract variable values from the current context (conversation state, command outputs, previous results)
   b. Write a condition script to `/tmp/jump_cond_<label>_<timestamp>.sh`
   c. Execute the script via `bash`
   d. Exit code 0 → condition satisfied
   e. Exit code non-zero → condition not met
   f. Clean up the script file
3. **For free-form conditions**: Evaluate using LLM judgment against current context
4. **Output the result**:
   - Condition satisfied → write exactly `jump LABEL_NAME` and stop
   - Condition not met → write exactly `continue` and resume conversation from current point

### Jump Trigger

The `jump LABEL_NAME` output is the activation signal. When this appears anywhere in a generated message:

1. The system locates the matching `label LABEL_NAME` marker in the conversation
2. Prompt processing resumes from that point onward
3. Everything between the jump and the label is skipped

This means `jump LABEL_NAME` can appear as the direct result of a condition evaluation, or be emitted organically during conversation — either way, it triggers an immediate jump to the labeled point.
