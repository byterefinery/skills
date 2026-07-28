# Aggregate Functions

## Table of Contents

- [Built-in Aggregates](#built-in-aggregates)
- [DISTINCT Modifier](#distinct-modifier)
- [FILTER Clause](#filter-clause)
- [ORDER BY in Aggregates](#order-by-in-aggregates)

## Built-in Aggregates

| Function | Description |
|---|---|
| `count(X)` | Count of non-NULL values of X |
| `count(*)` | Total row count (including NULLs) |
| `sum(X)` | Sum of non-NULL values; NULL if no rows |
| `total(X)` | Sum of non-NULL values; 0.0 if no rows (never overflows) |
| `avg(X)` | Average of non-NULL values; NULL if no rows |
| `min(X)` | Minimum non-NULL value |
| `max(X)` | Maximum non-NULL value |
| `group_concat(X)` | Concatenate non-NULL values, comma-separated |
| `group_concat(X, SEP)` | Concatenate with custom separator |
| `string_agg(X, SEP)` | Alias for group_concat (PostgreSQL-compatible) |
| `median(X)` | Median value (since 3.51.0, requires SQLITE_ENABLE_PERCENTILE) |
| `percentile(Y, P)` | Percentile, P in 0-100 (since 3.51.0) |
| `percentile_cont(Y, P)` | Percentile, P in 0.0-1.0 (since 3.51.0) |
| `percentile_disc(Y, P)` | Discrete percentile (since 3.51.0) |

```sql
-- Basic aggregates
SELECT
  COUNT(*) AS total,
  COUNT(active) AS active_count,
  SUM(salary) AS total_salary,
  AVG(salary) AS avg_salary,
  MIN(salary) AS min_salary,
  MAX(salary) AS max_salary
FROM employees;

-- group_concat
SELECT dept, group_concat(name, ', ') AS members
FROM employees GROUP BY dept;

-- total() vs sum()
SELECT total(salary);  -- returns 0.0 if no rows, never overflows
SELECT sum(salary);    -- returns NULL if no rows, can overflow on integers
```

### sum() vs total()

| Aspect | `sum()` | `total()` |
|---|---|---|
| No rows | Returns NULL | Returns 0.0 |
| Integer overflow | Throws error | Never overflows (uses REAL) |
| Return type | INTEGER if all inputs are INTEGER | Always REAL |
| SQL standard | Yes | No (SQLite extension) |

## DISTINCT Modifier

```sql
SELECT COUNT(DISTINCT dept) FROM employees;
SELECT SUM(DISTINCT salary) FROM employees;
```

Removes duplicates before aggregation. Works with any single-argument aggregate.

## FILTER Clause

Filter rows before aggregation (since 3.30.0):

```sql
SELECT
  COUNT(*) FILTER (WHERE status = 'active') AS active_count,
  AVG(salary) FILTER (WHERE dept = 'Engineering') AS eng_avg,
  MAX(salary) FILTER (WHERE year_hired > 2020) AS recent_max
FROM employees;
```

## ORDER BY in Aggregates

Control order of inputs to ordered aggregates like `group_concat()`:

```sql
SELECT dept,
  group_concat(name, ', ' ORDER BY name) AS members
FROM employees GROUP BY dept;
```

Without ORDER BY, the order is arbitrary and may vary between invocations.

## SQLite-Specific Aggregate Behavior

- `min()` / `max()` with GROUP BY: non-aggregate columns return values from the row that satisfied the min/max condition (SQLite extension, not standard SQL)

```sql
-- SQLite extension: returns the full row with the max salary
SELECT max(salary), name, dept FROM employees;
-- name and dept correspond to the row with max(salary)
```
