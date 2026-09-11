# Palm Observation Fact Schema Draft｜手相觀察事實草案

Status: **REFERENCE-ONLY / DRAFT｜僅供參考／草案**

Reviewed target baseline: `masini1491/ai-divination-playbook@8621f095cf68366cf67cc0e6b7e10b3e076fd0e4`

本 schema draft 只定義「從手掌影像可合理保存哪些 observation facts」與 tradition projection boundary。它不是 production schema，也不代表目前 Playbook 已正式支援 Palmistry。

## 1. Design goals

Palm Observation Fact 必須做到：

1. image observation 與 traditional interpretation 分離；
2. source-neutral geometry 先於 source-local terminology；
3. unknown / not-observable 能被明確表示；
4. 中國與 Western tradition 可以對同一組 raw facts 做不同 projection；
5. 不要求 CV model 一次判斷所有傳統術語；
6. 不讓 LLM 因 interpretation 需要而補畫不存在的 feature。

## 2. Proposed envelope

```yaml
schema_version: palm-observation-draft-v1
status: draft
image:
  hand_side: left | right | unknown
  view: palm | dorsal | oblique | unknown
  orientation_normalized: true | false | unknown
  quality:
    overall: sufficient | partial | insufficient
    focus: good | partial | poor | unknown
    lighting: good | uneven | poor | unknown
    glare: none | partial | severe | unknown
    occlusion: none | partial | severe | unknown
    crop: complete | partial | insufficient | unknown
    color_reliable: true | false | unknown

geometry:
  palm:
    width: normalized-number | unknown
    length: normalized-number | unknown
    aspect_ratio: number | unknown
  fingers:
    visible: true | false | partial
    proportions: []
  lines:
    - id: line-001
      anatomical_scope: palm
      geometry_class: major-crease | minor-crease | mark | unknown
      path_normalized: []
      length_normalized: number | unknown
      orientation: horizontal | vertical | diagonal | curved | mixed | unknown
      continuity: continuous | broken | fragmented | uncertain
      depth_or_contrast: strong | medium | weak | unknown
      branches: []
      intersections: []
      endpoints: []
      touches_boundary: true | false | unknown
      confidence: 0.0-1.0 | null

traditional_projections:
  - tradition: chinese-xiangshu
    source_id: SXQ-640 | TQ-V5 | TGKD | other
    source_section: string
    anatomical_scope: string
    source_term: string
    mapped_line_ids: []
    mapping_state: UNREVIEWED | GEOMETRICALLY_SIMILAR | SOURCE-SUPPORTED_EQUIVALENCE | CONFLICTING | PROHIBITED_ASSUMPTION
    mapping_confidence: 0.0-1.0 | null
    interpretation_allowed: false

provenance:
  observer: human | vision-model | cv-model | hybrid
  model_or_tool: string | null
  source_image_identity: string | null
  notes: []
```

所有 enum / key 都是 draft；正式化前仍需 behavioral / implementation validation。

## 3. Image Quality Gate

只有 `quality.overall == sufficient` 才能嘗試完整 palm-line observation。

`partial` 時只輸出可見 feature；`insufficient` 時 fail closed，不做傳統 interpretation。

### Minimum checks

至少要能回答：

- 掌面是否朝鏡頭；
- 左右手能否可靠辨認；
- 掌心與主要指根是否完整；
- 是否嚴重過曝、反光、陰影；
- 主要 crease 是否在有效解析度內；
- 是否有手指、物件、飾品遮擋；
- 影像顏色是否足以做 color observation。

若 `color_reliable == false`，任何來源中的掌色 rule 都不得啟用。

## 4. Source-neutral coordinates

所有 line / mark geometry 優先使用掌面 normalization 後座標，而不是直接以 pixel 值當 semantic position。

概念流程：

```text
hand landmarks
→ palm ROI / orientation normalization
→ normalized palm coordinate system
→ observed crease / mark geometry
→ optional tradition-specific region projection
```

這樣：

- CV layer 不需要知道巽／離／坤等 interpretation；
- tradition adapter 才把 source-defined region 投影到 normalized coordinates；
- 不同 source 若宮位定義不同，可各自有 projection，不覆寫 raw fact。

## 5. Major-line identification state

若使用 Western CV model，heart / head / life label 只能先存成 tool-local classification：

```yaml
tool_classification:
  model_family: western-principal-line
  label: heart | head | life
```

不能直接轉成：

```yaml
source_term: 天紋 | 人紋 | 地紋
```

同理，中國 source-local 三紋 mapping 不會反過來修改原始 segmentation label。

## 6. Observable feature vocabulary

第一版 raw vocabulary 可包含：

### Line geometry

- length
- orientation
- curvature / tortuosity
- normalized start / end region
- continuity / break count
- branch count / branch direction
- intersection count
- parallel relation
- boundary crossing
- line density around region

### Palm / finger morphology

- palm aspect ratio
- relative palm thickness only when image modality supports it
- finger length ratios
- visible knuckle prominence
- fingertip / nail visibility
- thumb angle / span when pose allows

### Surface / color

- apparent color only when color gate passes
- visible callus / scar / mole / pigmentation as neutral visual mark

不得直接把 visual mark 存成：

- 吉痣／凶痣
- 財紋／婚姻紋
- 長壽／短壽
- 性格
- 健康診斷

那些都是 interpretation 或高風險 inference。

## 7. Unknown semantics

避免用 `false` 代表「看不到」。至少區分：

- `absent`：有足夠影像 evidence，未觀察到；
- `unknown`：無法判斷；
- `not_observable`：影像或 modality 不支援；
- `not_applicable`：此 feature 對該 anatomical scope 不適用；
- `unresolved_mapping`：raw fact 已存在，但尚無可靠 source mapping。

這對傳統 pattern 尤其重要：沒有辨認出某 named pattern，不等於它一定不存在。

## 8. Traditional projection object

傳統 source mapping 應是 append-only interpretation preparation layer，不改寫 raw observation。

每個 mapping 至少保存：

```text
tradition
source_id
edition / revision
section
anatomical_scope
source_term
source_definition_summary
mapped raw fact ids
mapping state
mapping confidence
```

`source_definition_summary` 必須用自己的摘要，不搬大段第三方原文。

## 9. Interpretation activation gate

即使 projection 成功，也不代表立刻能解讀。

至少還需要：

1. source rule 已通過 provenance / license review；
2. rule definition 不依賴缺失圖版；
3. observation quality 足夠；
4. mapping state 不是 `UNREVIEWED / CONFLICTING / PROHIBITED_ASSUMPTION`；
5. interpretation owner 明確知道採用哪個 tradition / source。

否則輸出應停在 observation / unresolved mapping。

## 10. Privacy / biometric boundary

手掌照片可能包含可識別生物特徵。未來若使用外部 model / service：

- 不因 Palmistry use case 就自動允許上傳第三方；
- 優先 local / on-device observation path；
- 不把 palm image 用於身份辨識、掌紋 biometric matching 或跨樣本 re-identification；
- 不建立人員身份資料庫；
- public Playbook 不保存真實使用者手掌照片或 derived biometric template。

## 11. Current validation state

本 schema 目前只由 source review / architecture reasoning 支持，尚未：

- 以實際 hand images 做 field coverage validation；
- 驗證 normalized coordinate implementation；
- 驗證不同手勢／左右手／拍攝角度；
- 建立 deterministic schema validator；
- 建立 Palmistry behavioral regression。

所以 adoption state 仍是：

**REFERENCE-ONLY / DRAFT｜僅供參考／草案**

正式 promotion 前需回到 `PALMISTRY.md` 的 Promotion Gate。