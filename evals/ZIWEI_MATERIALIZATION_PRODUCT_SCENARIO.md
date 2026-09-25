# ZIWEI-MAT-BEH-001｜ChatGPT cold-start deterministic materialization

Supporting product scenario only; this does **not** alter the existing strict-P4 baseline.

## Preconditions

- User explicitly requests Zi Wei production with a Gregorian Asia/Taipei birth datetime inside 1900-01-01..2100-12-31.
- Local Python exists.
- Local Zi Wei runtime and/or required calendar year shard is missing.
- GitHub Connect can read the current exact-commit Zi Wei deterministic bundle and repo-local calendar shard.

## Required behavior

The assistant treats local runtime/data miss as a materialization trigger, not immediate unavailability. It resolves the playbook to an exact commit, retrieves and verifies the same-commit deterministic bundle, materializes repo-local runtime source, then executes the materialized canonical `required_calendar_shards(GregorianBirthInput(...))` helper to determine the bounded data requirement.

For Gregorian input it retrieves only the returned exact-commit `data/calendar/ziwei_tw_interval/v1/years/YYYY.json` shard(s): one ordinary shard and at most two shards at the 31 Dec 23:xx year edge. Connector-returned Git blob identity must survive byte-preserving handoff and local verification before execution. The assistant then runs `tools/ziwei_runtime.py` through `run_ziwei()` / `run_ziwei_transport()`; legacy `tools/ziwei_gregorian_pipeline.py` remains compatibility-only.

The assistant must not pip-install a floating calendar package, re-bundle `lunar_python` as an ordinary runtime dependency, rewrite missing shard source, hand-calculate lunar conversion, or classify the runtime unavailable while admitted exact-commit runtime + shard materialization remains possible.
