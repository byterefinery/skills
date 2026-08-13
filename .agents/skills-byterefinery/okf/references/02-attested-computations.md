# Attested Computations

An Attested Computation concept carries not just what a value *means* but a sanctioned way to *compute* it.

## Contract Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `runtime` | string | **Yes** | How to run the computation. Examples: `python`, `javascript`, `typescript`, `bash`, `sqlite`, `postgres`, `dbt`, `html`, `css`, `json`, `yaml`, `toml`. |
| `parameters` | [{name, type, required}] | No | Typed, named holes the agent may fill. |
| `computation` | path | No | Path to external file. Absent → inline body fence under `# Computation`. |
| `executor.resource` | path | No | Run instructions or code. |
| `executor.receipt` | [string] | No | Fields a run must return — the evidence the attester inspects. |
| `attester.resource` | path | No | Deterministic (no-LLM) code that takes a receipt and returns a verdict. |

## Example — Python

```yaml
---
type: Attested Computation
title: Monthly active users
runtime: python
parameters:
  - { name: month, type: string, required: true }
  - { name: data_path, type: string, required: true }
executor:
  resource: references/executors/run-python.sh
  receipt: [exit_code, stdout, stderr]
attester:
  resource: references/attesters/mau-check.py
---

# Computation

    import json
    def compute(month, data_path):
        with open(data_path) as f:
            events = json.load(f)
        return len({e["user_id"] for e in events if e["ts"].startswith(month)})
```

## Example — SQLite

```yaml
---
type: Attested Computation
title: Revenue by category
runtime: sqlite
parameters:
  - { name: db_path, type: string, required: true }
---

# Computation

    SELECT category, SUM(amount) AS revenue FROM orders GROUP BY category ORDER BY revenue DESC
```

## Computation Location

Provide the computation in one of two ways:

- **Inline:** a single fenced code block in the body under `# Computation`. Best for short computations reviewed alongside the contract.
- **File:** set `computation` to a path and omit the body fence. Best for long or generated computations.

```yaml
runtime: postgres
computation: references/computations/lib/revenue.sql
parameters:
  - { name: year, type: integer, required: true }
```

## How a Consumer Uses It

1. **Discover** via `type: Attested Computation` or by following a link.
2. **Load** the contract from frontmatter and the computation from body or file.
3. **Parameterize**: agent supplies values for declared parameters.
4. **Execute**: executor runs the bound computation, returns a receipt.
5. **Attest**: consumer runs attester over the receipt.
6. **Gate**: refuse failing attestation; warn when `today >= stale_after`.

## Verification vs Attestation

- `verified` confirms the *definition* still matches policy. Doc-level, slow, recorded in bundle.
- Attestation confirms a single *run* produced the value the sanctioned way. Per-call, runtime, not stored.

## Standalone Concepts

A computation is its own standalone concept; other concepts link to it. A document that needs multiple figures (revenue, profit, margin) stays one readable concept and links to one Attested Computation per figure.
