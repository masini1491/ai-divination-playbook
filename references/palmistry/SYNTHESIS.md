# Palmistry Research Synthesis｜手相參考收斂

Status: **REFERENCE-ONLY｜僅供參考**

Reviewed target baseline: `masini1491/ai-divination-playbook@776934ab5ea6a688ebf91a98c71511ded70657ef`

本檔只收斂外部研究與 Cold validation 結論，不建立 production Palmistry capability，也不修改 `METHOD_ROUTING.md`、`PLAYBOOK_INDEX.json`、`CHAT_INIT.md` 或既有 Tarot / Meihua / Liuyao contract。

## Research question

未來 Palmistry 若要安全加入本 Playbook，至少要拆開：

```text
raw image
→ image / target-hand quality gate
→ model-specific observation adapter
→ raw-image observation geometry
→ canonical palm coordinates
→ source-neutral Palm Observation Fact
→ tradition-specific projection
→ tradition-specific interpretation
→ user-visible synthesis
```

研究重點：

1. 掌紋／掌型 observation 是否有可重用技術；
2. preprocessing / coordinate normalization 能否形成可執行、可 fail-closed 的 contract；
3. landmark / mirror errors 如何傳到 canonical geometry；
4. real-image detector repeatability 是否足夠；
5. interpretation 是否有可追溯傳統來源；
6. source-specific terminology 如何避免無證據中西對照。

## Observation / CV conclusion

目前最有價值的 upstream：

- `samuelwbarber/palm-line-reader`：三大主線 segmentation、browser ONNX deployment、明確 model I/O contract；
- `yeonsumia/palmistry`：landmark-guided homography rectification、principal-line detection / classification / measurement pipeline。

### `palm-line-reader`

其 shipped student model contract 可重現：RGB / NCHW / 512×512、ImageNet normalization、plain resize、4-class logits、argmax mask；`model_meta.json` 記錄 held-out foreground Dice `0.8098`。

但 current `pipeline/hand_preprocess.py` 是對遺失原始 preprocessing module 的 reconstruction，因此 wrist→middle-MCP rotation、landmark bbox + 100 px margin、MediaPipe handedness mirror 只能是 technical reference，不能冒充原模型 historical training preprocessing authority。

其 repo 的 `pipeline/` 也確實包含 `hand_landmarker.task` binary；存在性與 object identity 可確認，但目前研究執行環境無法 materialize binary 到 container，也沒有預裝 MediaPipe runtime。

### `yeonsumia/palmistry`

實作使用：

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

這證明 landmark-guided rectification 是可行 decomposition，但 hard-coded target、RANSAC threshold、HSV threshold、cluster centers 都是 project-specific implementation，不升格成 canonical palm coordinate system。

### OpenPose fallback review

`CMU-Perceptual-Computing-Lab/openpose@5c5d96523ef917bd30301245fdc8343937cae48d` 官方 hand config 定義 21 points，且 topology 明確包含 `0→5`、`0→17`；模型檔名為：

```text
hand/pose_deploy.prototxt
hand/pose_iter_102000.caffemodel
```

所以 OpenPose 可作 topology-compatible fallback reference；但目前容器同樣無法取得 trained weights，因此本輪沒有 real-image OpenPose inference。

## Canonical coordinate decision

[`NORMALIZATION_CONTRACT_DRAFT.md`](NORMALIZATION_CONTRACT_DRAFT.md) 的核心：

```text
model-specific coordinates
≠ canonical Palm Observation Fact coordinates
```

canonical observation 先把 detector output inverse 回 raw-image geometry，再投影到 source-neutral palm basis。

第一版 draft basis：

```text
L0  wrist
L5  index MCP
L17 little MCP
```

以 wrist→MCP midpoint 定義 longitudinal axis，以 little→index MCP 的正交分量定義 transverse axis，分別以 palm height / width normalization。這只是 geometry frame，不代表 Western line labels 或中國掌宮。

## Deterministic synthetic invariant probe

[`normalization_probe.py`](normalization_probe.py) 是 Cold、standard-library-only executable probe。

首次執行：

```text
11 passed, 0 failed
```

已驗：translation / rotation / uniform-scale invariance、mirror/chirality、detector-only mirror inverse、crop/resize inverse、missing anchors fail closed、degenerate basis fail closed、multi-hand target selection、material foreshortening gate。

`TOL = 1e-9` 只驗理想 floating-point arithmetic，不是 production tolerance。

## Landmark perturbation / mirror sensitivity

[`SENSITIVITY_SWEEP.md`](SENSITIVITY_SWEEP.md) + [`normalization_sensitivity_probe.py`](normalization_sensitivity_probe.py) 對 `L0/L5/L17` 做 16-direction bounded sweep；每層 simultaneous combinations = `16^3 = 4096`。

Configured direction-grid maxima：

