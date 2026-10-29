# Whole-Playbook Release Preparation Snapshot — 2026-10-29

Status: **release preparation evidence, not a version tag, Release, promotion approval, new feature admission, or runtime deployment**.

## Frozen comparison

- Repository: `masini1491/ai-divination-playbook`
- Previous whole-repository published release: `v0.3.0`, tag commit `a07343d535eaf681b8045fc98eaac130fad012cc` (2026-10-01).
- Current candidate comparison snapshot: `c02472247ee6c5a19b1001a00d5bae132c292579` (PR #421 merged). This is a **preparation snapshot**: a future release must verify and freeze its **own exact main SHA** before publication.
- GitHub compare `v0.3.0...c0247224`: **76 commits ahead / 0 behind / 107 changed paths**, as returned by GitHub compare API. This count includes changes to the Git Sync MCP and its derived/generated files; it is not a count of newly supported divination methods.
- Exact-main CI: [Validate Playbook #40843002967](https://github.com/masini1491/ai-divination-playbook/actions/runs/40843002967) — `success` with `validate` and `casting-runtime` both `success`. This supports the **tested SHA only**, not future untested commits.
- The [root README](../../README.md) and [MCP README](../../integrations/chatgpt-mcp/README.md) already distinguish their feature scope. This preparation record does not duplicate canonical method or runtime policy.

## Material changes since v0.3.0

| Area | Verified comparison/evidence | Scope qualifier |
| --- | --- | --- |
| Git Sync MCP integration | New `integrations/chatgpt-mcp/**`, `tools/build_chatgpt_mcp_release.py`, `tests/chatgpt_mcp/**`, and selective-sync workflow; PRs #410, #413, #414, #416 and #418 | Separate MCP release series; not automatic Playbook-wide method admission |
| MCP stable 1.4.1 | [`git-sync-mcp-v1.4.1`](https://github.com/masini1491/ai-divination-playbook/releases/tag/git-sync-mcp-v1.4.1), target `c93bcc1bfa6855d71a298e93cf244ff23a88a67b`; pinned engine/policy source `38898aec30668056459bb0551f77ba6e72f805d7` | Tarot, Meihua and Liuyao only; 12-item mixed batch, compact receipts, 3-item default chunk planning with request hashes |
| Free ChatGPT stochastic transport | `runtime/casting/capsule-v3/**`, `RUNTIME_DRAW.md`, runtime capsule builder and related tests; PRs #388–#401 | Verified streaming/reassembly and recovery contracts; no new stochastic algorithm/admission |
| Astrology transit | `tools/astrology_swiss_transit_provider.py`, `admissions/astrology/ASTROLOGY_SWISS_TRANSIT_PROVIDER_ADMISSION_V1.json`, provider routing and JPL-based research evidence; PRs #405–#409 | Host-native PySwissEph conditional admitted modern transit scope, actual SWIEPH/MOSEPH backend provenance, portable fallback; not global astronomical accuracy |
| Zi Wei synthesis and brightness | New evaluation `reports/ziwei/ZIWEI_BRIGHTNESS_DEFAULT_EVALUATION_V1.md`, `tests/test_ziwei_natal_synthesis_brightness_focus.py`, contextual research/admission changes | Brightness remains an explicit optional module; **not** promoted as default based on the 48-case bounded evaluation |
| Routing / verification / public documentation | `PLAYBOOK_INDEX.json`, `BEHAVIORAL_EVAL.md`, load-pack/loader checks and PR #420/#421 stable documentation | Read/release contract improvements; README is an overview, not new method authority |

## Feature boundary at candidate snapshot

| Capability | Whole Playbook | Git Sync MCP 1.4.1 |
| --- | --- | --- |
| Tarot / Meihua / Liuyao | Production-ready; ordinary routing | Supported; server auto-routing, facts, policy retrieval, mixed batches |
| Astrology natal / transit | Production, explicit request only, bounded admitted deterministic providers | **Not admitted** |
| Zi Wei natal Scope-A / selected temporal layers | Production, explicit request only, bounded admitted modules and dynamic layers | **Not admitted** |
| Tarot × Meihua, Astrology natal × Zi Wei natal baseline reconciliation | Only the named canonical pairs | **Not claimed as generalized cross-method validation** |
| Palmistry | Cold research/architecture scaffold; not production-routable | **Not admitted** |
| Private Reading Record | User-side contract only; public repository must contain no private readings | `storage=none`; no persisted readings or server-side acknowledgement |

## Known limits / publication cautions

- MCP lost full HTTP responses cannot be recovered; no exactly-once, durable idempotency or automatic safe retry. Planning request SHA-256 is **not** recovery state.
- MCP transport is `noauth` and the current `public_guard.py` rate limit is process-local, **not** a cross-instance quota. This snapshot does not authorize advertising the hosted service as unlimited public API access.
- The release of MCP `1.4.1` does not imply that Astrology, Zi Wei or Palmistry can run through the MCP.
- Horoscope / divination interpretation remains symbolic, not an evidence-based forecast or guaranteed future outcome.
- Research evidence, scripts, and evaluation cases are not the same as production admission.
- Open Draft PRs #415, #417 and #419 remain separate pending publication candidates, not changes silently included in a new whole-Playbook Release.
- A new whole-repository version name has **not** been selected. Do not prelabel the candidate `v0.4.0` or another semantic version until publication decision.
- Git Sync MCP's tagged deployment commit differs intentionally from current main and from pinned runtime source. Do not treat different SHAs as deployment failures.

## Next whole-repository release gate

1. Decide release name and the scope of public claims, separately from `git-sync-mcp-v1.4.1`.
2. Re-probe main, exact target SHA and outstanding PRs. If main has moved, review the bounded diff from this preparation snapshot and adjust this summary.
3. Require exact-target `Validate Playbook` (`validate`, `casting-runtime`) success and any additional tests necessary for actually changed domains.
4. Final-review the Release body, declared limitations, governance/privacy boundary, and any required assets; retain no private personal-reading records in the public repository.
5. Only with separate release publication authorization, create Git Tag / Release targeting the exact validated main commit; read back tag object SHA, Release target, name, published/draft/prerelease state and Latest Release semantics. Do not deploy a separate runtime or alter existing Git Sync MCP stable tags through this action.

This preparation document preserves comparison findings and release-decision inputs only. It is **not** a PASS verdict for unexecuted cross-platform tests or for a future release publication.
