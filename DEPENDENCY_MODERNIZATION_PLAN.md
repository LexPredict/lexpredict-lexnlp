# Dependency Modernization With Zero-Skip Test Policy

## Summary

- Treat `AGENTS.md` as policy-enforcing documentation for engineering agents.
- Make dependency management current (`uv` + single source of truth).
- Keep behavior stable while upgrading packages and model artifacts.
- Require all collected tests to pass with fully provisioned dependencies.

## Scope

### In

- Add explicit “do not skip/disable tests” policy to `AGENTS.md`.
- Consolidate dependency definitions into one modern packaging workflow.
- Make full test execution deterministic, including currently optional integrations.
- Introduce a controlled model-improvement pipeline with measurable acceptance gates.

### Out

- Feature-level extraction redesign unrelated to dependency/model reliability.
- Permanent acceptance of partial-pass builds.

## Action Items

- [ ] Add a **Test Integrity Policy** section to `AGENTS.md` that forbids adding/removing `skip`, `skipif`, or `xfail` to bypass failures, and requires fixing root causes instead.
- [ ] Define a **100% pass target** as: all collected tests pass on a fully provisioned runner, including Stanford-gated tests when required assets are present.
- [ ] Add a **skip-audit check** in CI that fails if new skip/xfail markers are introduced without an approved issue link and expiry date.
- [ ] Consolidate packaging to `pyproject.toml` + lockfile and deprecate conflicting manifests (`Pipfile`, split requirements variants) after parity is captured.
- [ ] Standardize runtime on modern Python (default 3.11) and align metadata/docs/CI to that policy.
- [ ] Replace brittle setup scripts with deterministic bootstrap steps for NLTK corpora, contract pipeline artifacts, Java/Stanford assets, and optional Tika.
- [ ] Run compatibility validation for serialized ML pipelines against upgraded `scikit-learn`; retrain/re-export artifacts when incompatible, with explicit version tags.
- [ ] Add a model quality gate: compare old vs new models on fixed evaluation fixtures and accept upgrades only when metrics improve or regressions are within strict tolerance.
- [ ] Publish a migration runbook in repo docs with exact commands for local setup, full test run, optional component enablement, and failure triage.
- [ ] Roll out in staged PRs (policy/doc first, packaging second, CI third, model upgrades fourth), each required to stay green end-to-end.

## Important Changes to Interfaces

- Installation interface becomes `uv` + `pyproject.toml` driven.
- Dependency groups become explicit extras (`dev`, `test`, `stanford`, `tika`).
- Model artifact interface becomes versioned and benchmark-gated (new tags for improved models).
- No intended changes to user-facing extraction function signatures during dependency modernization.

## Test Scenarios

- Fresh environment bootstrap succeeds with documented commands only.
- Base suite passes with zero unexpected skips/failures.
- Stanford suite passes when provisioned and enabled.
- CI skip-audit catches any new bypass markers.
- Model regression suite compares baseline vs upgraded outputs and blocks degradations.
- Built wheel installs in clean venv and passes smoke tests.

## Assumptions and Defaults

- Default judgment: this should be done now.
- Default policy: no test disabling for convenience; failures are fixed, not hidden.
- Default Python target: 3.11 (with compatibility checks for adjacent supported versions).
- Default model policy: prefer newer models/methods only when measured outputs are better.
- Default blocker handling: if an external dependency outage prevents completion, build is marked blocked/failing with explicit root-cause notes, not treated as pass.
