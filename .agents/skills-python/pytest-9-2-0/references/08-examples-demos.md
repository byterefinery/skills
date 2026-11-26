# Examples and demos from the pytest repo

Walkthroughs of the demo material shipped in the 9.2.0 tree: `doc/en/example/` (demos + examples) and the doc how-to pages that embed runnable snippets.

## `xfail_demo.py` — every xfail flavor

`doc/en/example/xfail_demo.py` shows all forms in one file:

```python
xfail = pytest.mark.xfail

@xfail
def test_hello(): ...                    # plain marker (via alias variable)

@xfail(run=False)
def test_hello2(): ...                   # not executed, reported [NOTRUN]

@xfail("hasattr(os, 'sep')")
def test_hello3(): ...                   # condition as a string

@xfail(reason="bug 110")
def test_hello4(): ...                   # reason only

@xfail('pytest.__version__[0] != "17"')
def test_hello5(): ...                   # version-condition string

def test_hello6():
    pytest.xfail("reason")               # imperative

@xfail(raises=IndexError)
def test_hello7(): ...                   # only this exception counts
```

`pytest -rx xfail_demo.py` prints a short summary with one `XFAIL` line per test (with its reason/condition) and a `7 xfailed` session line.

## `customdirectory/` — custom directory collector

Shows `pytest_collect_directory` + a custom `pytest.Directory` collector. A `conftest.py` plugin reads a `manifest.json` per directory and collects only the listed files; `tests/test_third.py` exists but is not run because it is not in the manifest. The collection tree shows the custom node:

```
<Dir customdirectory>
  <ManifestDirectory tests>
    <Module test_first.py>
      <Function test_1>
    <Module test_second.py>
      <Function test_2>
```

Default collectors: `pytest.Package` for directories with `__init__.py`, `pytest.Dir` otherwise.

## `nonpython/` — collecting non-Python tests

A `conftest.py` with a `pytest_collect_file` hook collects `test*.yaml` files; `YamlFile(pytest.File)` yields `YamlItem(pytest.Item)` objects (one per top-level key); `Item.runtest` implements execution (a dumb `name != value` check raises), `repr_failure(excinfo)` returns a custom failure string, and `reportinfo()` returns `(path, lineno, description)` used for location reporting and verbose mode. The collection tree: `<YamlFile test_simple.yaml>` → `<YamlItem hello>` / `<YamlItem ok>`. Output: `1 failed, 1 passed`.

## `reportingdemo.rst` — failure report tour

`failure_demo.py` (44 failing tests) demonstrates every assertion-reporting shape: parametrize IDs in the header, nested local-function value display, multiline code frames, text diffs (`-`/`+`), "At index N diff" for lists, dict differing/extra items, set extra items, dataclass/attrs attribute drill-down, `in`-text containment markers, captured stdout call, `DID NOT RAISE` for `raises`, `Failed:` for `pytest.fail`, custom assert messages (single/multiline/repr), and a dynamically compiled module showing up in the traceback.

## `pythoncollection.py` — collection tree

A minimal module (`test_function`, `TestClass.test_method`, `test_anothermethod`) run with `pytest --collect-only` to show the tree: `<Dir> → <Module> → <Function>/<Class>`. The how-to page also shows custom `python_files`/`python_classes`/`python_functions` (e.g., `check_*.py`, `Check`, `*_check`) and `collect_ignore`/`collect_ignore_glob` in `conftest.py`.

## `simple.rst` patterns

**Defaults via `addopts`/`PYTEST_ADDOPTS`** — `addopts = ["-ra", "-q"]` in config plus `export PYTEST_ADDOPTS="-v"`; final line is `<addopts> $PYTEST_ADDOPTS <CLI>` with last-wins on conflicts.

**Custom CLI option → fixture (the `cmdopt` pattern)** — a `conftest.py` pairs `pytest_addoption` with a fixture:

```python
# conftest.py
def pytest_addoption(parser):
    parser.addoption("--cmdopt", action="store", default="type1",
                     help="my option: type1 or type2", choices=("type1", "type2"))

@pytest.fixture
def cmdopt(request):
    return request.config.getoption("--cmdopt")
```

`choices=(...)` gives argparse-level validation (`invalid choice: 'type3'`); for richer validation use `type=` and raise `pytest.UsageError`. The test then requests `cmdopt` like any fixture — run with `pytest --cmdopt=type2`.

## Demo patterns worth copying

- **Expensive shared artifact** — session-scoped fixture over `tmp_path_factory` (see [06-env-fixtures](06-env-fixtures.md)).
- **Cross-run value cache** — `cache.get/set` fixture (see [06-env-fixtures](06-env-fixtures.md)); first run computes, later runs read from `.pytest_cache`.
- **`--lf` workflow** — full run (e.g., 2 of 50 fail), then `pytest --lf` reruns just the 2; `--ff` runs them first among all 50.
- **`--durations`** — `pytest --durations=10 --durations-min=1.0` for slowest-first triage.
