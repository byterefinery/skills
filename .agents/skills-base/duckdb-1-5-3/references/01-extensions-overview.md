# Extensions Overview

DuckDB's extension system provides modular functionality beyond the core engine. Extensions are shared libraries loaded at runtime, either statically linked or dynamically loaded from the extension registry.

## Extension Categories

### In-Tree Extensions (bundled with DuckDB)

These live in the main DuckDB repository and are considered fundamental:

| Extension | Description |
|-----------|-------------|
| `parquet` | Parquet file reading/writing (always statically linked) |
| `json` | JSON parsing, serialization, and querying |
| `icu` | Time zones, collations, locale-aware string operations |
| `core_functions` | Core function library (always loaded) |
| `tpch` / `tpcds` | TPC-H and TPC-DS benchmark data generators |
| `autocomplete` | Shell autocomplete support |

### Out-of-Tree Extensions (DuckDB-managed)

These are maintained by DuckDB but in separate repositories, distributed via the extension registry:

#### Filesystem Extensions
- **`httpfs`** — HTTP/HTTPS file access, S3/GCS/Azure compatibility
- **`aws`** — AWS SDK-dependent features
- **`azure`** — Azure blob storage filesystem abstraction

#### Data Format Extensions
- **`excel`** — XLSX reading/writing, Excel number formatting
- **`delta`** — Delta Lake table support
- **`iceberg`** — Apache Iceberg table support
- **`avro`** — Apache Avro file support
- **`lance`** — Lance dataset format support
- **`ducklake`** — DuckLake SQL lakehouse format

#### Database Connector Extensions
- **`postgres_scanner`** — Query PostgreSQL databases directly
- **`mysql_scanner`** — Query MySQL/MariaDB databases directly
- **`sqlite_scanner`** — Query SQLite databases directly
- **`odbc_scanner`** — ODBC-compatible database access

#### Utility Extensions
- **`fts`** — Full-text search indexes
- **`spatial`** — Geospatial data types and functions
- **`inet`** — IP address data types and functions
- **`encodings`** — Unicode encoding conversion to UTF-8
- **`sqlsmith`** — SQL query fuzzer for testing

#### Data Transformation
- **`quack`** — CSV schema sniffing and preview

## Installation Patterns

### Automatic Loading (default)
```sql
-- Most common extensions autoload on first use
SELECT * FROM read_json('data.json');  -- json extension auto-loads
```

### Explicit Install and Load
```sql
INSTALL excel;
LOAD excel;
```

### Checking Extension Status
```sql
SELECT extension_name, loaded, installed, extension_version, install_mode
FROM duckdb_extensions();
```

Key columns:
- `loaded` — currently active in this session
- `installed` — downloaded to local cache
- `install_mode` — `STATICALLY_LINKED`, `REPOSITORY`, or `NOT_INSTALLED`
- `extension_version` — version identifier (commit hash for OOTEs)

### Extension Registry

Extensions download from: `http://extensions.duckdb.org/v{version}/{platform}/{name}.duckdb_extension.gz`

Custom registry:
```sql
SET custom_extension_repository = 'http://my-registry.org/';
```

Local storage: `~/.duckdb/extensions/v{version}/{platform}/`

### Disabling Autoloading
```sql
-- For testing or controlled environments
SET enable_autoload_extensions = false;
```

## Extension Architecture

### Build Types
1. **Statically linked** — compiled into the DuckDB binary (e.g., `parquet`)
2. **Loadable extension** — `.duckdb_extension` shared object, loaded at runtime
3. **External OOTE** — maintained in separate repo, independent CI/CD

### Version Compatibility

Each DuckDB version is tied to a specific set of extension versions. Mixing versions can cause incompatibilities. The extension binary embeds the DuckDB version it was built against.

```
DuckDB v1.5.3 → excel extension commit f4c72b5
DuckDB v1.5.3 → json extension (in-tree, same version)
```

### Creating Custom Extensions

Extensions follow the template at `github.com/duckdb/extension-template`. Key files:
- `CMakeLists.txt` — build configuration
- `src/{name}_extension.cpp` — entry point with `Load()` and `Name()` methods
- `vcpkg.json` — dependency manifest (optional)

Register functions via `ExtensionLoader`:
```cpp
void MyExtension::Load(ExtensionLoader &loader) {
    ScalarFunction my_func("my_function", {...}, ..., MyFunction);
    loader.RegisterFunction(my_func);
}
```
