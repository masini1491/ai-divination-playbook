# Randomizer Integration Migration Contract

Status: **PHASES 0–6 COMPLETE / REPOSITORY CONSOLIDATION COMPLETE**

This document defines the staged migration contract for consolidating `masini1491/divination-casting-randomizer` into `masini1491/ai-divination-playbook` without changing stochastic semantics, breaking provenance, or coupling migration to premature retirement of the legacy repository.

Current stochastic runtime and production deployment authority are both in `masini1491/ai-divination-playbook`: runtime authority is `RUNTIME_DRAW.md` + `runtime/casting/randomizer.py`, and Vercel production is sourced from this repository with root directory `runtime/casting`. Phase 6 converted the legacy repository to a compatibility / historical-provenance surface at `dd55452bb9a66f5f50c129422853654a315538f5`; it is no longer a current runtime or production authority.

## 1. Baseline and scope

Design baselines at admission time:

```text
ai-divination-playbook/main
57dbf0e9bdd91132c20ce238864dca949fd02fe3

divination-casting-randomizer/main
17cc4c84fd5c09b60de721b671c1d6511ab3d0e9
```

These SHAs are provenance for this design, not permanent moving-ref substitutes. Every implementation phase must fresh-check both repositories before mutation. If the Randomizer source changes materially, migration pauses until the new baseline is reconciled.

In scope:

- canonical stochastic core for Tarot / Meihua / Liuyao Raw Cast;
- Python import/CLI surface;
- compact AI transport;
- Web UI;
- `/api/cast` HTTP adapter;
- OpenAPI contract;
- shared contract vectors;
- Randomizer unit / API / HTTP / parity tests;
- GitHub Actions validation and production smoke behavior;
- `RUNTIME_DRAW.md` cache/acquisition/provenance migration;
- Playbook references to the external Randomizer repository;
- Vercel source-repository/root-directory cutover;
- legacy repository retirement after evidence gates pass.

Out of scope for the relocation phase:

- changing Tarot deck semantics;
- changing Meihua A/B formulas;
- changing Liuyao three-coin mapping or line order;
- changing RNG algorithm;
- adding new casting methods;
- changing method routing;
- changing interpretation semantics;
- moving Liuyao or Astrology deterministic engines merely for symmetry;
- deleting or archiving the legacy repository before cutover evidence exists.

## 2. Architectural decision

Long-term canonical topology should be one repository with separate authority boundaries:

```text
ai-divination-playbook
├─ method / interpretation governance
├─ stochastic casting runtime
│  ├─ Tarot Draw
│  ├─ Meihua A/B Cast
│  └─ Liuyao three-coin Raw Cast
├─ deterministic runtimes
│  ├─ Liuyao
│  └─ Astrology
├─ transport adapters / API / Web UI
├─ validation
└─ research
```

Repository consolidation does **not** collapse responsibility boundaries:

```text
stochastic Draw / Cast authority
≠ deterministic method-fact authority
≠ interpretation authority
```

Target stochastic package root:

```text
runtime/casting/
```

Planned shape:

```text
runtime/casting/
├─ randomizer.py
├─ API.md
├─ openapi.json
├─ contract_vectors.json
├─ index.html
└─ api/
   └─ cast.py

tests/casting/
├─ test_randomizer.py
├─ test_api.py
├─ test_api_http.py
└─ test_contract_vectors.py
```

Exact test filenames may be normalized during implementation only when imports/discovery require it. Source semantics must remain unchanged during the relocation phase.

## 3. Canonical identity and version semantics

Pure relocation must not pretend to be an algorithm revision.

During the first authority cutover:

```text
source = divination-casting-randomizer-python
algorithm_version = 2
schema_version = 4
ai_schema_version = 1
```

remain unchanged unless independent evidence requires a real contract-version change.

The existing source string is a logical runtime identity, not a promise that the implementation permanently lives in a repository of the same name.

`runtime_source_commit` remains the commit that contains the executed canonical source. After cutover, that means an `ai-divination-playbook` commit SHA.

Historical records that point to commits in `divination-casting-randomizer` remain valid and must not be rewritten.

Future durable provenance should distinguish repository/path when the Reading Record contract is next revised, but that enhancement must not be smuggled into the relocation as an unnecessary schema change.

## 4. Migration invariants

Every phase must preserve these invariants:

### Tarot

- 78 unique cards;
- 1..24 cards per reading;
- fresh full-deck shuffle per question identity;
- no duplicate card within one reading;
- independent orientation per card.

### Meihua

- A/B each `000..999`;
- `A % 8` → upper trigram;
- `B % 8` → lower trigram;
- `(A+B) % 6` → moving line;
- remainder 0 rules remain unchanged;
- 64-hexagram mapping remains exact.

### Liuyao Raw Cast

- exactly six lines;
- bottom-to-top order;
- three independent fair binary coins per line;
- yin=2 / yang=3;
- 6/7/8/9 mapping unchanged;
- 6/9 changing, 7/8 static;
- Randomizer still does not own Najia / six-relations / shi-ying / six spirits / interpretation.