| Per-anchor bound | Axis angle | Width error | Height error | Max canonical drift |
|---:|---:|---:|---:|---:|
| 0.25% | 0.2865° | 0.500% | 0.500% | 0.527% |
| 0.50% | 0.5729° | 1.001% | 1.000% | 1.059% |
| 1.00% | 1.1458° | 2.005% | 2.000% | 2.135% |
| 2.00% | 2.2906° | 4.019% | 4.000% | 4.341% |
| 5.00% | 5.7106° | 10.112% | 10.000% | 11.445% |

這是 configured grid maxima，不是 continuous mathematical worst-case，也不是 real-image distribution。

Anchor role：`L0` 對 longitudinal axis / palm-height 較敏感；`L5/L17` 對 transverse scale / palm-width 較敏感。

若漏做 detector-only mirror inverse，canonical frame 等價於 `x → -x`；在 `x∈[-0.5,0.5]` span 上 max drift = 1.0 canonical unit、mean = 0.6。這是 semantic frame inversion，不是 ordinary small noise。

## Real-image repeatability harness

本輪新增：

- [`REAL_IMAGE_REPEATABILITY.md`](REAL_IMAGE_REPEATABILITY.md)
- [`real_image_repeatability_probe.py`](real_image_repeatability_probe.py)

Harness 不做 detection；它接收固定 detector 已輸出的：

```text
baseline L0/L5/L17
variant L0/L5/L17
known inverse image transform
optional handedness label
```

並計算：

- max / mean anchor displacement as palm-width fraction；
- palm-axis angle drift；
- width / height scale drift；
- canonical 5×5 grid max drift；
- handedness label change。

Local self-test 已 PASS：

```text
exact rotate+translate + exact inverse
→ max anchor drift = 0
→ max canonical drift = 0

injected 1% wrist displacement
→ recovered max anchor drift = 1.0000%
→ max canonical drift ≈ 1.2532%
```

這證明 harness / interchange contract 可用；**不代表 MediaPipe 或 OpenPose real-image repeatability 已驗證**。

### Current execution boundary

本輪實際 reconciled：

- container 沒有 `mediapipe` runtime；
- network-isolated `pip install` 無法安裝；
- upstream `hand_landmarker.task` binary 存在，但 connector workflow 無法 materialize binary 到 container；
- OpenPose config / topology / model identity可讀，但 trained caffemodel 同樣無法在此環境取得。

因此 real-image numeric study 被環境阻擋，並明確 fail closed；沒有用人工目測、LLM vision 或不同 detector 假裝成 MediaPipe/OpenPose evidence。

## Traditional interpretation boundary

中國與西方 source normalization 結論維持：

- Cheiro 只代表 Western tradition；
- `SXQ-640` / `TQ-V5` / `TGKD` 為中國傳統 provenance anchors；
- `SXQ-640` 與 `TQ-V5` 高度近似段落不能機械視為獨立 corroboration；
- `天／人／地紋 ↔ heart/head/life` 與 `玉柱紋 ↔ fate line` 仍是 `PROHIBITED_ASSUMPTION`；
- CV detector class 不取得 Chinese terminology authority；
- traditional source 不取得 image observation authority。

## Current architecture

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

- adapter 可依自身需要 crop / rotate / warp / mirror / resize；
- transform lineage 必須可追溯，最好可 inverse；
- canonical observation 不受 model-specific mirror / pixel grid 污染；
- frame-level uncertainty 必須涵蓋 multi-anchor error；
- real-image detector evidence與 synthetic sensitivity evidence分開保存。

## Validation completed so far

1. 中國傳統 source provenance baseline；
2. source-specific rule-family normalization；
3. Palm Observation Fact draft v2；
4. 代表性真實照片 field-coverage / fail-closed review；
5. upstream preprocessing / rectification implementation review；
6. source-neutral normalization contract draft；
7. Cold invariant probe：11 passed / 0 failed；
8. controlled three-anchor perturbation sweep；
9. mirror-convention failure magnitude check；
10. detector-agnostic real-image repeatability harness self-test PASS；
11. MediaPipe / OpenPose runtime availability reconciliation。

## Remaining evidence gaps

目前仍不足以 promotion：

1. **real-image landmark repeatability numeric evidence 尚未取得**；
2. same-image rotate / scale / crop / mirror transform consistency 尚未真正跑 detector；
3. camera / selfie mirroring auto-reconciliation 尚未驗；
4. `palm-line-reader` aggregate Dice 不足以建立本專案 detector acceptance threshold；
5. branch / island / star / minor lines / mounts detector evidence不足；
6. Bagua / palm-palace projection geometry 未 formalize；
7. named patterns / illustrated marks仍有 unresolved mapping；
8. production numeric tolerance / landmark-version compatibility matrix尚未建立；
9. Palmistry behavioral regression尚未建立。

## Adoption decision

所有外部來源、schema、normalization contracts、synthetic probes、sensitivity sweep與 real-image harness 仍為：

**REFERENCE-ONLY / DRAFT｜僅供參考／草案**

production method set 不變。

下一個合理 research node：取得固定版本、可本地執行的 hand-landmark runtime/model，直接用 `REAL_IMAGE_REPEATABILITY.md` protocol 跑 Case A / B controlled-transform study。完成前不建立 production numeric threshold，也不 promotion Palmistry routing。
