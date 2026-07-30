# Modules

Valkey's module system allows extending the server with custom commands, data types, and integrations — all implemented in C.

## Module API Header

The main header is `src/valkeymodule.h`. It defines the `ValkeyModule_API` function table and type definitions.

## Module Lifecycle

```c
int ValkeyModule_OnLoad(ValkeyModuleCtx *ctx,
                        ValkeyModuleString **argv, int argc,
                        int apiversion) {
    if (ValkeyModule_IsModuleBuiltin(ctx)) {
        return VALKEYMODULE_OK;
    }

    if (ValkeyModule_Init(ctx, "mymodule", 1, VALKEYMODULE_APIVER_CURRENT)
        != VALKEYMODULE_OK) {
        return VALKEYMODULE_ERR;
    }

    // Register commands, data types, etc.
    ValkeyModule_CreateCommand(ctx, "my.command", MyCommand, "write", 1, 1, 1);

    return VALKEYMODULE_OK;
}
```

## Building Modules

```bash
# Build example modules
make -C src/modules

# Or with CMake
cmake .. -DBUILD_EXAMPLE_MODULES=yes
```

Module source files go in `src/modules/`. The Makefile builds them as `.so` shared libraries.

## Loading Modules

```conf
# In valkey.conf
loadmodule /path/to/my_module.so [arg1 arg2 ...]

# Or at runtime
MODULE LOAD /path/to/my_module.so
MODULE LOADEX /path/to/my_module.so ARGS arg1 arg2
```

```bash
# List loaded modules
MODULE LIST

# Unload (only if compiled with unload support)
MODULE UNLOAD mymodule
```

## Example Modules

Valkey ships with example modules in `src/modules/`:

| Module | Demonstrates |
|---|---|
| `helloworld.c` | Basic command creation, low-level and high-level APIs |
| `hellohook.c` | Server event hooks (key events, flush, etc.) |
| `hellotype.c` | Custom data type implementation |
| `helloblock.c` | Blocking commands |
| `hellotimer.c` | Timers and periodic work |
| `hellodict.c` | Dictionary iteration |
| `hellocluster.c` | Cluster-aware modules |
| `helloacl.c` | ACL integration |

## Key API Patterns

### Creating a simple command

```c
int MyCommand_ValkeyCommand(ValkeyModuleCtx *ctx,
                            ValkeyModuleString **argv, int argc) {
    if (argc != 2)
        return ValkeyModule_WrongArity(ctx);

    ValkeyModule_ReplyWithString(ctx, "Hello World");
    return VALKEYMODULE_OK;
}

// In OnLoad:
ValkeyModule_CreateCommand(ctx, "my.command", MyCommand_ValkeyCommand,
                           "write", 1, 1, 1);
```

### Low-level key operations

```c
ValkeyModuleKey *key = ValkeyModule_OpenKey(ctx, argv[1],
    VALKEYMODULE_READ | VALKEYMODULE_WRITE);

// List push
ValkeyModule_ListPush(key, VALKEYMODULE_LIST_TAIL, argv[2]);

// Get value length
size_t len = ValkeyModule_ValueLength(key);

ValkeyModule_CloseKey(key);
```

### High-level command call

```c
ValkeyModuleCallReply *reply = ValkeyModule_Call(ctx, "RPUSH", "ss",
    argv[1], argv[2]);
long long len = ValkeyModule_CallReplyInteger(reply);
ValkeyModule_FreeCallReply(reply);
```

### Auto memory management

```c
ValkeyModule_AutoMemory(ctx);
// No need to manually free strings/keys — cleaned up on function return
```

### Custom data types

```c
ValkeyModuleDataType *type = ValkeyModule_CreateDataType(ctx, "mytype", 0,
    &type_methods);

// type_methods includes: create, rdb_load, rdb_save, mem_usage, free, digest
```

## Module API Features

- **Command registration** with key specs, ACL categories, flags
- **Data type implementation** with RDB/AOF persistence hooks
- **Blocking commands** with timeout support
- **Timers** for periodic background work
- **Hooks** for key events, flush events, replication events
- **Cluster API** — `ValkeyModule_ClusterKeySlot()`, `ValkeyModule_ClusterKeySlotC()`
- **Client info** — flags, ACL permissions, tracking
- **Pub/Sub** — publish and subscribe from modules
- **I/O context** — for non-blocking operations
- **Command result callbacks** (since 9.1.0-rc2)

## Module API Changes in 9.1

- `ValkeyModule_ClusterKeySlotC()` — cluster key slot calculation
- Additional client info flags
- Prefix-aware ACL permission checks
- Unsigned 64-bit numeric config values
- Module command result callback addition

## Loading restrictions

```conf
# Block MODULE command at runtime (security hardening)
enable-module-command no
```

When enabled, modules can only be loaded at startup via `loadmodule` directive.

## License

New module source files should use:

```c
/*
 * Copyright (c) Valkey Contributors
 * All rights reserved.
 * SPDX-License-Identifier: BSD-3-Clause
 */
```
