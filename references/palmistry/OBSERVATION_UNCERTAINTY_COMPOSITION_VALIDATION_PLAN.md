# Palm Observation Uncertainty Composition — Validation Plan

Status: **REFERENCE-ONLY / PREDECLARED CONTRACT VALIDATION PLAN / NO PRODUCTION PROMOTION**

## Purpose

本文件凍結 `OBSERVATION_UNCERTAINTY_COMPOSITION_DRAFT.md` 的下一個 bounded validation node。

目標不是建立一個更漂亮的 confidence number，而是驗證：

> Palm Observation Fact 是否能在 scene/target、image quality、landmark/frame、feature extraction、tradition projection 五層 uncertainty 同時存在時，仍保持 provenance、capability-specific fail-closed 行為與不可互相 rescue 的 dependency contract。

此 node 不做 Palmistry reading，也不建立 production routing / threshold。

## Why this node is next

目前已具備足夠分層 evidence：

- scene / target-selection ambiguity；
- task-specific image-quality schema；
- first bounded line-detail quality-sensitivity result；
- landmark / canonical-frame transform sensitivity；
- same-palm multi-session repeatability；
- detector-to-detector disagreement；
- principal-line segmentation repeatability；
- blind manual principal-line alignment；
- tradition-mapping boundary。

`LINE_DETAIL_QUALITY_GATE_RESULTS.md` 又直接支持：

```text
model output present
!= image quality sufficient
!= observation fact automatically admissible
```

因此目前 bottleneck 已從「某一層 evidence 是否存在」轉成「多層 uncertainty 如何組合而不失真」。

## Source contracts under test

Primary documents：

```text
OBSERVATION_SCHEMA_DRAFT.md
OBSERVATION_UNCERTAINTY_COMPOSITION_DRAFT.md
NORMALIZATION_CONTRACT_DRAFT.md
LINE_DETAIL_QUALITY_GATE_RESULTS.md
DETECTOR_AGREEMENT_RESULTS.md
MOHI_REPEATABILITY_RESULTS.md
GTEA_SEQUENCE_HELDOUT_RESULTS.md
GTEA_NATURAL_NEARTIE_SCREEN.md
```

Tradition boundary参考：

```text
CHINESE_RULE_NORMALIZATION.md
```

Validation must not silently modify these source contracts while evaluating cases. If a case exposes an inconsistency, record it as a failed/insufficient contract state first; amendment comes afterward in a separate branch.

## Validation unit

本研究的 validation unit 不是一張真實照片，而是一個 **structured observation state case**。

Each case specifies：

```text
scene_target state
image_quality capability states
landmark/frame provenance state
feature-extraction state
tradition-projection state
requested observation capability
expected admissibility / block behavior
expected reason lineage
```

No synthetic numeric confidence is required.

## Frozen capability set

第一輪只驗證以下 observation capabilities：

```text
scene_fact
raw_hand_geometry
canonical_hand_geometry
principal_line_presence
principal_line_geometry
fine_line_detail
surface_mark_detail
color_observation
tradition_projection
```

這些 capability 不是 production API；只是 contract-validation vocabulary。

## Frozen state vocabulary

Where applicable：

```text
admitted
partial
insufficient
unresolved
not_applicable
```

Important：

- `unresolved` means evidence is insufficient to choose a defensible state；
- `insufficient` means a known blocker exists；
- `partial` means some bounded facts remain admissible while finer facts fail closed；
- `admitted` only means the requested observation capability has no known blocker under the current research contract；
- none of these states imply Palmistry interpretation validity。

## Composition principles to validate

### 1. Hard blockers outrank soft/local scores

Examples：

```text
line_detail = insufficient
+ segmentation present = true
+ local score high
→ principal_line_geometry must not be rescued
```

### 2. Lower layers cannot be repaired by higher layers

Examples：

```text
raw frame orientation unresolved
+ plausible principal-line mask
→ canonical geometry remains unresolved
```

and：

```text
tradition mapping unresolved
+ strong raw geometry
→ tradition projection remains unresolved
```

### 3. Higher-layer failure must not erase lower-layer facts

Example：

```text
tradition projection = prohibited_assumption
```

must not mutate or delete otherwise defensible raw geometry facts。

