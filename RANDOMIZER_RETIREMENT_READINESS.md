# Randomizer Retirement Readiness

Status: **PHASE 5 READINESS PASS — PHASE 6 RETIREMENT COMPLETE**

This record captures the evidence required by `RANDOMIZER_INTEGRATION_MIGRATION.md` before the legacy repository may be converted to a compatibility/archive surface, and records the completed Phase 6 transition.

## Evidence baseline

- Playbook production baseline: `1c9093eb040173b3bbfd7cc8f50ac6342829da56`
- Phase 5 completion main: `d5fcb6b8e79c7c183838974c3469967241f3eb79`
- Legacy rollback baseline: `17cc4c84fd5c09b60de721b671c1d6511ab3d0e9`
- Legacy retirement commit: `dd55452bb9a66f5f50c129422853654a315538f5`
- Production Vercel project: `ai-divination-playbook-casting`
- Production root directory: `runtime/casting`
- Canonical stochastic implementation: `runtime/casting/randomizer.py`

## Phase 5 gate audit

1. **Canonical runtime** — PASS. `RUNTIME_DRAW.md` names `runtime/casting/randomizer.py` as canonical implementation and acquisition resolves the Playbook repository.
2. **Randomizer CI on current main** — PASS. The Phase 4 main-push run completed the Python 3.13 casting validation successfully.
3. **Playbook CI on current main** — PASS. The same main-push run completed the Python 3.12 unit suite and structural checker successfully.
4. **Vercel production source / provenance** — PASS. The production project is Git-connected to `masini1491/ai-divination-playbook` with root directory `runtime/casting`; production smoke matched `runtime_source_commit` to the Playbook deployment SHA.
5. **Tarot production smoke** — PASS.
6. **Meihua production smoke** — PASS.
7. **Liuyao production smoke** — PASS.
8. **No active legacy runtime dependency** — PASS. Repository search found the legacy repository only in migration/history/provenance/rollback/compatibility surfaces; current runtime acquisition and implementation resolve locally in the Playbook repository.
9. **Historical provenance remains readable** — PASS. `MIGRATION_SOURCE.json` retains the pinned legacy repository, commit, tree and original production-file blob identities; historical records are not rewritten.
10. **Rollback readiness** — PASS conceptually. Before retirement, rollback remained: preserve fixed Draw/Cast facts → normal Playbook revert/PR if runtime authority must change → reconnect/redeploy the pinned legacy repository if production rollback is required → preserve failure evidence. The casting API requires no project-owned secret for source provenance; Vercel supplies `VERCEL_GIT_COMMIT_SHA` at deployment time.

## Phase 6 completion

Phase 6 completed on the legacy repository with final retirement commit:

```text
masini1491/divination-casting-randomizer
dd55452bb9a66f5f50c129422853654a315538f5
```

The retirement mutation:

- replaced the legacy README with a compatibility / historical-provenance pointer to `masini1491/ai-divination-playbook` → `runtime/casting/**`;
- marked the old Vercel endpoint as compatibility/historical rather than production authority;
- removed the legacy main-push Vercel production-smoke gate;
- preserved Python/OpenAPI/unit-contract validation;
- preserved `randomizer.py`, API/OpenAPI/contract-vector bytes, Git history, logical source identity and historical commit provenance;
- did not delete the repository.

Legacy post-merge workflow run #14 passed on `dd55452bb9a66f5f50c129422853654a315538f5`.

The legacy repository is therefore retired as a **compatibility/archive surface**. Physical GitHub archive mode is optional under the migration contract and is not required for provenance preservation or completion of the repository consolidation.
