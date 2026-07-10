# Evaluating Skill Output Quality

How to test whether your skill produces good outputs using eval-driven iteration.

## Designing test cases

A test case has three parts:

- **Prompt**: a realistic user message
- **Expected output**: a human-readable description of what success looks like
- **Input files** (optional): files the skill needs to work with

Store test cases in `evals/evals.json` inside your skill directory:

```json
{
  "skill_name": "csv-analyzer",
  "evals": [
    {
      "id": 1,
      "prompt": "I have a CSV of monthly sales data in data/sales_2025.csv. Can you find the top 3 months by revenue and make a bar chart?",
      "expected_output": "A bar chart image showing the top 3 months by revenue, with labeled axes and values.",
      "files": ["evals/files/sales_2025.csv"]
    }
  ]
}
```

**Tips for writing good test prompts:**

- **Start with 2-3 test cases** — don't over-invest before seeing first results
- **Vary the prompts** — different phrasings, levels of detail, and formality
- **Cover edge cases** — include at least one boundary condition (malformed input, unusual request)
- **Use realistic context** — real users mention file paths, column names, and personal context

## Running evals

Run each test case twice: once **with the skill** and once **without it** (or with a previous version). This gives you a baseline.

### Workspace structure

```
csv-analyzer/
├── SKILL.md
└── evals/
    └── evals.json
csv-analyzer-workspace/
└── iteration-1/
    ├── eval-top-months-chart/
    │   ├── with_skill/
    │   │   ├── outputs/
    │   │   ├── timing.json
    │   │   └── grading.json
    │   └── without_skill/
    │       ├── outputs/
    │       ├── timing.json
    │       └── grading.json
    └── benchmark.json
```

Each eval run should start with a clean context — no leftover state from previous runs.

### Capturing timing data

Record token count and duration after each run:

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332
}
```

## Writing assertions

Assertions are verifiable statements about what the output should contain or achieve. Add them after seeing the first round of outputs.

Good assertions:

- `"The output file is valid JSON"` — programmatically verifiable
- `"The bar chart has labeled axes"` — specific and observable
- `"The report includes at least 3 recommendations"` — countable

Weak assertions:

- `"The output is good"` — too vague
- `"The output uses exactly the phrase 'Total Revenue: $X'"` — too brittle

Add assertions to each test case in `evals/evals.json`:

```json
{
  "assertions": [
    "The output includes a bar chart image file",
    "The chart shows exactly 3 months",
    "Both axes are labeled",
    "The chart title or caption mentions revenue"
  ]
}
```

## Grading outputs

Grading means evaluating each assertion against actual outputs and recording **PASS** or **FAIL** with specific evidence:

```json
{
  "assertion_results": [
    {
      "text": "The output includes a bar chart image file",
      "passed": true,
      "evidence": "Found chart.png (45KB) in outputs directory"
    },
    {
      "text": "Both axes are labeled",
      "passed": false,
      "evidence": "Y-axis is labeled 'Revenue ($)' but X-axis has no label"
    }
  ],
  "summary": {
    "passed": 3,
    "failed": 1,
    "total": 4,
    "pass_rate": 0.75
  }
}
```

### Grading principles

- **Require concrete evidence for a PASS** — don't give the benefit of the doubt
- **Review the assertions themselves, not just results** — notice when assertions are too easy, too hard, or unverifiable

For comparing two skill versions, try **blind comparison**: present both outputs to an LLM judge without revealing which came from which version.

## Aggregating results

Compute summary statistics per configuration and save to `benchmark.json`:

```json
{
  "run_summary": {
    "with_skill": {
      "pass_rate": { "mean": 0.83, "stddev": 0.06 },
      "time_seconds": { "mean": 45.0, "stddev": 12.0 },
      "tokens": { "mean": 3800, "stddev": 400 }
    },
    "without_skill": {
      "pass_rate": { "mean": 0.33, "stddev": 0.10 },
      "time_seconds": { "mean": 32.0, "stddev": 8.0 },
      "tokens": { "mean": 2100, "stddev": 300 }
    },
    "delta": {
      "pass_rate": 0.50,
      "time_seconds": 13.0,
      "tokens": 1700
    }
  }
}
```

The `delta` tells you what the skill costs and what it buys.

## Analyzing patterns

- **Remove assertions that always pass in both configurations** — they don't tell you anything useful
- **Investigate assertions that always fail in both** — the assertion may be broken or the test too hard
- **Study assertions that pass with skill but fail without** — this is where the skill adds value
- **Tighten instructions when results are inconsistent** — high stddev means ambiguity
- **Check time and token outliers** — read execution transcripts to find bottlenecks

## Reviewing results with a human

Record specific feedback for each test case:

```json
{
  "eval-top-months-chart": "The chart is missing axis labels and the months are in alphabetical order instead of chronological.",
  "eval-clean-missing-emails": ""
}
```

Empty feedback means the output looked fine.

## Iterating on the skill

After grading and reviewing, you have three sources of signal:

- **Failed assertions** — specific gaps (missing step, unclear instruction, unhandled case)
- **Human feedback** — broader quality issues
- **Execution transcripts** — *why* things went wrong

Give all three along with the current `SKILL.md` to an LLM and ask it to propose changes. Guidelines:

- **Generalize from feedback** — fixes should address underlying issues broadly
- **Keep the skill lean** — fewer, better instructions often outperform exhaustive rules
- **Explain the why** — reasoning-based instructions work better than rigid directives
- **Bundle repeated work** — if every test run independently wrote similar helper code, bundle it into `scripts/`

### The loop

1. Give eval signals and current `SKILL.md` to an LLM; ask for improvements
2. Review and apply the changes
3. Rerun all test cases in a new `iteration-<N+1>/` directory
4. Grade and aggregate the new results
5. Review with a human. Repeat.

Stop when satisfied, feedback is consistently empty, or no meaningful improvement between iterations.
