# Format Conversion Reference

yq converts between 14+ formats. Use `-p` for input format, `-o` for output format.

## Supported formats

| Format | Input (`-p`) | Output (`-o`) |
|---|---|---|
| YAML | `yaml`, `y` | `yaml`, `y` |
| JSON | `json`, `j` | `json`, `j` |
| XML | `xml`, `x` | `xml`, `x` |
| TOML | `toml` | `toml` |
| HCL | `hcl`, `h` | `hcl`, `h` |
| CSV | `csv`, `c` | `csv`, `c` |
| TSV | `tsv`, `t` | `tsv`, `t` |
| Properties | `props`, `p` | `props`, `p` |
| INI | `ini`, `i` | `ini`, `i` |
| Lua | `lua`, `l` | `lua`, `l` |
| Shell vars | — | `shell`, `s` |
| Base64 | `base64` | `base64` |
| K8s KYAML | `kyaml`, `ky` | `kyaml`, `ky` |
| URI | `uri` | `uri` |

## Common conversions

**JSON to YAML (pretty):**
```bash
yq -Poy sample.json
yq -o yaml sample.json
```

**YAML to JSON:**
```bash
yq -o json file.yaml
yq -oj file.yaml           # compact JSON
yq -oj -I=0 file.yaml      # single-line JSON
```

**XML to YAML:**
```bash
yq -o yaml file.xml
```

**TOML to YAML:**
```bash
yq -p toml -o yaml config.toml
```

**HCL (Terraform) to YAML:**
```bash
yq -p hcl -o yaml main.tf
```

**CSV to YAML:**
```bash
yq -p csv -o yaml data.csv
```

**Properties to YAML:**
```bash
yq -p props -o yaml app.properties
```

**YAML to Shell variables:**
```bash
yq -o shell config.yml      # outputs KEY=value pairs
```

**YAML to Lua:**
```bash
yq -o lua config.yml        # outputs Lua table syntax
```

## Format-specific flags

- `--csv-separator char` — CSV delimiter (default `,`)
- `--csv-auto-parse` — auto-parse YAML/JSON values in CSV cells
- `--properties-separator string` — properties key-value separator
- `--xml-attribute-prefix string` — prefix for XML attributes (default `+@`)
- `--xml-content-name string` — name for XML text content (default `+content`)
- `--yaml-fix-merge-anchor-to-spec` — spec-compliant merge anchors
- `--indent n` / `-I n` — output indentation level
- `-P` — pretty print (shorthand for `... style = ""`)

## Auto-detection

When no `-p` flag is given, yq auto-detects input format from file extension. Piped input defaults to YAML. Override with `-p`:

```bash
cat file.xml | yq -p xml '.node'
```
