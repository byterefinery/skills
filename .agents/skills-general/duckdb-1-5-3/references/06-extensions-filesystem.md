# Filesystem Extensions — httpfs, aws, azure

DuckDB's filesystem extensions enable reading and writing files from cloud storage and remote locations directly in SQL queries.

## httpfs

The `httpfs` extension adds HTTP/HTTPS file access and S3/GCS/Azure compatibility through URL-based paths.

### Installation

```sql
INSTALL httpfs;
LOAD httpfs;
```

Autoloads when referencing HTTP/HTTPS/S3/GCS/Azure URLs.

### Supported Protocols

| Protocol | Example |
|----------|---------|
| `http://` | `SELECT * FROM 'http://example.com/data.csv'` |
| `https://` | `SELECT * FROM 'https://example.com/data.parquet'` |
| `s3://` | `SELECT * FROM 's3://bucket/path/file.parquet'` |
| `gcs://` | `SELECT * FROM 'gcs://bucket/path/file.csv'` |
| `azure://` | `SELECT * FROM 'azure://container/path/file.parquet'` |
| `gs://` | Alias for `gcs://` |

### S3 Configuration

```sql
-- AWS credentials
SET s3_access_key_id = 'YOUR_ACCESS_KEY';
SET s3_secret_access_key = 'YOUR_SECRET_KEY';
SET s3_region = 'us-east-1';

-- Or use environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION)
-- Or IAM role / instance profile (auto-detected on EC2/ECS)

-- Query S3
SELECT * FROM 's3://my-bucket/data/file.parquet';

-- Write to S3
COPY (SELECT * FROM my_table) TO 's3://my-bucket/output/result.csv' (FORMAT 'csv');
```

### GCS Configuration

```sql
SET gcs_key_id = 'YOUR_GCS_KEY_ID';
SET gcs_secret_access_key = 'YOUR_GCS_SECRET';
SET gcs_token = 'YOUR_GCS_TOKEN';  -- Optional, for short-lived access

-- Or use GOOGLE_APPLICATION_CREDENTIALS environment variable pointing to a service account JSON key

SELECT * FROM 'gcs://my-bucket/data.parquet';
```

### Azure Configuration

```sql
SET azure_storage_account_name = 'myaccount';
SET azure_storage_access_key = 'YOUR_KEY';

-- Or use SAS token
SET azure_use_sas_token = true;
SET azure_sas_token = 'sv=2021-06-08&sig=...';

SELECT * FROM 'azure://container/path/file.parquet';
```

### HTTP Options

```sql
-- Custom headers (e.g., for API authentication)
SET http_header = '[{"Authorization": "Bearer token123"}]';

-- User agent
SET http_user_agent = 'MyApp/1.0';

-- Timeout (milliseconds)
SET http_timeout = 30000;
```

### Glob Patterns on Remote Paths

```sql
-- Read multiple files matching a pattern
SELECT * FROM 's3://bucket/data/*.parquet';
SELECT * FROM 'https://example.com/data/part-*.csv';
```

## aws Extension

The `aws` extension provides AWS SDK-dependent features beyond what httpfs offers.

### Installation

```sql
INSTALL aws;
LOAD aws;
```

### Features
- Full AWS SDK integration
- STS token support
- Cross-region operations
- S3 multipart upload for large writes
- DynamoDB access (via separate configuration)

## azure Extension

The `azure` extension adds Azure blob storage filesystem abstraction.

### Installation

```sql
INSTALL azure;
LOAD azure;
```

### Features
- Azure AD authentication
- Managed identity support
- Hierarchical namespace support
- Large file block upload

## Filesystem Architecture

DuckDB's filesystem layer is abstracted through the `FileSystem` interface:

```
LocalFileSystem  (default, built-in)
HTTPFileSystem   (httpfs extension)
S3FileSystem     (httpfs or aws extension)
GCSFileSystem    (httpfs extension)
AzureFileSystem  (httpfs or azure extension)
```

The correct filesystem is selected automatically based on the URL scheme. Multiple filesystem extensions can be loaded simultaneously.

## Security Considerations

- Credentials set via `SET` are session-scoped and not persisted
- Environment variables take precedence over explicit SET values
- For production, use IAM roles, service accounts, or managed identities instead of hardcoded credentials
- HTTP headers set via `SET http_header` apply to all HTTP requests in the session

## Performance Tips

- **Parquet over CSV**: Prefer Parquet format for remote data — columnar compression reduces transfer size
- **Partition pruning**: Use WHERE clauses that match partition columns to avoid downloading unnecessary files
- **Concurrent reads**: DuckDB can parallelize reads across multiple files in a glob pattern
- **Caching**: Consider downloading large datasets locally first, then querying from disk
