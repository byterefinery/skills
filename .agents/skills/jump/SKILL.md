---
name: jump
description: Conditional branching — jump forward or backward to a named label and resume processing from that point. Deterministic conditions (math, logic) are evaluated via on-the-fly scripts. Only vague natural-language conditions fall back to LLM judgment.
metadata:
  tags:
    - meta
---

# jump

## Overview

Conditional branching meta skill. Evaluates a condition and, when satisfied, redirects processing to a named label placed by the `label` skill. Natural-language `goto` with a guard — `if (condition) goto label`.

## Core Principle: Deterministic by Default

**Math/logic conditions are NEVER evaluated by the LLM.** They are compiled into a script, executed, and the exit code determines the jump. Only **free-form natural language conditions** (subjective, intent-based) fall back to LLM judgment.

## Usage

### Activation

When loaded without a condition, output exactly:

```
jump activated
```

Skill is ready. No action until a condition is encountered.

### Syntax

```
jump <label-name> [if <condition>]
```

### Condition Types

#### 1. Mathematical — evaluated via script

Numeric comparisons and arithmetic. Variables may appear for the first time in the condition; extract values from context, write a script, run it.

```
jump label-retry if attempts < 3
jump label-done if score >= 90
jump label-overflow if count > max + 10
```

#### 2. Logical — evaluated via script

Boolean ops, equality, membership, string comparisons. Same script mechanism.

```
jump label-error-handling if status == "failed"
jump label-next-step if ready && connected
jump label-skip if not in_whitelist
jump label-fallback if method == "a" || method == "b"
```

#### 3. Free-form — evaluated by LLM (fallback only)

Subjective or context-dependent conditions. These are the ONLY conditions the LLM evaluates directly.

```
jump label-rewrite if the output is too verbose
jump label-clarify if the user seems confused
jump label-optimize if performance is a concern
jump label-summary if we have covered enough ground
```

### Execution Flow

1. **Classify**: deterministic (math/logic) or free-form (natural language)?
2. **Deterministic**:
   a. Extract variable values from context — variables may be introduced in the condition itself
   b. Write script to `/tmp/jump_cond_<label>_<timestamp>.sh`
   c. Execute via `bash`
   d. Exit 0 → condition met; non-zero → not met
   e. Clean up script
3. **Free-form**: evaluate via LLM judgment against current context
4. **Output**:
   - Condition met → write exactly `jump LABEL_NAME`, stop
   - Condition not met → write exactly `continue`, let agent/harness/LLM decide next step

### Jump Trigger

`jump LABEL_NAME` is the activation signal. When it appears in generated output:

1. Agent/harness locates matching `label LABEL_NAME` marker in conversation
2. Label not found → output exactly `error: LABEL_NAME does not exist`
3. Label found → processing resumes from that point onward
4. Everything between jump and label is skipped

`jump LABEL_NAME` can result from condition evaluation or be emitted organically — either way, it triggers an immediate jump.
