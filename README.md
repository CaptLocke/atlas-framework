# Atlas maintainer files

This branch holds files for building and releasing Atlas that don't ship to users. It shares no history with `main`; a repo created from the Atlas template copies only `main`, so none of this reaches a user's Atlas.

| Path | What it is |
|---|---|
| `docs/maintainers/releasing.md` | The release checklist: changelog rules, version and boot-marker bumps, checks, tagging, the release zip. |
| `system/tests/regression/` | The regression suite: fictional work inputs and the records Atlas should produce from them. Run before every release. |

The paths match where these files sat on `main`, so their instructions work unchanged. To use them, from a checkout of `main`:

```bash
git fetch origin maintainers
git checkout origin/maintainers -- docs/maintainers system/tests/regression
```

Don't commit them to `main`. To remove them again:

```bash
git restore --staged docs/maintainers system/tests/regression && rm -rf docs/maintainers system/tests/regression
```

Edit them here, on `maintainers`, through a pull request into this branch.
