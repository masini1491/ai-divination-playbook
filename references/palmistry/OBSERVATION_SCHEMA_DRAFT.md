# Palm Observation Fact Schema Draft｜手相觀察事實草案

Status: **REFERENCE-ONLY / DRAFT｜僅供參考／草案**

Reviewed target baseline: `masini1491/ai-divination-playbook@91eeb9423febb486aaa558c953bf159b835d0c27`

本 schema draft 只定義「從手掌影像可合理保存哪些 observation facts」與 tradition projection boundary。它不是 production schema，也不代表目前 Playbook 已正式支援 Palmistry。

目前已經過第一輪公開真實照片 field-coverage validation，詳見 [`PHOTO_VALIDATION.md`](PHOTO_VALIDATION.md)。這只證明 schema coverage 比純架構推導更完整，不代表 CV accuracy、傳統 mapping 或 production behavior 已驗證。

## 1. Design goals

Palm Observation Fact 必須做到：

1. image observation 與 traditional interpretation 分離；
2. source-neutral geometry 先於 source-local terminology；
3. unknown / not-observable 能被明確表示；
4. 中國與 Western tradition 可以對同一組 raw facts 做不同 projection；
5. 不要求 CV model 一次判斷所有傳統術語；
6. 不讓 LLM 因 interpretation 需要而補畫不存在的 feature；
7. 支援同一畫面有多隻手，且 analysis target 可明確指定或 fail closed；
8. quality 要依 observation capability 分開，而不是只靠一個 global score；
9. 不保存與 Palmistry 無關的 raw EXIF / location / device metadata。

## 2. Proposed envelope

```yaml
schema_version: palm-observation-draft-v2
status: draft
scene:
  hand_count: integer | unknown
  target_hand_id: string | null
  target_selection_state: selected | ambiguous | none | unknown
  notes: []

hands:
  - id: hand-001
    hand_side: left | right | unknown
    view: palm | dorsal | oblique | unknown
    orientation_normalized: true | false | unknown
    selection_confidence: 0.0-1.0 | null

    pose:
      frontalness: frontal | near-frontal | oblique | side | unknown
      foreshortening: none | mild | material | severe | unknown
      finger_spread: open | partial | closed | mixed | unknown
      externally_manipulated: true | false | unknown

    quality:
      overall: sufficient | partial | insufficient
      geometry: sufficient | partial | insufficient | unknown
      line_detail: sufficient | partial | insufficient | unknown
      surface_detail: sufficient | partial | insufficient | unknown
      color: sufficient | partial | insufficient | unknown
      focus: good | partial | poor | unknown
      lighting: good | uneven | poor | unknown
      glare: none | partial | severe | unknown
      crop: complete | partial | insufficient | unknown
      color_reliable: true | false | unknown

    occlusion:
      overall: none | partial | severe | unknown
      occluders:
        - type: accessory | other-hand | object | self-occlusion | unknown
          affected_region: string | unknown
          severity: partial | severe | unknown
      accessory_occlusion: none | partial | severe | unknown

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

    surface_state:
      apparent_moisture_or_oil: none | possible | visible | unknown
      visible_accessories: []
      neutral_marks: []

traditional_projections:
  - hand_id: hand-001
    tradition: chinese-xiangshu
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
  source_or_license_note: string | null
  task_relevant_capture_notes: []
  raw_exif_preserved: false
  notes: []
```

所有 enum / key 都是 draft；正式化前仍需 behavioral / implementation validation。

## 3. Scene / Target Selection Gate

Palmistry input 不應假設一張圖只有一隻手。

若畫面有多隻手：

1. 每隻手取得 scene-local `hand-xxx` ID；
2. 使用者已指定目標時，將對應 hand 設成 `target_hand_id`；
3. 若沒有指定而模型能高可信選出唯一 target，可保存 `selection_confidence`；
4. 若 target 不明確：

```yaml
target_hand_id: null
target_selection_state: ambiguous
```

此時不得進行 tradition-specific interpretation。

scene-local hand ID 只用於同張影像 association，不得作 biometric identity、跨照片 re-identification 或使用者身份 key。

## 4. Image Quality Gate

單一 `quality.overall` 只作摘要，不再決定所有 observation capability。

至少拆成：

```text
geometry
line_detail
surface_detail
color
```

例如一張照片可以是：

```yaml
quality:
  overall: partial
  geometry: sufficient
  line_detail: partial
  surface_detail: partial
  color: insufficient
```

### Capability rules

- `geometry == sufficient`：可嘗試 outline / proportions / coarse line path observation；
- `line_detail == sufficient`：才允許較細 crease / branch / break analysis；
- `surface_detail == sufficient`：才描述細小 scar / mole / texture-like neutral marks；
- `color == sufficient` 且 `color_reliable == true`：才允許 source-specific palm-color projection；
- 任一 capability `insufficient` 時，該類 observation fail closed，但不必把整張圖全部判 invalid。

### Minimum checks

至少要能回答：

