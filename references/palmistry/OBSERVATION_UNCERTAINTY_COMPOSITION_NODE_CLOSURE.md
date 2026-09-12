# Palm Observation Uncertainty Composition — Bounded Node Closure

Status: **REFERENCE-ONLY / BOUNDED CONTRACT NODE CLOSED / NO PRODUCTION PROMOTION**

## Purpose

本文件在 V2 deterministic validation 完成後，關閉 Palm Observation uncertainty-composition 的窄研究節點。

Closure 只回答：

> 多層 observation uncertainty 是否能以 deterministic、fail-closed、capability-specific 方式組合，而不被單一 confidence、model presence、tradition layer 或 research metric 非法 rescue。

它不建立 production schema / threshold / routing。

## Evidence chain

本 node 的 durable evidence chain：

```text
OBSERVATION_UNCERTAINTY_COMPOSITION_DRAFT.md
→ OBSERVATION_UNCERTAINTY_COMPOSITION_VALIDATION_PLAN.md
→ observation_uncertainty_composition_validator.py
→ OBSERVATION_UNCERTAINTY_COMPOSITION_VALIDATION_RESULT_FREEZE.md
→ OBSERVATION_UNCERTAINTY_COMPOSITION_VALIDATION_V1_DISCREPANCY.md
→ OBSERVATION_UNCERTAINTY_COMPOSITION_V2_AMENDMENT.md
→ observation_uncertainty_composition_validator_v2.py
→ OBSERVATION_UNCERTAINTY_COMPOSITION_VALIDATION_V2_RESULT_FREEZE.md
→ OBSERVATION_UNCERTAINTY_COMPOSITION_VALIDATION_V2_RESULTS.md
```

V1 artifact was not erased after the post-freeze discrepancy；V2 received a new source identity and a new formal result SHA。

## V2 formal result identity

```text
formal V2 result SHA256
1d88fdec8f9cbaf34e213af5319900a4cd71a23120812578fcd1443d805bbd7f

cases_total = 12
cases_pass  = 12
cases_fail  = 0
```

Validated invariants：

```text
hard_dependency_fail_closed = true
local_scores_cannot_rescue_hard_blockers = true
tradition_layer_isolated = true
candidate_index_not_identity = true
detector_handedness_not_anatomical_authority = true
research_metrics_not_promoted_to_cutoff = true
```

## Closure decisions

### 1. Capability-specific state is authoritative

Validated cases show one record can simultaneously contain admitted、partial、insufficient、unresolved states across different observation capabilities。

Therefore：

> **Any top-level admission field may only be summary metadata. Capability-specific states remain authoritative.**

A future implementation must not reduce the record to one authoritative scalar or one global categorical pass/fail without preserving the underlying capability vector。

### 2. Hard blockers are non-rescuable

Examples validated：

```text
line_detail insufficient
+ model present
+ high local score
→ principal_line_geometry insufficient
```

and：

```text
target unresolved
→ target-specific geometry unresolved
```

Higher/local confidence cannot override a lower-layer blocker。

### 3. Model output is not observation authority

Validated distinction：

```text
model presence
!= quality sufficient
!= anatomical truth
```

and：

```text
model non-detection
!= anatomical absence
```

This remains aligned with the bounded principal-line quality study。

### 4. Tradition projection has explicit lower-layer dependency

V2 establishes a required-capability relation for tradition projection。

Conceptually：

```text
tradition projection
  source/tradition state
  + required observation capability
  → projection state
```

A source-supported rule is still blocked when its required lower-layer observation capability is insufficient or unresolved。

### 5. Higher layers cannot mutate lower layers

Tradition conflict、prohibited mapping、or unavailable color projection cannot rewrite：

- raw geometry；
- canonical geometry；
- model output；
- side / frame provenance。

Observation facts remain append-only inputs to later projection layers。

### 6. Research evidence remains provenance until calibrated

Existing detector disagreement、repeatability、quality-sensitivity metrics may be referenced, but are not automatically converted into per-observation cutoffs。

No mean / median / p95 / minimum becomes a hidden admission threshold from this node。

### 7. Candidate index / handedness remain non-authoritative

Validated：

```text
candidate list index != physical identity
MediaPipe/detector handedness metadata != anatomical-side authority
```

Capture/mirror lineage remains the required authority path for anatomical side。

## Validated amendment to the earlier draft

The earlier conceptual draft included a top-level：

```text
admission_state: admitted | partial | insufficient | unresolved
```

After V2 validation, this field must be interpreted as：

```text
summary-only convenience state
```

not the sole authoritative observation decision。

Authoritative state belongs to the requested capability, e.g.：

```text
raw_hand_geometry
canonical_hand_geometry
principal_line_presence
principal_line_geometry
fine_line_detail
surface_mark_detail
color_observation
tradition_projection
```

Likewise, tradition projection should preserve an explicit reference to its required lower-layer capability rather than assuming every projection depends on the same observation evidence。

## What this node closes

Boundedly closed：

- deterministic multi-layer fail-closed composition；
- mixed capability state representation；
- no-rescue behavior；
- reason-lineage requirement；
- tradition isolation；
- tradition required-capability dependency；
- top-level admission expressiveness question。

The top-level expressiveness question is answered：

```text
single authoritative top-level state = insufficient
summary-only top-level state = acceptable
capability-specific states = authoritative
```

## What remains open

The node does not close：

- numeric image-quality admission calibration；
- natural low-quality photo validation beyond current bounded evidence；
- MediaPipe runtime / model-version portability；
- device-to-device capture repeatability；
- selfie / camera mirroring reconciliation；
- source-specific Chinese projection geometry；
- minor-line / named-pattern detection；
- production routing / behavioral regression。

## Next dependency-central research node

After the line-detail quality node and uncertainty-composition node are boundedly closed, the next planned portability node is：

> **MediaPipe runtime / Hand-Landmarker model compatibility**

using the already predeclared `MEDIAPIPE_RUNTIME_MODEL_COMPATIBILITY_PLAN.md`。

Runtime/model compatibility remains separate from production upgrade policy；the first study must build distributions rather than thresholds。

## Boundary

Closure here means internal research-contract coherence only。

It does not establish：

- production Palmistry support；
- anatomical ground truth；
- biometric identity；
- Palmistry prediction validity；
- Chinese/Western terminology equivalence；
- production admission thresholds。

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**。
