# ZIWEI-MAT-BEH-001｜ChatGPT cold-start deterministic materialization

Supporting product scenario only; this does **not** alter the existing strict-P4 baseline.

## Preconditions

- User explicitly requests Zi Wei production with a Gregorian Asia/Taipei birth datetime inside the admitted 1900-01-01..2100-12-31 range.
- Local Python exists.
- Local Zi Wei runtime and/or required calendar year shard is missing.
- GitHub Connect can read the current exact-commit Zi Wei deterministic bundle and query-bounded calendar data.

## Required behavior

The assistant treats local cache/data miss as a materialization trigger, not immediate unavailability. It resolves the playbook to an exact commit, retrieves and verifies the same-commit deterministic bundle, materializes its runtime files plus the admitted calendar manifest, derives the required Gregorian year shard path(s) from the input, retrieves only those same-commit shard(s), verifies their byte size and SHA-256 against the manifest, then executes the materialized canonical `tools/ziwei_runtime.py` through `run_ziwei()` / `run_ziwei_transport()`; legacy `tools/ziwei_gregorian_pipeline.py` remains compatibility-only.

Ordinary requests require one year shard. The 31 December 23:00 cross-year edge may require the current year plus the next-year policy-tail shard. The full calendar dataset and the pinned `lunar_python` implementation are not transported into ordinary ChatGPT runtime.

The assistant must produce deterministic Scope-A facts before `ZIWEI.md` interpretation. It must not silently pip-install a calendar dependency, rewrite missing shard data, hand-calculate lunar conversion, fetch a shard from a different revision, or immediately classify the runtime as unavailable while the admitted verified bundle + query-bounded data path remains available.
