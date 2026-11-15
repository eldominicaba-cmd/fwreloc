# Contributing a new tool to fwreloc-tools

This is a monorepo of small, well-tested CLI tools. To add a new tool:

## 1. Create the folder

```sh
mkdir -p tools/<name>/tests
```

Inside `tools/<name>/` place:

| file | purpose |
| --- | --- |
| `__init__.py` | makes `tools.<name>` a package (empty) |
| `main.py` | CLI entry point: `def main(argv=None) -> int` |
| `tests/test_<name>.py` | `unittest` suite using `unittest`; import the tool as `tools.<name>` |
| `README.md` | install line, usage example, what-it-does / does-not-do |
| `requirements.txt` | only external Python deps; no system binaries here |

## 2. Naming and layout

- Directory: `tools/<kebab-name>/`
- package: `tools.<kebab-name>`
- entry point: `def main(argv=None)` in `main.py`
- test file: `tests/test_<name>.py`; import the tool as `tools.<name>`
- keep the dependency scope tight — no system binaries inside a tool's
  `requirements.txt`

## 3. Shared helpers

Common helpers live in `shared/`. Import them as:

```python
from shared.cli import run_r2, resolve_r2
```

## 4. Tests that run in CI

- Use `unittest`; test on real input where possible (real firmware dumps,
  real SVG files, real binaries).
- Header of every test:

```python
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
```

- Keep tests fast — mock expensive external calls where it makes sense.

## 5. Register the tool

1. Add `tools.<name>` to `[tool.setuptools] packages` in the root
   `pyproject.toml`.
2. Add a `[project.scripts]` entry:

   ```toml
   <name> = "tools.<name>.main:main"
   ```

3. Add a one-line entry to the top-level `README.md` index.

## 6. Verify

```sh
python -m unittest discover -s tools -t . -p "test_*.py" -v
```

CI runs this on every push and reports green/red. Do not open a PR until the
CI is green and the tool is listed in the top-level README.
