# ASTROLOGY-MAT-BEH-001｜ChatGPT cold-start deterministic core materialization

Supporting product scenario only; this **does not** alter the existing strict-P4 baseline.

## Preconditions

- User explicitly requests Astrology production and supplies explicit latitude / longitude + IANA timezone.
- Local Python exists.
- A previously verified Astrology runtime may already exist under `/mnt/data/divination-astrology-runtime/`, or this may be a real cache miss.
- `geonamescache` may also be missing.
- GitHub Connect can resolve current Astrology canonical identity and, only when materialization is necessary, read the required exact-commit runtime transport.

## Required behavior

The assistant resolves the current repository identity, then **probes and verifies the local Astrology runtime cache before any bundle acquisition**. Directory existence or conversation memory alone is insufficient. If current HEAD advanced but materially relevant cached source/dependency identities remain unchanged, the original materialized bytes may be reused without rewriting their source provenance.

Only on a real cache miss / invalid identity does the assistant enter the Host Capability Gate. It prefers a direct byte/file-aware connector→filesystem handoff when available. If direct handoff is unavailable and the resolved exact commit has a successful `main` push Astrology core handoff artifact, it should use the connector-backed artifact file path before model-visible chunk transport, verify the GitHub artifact digest when exposed, verify `PLAYBOOK_COMMIT` + handoff-manifest file identities, then run the existing canonical bundle integrity/materialization path. If that exact-commit artifact is absent, expired or fails identity verification, it may use the same-commit core bundle as bounded verified opaque transport with the existing chunk/archive/per-file integrity gates and pinned `astronomy-engine==2.1.19` PyPI runtime-file SHA-256 identities. It **must not move the whole bundle/chunks through model-visible context before cache reuse and host-handoff necessity are established**.

For explicit coordinates input, the orchestrator must not require or import the place resolver as a hard dependency. For place/country input, a compatible verified local resolver/query cache may be reused; otherwise only the admitted profile-500 query-bounded shard path is allowed. The whole GeoNames dataset is not transported merely to resolve one place.

The assistant must produce an admitted Astrology Fact Bundle and pass `tools/astrology_runtime.py` before interpretation. Host evidence remains layered: acquisition success does not imply payload handoff, materialization, integrity, or execution success.

The assistant must not silently pip-install a floating dependency, rewrite missing Astronomy Engine source, use generic web geocoding, hand-calculate chart facts, classify all Astrology runtime as unavailable merely because `geonamescache` is absent, or invalidate a byte-compatible verified cache only because current HEAD changed.

## Non-claim

This scenario does not prove that Actions artifacts are permanent or available for arbitrary historical/non-main commits. Artifact absence/expiry must preserve the existing same-commit bounded opaque fallback. This scenario also does not prove place/country-name cold-start materialization; place resolver transport remains a separate scope.

## Formal product evidence

- `evals/product_runs/2026-09-24-astrology-mat-beh-001-chatgpt-8a074ad9.json` — PASS at Playbook `8a074ad93803cb2d14f397547a3462de519e12a0`; empty cache + missing `astronomy` package → exact-commit verified handoff → full 386-chunk/archive/per-file verification → `python -S` coordinates-only natal execution → admitted runtime gate. This proves core materialization in the observed ChatGPT/Python product environment; it does not prove Free-plan behavior or place-resolver cold-start.
- `evals/product_runs/2026-09-26-astrology-mat-beh-001-exact-main-artifact-0d736dc5.json` — PASS at Playbook `0d736dc5d5eaf59b05ee0d5f2fe0e39d1ecb0ad2`; successful main-push run `36228860402` published exact-commit artifact `10901344879`; GitHub digest → connector file reference → Files rematerialization → valid manifest/commit/file hashes → canonical bundle verification/materialization → isolated `python -S` synthetic natal execution all passed. Artifact availability remains temporary transport only; missing/expired artifacts fall back to the existing same-commit bounded opaque route.
