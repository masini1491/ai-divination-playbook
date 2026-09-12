# Palm Observation Uncertainty Composition — V2 Validation Results

Status: **REFERENCE-ONLY / BOUNDED CONTRACT VALIDATION COMPLETE / NO PRODUCTION PROMOTION**

## Purpose

本文件解讀 `OBSERVATION_UNCERTAINTY_COMPOSITION_VALIDATION_PLAN.md` 的 V2 formal result。

V1 formal run 已先 freeze，但 substantive inspection 發現 Cases A / J 沒有完整覆蓋 predeclared tradition-dependency semantics；該 discrepancy 已由 `OBSERVATION_UNCERTAINTY_COMPOSITION_VALIDATION_V1_DISCREPANCY.md` 獨立記錄。

V2 amendment 與新的 formal artifact 皆在 interpretation 前重新固定。

## Frozen V2 artifact identity

Formal V2 result SHA256：

```text
1d88fdec8f9cbaf34e213af5319900a4cd71a23120812578fcd1443d805bbd7f
```

V1 lower-layer validator Git blob：

```text
fe98e29bbcf3cb3d836b4409dfb29376ab9c7a51
```

V2 amendment validator Git blob：

```text
b947d6211d6622bee74da619a8fdd7afe5961dfe
```

## Formal summary

Observed V2 summary：

```text
cases_total = 12
cases_pass  = 12
cases_fail  = 0

hard_dependency_fail_closed              = true
local_scores_cannot_rescue_hard_blockers = true
tradition_layer_isolated                  = true
candidate_index_not_identity              = true
detector_handedness_not_anatomical_authority = true
research_metrics_not_promoted_to_cutoff  = true
```

Therefore the predeclared case family passes as a bounded internal-coherence validation under the committed deterministic rules。

## Mixed capability finding

The following cases contain simultaneously different capability states：

```text
A B C D E F G I J L
```

That is 10 / 12 cases。

Formal result：

```text
authoritative_single_top_level_admission_state_sufficient = false
recommended_top_level_admission_role =
  summary-only; capability-specific states remain authoritative
```

This is the most important schema-level finding of the node。

A Palm Observation record can defensibly be, at the same time：

```text
raw geometry admitted
principal-line geometry partial / insufficient / unresolved
color insufficient
tradition projection unresolved
```

A single authoritative top-level `admission_state` cannot preserve that structure without information loss。

## Case-level contract findings

### Case A — unresolved tradition does not poison raw observation

V2 now explicitly tests：

```text
tradition requested = true
tradition mapping = unresolved
required capability = principal_line_geometry
```

Observed：

```text
raw_hand_geometry          = admitted
canonical_hand_geometry    = admitted
principal_line_presence    = admitted
principal_line_geometry    = admitted
tradition_projection       = unresolved
```

This supports one-way dependency：higher-layer tradition uncertainty does not mutate or erase lower-layer observation facts。

### Case B / G — model output cannot rescue insufficient line detail

Both insufficient-line-detail cases retain model-output evidence but produce：

```text
principal_line_presence = partial
principal_line_geometry = insufficient
fine_line_detail        = insufficient
```

The high local model score in Case G does not change that outcome。

This directly matches the earlier line-detail quality study：model class presence is not its own image-quality certificate。

### Case C — partial state remains capability-specific

With：

```text
geometry = sufficient
line_detail = partial
surface_detail = insufficient
color = insufficient
```

observed states remain split by capability rather than collapsing the entire record to fail。

This is the required partial-observation behavior。

### Case D — ambiguous target blocks target-specific facts

Observed：

```text
scene_fact               = admitted
raw_hand_geometry        = unresolved
canonical_hand_geometry  = unresolved
principal_line_geometry  = unresolved
tradition_projection     = unresolved
```

Scene facts remain recordable, but candidate index is not used as a physical-target rescue。

### Case E — frame provenance blocks canonical geometry, not all raw facts

With unresolved raw-frame / mirror lineage：

```text
raw_hand_geometry       = admitted
canonical_hand_geometry = unresolved
principal_line_geometry = unresolved
```

This preserves detector/raw evidence while refusing to promote it into canonical geometry without verified frame provenance。

### Case F — model non-detection is not anatomical absence

Under otherwise sufficient quality and frame provenance：

```text
principal_line_presence = partial
principal_line_geometry = unresolved
```

The validator does not infer：

```text
model absent → anatomical crease absent
```

### Case H — research disagreement evidence is provenance, not a cutoff

Detector-disagreement evidence is preserved, while compatibility assessment remains unresolved because no calibrated per-observation compatibility threshold exists。

Canonical geometry is not automatically failed merely because a bounded research disagreement study exists；nor is a research mean / p95 / minimum promoted into a hidden threshold。

### Case I — prohibited tradition assumption stays higher-layer only

Observed：

```text
raw_hand_geometry       = admitted
principal_line_geometry = admitted
tradition_projection    = insufficient
```

A prohibited cross-tradition mapping does not rewrite the observed line facts。

### Case J — color-dependent tradition projection now fails closed

V2 explicitly tests：

```text
color_observation = insufficient
tradition state = source_supported
required capability = color_observation
```

Observed：

```text
raw_hand_geometry       = admitted
principal_line_geometry = admitted
color_observation       = insufficient
tradition_projection    = insufficient
```

This confirms that source support alone cannot execute a projection when its lower-layer observation capability is unavailable。

### Case K — handedness metadata remains metadata

Detector handedness metadata does not become anatomical-side authority。

This preserves the repository-wide rule that capture/mirror lineage, not detector label alone, owns anatomical side。

### Case L — tradition conflict remains isolated

Raw and canonical geometry remain admitted while：

```text
tradition_projection = unresolved
```

No backward mutation of observation occurs。

## Contract decision

This node supports the following bounded contract：

1. **Capability-specific states are authoritative.**
2. Any top-level admission field may exist only as a convenience summary, not as the sole decision source。
3. Hard lower-layer blockers cannot be overridden by local/model confidence。
4. Unknown / unresolved remains explicit。
5. Tradition projection must declare and respect its required lower-layer observation capability。
6. Higher-layer interpretation/projection cannot mutate lower-layer raw facts。
7. Candidate index and detector handedness are not identity/anatomical authority。
8. Research metrics remain provenance until a separate calibration node establishes a justified threshold。

## What this node closes

Boundedly closed：

- whether the draft fail-closed dependency ordering can be represented deterministically；
- whether mixed capability states can coexist without global collapse；
- whether line-detail blockers survive high model score / presence；
- whether tradition-layer failure remains isolated；
- whether color-dependent tradition projection can be blocked independently of geometry；
- whether a single authoritative top-level admission state is expressive enough。

The final answer to the last question is：**no**。

## Still open

This result does not close：

- production numeric thresholds；
- natural low-quality image calibration；
- device-to-device capture portability；
- MediaPipe runtime/model-version compatibility；
- explicit capture/selfie mirroring reconciliation；
- source-specific Chinese projection geometry；
- minor line / named-pattern detector evidence；
- production Palmistry routing。

## Boundary

Passing the deterministic case family proves internal contract coherence only。

It does not establish：

- anatomical ground truth；
- biometric identity；
- Palmistry prediction validity；
- production safety / accuracy；
- Chinese/Western terminology equivalence。

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**。
