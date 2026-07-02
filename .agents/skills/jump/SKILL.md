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

| Type | Eval | Examples |
|---|---|---|
| **Math** | script | `attempts < 3`, `score >= 90`, `count > max + 10` |
| **Logic** | script | `status == "failed"`, `ready && connected`, `not in_whitelist` |
| **Free-form** | LLM | `output is too verbose`, `user seems confused`, `performance is a concern` |

Math/logic → extract vars from context, write script, execute, exit 0 = met. Free-form → LLM judgment (fallback only).

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
