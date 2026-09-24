# Zi Wei Scope-A Natal Provider Admission v0

> Current-state reconciliation (2026-09-24): this file records the earlier G1 provider admission only. G7 Scope-A production binding was subsequently admitted; `ZIWEI.md` now owns explicit Zi Wei production activation. Gregorian normalization and optional brightness are separate later admission layers, so this provider's narrower responsibilities remain unchanged.

Authority：`G1 ADMITTED — SCOPE-A NATAL / NOT G7 PRODUCTION ADMISSION`

## Runtime owner

`tools/ziwei_natal_provider.py` is the admitted deterministic G1 calculation authority for the selected Scope A; this does not grant G7 production method admission or G8 ordinary routing.

It accepts already-normalized traditional-lunar birth facts and computes only:

- year stem/branch identity from the normalized lunar year;
- Life / Body Palace branches;
- twelve natal palace roles and palace stems;
- Five-Element Bureau;
- Zi Wei start and fourteen-major-star placements;
- opposite / Sanfang topology;
- the 26 presence tokens consumed by the current first-layer retriever.

## Boundary

The provider deliberately does **not** perform Gregorian→lunisolar conversion or decide leap-month identity. Those are upstream normalization responsibilities and must carry provenance.

It also does not compute brightness, auxiliary/minor stars, Four Transformations, decadal/yearly/monthly/daily/hourly layers, or other dynamic facts.

Unsupported layers remain explicit `not_computed`; they must not be inferred from model memory.

## Profile identity

```text
provider_id       = ziwei-scope-a-natal-python
provider_version  = 0.1.0
profile_id        = ziwei.scope_a.natal_v0
research_parent   = ziwei.baseline.tw_v1
chart_mode        = tian_pan
clock             = civil
true_solar        = disabled
```

This child profile intentionally narrows the research parent to facts required by Scope A. It does not inherit unconsumed decadal, Four-Transformation, brightness, auxiliary or dynamic authority.

## Reference parity

Pinned implementation comparator:

`matharts/ziwei@596f43c43ff6fbae526314c7f668bbf346445ff1`

The implementation follows the already reconciled same-rule families for Life/Body, Five-Element Bureau, Zi Wei start and fourteen major stars. Regression fixtures use two public upstream worked charts:

- 丁卯 / lunar 5-20 / 酉: Life 酉, Body 卯, 土五局, 紫微巳;
- 辛酉 / lunar 11-7 / 丑: Life 亥, Body 丑, 木三局, 紫微午.

These fixtures validate deterministic parity; they do not grant scientific validity.

## Admission gate

G1 may move from `BLOCKED` to `ADMITTED — SCOPE-A NATAL` only after:

1. provider unit/parity tests pass in canonical CI;
2. fail-closed normalization tests pass;
3. canonical read-back confirms profile/provenance identity;
4. the merged `main` CI passes.

Even after G1 admission, G7 production binding/admission remains separate and G8 ordinary routing remains blocked.
