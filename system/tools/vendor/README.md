---
type: tool-spec
name: vendor
---
# Vendored libraries

Atlas's hooks (`.claude/hooks/`) and validator (`system/tools/validate.py`) use only the Python 3 standard library plus the packages in this folder, so they run in any cloud session without installing anything.

| Package | Version | Source | License |
|---|---|---|---|
| `yaml/` (PyYAML, pure-Python part) | 6.0.3 | PyPI sdist `pyyaml-6.0.3.tar.gz` (sha256 `d76623373421df22fb4cf8817020cbb7ef15c725b9d5e45f17e189bfc384190f`), folder `lib/yaml/` copied unchanged | MIT, see `yaml/LICENSE` |

**How it is used:** callers put this folder first on `sys.path` (`sys.path.insert(0, "<repo>/system/tools/vendor")`) and call `yaml.safe_load` only. The optional C accelerator (`_yaml`) is not shipped; PyYAML falls back to pure Python automatically.

**Updating:** download the new sdist from PyPI, verify its sha256 against PyPI's published digest, replace `yaml/` with the sdist's `lib/yaml/` and `LICENSE`, update this table, and run the hook and validator tests from the `maintainers` branch (they must pass).