### 4. Capability-specific state outranks a global summary

A single image may simultaneously support：

```text
raw_hand_geometry = admitted
principal_line_presence = admitted
principal_line_geometry = partial
fine_line_detail = insufficient
color_observation = insufficient
tradition_projection = unresolved
```

If the current draft's top-level `admission_state` cannot express this without ambiguity, that is a contract finding rather than something to hide with a scalar score。

### 5. Unknown stays unknown

No case may infer：

```text
unknown → sufficient
unknown → anatomical side
unknown → source-supported mapping
```

without explicit evidence。

### 6. Provenance must explain the state

A blocked or partial capability must retain reason lineage indicating which uncertainty layer caused the state。

## Predeclared validation cases

### Case A — Clean single-palm, bounded principal-line observation

Input state：

```text
scene target resolved
geometry quality sufficient
line_detail sufficient
raw frame policy known
mirror lineage reconciled
inverse mapping verified
principal-line feature extraction present
tradition mapping unresolved
```

Expected：

```text
scene_fact = admitted
raw_hand_geometry = admitted
canonical_hand_geometry = admitted
principal_line_presence = admitted
principal_line_geometry = admitted or bounded-admitted under current draft semantics
tradition_projection = unresolved
```

Raw observation must remain usable even though tradition projection is unresolved。

### Case B — Line detail insufficient but model output present

Input state：

```text
scene resolved
geometry sufficient
line_detail insufficient
segmentation presence = true
local model score = high / model-specific
```

Expected：

```text
raw_hand_geometry may remain admitted
principal_line_presence may be recorded as model-output fact
principal_line_geometry = insufficient
fine_line_detail = insufficient
```

Model presence / local score may not rescue line-detail admission。

This case is directly motivated by the bounded quality-sensitivity result where degraded contrast can preserve class presence while spatial agreement worsens。

### Case C — Geometry sufficient, line detail partial

Input state：

```text
scene resolved
geometry sufficient
line_detail partial
surface_detail insufficient
color insufficient
```

Expected：

```text
raw_hand_geometry = admitted
coarse principal-line presence = partial/admitted depending explicit requested granularity
fine_line_detail = insufficient or partial according frozen capability definition
surface_mark_detail = insufficient
color_observation = insufficient
```

The contract must not collapse all capabilities to one image-level fail state。

### Case D — Ambiguous target in multi-hand scene

Input state：

```text
multiple visible hands expected
retained detector candidates insufficient to resolve requested target
candidate index available but not identity-safe
image quality otherwise sufficient
```

Expected：

```text
scene_fact may record candidate facts
target-specific raw geometry = unresolved/insufficient
canonical_hand_geometry = unresolved/insufficient
tradition_projection = blocked
```

Candidate list index must not be used as identity rescue。

### Case E — Raw orientation / mirror lineage unresolved

Input state：

```text
target resolved
landmarks present
raw-frame orientation uncertain or detector-only mirror cannot be inversed
```

Expected：

```text
scene facts may remain admitted
raw detector output may be preserved with provenance
canonical_hand_geometry = unresolved
anatomical-side dependent claims = unresolved
```

Plausible-looking canonical coordinates must not override frame provenance failure。

### Case F — Feature extraction absent under otherwise sufficient quality

Input state：

```text
scene resolved
line_detail sufficient
canonical frame valid
principal-line model class absent
```

Expected：

```text
feature_extraction.presence = false
```

The contract may record model non-detection, but must not automatically promote it to：

```text
"the anatomical crease does not exist"
```

unless a separate observation authority supports that claim。

### Case G — High local model score with hard image-quality blocker

Input state：

```text
line_detail insufficient
model local score high
model presence true
```

Expected：

```text
principal_line_geometry remains insufficient
```

`local_score` must preserve source semantics and cannot act as a universal override。

### Case H — Detector disagreement evidence exists but no production cutoff

Input state：

```text
canonical geometry derived
cross-detector disagreement evidence reference present
no calibrated per-observation compatibility threshold
```

Expected：

```text
evidence reference preserved
no automatic numeric fail/pass derived solely from research mean/p95/min
```

If current evidence is insufficient to classify the specific observation, state must remain `unresolved` rather than inventing a cutoff。

### Case I — Tradition mapping prohibited assumption

