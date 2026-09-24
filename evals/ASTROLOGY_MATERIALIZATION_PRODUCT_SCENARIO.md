# ASTROLOGY-MAT-BEH-001｜ChatGPT cold-start deterministic core materialization

Supporting product scenario only; this **does not** alter the existing strict-P4 baseline.

## Preconditions

- User explicitly requests Astrology production and supplies explicit latitude / longitude + IANA timezone.
- Local Python exists.
- Local Astrology core tools and/or `astronomy-engine` package are missing.
- `geonamescache` may also be missing.
- GitHub Connect can read the current exact-commit Astrology deterministic core bundle.

## Required behavior

The assistant treats local core-cache/package miss as a materialization trigger, not immediate Astrology unavailability. It resolves the Playbook to an exact commit, retrieves the same-commit core bundle, verifies chunk/archive/per-file identities including pinned `astronomy-engine==2.1.19` PyPI runtime-file SHA-256 identities, source provenance, and MIT license payload, writes a verified local cache plus `core_bundle_verification.json`, then executes the materialized Astrology provider/orchestrator.

For explicit coordinates input, the orchestrator must not require or import the place resolver as a hard dependency. The assistant must produce an admitted Astrology Fact Bundle and pass `tools/astrology_runtime.py` before interpretation.

The assistant must not silently pip-install a floating dependency, rewrite missing Astronomy Engine source, use generic web geocoding, hand-calculate chart facts, or classify all Astrology runtime as unavailable merely because `geonamescache` is absent.

## Non-claim

This scenario does not prove place/country-name cold-start materialization. Place resolver transport remains a separate scope.

## Formal product evidence

- `evals/product_runs/2026-09-24-astrology-mat-beh-001-chatgpt-8a074ad9.json` — PASS at Playbook `8a074ad93803cb2d14f397547a3462de519e12a0`; empty cache + missing `astronomy` package → exact-commit verified handoff → full 386-chunk/archive/per-file verification → `python -S` coordinates-only natal execution → admitted runtime gate. This proves core materialization in the observed ChatGPT/Python product environment; it does not prove Free-plan behavior or place-resolver cold-start.
