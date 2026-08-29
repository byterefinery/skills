# Saving and loading

Two modes: save the **state only** (like weights-only in PyTorch), or save the **whole program** (architecture + state).

## State-only saving

```python
compiled.save("dspy_program/program.json", save_program=False)   # JSON (recommended)
compiled.save("dspy_program/program.pkl", save_program=False)    # pickle (dangerous)
```

State includes each predictor's signature (instructions), demos, LM config, and configurable module attributes (e.g., a retriever's `k`). JSON is readable, auditable, and safe; pickle can only be loaded with `allow_pickle=True` and **can execute arbitrary code** — use it only for non-JSON-serializable values (`dspy.Image`, `datetime`, …) from trusted sources.

Loading requires recreating the same program shape:

```python
loaded = dspy.ChainOfThought("question -> answer")   # recreate the same program
loaded.load("dspy_program/program.json")
# .pkl: loaded.load("dspy_program/program.pkl", allow_pickle=True)
```

Loaded demos are plain dicts; the original program's demos are `dspy.Example` objects (`demo.toDict()` equals the loaded dict).

## Whole-program saving

```python
compiled.save("./dspy_program/", save_program=True)   # directory path
loaded = dspy.load("./dspy_program/")                 # no recreation needed
```

The program architecture is serialized to disk, so loading rebuilds the module tree — including custom `dspy.Module` subclasses you wrote. If your program depends on custom modules that are not importable at load time (different machine, different environment), you must make them importable first; saving with `save_program=True` records what is needed so you know what to ship.

## The `_compiled` flag

`.compile()` sets `_compiled=True` on the returned module. When you embed a compiled module inside a bigger program and run another optimizer on the outer one, `named_parameters()` skips the inner compiled module — its predictors keep exactly what the first optimizer produced. This enables the optimize-inner → embed → optimize-outer workflow.

## LM state in saved programs

Each LM attached to a module serializes via `lm.dump_state()` (model id, kwargs, endpoint config). Custom `dspy.BaseLM` subclasses need extra constructor args or runtime state, so they should override `dump_state`/`load_state`. Loading a state that imports a custom LM class requires trusted opt-in:

```python
program.load("program.json", allow_unsafe_lm_state=True)   # trusted files only
```

## Economics

`.compile()` is expensive (tens of dollars and minutes-to-hours of LM calls); serving the saved artifact is cheap. The loop that makes optimizers pay off: compile once per program version, save the JSON, and reload for inference. Rerun the compile when you swap the task LM — the same program optimizes to different instructions per model.
