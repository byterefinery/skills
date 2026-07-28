# Window Functions

## Table of Contents

- [Syntax](#syntax)
- [Built-in Window Functions](#built-in-window-functions)
- [PARTITION BY](#partition-by)
- [Frame Specifications](#frame-specifications)
- [EXCLUDE Clause](#exclude-clause)
- [Named Windows](#named-windows)
- [Examples](#examples)

## Syntax

```sql
function() OVER (
  [PARTITION BY expr [, ...]]
  [ORDER BY expr [ASC|DESC] [, ...]]
  [frame-spec]
  [EXCLUDE exclude-clause]
)
```

Window functions appear in SELECT result columns or ORDER BY. They cannot use DISTINCT and cannot appear in WHERE or GROUP BY.

## Built-in Window Functions

### Ranking

| Function | Description |
|---|---|
| `row_number()` | Sequential row number within partition (1-based) |
| `rank()` | Rank with gaps (tied rows get same rank, next rank skips) |
| `dense_rank()` | Rank without gaps |
| `percent_rank()` | (rank-1)/(partition_rows-1), range 0.0-1.0 |
| `cume_dist()` | Cumulative distribution: row_number/partition_rows |
| `ntile(N)` | Divide partition into N buckets (1-based) |

### Offset / Value Access

| Function | Description |
|---|---|
| `lag(expr [, offset [, default]])` | Value from preceding row |
| `lead(expr [, offset [, default]])` | Value from following row |
| `first_value(expr)` | Value from first row in frame |
| `last_value(expr)` | Value from last row in frame |
| `nth_value(expr, N)` | Value from Nth row in frame |

### Aggregate Window Functions

Any aggregate function can be used as a window function with OVER:

```sql
SUM(salary) OVER (PARTITION BY dept)
COUNT(*) OVER (ORDER BY hire_date ROWS UNBOUNDED PRECEDING)
AVG(score) OVER (ORDER BY score ROWS BETWEEN 2 PRECEDING AND 2 FOLLOWING)
```

## PARTITION BY

Divides the result set into groups. Each partition is processed independently.

```sql
SELECT name, dept, salary,
  RANK() OVER (PARTITION BY dept ORDER BY salary DESC) AS dept_rank
FROM employees;
```

Without PARTITION BY, the entire result set is one partition.

## Frame Specifications

The frame determines which rows are visible to the window function:

```
[frame-type] BETWEEN start AND end
```

### Frame Types

| Type | Description |
|---|---|
| `ROWS` | Count individual rows |
| `RANGE` | Group by peer values (same ORDER BY values) |
| `GROUPS` | Count groups of peers |

### Boundaries

| Boundary | Description |
|---|---|
| `UNBOUNDED PRECEDING` | First row of partition |
| `N PRECEDING` | N rows/groups before current |
| `CURRENT ROW` | Current row (and peers for RANGE/GROUPS) |
| `N FOLLOWING` | N rows/groups after current |
| `UNBOUNDED FOLLOWING` | Last row of partition |

### Default Frame

```
RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW EXCLUDE NO OTHERS
```

This means: all rows from partition start through the current row and its peers.

### Examples

```sql
-- Running total
SUM(salary) OVER (ORDER BY id ROWS UNBOUNDED PRECEDING)

-- Moving average (3 rows: previous, current, next)
AVG(salary) OVER (ORDER BY id ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING)

-- All rows in partition
MAX(salary) OVER (PARTITION BY dept)
-- default frame: RANGE UNBOUNDED PRECEDING AND CURRENT ROW
-- but since there's no ORDER BY, all rows are peers
```

## EXCLUDE Clause

Control whether current row and peers are included:

| Clause | Effect |
|---|---|
| `EXCLUDE NO OTHERS` | Default — include everything |
| `EXCLUDE CURRENT ROW` | Exclude current row, keep peers |
| `EXCLUDE TIES` | Include current row, exclude peers |
| `EXCLUDE GROUP` | Exclude current row and all peers |

```sql
SUM(salary) OVER (
  ORDER BY dept
  RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
  EXCLUDE CURRENT ROW
)
```

## Named Windows

Define windows in a WINDOW clause for reuse:

```sql
SELECT name, salary,
  RANK() OVER w AS rank,
  AVG(salary) OVER w AS dept_avg
FROM employees
WINDOW w AS (PARTITION BY dept ORDER BY salary DESC);
```

Window chaining: define a new window based on an existing one:

```sql
SELECT ...
  SUM(salary) OVER (w ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
WINDOW w AS (PARTITION BY dept ORDER BY id);
```

## Examples

```sql
-- Row numbers within departments
SELECT name, dept, salary,
  ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salary DESC) AS rn
FROM employees;

-- Running total
SELECT date, amount,
  SUM(amount) OVER (ORDER BY date ROWS UNBOUNDED PRECEDING) AS running_total
FROM transactions;

-- Previous and next values
SELECT name, salary,
  LAG(salary) OVER (ORDER BY hire_date) AS prev_salary,
  LEAD(salary) OVER (ORDER BY hire_date) AS next_salary
FROM employees;

-- Percentile ranking
SELECT name, score,
  NTILE(4) OVER (ORDER BY score DESC) AS quartile,
  PERCENT_RANK() OVER (ORDER BY score) AS pct_rank
FROM students;

-- First/last value in window
SELECT date, price,
  FIRST_VALUE(price) OVER (
    ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
  ) AS week_start_price
FROM stock_prices;
```