### Transport

- full JSON and compact AI projection preserve stochastic fact parity;
- HTTP API accepts only admitted fields/methods;
- request size / repeat bounds remain enforced unless separately versioned;
- responses remain `no-store`;
- API still receives no reading context or personal question text.

## 5. Phase plan

### Phase 0 — Design admission

Goal: freeze migration semantics before implementation.

Required evidence:

- current Playbook main fresh-checked;
- current Randomizer main fresh-checked;
- this contract merged;
- no runtime authority changes.

Exit condition:

```text
migration design admitted
current external Randomizer remains canonical
```

### Phase 1 — Import snapshot, no authority cutover

Copy the exact admitted Randomizer implementation surface into the target paths under `runtime/casting/` and `tests/casting/`.

Rules:

- start from a fresh immutable Randomizer SHA;
- record source file/blob identities in the PR description or execution report;
- minimize edits needed only for package/test path resolution;
- no stochastic behavior changes;
- do not update `RUNTIME_DRAW.md` canonical source yet;
- do not change Vercel project source yet;
- legacy repository remains writable/canonical until the migration branch proves parity.

Required validation:

- imported unit tests pass from the monorepo;
- Playbook tests pass;
- structural checker passes;
- exact known contract vectors pass;
- direct Python API and CLI shapes match the source baseline.

### Phase 2 — Dual-source parity and integrated CI

Goal: prove the imported implementation is behaviorally equivalent before it becomes canonical.

Add monorepo CI coverage for:

```text
Playbook unit tests
+ structural checker
+ Randomizer unit tests
+ API validation tests
+ HTTP adapter tests
+ contract-vector parity
```

For deterministic fixtures / contract vectors, outputs must be exact where exact parity is defined. For fresh RNG outputs, validate invariant/schema equivalence rather than expecting identical stochastic results.

No production source cutover yet.

Exit condition:

```text
monorepo runtime surface passes all local/CI parity gates
```

### Phase 3 — Runtime authority cutover

Only after Phase 2 passes, update current-owner references in one bounded migration:

- `AGENTS.md`;
- `CHAT_INIT.md` where repository acquisition examples are current-runtime-specific;
- `RUNTIME_DRAW.md`;
- `PLAYBOOK_INDEX.json`;
- `BEHAVIORAL_EVAL.md`;
- `INPUT_CONTRACT.md` only where the source label/path is normative;
- `MEIHUA.md` / `LIUYAO.md` only where the current canonical source path is named;
- `READING_RECORD.md` only as needed to accept new-source provenance without rewriting history;
- README;
- current, non-historical reference text that materially asserts the old repository as canonical.

The new canonical runtime path becomes:

```text
runtime/casting/randomizer.py
```

`RUNTIME_DRAW.md` cache acquisition changes from cross-repository acquisition to current-repository acquisition. Cache verification must still pin the exact source commit and content hash.

If cache marker shape changes, increment the cache-locator/marker version independently from Randomizer algorithm/schema versions.

Historical documentation, old Reading Records and execution reports must retain old repository identities when they describe past facts.

Exit condition:

```text
Playbook current authority points to local stochastic runtime
legacy repository remains available as rollback source
```

### Phase 4 — Vercel production cutover

This is an external deployment mutation and requires explicit execution authorization at that time.

Preferred target:

```text
Vercel project source repository:
masini1491/ai-divination-playbook

Root directory:
runtime/casting
```

The existing public URL may remain unchanged if the Vercel project is reconnected rather than replaced.

Production smoke must prove:

- deployed `/api/cast` returns HTTP 200 for valid request;
- `Cache-Control` includes `no-store`;
- compact AI schema remains admitted;
- response contains the expected number of stochastic facts;
- `runtime_source_commit` equals the monorepo deployment commit SHA;
- Tarot / Meihua / Liuyao each pass at least one production contract smoke;
- invalid/unknown input remains rejected.

Do not archive the legacy repository during this phase.

### Phase 5 — Retirement readiness

Legacy repository can be retired only when all are true:

1. monorepo stochastic runtime is canonical in `RUNTIME_DRAW.md`;
2. monorepo Randomizer CI passes on current main;
3. Playbook CI passes on current main;
4. Vercel production is sourced from the monorepo and commit provenance matches;
5. Tarot production smoke passes;
6. Meihua production smoke passes;
7. Liuyao production smoke passes;
8. repository search finds no active current-runtime dependency on `masini1491/divination-casting-randomizer` except migration/history/compatibility references;
9. historical provenance remains readable without rewriting old records;
10. rollback procedure has been tested conceptually and no required secret/config would be lost by retirement.

Evidence record: `RANDOMIZER_RETIREMENT_READINESS.md`.

Only then may the old repository be converted to a compatibility/archive surface.

### Phase 6 — Legacy repository retirement

Retirement means:

