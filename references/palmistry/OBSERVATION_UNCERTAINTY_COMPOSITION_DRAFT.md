# Palm Observation Uncertainty Composition Draft

Status: **REFERENCE-ONLY / DRAFT CONTRACT / NO SINGLE CONFIDENCE SCORE**

## Purpose

本文件收斂 Palm Observation Fact 在 observation layer 應如何保存 uncertainty provenance。

目前 repository 已分別建立：

- scene / target-selection ambiguity evidence；
- task-specific image-quality schema；
- landmark / canonical-frame transform sensitivity；
- same-palm multi-session repeatability；
- detector-to-detector disagreement；
- principal-line segmentation repeatability與 bounded manual alignment。

問題是這些量並不在同一 scale，也不是同一種 probability。

因此本 draft 的核心原則是：

> **先組合 provenance 與 fail-closed state，不把異質 uncertainty 指標壓成一個偽精確的 confidence score。**

## 1. Uncertainty layers

Palm Observation Fact 至少保留以下五層 uncertainty：

### U1 — Scene / target-selection uncertainty

回答：

- 畫面中有幾個 detector candidates；
- 預期 target 是否存在；
- target selection 是否唯一；
- best-vs-second association 是否有足夠分離；
- candidate count 是否在相鄰 capture / perturbation 下 collapse / recover；
- scene-local association 是否依賴 unstable candidate list index。

不得把 MediaPipe handedness 或 candidate index 當 anatomical identity authority。

### U2 — Image-quality / observability uncertainty

按 observation capability 分開：

```text
geometry
line_detail
surface_detail
color
```

並保留直接影響 capability 的 state：

```text
focus
lighting
glare
crop
foreshortening
occlusion
surface manipulation
```

`pipeline executed successfully` 不等於 `quality sufficient`。

### U3 — Landmark / frame uncertainty

保留：

- detector ID / version；
- model artifact SHA；
- raw-image orientation / EXIF decode policy；
- mirror lineage；
- L0/L5/L17 source coordinates；
- palm width / height / axis；
- transform / inverse-transform provenance；
- cross-detector或 recapture evidence若有。

Canonical coordinates不是 uncertainty-free ground truth。

### U4 — Feature-extraction uncertainty

例如 principal-line segmentation：

- model / class mapping；
- mask / path output；
- class presence；
- perturbation repeatability；
- model-to-reference agreement evidence；
- per-observation exceptions；
- output mask digest / provenance。

`heart/head/life` class confidence 不可取代 image-quality admission evidence。

### U5 — Tradition-projection uncertainty

即使 observation fact 可 defensibly建立，傳統 projection仍可能 unresolved：

- Western tool-local class與 Chinese source term mapping；
- Bagua / palm-palace region geometry；
- named pattern source scope；
- source conflict / prohibited assumption。

此層 uncertainty 不得反向修改 raw observation。

## 2. Proposed envelope

Conceptual draft：

```yaml
observation_uncertainty:
  admission_state: admitted | partial | insufficient | unresolved

  scene_target:
    state: resolved | ambiguous | insufficient | unknown
    candidate_count: integer | unknown
    expected_target_count: integer | unknown
    association_method: string | null
    best_cost: number | null
    second_cost: number | null
    gap: number | null
    gap_unit: string | null
    candidate_index_used_as_identity: false
    reasons: []

  image_quality:
    geometry: sufficient | partial | insufficient | unknown
    line_detail: sufficient | partial | insufficient | unknown
    surface_detail: sufficient | partial | insufficient | unknown
    color: sufficient | partial | insufficient | unknown
    focus: good | partial | poor | unknown
    lighting: good | uneven | poor | unknown
    glare: none | partial | severe | unknown
    crop: complete | partial | insufficient | unknown
    reasons: []

  landmark_frame:
    detector_id: string | null
    detector_version: string | null
    model_sha256: string | null
    raw_frame_policy: string | null
    mirrored_for_model: true | false | unknown
    inverse_mapping_verified: true | false | unknown
    axis_angle_evidence: number | null
    scale_evidence: object | null
    repeatability_evidence_ref: string | null
    cross_detector_evidence_ref: string | null
    reasons: []

  feature_extraction:
    method: string | null
    method_version: string | null
    artifact_sha256: string | null
    class_or_feature: string | null
    presence: true | false | unknown
    local_score: number | null
    local_score_semantics: string | null
    perturbation_evidence_ref: string | null
    reference_agreement_ref: string | null
    reasons: []

  tradition_projection:
    state: source_supported | geometrically_similar | unresolved | conflicting | prohibited_assumption
    tradition: string | null
    source_id: string | null
    reasons: []
```

所有 key / enum 仍為 draft。

## 3. Admission semantics

### `admitted`

只代表：

> 對「目前指定的 observation capability」而言，沒有已知 hard blocker，且必要 provenance 足夠。

它不是 production pass，也不是 Palmistry interpretation validity。

### `partial`

表示某些 raw facts可保存，但較細 observation應 fail closed。

例如：

