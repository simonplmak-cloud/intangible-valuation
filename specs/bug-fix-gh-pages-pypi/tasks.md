# Tasks: Bug Fix — GitHub Pages Layout, PyPI Deployment, Test Repo

## Dependencies

```
T1 (tests) ─┐
T2 (mkdocs) ─┤
T3 (examples)┤──→ T4 (commit/push)
T4           ┤
T5 (verify) ─┘
```

T1 and T2 can run in parallel. T3 depends on T2. T4 depends on T1+T2+T3. T5 depends on T4.

## Tasks

### T1 — Verify Test Suite [P] [S]
**Test task:** Run full test suite, lint, and type check.
- Run `pytest --cov=src --cov-report=term-missing -v` — expect 0 failures
- Run `ruff check .` — expect 0 errors
- Run `mypy src/` — expect 0 errors
- Run `python3 -m build` — expect successful build

### T2 — Align mkdocs.yml with startup-valuation [M]
**Implementation task:** Update `mkdocs.yml` to match startup-valuation structure.
- Add `site_url`, `repo_name` fields
- Add `navigation.instant`, `navigation.tracking`, `navigation.top` features
- Add `inlinehilite`, `snippets` markdown extensions
- Add Examples section to nav with 3 sub-pages
- Add Chapter Index to nav
- Add `extra` section with social links and generator: false
- Verify copyright format matches startup-valuation

### T3 — Create Missing Docs Pages [M]
**Implementation task:** Create placeholder pages referenced in nav.
- Create `docs/examples/core-methods.md` — placeholder for core methods examples
- Create `docs/examples/advanced-methods.md` — placeholder for advanced methods examples
- Create `docs/examples/industry-models.md` — placeholder for industry models examples
- Create `docs/chapters.md` — chapter-to-module mapping page
- Copy `docs/assets/stylesheets/extra.css` verbatim from startup-valuation (verify no drift)

### T4 — Update publish.yml for docs deploy on push [S]
**Implementation task:** Add a docs-deploy job that runs on push to main.
- Add `push` trigger to workflow for docs-deploy job only
- Keep PyPI publish on release only
- Ensure docs build with `mkdocs build` (not --strict yet, add after warnings resolved)

### T5 — Gate 1: Build & Lint Verification [S]
**Test task:** Verify all checks pass.
- Run `ruff check .`
- Run `mypy src/`
- Run `python3 -m build`
- Run `mkdocs build`

### T6 — Gate 2: Test Verification [S]
**Test task:** Run full test suite.
- Run `pytest --cov=src --cov-report=term-missing -v`
- Verify 0 failures
- Verify coverage >= 85%

### T7 — Gate 3: Docs Build Verification [S]
**Test task:** Verify docs build cleanly.
- Run `mkdocs build --strict`
- Verify zero warnings
- Verify all nav links resolve
- Verify book hero renders correctly
