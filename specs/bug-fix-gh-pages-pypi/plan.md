# Plan: Bug Fix — GitHub Pages Layout, PyPI Deployment, Test Repo

## Technical Approach

### 1. GitHub Pages Layout Fix

**Root cause:** The intangible-valuation `mkdocs.yml` and `docs/index.md` were aligned to startup-valuation but diverged in:
- Navigation structure: missing Examples section, Chapter Index
- mkdocs.yml: missing `site_url`, `repo_name`, version display, inlinehilite/snippets extensions
- Footer: copyright text format differs
- Sidebar: no version badge display

**Fix:** Update `mkdocs.yml` to match startup-valuation exactly (nav structure, theme config, extensions). Update `docs/index.md` to include Examples section reference. Create placeholder docs for Examples and Chapter Index if they don't exist.

### 2. PyPI Deployment Fix

**Root cause:** The `description` field in `pyproject.toml` exceeded 512 characters (already fixed). The workflow only triggers on release — this is by design. No actual error exists beyond the description length.

**Fix:** Verify the workflow is correct. Add a `deploy-docs` job that runs on push to main (separate from release-triggered PyPI publish).

### 3. Test Repo Verification

**Root cause:** No issue found — 1056 tests pass, 91% coverage, CI workflow is correct.

**Fix:** Run full CI verification (ruff, mypy, pytest) to confirm.

## Component Breakdown

| Component | Change | Files |
|-----------|--------|-------|
| MkDocs config | Align nav, theme, extensions with startup-valuation | `mkdocs.yml` |
| Docs CSS | Already copied, verify no drift | `docs/assets/stylesheets/extra.css` |
| Docs index | Verify structure matches startup-valuation | `docs/index.md` |
| Examples pages | Create 3 placeholder pages | `docs/examples/*.md` |
| Chapter Index page | Create placeholder page | `docs/chapters.md` |
| CI workflow | Add docs-deploy on push to main | `.github/workflows/publish.yml` |
| Tests | Run full suite | N/A |

## Technology Choices

- MkDocs Material — already in use, no change
- peaceiris/actions-gh-pages — already in use, no change
- pypa/gh-action-pypi-publish — already in use, no change

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| MkDocs build fails with new nav entries | High | Create placeholder pages before adding to nav |
| CSS styling doesn't match exactly | Medium | Copy extra.css verbatim from startup-valuation |
| PyPI workflow still fails | Low | Already fixed description length, verified upload works |

## Traceability

| AC | Component |
|----|-----------|
| AC-1, AC-2, AC-3, AC-4, AC-5, AC-6 | mkdocs.yml, extra.css, index.md |
| AC-7, AC-8, AC-9, AC-13 | publish.yml, pyproject.toml |
| AC-10, AC-11, AC-12 | pytest, ruff, mypy (verification only) |
| AC-14 | mkdocs.yml (add --strict flag) |
