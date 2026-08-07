# Scripting Examples

Language-specific shebang patterns for `pkgx` scripts.

## Python

### With uv (PyPI dependencies)

```python
#!/usr/bin/env -S pkgx +python@3.11 uv run --with requests<=3 --with rich

import requests
from rich.pretty import pprint

resp = requests.get("https://peps.python.org/api/peps.json")
data = resp.json()
pprint([(k, v["title"]) for k, v in data.items()][:10])
```

### Simple script

```python
#!/usr/bin/env -S pkgx python@3.9

import sys
print(sys.version)
```

### With additional system deps

```python
#!/usr/bin/env -S pkgx +openssl python@3.11

# openssl libraries are available for compilation
```

## Ruby

```ruby
#!/usr/bin/env -S pkgx ruby@3

require 'bundler/inline'

gemfile do
  source 'https://rubygems.org'
  gem 'ruby-macho', '~> 3'
end
```

## JavaScript / TypeScript (Deno)

```javascript
#!/usr/bin/env -S pkgx deno@2 run

import fs from "npm:fs";
```

## Rust

```rust
#!/usr/bin/env -S pkgx rust-script

//! ```cargo
//! [dependencies]
//! time = "0.1.25"
//! ```
```

## C / C++ (Scriptisto)

```c
#!/usr/bin/env pkgx +clang +pkg-config scriptisto

#include <stdio.h>
#include <glib.h>

// scriptisto-begin
// script_src: main.c
// build_cmd: clang -O2 main.c `pkg-config --libs --cflags glib-2.0` -o ./script
// scriptisto-end

int main(int argc, char *argv[]) {
  gchar* user = g_getenv("USER");
  printf("Hello, C! Current user: %s\n", user);
  return 0;
}
```

## Bash with multiple deps

```bash
#!/usr/bin/env -S pkgx +gum +gh +npx +git bash>=4 -eo pipefail

gum format "# determining new version"

versions="$(git tag | grep '^v[0-9]\+\.[0-9]\+\.[0-9]\+')"
v_latest="$(npx -- semver --include-prerelease $versions | tail -n1)"
v_new=$(npx -- semver bump $v_latest --increment $1)

gum format "# releasing v$v_new"

gh release create \
  $v_new \
  --title "$v_new Released" \
  --generate-notes \
  --notes-start-tag=v$v_latest
```

## Ultra-portable (no pkgx required on system)

```bash
#!/bin/bash

eval "$(sh <(curl https://pkgx.sh) +git)"

which git  # prints /tmp/pkgx/git-scm.org/v2.46.3/bin/git
```

This pattern downloads pkgx to a temp location and uses it — no installation needed.

## Cross-language dependency mixing

```bash
#!/usr/bin/env -S pkgx +python@3.11 uv run

# /// script
# dependencies = [
#   "requests<3",
#   "rich",
# ]
# ///

import requests
from rich.pretty import pprint

resp = requests.get("https://peps.python.org/api/peps.json")
data = resp.json()
pprint([(k, v["title"]) for k, v in data.items()][:10])
```

Here `pkgx` provides both `python@3.11` and `uv`, then `uv run` handles PyPI deps.

## Recursive run (language ecosystem tools)

```bash
pkgx uvx cowsay "Run Python (PyPi) programs with uvx"
pkgx bunx cowsay "Run JavaScript (NPM) programs with bunx"
```

Use pkgx to invoke language-specific package runners without installing them.
