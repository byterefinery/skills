# wasm-tools commands

Source material: `jco` CLI source (`packages/jco/src/jco.ts`) and jco book (docs at tag jco-v1.42.0). These wrap the Rust `wasm-tools` project for use in JS environments.

| Command | Purpose |
|---|---|
| `jco wit <component> [-o file] [--document name]` | Extract a component's WIT world. `--document` picks a specific document. |
| `jco print <input> [-o file]` | Render a Wasm binary as WAT text. |
| `jco parse <input.wat> -o <file>` | Encode WAT text as a Wasm binary (`-o` required). |
| `jco metadata-show [wasm] [--json]` | Inspect producer metadata, including nested module metadata. |
| `jco metadata-add [module] -m <field=name[@version]>... -o <file>` | Add producer metadata (`-m/--metadata` repeatable; `-o` required). |
| `jco new <core.wasm> [-o component.wasm]` | Create a component from a typed core Wasm module; can apply `[NAME=]adapter` files or built-in `--wasi-command` / `--wasi-reactor` adapters. |
| `jco embed [core.wasm] --wit <path> [-o file]` | Embed component type metadata into a core module; select world, string encoding, dummy mode, and producer metadata as needed. |
| `jco tool core-to-component ...` | Low-level equivalent of the core-to-component conversion workflow. |
| `jco opt <component> -o <output> [--asyncify] -- [wasm-opt args]` | Optimize every internal core module with Binaryen; defaults favor size optimization. Raw `wasm-opt` args go after `--`. |

## Useful diagnostic sequence

```sh
pnpm exec jco metadata-show --json input.wasm
pnpm exec jco wit input.wasm
pnpm exec jco transpile input.wasm -o out
```

If `jco wit` fails, verify the input is actually a Component Model component (not a plain core module). If generated code cannot resolve an import, inspect the transpile summary and generated module specifiers, then add an exact `--map` entry or provide imports through custom instantiation.
