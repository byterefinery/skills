# Command-Line Interface (CLI)

## Table of Contents

- [Invocation](#invocation)
- [Dot-Commands](#dot-commands)
- [Output Modes](#output-modes)
- [Import/Export](#importexport)
- [Useful Patterns](#useful-patterns)

## Invocation

```bash
sqlite3 [options] [database_file] [SQL]
sqlite3 [options] :memory:
```

Options:
- `-bail` — Stop on error
- `-header` — Show headers
- `-column` — Column mode output
- `-csv` — CSV output
- `-html` — HTML table output
- `-json` — JSON output (since 3.43.0)
- `-batch` — Batch mode (no prompts)
- `-echo` — Echo input
- `-init file` — Read and execute SQL from file
- `-version` — Show version

```bash
# Interactive mode
sqlite3 mydb.db

# One-shot query
sqlite3 mydb.db "SELECT * FROM users LIMIT 5;"

# Pipe SQL
echo "SELECT count(*) FROM users;" | sqlite3 mydb.db

# Read SQL from file
sqlite3 mydb.db < schema.sql
```

## Dot-Commands

Dot-commands are CLI-only (not SQL):

| Command | Description |
|---|---|
| `.help` | Show help |
| `.schema [pattern]` | Show CREATE statements |
| `.tables [pattern]` | List tables |
| `.indexes [table]` | List indices |
| `.dump [table]` | SQL dump of database/tables |
| `.output file` | Send output to file |
| `.output stdout` | Send output to terminal |
| `.system command` | Run shell command |
| `.read file` | Read and execute SQL from file |
| `.timer on/off` | Show CPU time for each statement |
| `.timeout ms` | Set busy timeout |
| `.width col1 col2 ...` | Set column widths |
| `.mode mode` | Set output mode |
| `.headers on/off` | Show column headers |
| `.explain on/off` | Show EXPLAIN output |
| `.backup ?DB? FILE` | Backup database |
| `.restore FILE` | Restore from backup |
| `.import FILE TABLE` | Import data into table |
| `.archive` | Create/list/extract SQLite archives |
| `.changes on/off` | Show row change counts |
| `.clone NEWDB` | Clone database |
| `.preserve on/off` | Preserve .schema and .width settings |
| `.exit` / `.quit` | Exit |

## Output Modes

| Mode | Description |
|---|---|
| `ascii` | ASCII delimited output |
| `align` | Enable/disable alignment in column mode |
| `column` | Left-aligned columns with headers |
| `csv` | Comma-separated values |
| `html` | HTML table |
| `insert` | SQL INSERT statements |
| `json` | JSON array of objects (since 3.43.0) |
| `line` | One value per line |
| `list` | Pipe-separated (default) |
| `markdown` | Markdown table (since 3.38.0) |
| `tabs` | Tab-separated |
| `tcl` | TCL list format |

```bash
sqlite3 mydb.db
.mode csv
.headers on
.output results.csv
SELECT * FROM users;
.output stdout
```

### Setting Delimiters

```bash
.separator ","       # For list mode
.separator "|" "\n"  # Field and record separators
```

## Import/Export

### Export

```bash
# Full SQL dump
sqlite3 mydb.db .dump > backup.sql

# CSV export
sqlite3 -csv -header mydb.db "SELECT * FROM users;" > users.csv

# JSON export (since 3.43.0)
sqlite3 -json mydb.db "SELECT * FROM users;"

# HTML export
sqlite3 -html mydb.db "SELECT * FROM users;"
```

### Import

```bash
# Import CSV
sqlite3 mydb.db
.mode csv
.import users.csv users

# Import SQL
sqlite3 mydb.db < schema.sql

# Import with specific separator
sqlite3 mydb.db -separator '|'
.import data.txt users
```

### Backup

```bash
# Using .backup command
sqlite3 mydb.db ".backup backup.db"

# Using sqlite3 command
sqlite3 mydb.db ".dump" | sqlite3 backup.db

# Using sqlite3_cli_backup() or online backup API in C
```

## Useful Patterns

```bash
# Quick inspection
sqlite3 mydb.db ".tables"
sqlite3 mydb.db ".schema users"

# Run multiple commands
sqlite3 mydb.db <<EOF
.headers on
.mode column
SELECT * FROM users LIMIT 5;
SELECT count(*) AS total FROM users;
EOF

# Analyze database size
sqlite3 mydb.db "SELECT page_count * page_size AS size FROM pragma_page_count(), pragma_page_size();"

# Find large tables
sqlite3 mydb.db "
SELECT name,
  (SELECT count(*) FROM sqlite_master WHERE type='table' AND tbl_name=name) AS tables
FROM sqlite_master WHERE type='table';
"

# Check for corruption
sqlite3 mydb.db "PRAGMA integrity_check;"

# Optimize
sqlite3 mydb.db "PRAGMA optimize;"

# Vacuum (rebuild database)
sqlite3 mydb.db "VACUUM;"
```
