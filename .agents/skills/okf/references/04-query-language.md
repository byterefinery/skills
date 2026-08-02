# Query Language

Reference for `okf.py visit` and `okf.py search` query expressions.

## Temporal Validity

```
valid-on:2022-03-15              # valid on this exact date
valid-between:2020-01-01,2024-06-30   # valid for the full range
valid-from:2023-01-01            # valid on any date >= this
valid-until:2025-12-31           # valid on any date <= this
not-stale                        # not stale today
not-stale-on:2024-06-30          # not stale on this date
```

Validity derived from: `status == stable`, `generated.at` (valid from), `stale_after` (valid until).

## Actor / Authorship

```
written-by:human                 # generated.by starts with "human:"
written-by:ai                    # generated.by is producer/version (not human/process)
written-by:process               # generated.by starts with "process:"
written-by:"human:alice"         # exact actor match
reviewed-by:human                # any verified[].by is human:
reviewed-by:ai                   # any verified[].by is producer/version
reviewed-by:process              # any verified[].by is process:
reviewed-by:"human:alice"        # exact actor match
```

## Trust Tier

```
trust-tier:unverified
trust-tier:machine-confirmed
trust-tier:human-reviewed
```

## Lifecycle

```
status:draft
status:stable
status:deprecated
```

## Type, Tags, Presence

```
type:Metric
type:"Attested Computation"      # quotes for multi-word values
tag:finance
has:sources                      # field exists and non-empty
has:verified
has:stale_after
has:runtime
```

## Date Comparisons

```
generated.after:2024-01-01       # generated.at > date
generated.before:2025-01-01      # generated.at < date
verified.after:2024-06-01        # any verified[].at > date
verified.before:2024-06-01       # any verified[].at < date
source-modified.after:2024-01-01 # any sources[].last_modified > date
source-modified.before:2024-01-01
```

## Source Author

```
source-author:human              # any sources[].author is human:
source-author:team:data-platform # exact source author match
```

## Text Search

```
title~:revenue                   # title contains (case-insensitive)
desc~:active users               # description contains
body~:recognition policy         # body text contains
```

## Boolean Composition

```
status:stable AND not-stale AND trust-tier:human-reviewed
written-by:human OR reviewed-by:human
NOT status:deprecated
(valid-on:2022-03-15 AND tag:finance) OR tag:legal
```

Space-separated terms default to AND. Explicit AND/OR/NOT/parens for complex expressions.

## Usage

```bash
# List matching paths
okf.py visit --bundle ./bundle --query "valid-on:2022-03-15"

# JSON output with frontmatter
okf.py visit --bundle ./bundle --query "written-by:human" --output json

# Structured search table
okf.py search --bundle ./bundle --query "tag:finance AND status:stable"

# JSON structured search
okf.py search --bundle ./bundle --query "trust-tier:human-reviewed" --json

# Summary table
okf.py visit --bundle ./bundle --query "status:stable" --output summary
```
