# SQLite Extensions

USearch ships SIMD-accelerated distance functions as SQLite extensions, bundled with the Python wheels.

## Installation

```sh
pip install usearch  # brings sqlite extensions
```

## Loading

```python
import sqlite3
import usearch

conn = sqlite3.connect(":memory:")
conn.enable_load_extension(True)
conn.load_extension(usearch.sqlite_path())
```

## Dense Vector Functions

Function names: `distance_<metric>_<type>`

| Metric | Functions |
|--------|-----------|
| Cosine | `distance_cosine_f64`, `distance_cosine_f32`, `distance_cosine_f16`, `distance_cosine_i8` |
| Inner Product | `distance_inner_f64`, `distance_inner_f32`, `distance_inner_f16`, `distance_inner_i8` |
| Squared Euclidean | `distance_sqeuclidean_f64`, `distance_sqeuclidean_f32`, `distance_sqeuclidean_f16`, `distance_sqeuclidean_i8` |
| Divergence | `distance_divergence_f64`, `distance_divergence_f32`, `distance_divergence_f16`, `distance_divergence_i8` |

### Usage (JSON vectors)

```sql
CREATE TABLE vectors_table (
    id INTEGER PRIMARY KEY,
    vector JSON NOT NULL
);

INSERT INTO vectors_table (id, vector)
VALUES
    (42, '[1.0, 2.0, 3.0]'),
    (43, '[4.0, 5.0, 6.0]');

SELECT
    id,
    distance_cosine_f32(vt.vector, '[7.0, 8.0, 9.0]') AS distance
FROM vectors_table AS vt;
```

### Usage (BLOB vectors)

```sql
-- BLOB storage is more efficient than JSON
CREATE TABLE vectors_blob (
    id INTEGER PRIMARY KEY,
    vector BLOB NOT NULL
);

SELECT
    id,
    distance_cosine_f32(vb.vector, X'00000040 00000040 00000040') AS distance
FROM vectors_blob AS vb;
```

## Binary Vector Functions

| Function | Description |
|----------|-------------|
| `distance_hamming_binary` | Number of differing bits |
| `distance_jaccard_binary` | Jaccard distance (bits) |

```sql
CREATE TABLE binary_vectors (
    id INTEGER PRIMARY KEY,
    vector BLOB NOT NULL
);

INSERT INTO binary_vectors (id, vector)
VALUES
    (42, X'FFFFFF'),  -- 111111111111111111111111
    (43, X'000000');  -- 000000000000000000000000

SELECT
    bv.id,
    distance_hamming_binary(bv.vector, X'FFFF00') AS hamming_distance,
    distance_jaccard_binary(bv.vector, X'FFFF00') AS jaccard_distance
FROM binary_vectors AS bv;
```

## String Distance Functions

| Function | Description |
|----------|-------------|
| `distance_levenshtein_bytes` | Levenshtein (byte-level) |
| `distance_levenshtein_unicode` | Levenshtein (code point level) |
| `distance_hamming_bytes` | Hamming (byte-level) |
| `distance_hamming_unicode` | Hamming (code point level) |

```sql
CREATE TABLE strings_table (
    id INTEGER PRIMARY KEY,
    word TEXT NOT NULL
);

INSERT INTO strings_table (id, word)
VALUES
    (42, 'é́cole'),
    (43, 'école');

SELECT
    st.id,
    distance_levenshtein_bytes(st.word, 'écolé') AS lb,
    distance_levenshtein_unicode(st.word, 'écolé') AS lu,
    distance_hamming_bytes(st.word, 'écolé') AS hb,
    distance_hamming_unicode(st.word, 'écolé') AS hu,
    -- Bounded versions (early stopping at threshold)
    distance_levenshtein_bytes(st.word, 'écolé', 2) AS lbb,
    distance_levenshtein_unicode(st.word, 'écolé', 2) AS lub,
    distance_hamming_bytes(st.word, 'écolé', 2) AS hbb,
    distance_hamming_unicode(st.word, 'écolé', 2) AS hub
FROM strings_table AS st;
```

The bounded versions (last parameter = threshold) stop early when the distance exceeds the threshold. Useful for autocomplete and fuzzy matching with a cutoff.

## Geographical Distance

```sql
-- Haversine distance in meters
SELECT
    distance_haversine_meters(
        '[48.8566, 2.3522]',   -- Paris [lat, lon]
        '[51.5074, -0.1278]'   -- London [lat, lon]
    ) AS distance_meters;
```

## Performance Notes

- SIMD acceleration covers AVX2, AVX-512 subsets, ARM NEON, and Arm SVE
- BLOB storage is more efficient than JSON for vectors
- String functions come from [StringZilla](https://github.com/ashvardanian/stringzilla)
- Vector functions come from [NumKong](https://github.com/ashvardanian/numkong)
- These are scalar functions, not an index — for large tables, combine with USearch's HNSW index in application code

## Gotchas

- **Extension loading must be enabled** — `conn.enable_load_extension(True)` is required before `load_extension()`
- **`usearch.sqlite_path()`** returns the path to the bundled extension — do not hardcode paths
- **JSON vs BLOB** — JSON vectors are parsed on each call (slower). BLOB vectors are read directly (faster)
- **Not an index** — these are distance functions, not an ANN index. For vector search on large tables, use USearch's HNSW index in your application layer
- **Unicode handling** — `_unicode` variants assume UTF-8 encoding. The `_bytes` variants count raw bytes, which differs for multi-byte characters
