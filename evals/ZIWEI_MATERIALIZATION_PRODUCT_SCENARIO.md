# ZIWEI-MAT-BEH-001｜ChatGPT cold-start deterministic materialization

Supporting product scenario only; this does **not** alter the existing strict-P4 baseline.

## Preconditions

- User explicitly requests Zi Wei production with a Gregorian Asia/Taipei birth datetime inside the admitted 1900-01-01..2100-12-31 range.
- Local Python exists.
- Either a previously materialized Zi Wei runtime may exist under `/mnt/data/divination-ziwei-runtime/`, or this is a real cache miss.
- GitHub Connect can resolve current Zi Wei canonical identity and, when materialization is necessary, read the exact-commit deterministic transport / query-bounded calendar data.

## Required behavior

The assistant resolves current repository identity, then **probes and verifies the local Zi Wei runtime cache before any bundle acquisition**. A cache that is present, executable and identity-compatible with the current execution contract is reused; conversation memory or directory existence alone is insufficient evidence. If current HEAD advanced but materially relevant cached source identities are unchanged, the assistant may reuse the original materialized bytes without rewriting their provenance.

Only on a real cache miss / invalid identity does the assistant enter host-aware materialization. It prefers a direct byte/file-aware connector→filesystem handoff if available. If direct handoff is unavailable, it checks for a successful exact-main connector-backed Zi Wei handoff artifact before model-visible chunk transport. A matching artifact must bind the exact commit through its name, `PLAYBOOK_COMMIT`, and `HANDOFF_MANIFEST.json`; platform digest (when exposed) and every manifest payload identity must verify before the canonical bundle verifier/materializer is used. Artifact absence/expiry/identity failure must preserve the existing same-commit bounded opaque fallback. If no valid artifact route exists, it may use the admitted same-commit deterministic bundle as bounded verified opaque transport, with chunk/archive/per-file verification and deterministic reassembly before execution. It must not move the whole bundle through model-visible context before cache reuse and transport necessity are established.

After runtime materialization/reuse, it derives the required Gregorian year shard path(s) from the input, reuses a matching verified local shard when possible, otherwise retrieves only those same-commit shard(s), verifies byte size and SHA-256 against the admitted manifest, then executes the canonical `tools/ziwei_runtime.py` through `run_ziwei()` / `run_ziwei_transport()`; legacy `tools/ziwei_gregorian_pipeline.py` remains compatibility-only.

Ordinary requests require one year shard. The 31 December 23:00 cross-year edge may require the current year plus the next-year policy-tail shard. Calendar year shards are not packaged in the exact-main handoff artifact. The full calendar dataset and the pinned `lunar_python` implementation are not transported into ordinary ChatGPT runtime.

The assistant must produce deterministic Scope-A facts before `ZIWEI.md` interpretation. It must not silently pip-install a calendar dependency, rewrite missing shard data, hand-calculate lunar conversion, fetch a shard from a different revision, or immediately classify the runtime as unavailable while the admitted verified bundle + query-bounded data path remains available.

The assistant reports host evidence without collapsing layers: acquisition success does not imply payload handoff, materialization, integrity, or execution success. If no admissible handoff can establish exact materialization, it stops at the corresponding materialization boundary rather than reconstructing canonical runtime bytes semantically.