- no new feature development in the old repository;
- README clearly points to the new canonical source path;
- repository may be archived after the final pointer commit;
- existing Git history remains available for historical `runtime_source_commit` provenance;
- existing public URLs are preserved where practical;
- do not delete the repository merely to reduce repository count.

Completed evidence:

```text
legacy repository final compatibility-surface commit:
dd55452bb9a66f5f50c129422853654a315538f5
```

That commit replaced the README with the canonical Playbook pointer, removed the legacy main-push production-authority smoke, preserved unit/contract validation and historical Git provenance, and passed legacy main-push workflow run #14. Physical GitHub archive mode remains optional; the repository is retired by policy and surface ownership regardless of the archive UI flag.

## 6. Source-freeze and drift rule

Migration should not race active Randomizer feature work.

Once Phase 1 starts from an immutable source SHA:

```text
material Randomizer change on legacy main
→ STOP migration
→ compare against pinned source SHA
→ either rebase migration baseline intentionally
   or complete/reject the source change first
→ rerun parity
```

Do not dual-write the same feature independently into both repositories.

Preferred transition rule:

```text
before authority cutover:
legacy repo = canonical feature source
monorepo copy = migration candidate

after authority cutover:
monorepo = canonical feature source
legacy repo = compatibility / rollback only
```

## 7. CI contract

The final monorepo must retain both validation classes rather than silently replacing one with the other.

Current Playbook validation class:

```text
Python 3.12
→ Playbook unit tests
→ structural checker
```

Current Randomizer validation classes:

```text
general validation.yml
→ Python 3.13
→ OpenAPI JSON validation
→ unit + contract tests

casting-production-smoke.yml
→ main push only
→ paths: runtime/casting/**
→ Vercel production smoke
```

Current monorepo deployment semantics are path-bounded at both deployment and online-smoke layers. Vercel may skip a Git deployment when `runtime/casting/**` is unchanged, and the live production smoke workflow is triggered only when `runtime/casting/**` changes on `main`. The smoke still validates that the deployed `runtime_source_commit` is an ancestor of current main and that its `runtime/casting` Git tree exactly matches current main. Exact equality with the monorepo HEAD is required only when that HEAD is the deployed casting-source commit; unrelated Astrology/docs/governance commits neither force a redundant casting deployment nor inherit live Vercel availability as a general validation gate.

Migration may normalize Python versions later only as a separately evidenced compatibility decision. Version normalization is not required to prove repository consolidation.

The final GitHub Actions topology may use one workflow or multiple workflows, but failure visibility must remain distinct enough to identify:

```text
Playbook governance failure
Randomizer contract failure
deployment smoke failure
```

## 8. Provenance contract

### Historical results

No rewrite:

```text
repository: masini1491/divination-casting-randomizer
source_commit: <legacy SHA>
```

remains a valid historical fact when originally recorded.

### Post-cutover results

The executed source commit becomes the `ai-divination-playbook` SHA that contains `runtime/casting/randomizer.py`.

At minimum, runtime/cache/audit context must be able to reconstruct:

```text
logical source identity
exact commit SHA
exact source path
algorithm version
schema version
actual draw/cast timestamp
```

A future Reading Record schema may add explicit repository/path fields, but old records remain append-only and compatible.

## 9. Rollback contract

Before legacy retirement, rollback remains intentionally cheap.

If monorepo runtime authority or Vercel cutover fails:

1. do not regenerate or overwrite already-fixed Draw/Cast facts;
2. revert current-runtime authority through a normal PR/commit, never force-update main;
3. reconnect/redeploy the last known-good legacy Randomizer source if production API rollback is required;
4. preserve failed migration evidence for diagnosis;
5. fix forward or restart from a new pinned baseline;
6. do not archive/delete the legacy repository until rollback is no longer materially dependent on it.

A rollback changes future execution source; it does not invalidate prior results whose provenance is already fixed.

## 10. Stop conditions

Stop and reassess if any of these occur:

- algorithm/schema behavior differs unexpectedly after relocation;
- contract vectors fail;
- source commit provenance cannot be traced unambiguously;
- Vercel cannot deploy the subdirectory without changing public contract unexpectedly;
- current Playbook structural/runtime tests regress;
- Randomizer main materially changes during migration without reconciliation;
- migration requires a method-routing or interpretation-policy change to succeed;
- external deployment/config mutation lacks explicit authorization.

## 11. Completion definition

Repository consolidation is complete because all of the following are true:

```text
stochastic runtime canonical in ai-divination-playbook
+ imported tests/contracts canonical there
+ current Playbook references local runtime
+ Vercel production sourced from monorepo
+ runtime_source_commit proves monorepo deployment SHA
+ Tarot/Meihua/Liuyao production smoke PASS
+ old repo no longer required for current execution
+ historical old-repo provenance still resolvable
+ legacy repo converted to compatibility/archive surface
```

The Randomizer repository consolidation is complete. Future Randomizer feature development belongs in `masini1491/ai-divination-playbook` under `runtime/casting/**` and `tests/casting/**`; the legacy repository remains only for compatibility, rollback evidence and historical provenance.
