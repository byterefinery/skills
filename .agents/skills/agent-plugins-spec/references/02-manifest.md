# Manifest (plugin.json)

## Location and loading

- Clients MUST check for `plugin.json` at the plugin root.
- One portable manifest per plugin — no other file replaces, supplements, or overrides root `plugin.json`.
- Client loads and validates `plugin.json` before discovering components.

## Schema

The manifest MUST be a JSON object. Schema is closed — only these top-level fields are permitted:

| Field | Type | Required | Description |
|---|---|---|---|
| `$schema` | string | Yes | Canonical schema identifier |
| `name` | string | Yes | Human-readable plugin name |
| `version` | string | No | Version string (semver recommended) |
| `description` | string | No | Short description |
| `author` | object | No | `name`, `email`, `url` (all strings) |
| `homepage` | string | No | Documentation URL |
| `repository` | string | No | Source repository URL |
| `license` | string | No | License identifier (SPDX recommended) |
| `keywords` | string[] | No | Search/discovery tags |
| `extensions` | object | No | Client-specific data by namespace |

### Schema violations

- **Unknown top-level field** — report and ignore (non-fatal). Continue loading if the rest is valid.
- **Non-object `extensions`** — report and ignore (non-fatal).
- **Any other schema violation** — fatal. Reject the plugin, do not discover or execute any components.

### `$schema` value

For Agent Plugins 1.0.0:

```
https://agent-plugins.org/schemas/1.0.0/plugin.schema.json
```

Clients use `$schema` to select locally supported validation rules. Clients MUST NOT retrieve a schema while loading a plugin. If the declared version is unsupported, reject the plugin.

## Name constraints

The `name` field MUST satisfy all constraints:

| Constraint | Rule |
|---|---|
| Length | 1–64 characters |
| Characters | `a-z`, `0-9`, `-`, `.` only |
| Start/end | Must be alphanumeric |
| Repetition | No `--` or `..` |

Valid: `my-plugin`, `acme.tools`, `lint3r`, `a`

Invalid: `My-Plugin` (uppercase), `-start` (leading hyphen), `has--double` (consecutive hyphens), `too.many..dots` (consecutive periods)

## Metadata validation

Clients MUST NOT reject a manifest solely because:

- `version` is not valid Semantic Versioning
- `homepage`, `repository`, or `author.url` is not a recognized URL
- `author.email` is not a recognized email address
- `license` is not an SPDX identifier

Metadata fields are validated only by their JSON types, except where the spec states explicit constraints.

## Author object

The `author` object MAY contain only `name`, `email`, and `url`, each a string. Any other field or value type makes the manifest invalid.

## Full manifest example

```json
{
  "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
  "name": "plugin-name",
  "version": "1.2.0",
  "description": "Brief plugin description",
  "author": {
    "name": "Author Name",
    "email": "author@example.com",
    "url": "https://example.com"
  },
  "homepage": "https://docs.example.com/plugin",
  "repository": "https://github.com/example/plugin",
  "license": "MIT",
  "keywords": ["keyword1", "keyword2"],
  "extensions": {
    "com.example.client": {
      "setting": true
    }
  }
}
```