```text
geometry = sufficient
line_detail = partial
```

可以保存 palm outline / coarse principal-line presence，但不應宣稱 branch / break / island details。

### `insufficient`

表示目前 capability有明確 blocker。

例如：

```text
line_detail = insufficient
```

則 principal-line fine geometry不得 rescue，即使 segmentation model仍輸出 foreground。

### `unresolved`

表示證據互相不足以決定，而不是把 unknown硬轉成 pass / fail。

## 4. Hard fail-closed dependencies

### Target-specific observation

若：

```text
scene.target_selection_state = ambiguous
```

則：

```text
target-specific geometry = unresolved / insufficient
tradition projection = blocked
```

### Canonical geometry

若：

- raw-frame orientation未確定；
- detector-only mirror未能 inverse；
- target candidate unresolved；

則 canonical coordinates不得標成 admitted。

### Principal-line observation

若：

```text
quality.line_detail = insufficient
```

則 principal-line observation fail closed。

模型 presence / high local score不得 override這個 gate。

### Fine branch / break / minor mark observation

必須比 coarse major-line presence需要更高 line-detail / surface-detail evidence；major-line model的 bounded success不可外推。

### Color observation

若：

```text
quality.color != sufficient
or color_reliable != true
```

則任何 source-specific掌色 projection blocked。

## 5. Why there is no scalar composition formula yet

目前已知 evidence的 units / semantics不同：

```text
candidate association gap          → geometry cost separation
anchor drift                       → normalized spatial distance
axis difference                    → degrees
width/height disagreement          → relative scale difference
line-mask Dice / harmonic coverage → segmentation overlap
image blur / gradient descriptors  → image-content statistics
model local confidence             → model-specific score
```

這些不能合法地直接：

```text
weighted average → overall confidence = 0.83
```

原因：

1. 無共同 calibration target；
2. 無證據支持線性可加；
3. 不同層有 hard dependency，而不是 soft penalty；
4. 某些 metric只是 descriptive research evidence，沒有 per-observation probability semantics；
5. scalarization會隱藏「哪一層出問題」。

因此本 draft只允許 structured state + evidence references。

## 6. Local score semantics

Schema 中若保存 `confidence` / `score`，必須附上它是什麼：

```yaml
local_score: 0.91
local_score_semantics: "RTMPose keypoint mean score"
```

不得只保存：

```yaml
confidence: 0.91
```

而不說 source / calibration / meaning。

不同 model score禁止直接比較或平均。

## 7. Evidence references over copied thresholds

Palm Observation Fact 可以引用 bounded evidence family：

```text
MOHI multi-session repeatability
MediaPipe↔RTMPose detector agreement
GTEA candidate-retention studies
principal-line segmentation repeatability
blind manual principal-line audit
future line-detail quality study
```

但不應把 research p95 / mean / minimum直接複製成 production cutoff。

Research evidence的作用是解釋 uncertainty provenance，不是自動 admission threshold。

## 8. Proposed observation-fact behavior

Example A — clean single palm, major lines only：

```yaml
admission_state: admitted
scene_target.state: resolved
image_quality.geometry: sufficient
image_quality.line_detail: sufficient
landmark_frame.inverse_mapping_verified: true
feature_extraction.class_or_feature: principal-lines
tradition_projection.state: unresolved
```

Raw major-line geometry可保存；Chinese mapping仍 blocked。

Example B — blurry palm similar to the P001 caveat：

```yaml
admission_state: partial
scene_target.state: resolved
image_quality.geometry: sufficient
image_quality.line_detail: partial
feature_extraction.presence: true
feature_extraction.reasons:
  - "model output exists but line-detail observability is degraded"
```

這種 case不能因 model輸出三類就自動提升成 reliable fine line fact。

Example C — two visible hands but one candidate retained：

```yaml
admission_state: unresolved
scene_target.state: insufficient
scene_target.candidate_count: 1
scene_target.expected_target_count: 2
```

不得猜哪個 candidate是指定 target的唯一可信 geometry。

## 9. Relationship to existing schema

`OBSERVATION_SCHEMA_DRAFT.md`目前已有：

- scene target state；
- task-specific quality fields；
- geometry / line facts；
- tradition projection state；
- provenance。

本 draft不取代它，而是補足「這些層如何共同決定 observation admission，以及 uncertainty怎麼保存」的 contract。

未來若要 merge進 schema，應新增 structured `observation_uncertainty` / `admission_state`，而不是新增一個 global confidence number。

## 10. Validation requirements before any promotion

至少仍需：

1. line-detail quality study；
2. runtime/model compatibility evidence；
3. controlled device-to-device repeatability；
4. mirroring / anatomical-side capture contract validation；
5. executable examples proving hard fail-closed dependencies；
6. behavioral regression only after a real promotion candidate exists。

## Boundary

本 draft不建立：

- production admission score；
- production threshold；
- biometric identity confidence；
- medical/anatomical truth；
- Palmistry fortune validity；
- Chinese terminology equivalence；
- production routing。

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**。
