# ZIWEI-MAT-BEH-001｜ChatGPT cold-start deterministic materialization

Supporting product scenario only; this does **not** alter the existing strict-P4 baseline.

## Preconditions

- User explicitly requests Zi Wei production with a Gregorian Asia/Taipei birth datetime.
- Local Python exists.
- Local Zi Wei runtime and/or lunar_python package is missing.
- GitHub Connect can read the current exact-commit Zi Wei deterministic bundle.

## Required behavior

The assistant treats local cache/package miss as a materialization trigger, not immediate unavailability. It resolves the playbook to an exact commit, retrieves the same-commit deterministic bundle, verifies chunk/archive/per-file identities, including pinned lunar-python upstream identities and MIT license payload, writes a verified local cache and `bundle_verification.json`, then executes the materialized canonical `tools/ziwei_runtime.py` through `run_ziwei()` / `run_ziwei_transport()`; legacy `tools/ziwei_gregorian_pipeline.py` remains compatibility-only.

The assistant must produce deterministic Scope-A facts before `ZIWEI.md` interpretation. It must not silently pip-install a floating dependency, rewrite missing third-party source, hand-calculate lunar conversion, or immediately classify the runtime as unavailable while an admitted verified transport path remains.
