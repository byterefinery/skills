# Database Connector Extensions — postgres_scanner, mysql_scanner, sqlite_scanner

DuckDB's scanner extensions allow querying external databases directly as if they were local tables. Data is pulled on-demand during query execution — no ETL required.

## postgres_scanner

Query PostgreSQL databases directly from DuckDB SQL.

### Installation

```sql
INSTALL postgres_scanner;
LOAD postgres_scanner;
```

### Connecting

```sql
-- Create a connection
CALL postgres_attach(
    database := 'mydb',
    host := 'localhost',
    port := 5432,
    user := 'postgres',
    password := 'secret',
    schemas := ['public']
);

-- Now query PostgreSQL tables as if they were local
SELECT * FROM pg_public.my_table WHERE id > 100;
```

### Alternative: read_postgres()

```sql
-- One-off query without attaching
SELECT * FROM read_postgres(
    'SELECT * FROM users WHERE active = true',
    'host=localhost port=5432 dbname=mydb user=postgres password=secret'
);
```

### Features
- Read-only access to PostgreSQL tables
- Schema discovery (tables appear under the specified schema namespace)
- Predicate pushdown (WHERE clauses sent to PostgreSQL when possible)
- Column projection pushdown
- Supports multiple simultaneous connections

### Detaching

```sql
CALL postgres_detach('pg_public');
```

## mysql_scanner

Query MySQL/MariaDB databases directly from DuckDB SQL.

### Installation

```sql
INSTALL mysql_scanner;
LOAD mysql_scanner;
```

### Connecting

```sql
-- Create a connection
CALL mysql_attach(
    database := 'mydb',
    host := 'localhost',
    port := 3306,
    user := 'root',
    password := 'secret'
);

-- Query MySQL tables
SELECT * FROM mysql_mydb.users WHERE created_at > '2024-01-01';
```

### Alternative: read_mysql()

```sql
SELECT * FROM read_mysql(
    'SELECT * FROM orders WHERE total > 100',
    'host=localhost port=3306 dbname=mydb user=root password=secret'
);
```

### Features
- Read-only access to MySQL/MariaDB tables
- Schema discovery
- Works with MySQL 5.7+ and MariaDB 10.5+
- SSL connection support

## sqlite_scanner

Query SQLite databases directly from DuckDB SQL.

### Installation

```sql
INSTALL sqlite_scanner;
LOAD sqlite_scanner;
```

### Connecting

```sql
-- Attach a SQLite database
CALL sqlite_attach('/path/to/database.sqlite');

-- Query SQLite tables
SELECT * FROM sqlite_database.my_table;
```

### Alternative: read_sqlite()

```sql
SELECT * FROM read_sqlite(
    'SELECT * FROM users',
    '/path/to/database.sqlite'
);
```

### Features
- Read-only access to SQLite databases
- No network connection needed (local files)
- Schema discovery
- Lightweight — no additional dependencies beyond DuckDB

## odbc_scanner

Query any ODBC-compatible database from DuckDB SQL.

### Installation

```sql
INSTALL odbc_scanner;
LOAD odbc_scanner;
```

### Connecting

```sql
-- Attach via ODBC DSN
CALL odbc_attach('MyDSN');

-- Or via connection string
CALL odbc_attach(
    'Driver={ODBC Driver 17 for SQL Server};Server=myserver;Database=mydb;UID=user;PWD=pass'
);

-- Query tables
SELECT * FROM odbc_mydsn.my_table;
```

### Features
- Works with any ODBC driver (SQL Server, Oracle, SAP, etc.)
- Schema discovery
- Read-only access
- Requires ODBC driver installed on the system

## Cross-Database Queries

A powerful pattern: join data from multiple sources in a single query.

```sql
-- Join PostgreSQL data with local CSV
SELECT
    p.name,
    p.amount,
    c.category
FROM pg_public.products p
JOIN read_csv('categories.csv') c ON p.cat_id = c.id;

-- Aggregate MySQL data with DuckDB analytics
SELECT
    region,
    COUNT(*) AS order_count,
    AVG(total) AS avg_total
FROM mysql_salesdb.orders
GROUP BY region;
```

## Performance Considerations

### Data Transfer
- Scanner extensions pull data over the network during query execution
- Large tables can be slow — use WHERE filters and column selection to minimize transfer
- Consider exporting to Parquet for repeated analysis

### Pushdown Optimization
- Column projection: only requested columns are fetched
- Predicate pushdown: simple WHERE clauses may be evaluated on the source database
- Complex expressions (aggregations, joins across sources) are evaluated in DuckDB

### Connection Management
- Attachments persist for the session duration
- Multiple attachments to different databases are supported
- Use distinct schema names to avoid table name collisions

```sql
-- Attach multiple databases
CALL postgres_attach(database := 'sales', host := 'sales-db', user := 'reader', password := '***', schemas := ['public']);
CALL mysql_attach(database := 'inventory', host := 'inv-db', user := 'reader', password := '***');

-- Cross-database join
SELECT s.product_name, i.stock_level
FROM postgres_sales.public.products s
JOIN mysql_inventory.inventory.stock i ON s.sku = i.sku;
```

## Security Notes

- Credentials passed to scanner functions are session-scoped
- Scanner extensions provide read-only access — no DML operations
- Network connectivity required for remote databases
- Consider using environment variables or connection strings stored securely
- For production, use dedicated read-replica connections to avoid impacting source database performance
