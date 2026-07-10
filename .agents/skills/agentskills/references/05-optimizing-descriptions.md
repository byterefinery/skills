# Optimizing Skill Descriptions

How to improve your skill's description so it triggers reliably on relevant prompts.

## How skill triggering works

Agents use progressive disclosure. At startup, they load only `name` and `description` of each available skill — just enough to decide when a skill might be relevant. When a user's task matches a description, the agent reads the full `SKILL.md` into context.

The description carries the entire burden of triggering. If it doesn't convey when the skill is useful, the agent won't know to reach for it.

Agents typically only consult skills for tasks requiring knowledge or capabilities beyond what they can handle alone. A simple one-step request may not trigger a skill even if the description matches perfectly.

## Writing effective descriptions

- **Use imperative phrasing** — "Use this skill when..." rather than "This skill does..."
- **Focus on user intent, not implementation** — describe what the user is trying to achieve
- **Err on the side of being pushy** — explicitly list contexts where the skill applies, including cases where the user doesn't name the domain directly
- **Keep it concise** — a few sentences to a short paragraph. The spec enforces 1024 characters max.

## Designing trigger eval queries

Test triggering with realistic user prompts labeled with whether they should or shouldn't trigger your skill.

```json
[
  { "query": "I've got a spreadsheet in ~/data/q4_results.xlsx with revenue in col C and expenses in col D — can you add a profit margin column and highlight anything under 10%?", "should_trigger": true },
  { "query": "whats the quickest way to convert this json file to yaml", "should_trigger": false }
]
```

Aim for about 20 queries: 8-10 that should trigger and 8-10 that shouldn't.

### Should-trigger queries

Vary along several axes:

- **Phrasing**: formal, casual, with typos or abbreviations
- **Explicitness**: some name the domain directly, others describe the need without naming it
- **Detail**: mix terse prompts with context-heavy ones
- **Complexity**: single-step tasks alongside multi-step workflows

The most useful should-trigger queries are ones where the skill would help but the connection isn't obvious.

### Should-not-trigger queries

The most valuable negative test cases are **near-misses** — queries that share keywords or concepts but actually need something different.

For a CSV analysis skill, strong negative examples:

- `"I need to update the formulas in my Excel budget spreadsheet"` — shares "spreadsheet" and "data" concepts, but needs Excel editing
- `"can you write a python script that reads a csv and uploads each row to our postgres database"` — involves CSV, but the task is database ETL

### Tips for realism

Include file paths, personal context, specific details, casual language, abbreviations, and occasional typos.

## Testing whether a description triggers

Run each query through your agent with the skill installed and observe whether the agent invokes it. The skill triggered if the agent loaded `SKILL.md`; it didn't trigger if the agent proceeded without consulting it.

A query passes if:
- `should_trigger` is `true` and the skill was invoked, or
- `should_trigger` is `false` and the skill was not invoked

### Running multiple times

Model behavior is nondeterministic — run each query multiple times (3 is a reasonable starting point) and compute a **trigger rate**: the fraction of runs where the skill was invoked.

A should-trigger query passes if its trigger rate is above threshold (0.5 is reasonable). A should-not-trigger query passes if its trigger rate is below that threshold.

## Avoiding overfitting with train/validation splits

If you optimize the description against all queries, you risk overfitting.

Split your query set:

- **Train set (~60%)**: queries used to identify failures and guide improvements
- **Validation set (~40%)**: queries set aside and only used to check whether improvements generalize

Both sets should contain proportional mix of should-trigger and should-not-trigger queries.

## The optimization loop

1. **Evaluate** the current description on both train and validation sets. Train results guide changes; validation results tell you whether changes generalize.
2. **Identify failures** in the train set: which should-trigger queries didn't trigger? Which should-not-trigger queries did?
3. **Revise the description:**
   - If should-trigger queries are failing, the description may be too narrow. Broaden scope or add context.
   - If should-not-trigger queries are false-triggering, the description may be too broad. Add specificity about boundaries.
   - Avoid adding specific keywords from failed queries — that's overfitting. Find the general category instead.
   - If stuck after several iterations, try a structurally different approach.
   - Stay under the 1024-character limit.
4. **Repeat** until all train set queries pass or no meaningful improvement.
5. **Select the best iteration** by validation pass rate. The best description may not be the last one produced.

Five iterations is usually enough.

## Applying the result

1. Update the `description` field in `SKILL.md` frontmatter
2. Verify it's under the 1024-character limit
3. Verify it triggers as expected — try a few prompts manually. For a rigorous test, write 5-10 fresh queries and run them through the eval script.

Before and after:

```yaml
# Before
description: Process CSV files.

# After
description: >
  Analyze CSV and tabular data files — compute summary statistics,
  add derived columns, generate charts, and clean messy data. Use this
  skill when the user has a CSV, TSV, or Excel file and wants to
  explore, transform, or visualize the data, even if they don't
  explicitly mention "CSV" or "analysis."
```

The improved description is more specific about what the skill does and broader about when it applies.
