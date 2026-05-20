# Spec: Bug Fix — GitHub Pages Layout, PyPI Deployment, Test Repo

**Status:** Draft
**Version:** 1.0
**Date:** 2026-05-20

## Overview

Three issues need fixing: (1) GitHub Pages docs site layout does not match the reference startup-valuation site — missing Examples navigation, Chapter Index, version badge in sidebar, and footer styling differences; (2) PyPI deployment workflow only triggers on release, not providing a way to test deployment; (3) Test repository coverage and CI validation needs verification.

## User Stories

- As a developer, I want the GitHub Pages site to match the startup-valuation layout so the two documentation sites look consistent under the Ascent Partners brand.
- As a maintainer, I want PyPI deployment to be testable without creating a release so I can verify the publish pipeline works.
- As a contributor, I want the test suite and CI to pass on every push so I know the codebase is healthy.

## Acceptance Criteria

### GitHub Pages Layout [MUST]

**AC-1:** Given a user visits the GitHub Pages site, when the page loads, then the header displays the Ascent Partners logo, site name, dark/light mode toggle, and search bar — matching startup-valuation header exactly.

**AC-2:** Given a user views the sidebar, when they expand navigation sections, then the sidebar shows: Home, API Reference (with all sub-pages), Examples (with Core Methods, Advanced Methods, Industry Models sub-pages), and Chapter Index — matching startup-valuation navigation structure.

**AC-3:** Given a user views the sidebar bottom, when the repo link is visible, then it shows the repository name with version badge (v0.1.0) — matching startup-valuation sidebar repo display.

**AC-4:** Given a user scrolls to the footer, when the footer is visible, then it shows the copyright text "© 2026 Ascent Partners Group Ltd, All rights reserved. | Part of the Valuation in Practice Series" with Amazon link, and the LinkedIn social icon — matching startup-valuation footer exactly.

**AC-5:** Given a user views the homepage, when the book hero section renders, then it uses the same CSS classes (`.book-hero`, `.book-cover`, `.book-info`, `.amazon-btn`) and styling as startup-valuation.

**AC-6:** Given a user views any page, when the color scheme is applied, then the primary color (#0083AB), accent color, fonts (Titillium Web for headings, Open Sans for body), and code block styling match startup-valuation.

### PyPI Deployment [MUST]

**AC-7:** Given a maintainer pushes a tag (e.g., v0.1.0), when the publish workflow runs, then the package builds successfully and uploads to PyPI without errors.

**AC-8:** Given the `pyproject.toml` description field, when the package is built, then the summary is under 512 characters (PyPI requirement).

**AC-9:** Given the publish workflow, when it completes, then the GitHub Pages docs are also deployed in the same workflow.

### Test Repo [MUST]

**AC-10:** Given the test suite runs, when `pytest` executes, then all tests pass (0 failures).

**AC-11:** Given the coverage report, when tests complete, then coverage is at least 85%.

**AC-12:** Given the CI workflow runs, when the pipeline executes, then ruff linting, mypy type checking, and pytest all pass.

### PyPI Test Deployment [SHOULD]

**AC-13:** Given a maintainer wants to test PyPI deployment, when they create a GitHub release, then the workflow publishes to PyPI and deploys docs without manual intervention.

### MkDocs Strict Build [SHOULD]

**AC-14:** Given `mkdocs build --strict` runs, when the docs are built, then there are zero warnings (broken links, missing pages, etc.).

## Out of Scope

- Adding new API documentation pages beyond existing module structure
- Changing the content of existing documentation pages
- Modifying the Python library code or test assertions
- Creating new MkDocs pages that don't exist in startup-valuation

## Open Questions

- [NEEDS CLARIFICATION] Should Examples pages be actual content pages or placeholder pages?
- [NEEDS CLARIFICATION] Should Chapter Index be a new page or just a nav link?

## Boundaries

**Always do:**
- Match startup-valuation mkdocs.yml structure (nav, theme, plugins, extensions)
- Copy extra.css styling exactly from startup-valuation
- Keep all existing content (book hero, quick start, modules table)

**Never do:**
- Change any Python source code in this fix
- Modify test assertions or expected values
- Remove existing navigation items
- Change the package version
