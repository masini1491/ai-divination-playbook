# Palmistry Research Synthesis｜手相參考收斂

Status: **REFERENCE-ONLY｜僅供參考**

Reviewed target baseline: `masini1491/ai-divination-playbook@20317de314346d81bb3ee732d05650af0c4fd37c`

本檔只收斂外部研究結論，不建立 production Palmistry capability，也不修改 `METHOD_ROUTING.md`、`PLAYBOOK_INDEX.json`、`CHAT_INIT.md` 或既有 Tarot / Meihua / Liuyao contract。

## Research question

未來 Palmistry 若要安全加入本 Playbook，至少要把這些責任拆開：

```text
raw image
→ image / target-hand quality gate
→ model-specific observation adapter
→ source-neutral Palm Observation Fact
→ tradition-specific projection
→ tradition-specific interpretation
→ user-visible synthesis
```

研究重點不是找「會算命的 App」，而是確認：

1. 掌紋／掌型 observation 是否已有可重用技術；
2. image preprocessing / coordinate normalization 能否形成可重現 contract；
3. interpretation 是否有可追溯的傳統來源；
4. source-specific terminology 如何正規化而不製造無證據的中西對照。

## Current conclusion

### Observation / CV

目前最有價值的兩個 upstream 仍是：

- `samuelwbarber/palm-line-reader`：三大主線 segmentation、browser ONNX deployment、明確 model I/O contract；
- `yeonsumia/palmistry`：landmark-guided homography rectification、principal-line detection / classification / measurement pipeline。

但第四輪 implementation review 把兩者的 authority boundary進一步釐清。

#### `palm-line-reader`

其 shipped student model contract 可重現：RGB / NCHW / 512×512、ImageNet normalization、plain resize、4-class logits、argmax mask；`model_meta.json` 記錄 held-out foreground Dice `0.8098`。

然而 current `pipeline/hand_preprocess.py` 明確是對遺失原始 preprocessing module 的 **reconstruction**。因此 current wrist→middle-MCP rotation、landmark bbox + 100 px margin、MediaPipe handedness mirror 只能是 technical reference，不能冒充原模型 training preprocessing 的完整 historical authority。

#### `yeonsumia/palmistry`

實作可重現地使用：

```text
cv2.flip
→ MediaPipe 21 landmarks
→ hard-coded 21-point target template
→ RANSAC homography
→ warpPerspective
→ HSV background heuristic
→ fixed resize
→ segmentation / graph / K-means classification
→ landmark-relative measurement
```

這證明 landmark-guided rectification 是可行 decomposition，但 hard-coded target、RANSAC threshold、HSV threshold、cluster centers 等都屬 project-specific implementation，不應直接升格成 canonical palm coordinate system。

### Canonical coordinate decision

已新增 [`NORMALIZATION_CONTRACT_DRAFT.md`](NORMALIZATION_CONTRACT_DRAFT.md)。核心決策：

```text
model-specific coordinates
≠ canonical Palm Observation Fact coordinates
```

canonical observation 應先把 detector output invert 回 raw-image geometry，再投影到 source-neutral palm basis。

第一版 draft basis 使用：

```text
L0  wrist
L5  index MCP
L17 little MCP
```

以 wrist→MCP midpoint 定義 palm longitudinal axis，以 little→index MCP 的正交分量定義 transverse axis，分別以 palm height / width normalization。這個 frame 的目的只是建立 geometry observation coordinates，不是 Western line label 或中國掌宮。

### Mirroring / handedness boundary

必須分開：

```text
anatomical hand side = observation fact
mirrored_for_model    = adapter implementation detail
```

任何 detector 為了降低 shape variation 而 mirror hand，都必須在進 canonical basis 前 undo；MediaPipe handedness label 也不能在未 reconciliation camera/selfie convention 前直接當 anatomical truth。

### Traditional interpretation

中國與西方 source normalization 結論維持不變：

- Cheiro 只代表 Western tradition；
- `SXQ-640` / `TQ-V5` / `TGKD` 為中國傳統 provenance anchors；
- `SXQ-640` 與 `TQ-V5` 高度近似的段落不能機械視為獨立 corroboration；
- `天／人／地紋 ↔ heart/head/life` 與 `玉柱紋 ↔ fate line` 仍是 `PROHIBITED_ASSUMPTION`。

## Current architecture

目前 evidence 支持：

```text
Scene / Target Selection Gate
→ Task-specific Image Quality Gate
→ Model Adapter
→ Raw-image Observation Geometry
→ Canonical Palm Coordinates
→ Palm Observation Fact
→ Tradition-specific Projection
→ Tradition-specific Interpretation
→ User-visible synthesis
```

其中：

- model adapter 可依自身需要 crop / rotate / warp / mirror / resize；
- transform chain 必須可追溯，最好可 inverse；
- canonical observation 不應被 model-specific mirror / pixel grid 污染；
- traditional source 不取得 image observation authority；
- detector class 不取得 Chinese terminology authority。

## Validation completed so far

已完成：

1. 中國傳統 source provenance baseline；
2. source-specific rule-family normalization；
3. Palm Observation Fact draft v2；
4. 代表性真實照片 field-coverage / fail-closed review；
5. upstream preprocessing / rectification implementation review；
6. source-neutral normalization contract draft；
7. synthetic reasoning check：draft palm basis 對 translation / in-plane rotation / uniform scale 可保持 canonical coordinate 不變，mirror 後只要 anatomical landmark identity 保留，也可維持 index-side positive orientation。

上述 synthetic check 目前只是研究計算，不是 repository tool / regression test。

## Remaining evidence gaps

目前仍不足以 promotion 到 production：

1. normalization contract 尚無 repository implementation / deterministic tests / numeric tolerance；
2. 尚未建立 MediaPipe landmark version / camera mirroring compatibility contract；
3. `palm-line-reader` aggregate Dice 不足以建立本專案 detector acceptance threshold，也缺 per-case / cross-device validation；
4. branch / island / star / minor lines / mounts 等 detector evidence 仍不足；
5. Bagua / palm-palace projection geometry 尚未 source-specifically formalize；
6. named patterns / illustrated marks 仍有大量 unresolved mapping；
7. 尚未建立 Palmistry behavioral regression，證明正式加入後不影響 Tarot / Meihua / Liuyao routing。

## Adoption decision

目前所有外部來源、schema、normalization contract 仍為：

**REFERENCE-ONLY / DRAFT｜僅供參考／草案**

production method set 不變。

下一個合理 research node 是：**建立 synthetic landmark fixtures 的 deterministic normalization probe**，先驗 translation / rotation / scale / mirror / inverse-transform / fail-closed properties；只有這段穩定後，才值得討論 production implementation owner。