- 掌面是否朝鏡頭；
- 左右手能否可靠辨認；
- target hand 是否唯一且清楚；
- 掌心與主要指根是否完整；
- 是否有 material perspective / foreshortening；
- 是否嚴重過曝、反光、陰影；
- 主要 crease 是否在有效解析度內；
- 是否有他人手、物件或飾品局部遮擋；
- 是否有人為按壓／按摩造成掌形變形；
- 是否有油、水、強反光改變表面觀感；
- 影像顏色是否足以做 color observation。

一般手機照片若沒有校色／受控光源 evidence，不應只因「看起來正常」就把 `color_reliable` 設成 `true`。

## 5. Occlusion / Accessory Semantics

`occlusion` 必須能表達「誰遮到哪裡」。

常見類型：

- `accessory`：ring / watch / bracelet；
- `other-hand`：另一隻手遮住 target；
- `object`：工具、手機、布料等；
- `self-occlusion`：手指或姿勢遮到自己的掌面。

只要 affected region 不碰 palm-line ROI，局部 accessory 不需要讓整張照片 fail closed；但它會讓相關 finger / surface observation 變成 partial / not_observable。

## 6. Source-neutral coordinates

所有 line / mark geometry 優先使用掌面 normalization 後座標，而不是直接以 pixel 值當 semantic position。

概念流程：

```text
hand landmarks
→ target-hand ROI
→ perspective / orientation assessment
→ palm ROI / orientation normalization
→ normalized palm coordinate system
→ observed crease / mark geometry
→ optional tradition-specific region projection
```

若 `foreshortening == material | severe` 且無可靠 rectification，精細 region mapping 應標成 `unknown / unresolved_mapping`。

這樣：

- CV layer 不需要知道巽／離／坤等 interpretation；
- tradition adapter 才把 source-defined region 投影到 normalized coordinates；
- 不同 source 若宮位定義不同，可各自有 projection，不覆寫 raw fact。

## 7. Major-line identification state

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

## 8. Observable feature vocabulary

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
- visible oil / moisture / glare as capture-relevant surface state

不得直接把 visual mark 存成：

- 吉痣／凶痣
- 財紋／婚姻紋
- 長壽／短壽
- 性格
- 健康診斷

那些都是 interpretation 或高風險 inference。

## 9. Unknown semantics

避免用 `false` 代表「看不到」。至少區分：

- `absent`：有足夠影像 evidence，未觀察到；
- `unknown`：無法判斷；
- `not_observable`：影像或 modality 不支援；
- `not_applicable`：此 feature 對該 anatomical scope 不適用；
- `unresolved_mapping`：raw fact 已存在，但尚無可靠 source mapping。

這對傳統 pattern 尤其重要：沒有辨認出某 named pattern，不等於它一定不存在。

## 10. Traditional projection object

傳統 source mapping 應是 append-only interpretation preparation layer，不改寫 raw observation。

每個 mapping 至少保存：

```text
hand_id
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

## 11. Interpretation activation gate

即使 projection 成功，也不代表立刻能解讀。

至少還需要：

1. target hand 已唯一選定；
2. source rule 已通過 provenance / license review；
3. rule definition 不依賴缺失圖版；
4. 該 rule 所需的 observation capability quality 足夠；
5. mapping state 不是 `UNREVIEWED / CONFLICTING / PROHIBITED_ASSUMPTION`；
6. interpretation owner 明確知道採用哪個 tradition / source。

否則輸出應停在 observation / unresolved mapping。

## 12. Privacy / biometric / metadata boundary

手掌照片可能包含可識別生物特徵。未來若使用外部 model / service：

- 不因 Palmistry use case 就自動允許上傳第三方；
- 優先 local / on-device observation path；
- 不把 palm image 用於身份辨識、掌紋 biometric matching 或跨樣本 re-identification；
- 不建立人員身份資料庫；
- public Playbook 不保存真實使用者手掌照片或 derived biometric template。

另外遵守 metadata minimization：

- 不保存 GPS / exact capture location；
- 不保存 camera serial / device identifiers；
- 不原樣保留 EXIF dump；
- 只保留本次 observation 所需的 source identity、license 與 task-relevant capture note。

## 13. Current validation state

本 schema 已完成第一輪**代表性真實照片 field-coverage validation**，目前確認：

- single-hand near-frontal palm 可由現有 geometry vocabulary 表達；
- multi-hand image 需要 scene / target selection；
- ring 等 accessory 需要 localized occlusion；
- low-light / auto-white-balance image 顯示 color quality 必須獨立；
- manipulated / oily / occluded palm 顯示 geometry、line detail 與 color 可以有不同 capability state；
- raw metadata 不應因來源公開就全部帶入 observation record。

仍未完成：

- deterministic landmark / ROI normalization；
- normalized coordinate implementation validation；
- CV segmentation accuracy；
- branch / island / star / named-pattern detector performance；
- source-specific Bagua / palace projection geometry；
- repeatability across camera devices；
- deterministic schema validator；
- Palmistry behavioral regression。

所以 adoption state 仍是：

**REFERENCE-ONLY / DRAFT｜僅供參考／草案**

正式 promotion 前需回到 `PALMISTRY.md` 的 Promotion Gate。