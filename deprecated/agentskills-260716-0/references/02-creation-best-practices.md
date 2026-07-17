# Skill Creation Best Practices

How to write skills that are well-scoped and calibrated to the task.

## Start from real expertise

A common pitfall is asking an LLM to generate a skill without providing domain-specific context — relying solely on the LLM's general training knowledge. The result is vague, generic procedures rather than the specific API patterns, edge cases, and project conventions that make a skill valuable.

Effective skills are grounded in real expertise. Feed domain-specific context into the creation process.

### Extract from a hands-on task

Complete a real task in conversation with an agent, providing context, corrections, and preferences. Then extract the reusable pattern into a skill. Pay attention to:

- **Steps that worked** — the sequence of actions that led to success
- **Corrections you made** — places where you steered the agent's approach
- **Input/output formats** — what the data looked like going in and coming out
- **Context you provided** — project-specific facts, conventions, or constraints the agent didn't already know

### Synthesize from existing project artifacts

Feed existing knowledge into an LLM and ask it to synthesize a skill. A data-pipeline skill synthesized from your team's actual incident reports and runbooks will outperform one from a generic "data engineering best practices" article.

Good source material:

- Internal documentation, runbooks, and style guides
- API specifications, schemas, and configuration files
- Code review comments and issue trackers (captures recurring concerns)
- Version control history, especially patches and fixes (reveals patterns)
- Real-world failure cases and their resolutions

## Refine with real execution

The first draft of a skill usually needs refinement. Run the skill against real tasks, then feed the results — all of them, not just failures — back into the creation process. Ask: what triggered false positives? What was missed? What could be cut?

Even a single pass of execute-then-revise noticeably improves quality.

Read agent execution traces, not just final outputs. If the agent wastes time on unproductive steps, common causes include:

- Instructions that are too vague (the agent tries several approaches)
- Instructions that don't apply to the current task (the agent follows them anyway)
- Too many options presented without a clear default

## Spending context wisely

Once a skill activates, its full `SKILL.md` body loads into the agent's context window alongside conversation history, system context, and other active skills. Every token competes for the agent's attention.

### Add what the agent lacks, omit what it knows

Focus on what the agent *wouldn't* know without your skill: project-specific conventions, domain-specific procedures, non-obvious edge cases, and the particular tools or APIs to use. You don't need to explain what a PDF is, how HTTP works, or what a database migration does.

Ask about each piece of content: "Would the agent get this wrong without this instruction?" If no, cut it. If unsure, test it.

### Design coherent units

Deciding what a skill should cover is like deciding what a function should do: encapsulate a coherent unit of work that composes well with other skills. Skills scoped too narrowly force multiple skills to load for a single task. Skills scoped too broadly become hard to activate precisely.

### Aim for moderate detail

Overly comprehensive skills can hurt more than they help — the agent struggles to extract what's relevant and may pursue unproductive paths triggered by instructions that don't apply. Concise, stepwise guidance with a working example tends to outperform exhaustive documentation.

### Structure large skills with progressive disclosure

Keep `SKILL.md` under 500 lines and 5000 tokens — just the core instructions needed on every run. Move detailed reference material to separate files in `references/`.

The key is telling the agent *when* to load each file. "Read `references/api-errors.md` if the API returns a non-200 status code" is more useful than a generic "see references/ for details."

## Calibrating control

Match the specificity of instructions to the fragility of the task.

### High freedom — multiple valid approaches

Explain *why* rather than giving rigid directives. An agent that understands the purpose behind an instruction makes better context-dependent decisions.

```markdown
## Code review process

1. Check all database queries for SQL injection (use parameterized queries)
2. Verify authentication checks on every endpoint
3. Look for race conditions in concurrent code paths
4. Confirm error messages don't leak internal details
```

### Low freedom — fragile operations

Be prescriptive when consistency matters or a specific sequence must be followed:

```markdown
## Database migration

Run exactly this sequence:

```bash
python scripts/migrate.py --verify --backup
```

Do not modify the command or add additional flags.
```

### Provide defaults, not menus

When multiple tools could work, pick a default and mention alternatives briefly:

```markdown
Use pdfplumber for text extraction:

```python
import pdfplumber
```

For scanned PDFs requiring OCR, use pdf2image with pytesseract instead.
```

### Favor procedures over declarations

Teach the agent *how to approach* a class of problems, not *what to produce* for a specific instance. The approach should generalize even when individual details are specific.

## Patterns for effective instructions

### Gotchas sections

The highest-value content in many skills is a list of gotchas — environment-specific facts that defy reasonable assumptions. These are concrete corrections to mistakes the agent will make without being told:

```markdown
## Gotchas

- The `users` table uses soft deletes. Queries must include
  `WHERE deleted_at IS NULL` or results will include deactivated accounts.
- The user ID is `user_id` in the database, `uid` in the auth service,
  and `accountId` in the billing API. All three refer to the same value.
- The `/health` endpoint returns 200 as long as the web server is running,
  even if the database connection is down. Use `/ready` for full health.
```

Keep gotchas in `SKILL.md` where the agent reads them before encountering the situation.

### Templates for output format

When you need specific output format, provide a template. Agents pattern-match well against concrete structures:

```markdown
## Report structure

Use this template, adapting sections as needed:

```markdown
# [Analysis Title]

## Executive summary
[One-paragraph overview of key findings]

## Key findings
- Finding 1 with supporting data
- Finding 2 with supporting data

## Recommendations
1. Specific actionable recommendation
2. Specific actionable recommendation
```
```

### Checklists for multi-step workflows

An explicit checklist helps track progress and avoid skipping steps:

```markdown
## Form processing workflow

Progress:
- [ ] Step 1: Analyze the form (run `scripts/analyze_form.py`)
- [ ] Step 2: Create field mapping (edit `fields.json`)
- [ ] Step 3: Validate mapping (run `scripts/validate_fields.py`)
- [ ] Step 4: Fill the form (run `scripts/fill_form.py`)
- [ ] Step 5: Verify output (run `scripts/verify_output.py`)
```

### Validation loops

Instruct the agent to validate its own work before moving on:

```markdown
## Editing workflow

1. Make your edits
2. Run validation: `python scripts/validate.py output/`
3. If validation fails:
   - Review the error message
   - Fix the issues
   - Run validation again
4. Only proceed when validation passes
```

### Plan-validate-execute

For batch or destructive operations, create an intermediate plan, validate it against a source of truth, then execute:

```markdown
## PDF form filling

1. Extract form fields: `python scripts/analyze_form.py input.pdf` → `form_fields.json`
2. Create `field_values.json` mapping each field name to its intended value
3. Validate: `python scripts/validate_fields.py form_fields.json field_values.json`
4. If validation fails, revise `field_values.json` and re-validate
5. Fill the form: `python scripts/fill_form.py input.pdf field_values.json output.pdf`
```

The key ingredient is step 3: a validation script that checks the plan against the source of truth. Errors like "Field 'signature_date' not found" give the agent enough information to self-correct.

### Bundling reusable scripts

When iterating on a skill, compare execution traces across test cases. If the agent independently reinvents the same logic each run — building charts, parsing a specific format, validating output — that's a signal to write a tested script once and bundle it in `scripts/`.
