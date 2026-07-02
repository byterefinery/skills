---
name: jump
description: Conditional branching — jump forward or backward to a named label and resume processing from that point. Deterministic conditions (math, logic) are evaluated via on-the-fly scripts. Only vague natural-language conditions fall back to LLM judgment.
metadata:
  tags:
    - meta
---

# jump

## Overview

Evaluates a condition and, when satisfied, redirects processing to a named label placed by the `label` skill.

## Core Principle: Deterministic by Default

**Math/logic conditions are NEVER evaluated by the LLM:** They are compiled into a script (prefer inline on the fly), executed, and the exit code determines the jump.
**Free-form natural language conditions:** subjective, intent-based, fall back to LLM judgment.

## Usage

### Activation

When loaded without a condition, output exactly:

```
jump activated
```

Skill is ready. No action until a condition is encountered.

### Conditional Jump to Label
```
jump <label-name> [if <condition>]
```

## References

- [01-condition-types](references/01-condition-types.md) — Math, logic, and free-form condition classification
- [02-execution-flow](references/02-execution-flow.md) — Step-by-step evaluation and output procedure
- [03-jump-trigger](references/03-jump-trigger.md) — How `jump LABEL_NAME` activates label resolution