Input state：

```text
Western tool-local heart/head/life geometry available
requested Chinese 天/人/地紋 projection
no source-supported equivalence record
```

Expected：

```text
raw line facts remain unchanged
tradition_projection.state = prohibited_assumption or unresolved per source contract
interpretation blocked
```

No automatic label substitution is allowed。

### Case J — Color unreliable while geometry remains good

Input state：

```text
geometry sufficient
line_detail sufficient
color insufficient or color_reliable = false
```

Expected：

```text
geometry capabilities may remain admitted
principal-line capabilities may remain admitted
color_observation = insufficient
source-specific palm-color projection = blocked
```

### Case K — Handedness metadata conflicts with anatomical-side evidence

Input state：

```text
detector handedness metadata present
capture/mirror lineage indicates metadata is not anatomical authority
```

Expected：

```text
detector handedness retained as metadata
anatomical side not overwritten by detector label
```

### Case L — Tradition projection failure must not contaminate observation

Input state：

```text
raw geometry defensible
tradition source conflict present
```

Expected：

```text
raw observation remains stable
tradition projection = conflicting/unresolved
```

No backward mutation of raw path, class, side, or coordinate values。

## Negative tests

The validation must explicitly reject these compositions：

```text
average(association_gap, blur_score, mask_dice, detector_score)
→ global confidence
```

```text
model_present = true
→ line_detail sufficient
```

```text
MediaPipe handedness = Left
→ anatomical_side = left
```

```text
heart_line
→ 天紋
```

```text
unknown mirror state
→ assume non-mirrored
```

```text
candidate index 0
→ same physical target across frames
```

## Required output of validation

For each case record：

```text
input structured state
requested capability
expected state
computed/derived state
blocking layer(s)
reason lineage
illegal rescue attempted? yes/no
raw facts mutated by higher layer? yes/no
contract result = pass/fail/ambiguous
```

The result must separately summarize：

- hard-dependency pass/fail；
- capability-specific expressiveness；
- unknown preservation；
- provenance completeness；
- no-rescue behavior；
- tradition-layer isolation；
- whether top-level `admission_state` is expressive enough as authoritative state or should become summary-only。

## Contract failure handling

If a predeclared case cannot be represented without contradiction：

1. record `contract result = fail/ambiguous`；
2. do not alter expected outcome after seeing the failure；
3. freeze validation result；
4. only then open a separate amendment branch for the schema/draft。

No case may be deleted because it exposes an awkward contract boundary。

## No numeric threshold calibration

This node does not calibrate：

```text
Laplacian cutoff
Tenengrad cutoff
mask Dice cutoff
detector disagreement cutoff
association-gap cutoff
global confidence cutoff
```

Research metrics may be referenced as provenance, but not converted into production boundaries。

## Execution strategy

Preferred implementation is a small deterministic reference validator with declarative case fixtures and no external CV model dependency。

The validator should：

1. parse each frozen structured case；
2. apply explicit dependency rules only；
3. emit capability-specific states + reason lineage；
4. compare output against predeclared expectations；
5. fail loudly on unknown rule, contradictory state, illegal rescue, or higher-layer mutation；
6. produce a deterministic JSON artifact that can be SHA256-frozen before interpretation。

Because no image/model inference is required, this validation should be runnable in ordinary repository CI or a minimal local Python environment once implemented。

## Success criteria

This bounded node succeeds if：

- all predeclared hard blockers behave fail-closed；
- capability-specific partial states are representable without global collapse；
- unknown remains explicit；
- local/model scores cannot rescue hard blockers；
- tradition projection cannot modify raw observation；
- no cross-unit scalar confidence is synthesized；
- every blocked/partial state carries reason lineage；
- any schema ambiguity is surfaced rather than silently normalized away。

A validation failure may still be a useful research result if it identifies a schema contract that needs amendment。

## Evidence boundary

Passing this node would support only：

> the draft uncertainty-composition rules are internally coherent across the frozen case family and can be executed deterministically without illegal rescue or provenance loss.

It would not establish：

- production admission policy；
- calibrated thresholds；
- anatomical truth；
- biometric identity；
- Palmistry prediction validity；
- Chinese/Western terminology equivalence；
- runtime/model portability。

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**。
