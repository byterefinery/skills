# Date/Time Operators Reference

Parse, format, and manipulate dates and timestamps.

## `now()` — current time

Returns the current timestamp as a string:

```bash
yq -n '.timestamp = now()'
```

## `now_tz(tz)` — current time in timezone

```bash
yq -n '.ts = now_tz("America/New_York")'
```

Docker/Podman note: the Alpine image lacks timezone data. Add `tzdata`:

```dockerfile
FROM mikefarah/yq
USER root
RUN apk add --no-cache tzdata
USER yq
```

## `nowIso8601()` — ISO 8601 format

```bash
yq -n '.ts = nowIso8601()'
# → 2024-01-15T10:30:00Z
```

## Date formatting with `strftime` / `strptime`

### `strftime(format)` — format a date string

```bash
yq '.created |= strftime("%Y-%m-%d %H:%M:%S %Z")' data.yml
```

Common format specifiers: `%Y` (year), `%m` (month), `%d` (day), `%H` (hour), `%M` (minute), `%S` (second), `%Z` (timezone).

### `strptime(format)` — parse a date string

```bash
yq '.date |= strptime("%Y-%m-%d") | strftime("%B %d, %Y")' data.yml
```

## Date arithmetic

Add or subtract durations:

```bash
yq '.expiry = (.created | now | . + 86400 * 30)' config.yml
```

Use `to_number` to convert date strings to epoch seconds for arithmetic.

## `tz(zone)` — convert timezone

Convert a timestamp to a different timezone:

```bash
yq '.utc_time |= tz("UTC") | tz("America/Los_Angeles")' data.yml
```
