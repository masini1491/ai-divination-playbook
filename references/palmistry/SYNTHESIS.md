# Palmistry Research Synthesis｜手相參考收斂

Status: **REFERENCE-ONLY｜僅供參考**

Reviewed target baseline: `masini1491/ai-divination-playbook@41f2a89a1c2e09cb5059fb788331d267a4bd2958`

本檔只收斂外部研究與 Cold validation 結論，不建立 production Palmistry capability，也不修改 `METHOD_ROUTING.md`、`PLAYBOOK_INDEX.json`、`CHAT_INIT.md` 或既有 Tarot / Meihua / Liuyao contract。

## Research question

未來 Palmistry 若要安全加入本 Playbook，至少要把這些責任拆開：

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

研究重點不是找「會算命的 App」，而是確認：

1. 掌紋／掌型 observation 是否已有可重用技術；
2. image preprocessing / coordinate normalization 能否形成可執行、可失敗關閉的 contract；
3. landmark / mirror errors 如何傳到 canonical geometry；
4. interpretation 是否有可追溯的傳統來源；
5. source-specific terminology 如何正規化而不製造無證據的中西對照。

## Observation / CV conclusion

目前最有價值的兩個 upstream 仍是：

- `samuelwbarber/palm-line-reader`：三大主線 segmentation、browser ONNX deployment、明確 model I/O contract；
- `yeonsumia/palmistry`：landmark-guided homography rectification、principal-line detection / classification / measurement pipeline。

### `palm-line-reader`

其 shipped student model contract 可重現：RGB / NCHW / 512×512、ImageNet normalization、plain resize、4-class logits、argmax mask；`model_meta.json` 記錄 held-out foreground Dice `0.8098`。

但 current `pipeline/hand_preprocess.py` 明確是對遺失原始 preprocessing module 的 reconstruction，因此 current wrist→middle-MCP rotation、landmark bbox + 100 px margin、MediaPipe handedness mirror 只能是 technical reference，不能冒充原模型 training preprocessing 的完整 historical authority。

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

這證明 landmark-guided rectification 是可行 decomposition，但 hard-coded target、RANSAC threshold、HSV threshold、cluster centers 等都屬 project-specific implementation，不應直接升格成 canonical palm coordinate system。

## Canonical coordinate decision

[`NORMALIZATION_CONTRACT_DRAFT.md`](NORMALIZATION_CONTRACT_DRAFT.md) 的核心決策：

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

以 wrist→MCP midpoint 定義 palm longitudinal axis，以 little→index MCP 的正交分量定義 transverse axis，分別以 palm height / width normalization。這個 frame 只代表 geometry observation coordinates，不代表 Western line label 或中國掌宮。

## Deterministic synthetic invariant probe

[`normalization_probe.py`](normalization_probe.py) 是 Cold、standard-library-only executable probe，不放入 production `tools/`。

首次執行：

```text
11 passed, 0 failed
```

已 executable-validated：

- anchor expectations；
- translation invariance；
- in-plane rotation invariance；
- uniform-scale invariance；
- anatomical landmark labels 保留時的 mirror/chirality invariance；
- detector-only mirror inverse round-trip；
- crop/resize inverse round-trip；
- missing L0/L5/L17 fail closed；
- degenerate palm width / height fail closed；
- multi-hand 必須先 selected target；
- material foreshortening 無 reliable rectifier 時阻止 fine mapping。

`TOL = 1e-9` 只驗理想 synthetic floating-point arithmetic，**不是 production tolerance**。

## Landmark perturbation / mirror sensitivity

已新增：

- [`SENSITIVITY_SWEEP.md`](SENSITIVITY_SWEEP.md)
- [`normalization_sensitivity_probe.py`](normalization_sensitivity_probe.py)

Companion probe 對 `L0/L5/L17` 各用 16 個方向，三 anchor simultaneous sweep 為每層 `16^3 = 4096` 組 bounded combinations。測試 perturbation level：0.25%、0.5%、1%、2%、5% palm width。

Configured direction-grid maxima：

| Per-anchor perturbation bound | Axis angle | Width error | Height error | Max canonical drift |
|---:|---:|---:|---:|---:|
| 0.25% | 0.2865° | 0.500% | 0.500% | 0.527% |
| 0.50% | 0.5729° | 1.001% | 1.000% | 1.059% |
| 1.00% | 1.1458° | 2.005% | 2.000% | 2.135% |
| 2.00% | 2.2906° | 4.019% | 4.000% | 4.341% |
| 5.00% | 5.7106° | 10.112% | 10.000% | 11.445% |

這些是 16-direction grid 的 deterministic maxima，不是 continuous mathematical worst-case bound，也不是 real-image landmark distribution。

### Anchor role at 1%

單一 anchor perturbation 的 fixture 結果：

- `L0 / wrist`：axis 約 0.5729°、height 約 1.0%、max drift 約 1.282%；
- `L5 / index MCP`：axis 約 0.2865°、width 約 1.001%、max drift 約 1.041%；
- `L17 / little MCP`：與 L5 對稱，結果相同。

因此 `L0` 對 longitudinal axis / palm-height 較敏感；`L5/L17` 對 transverse scale / palm-width 較敏感。

### Mirror-convention failure

若 detector-only mirror 應 inverse 卻漏做，canonical frame 相當於：

```text
x → -x
```

在 `x ∈ [-0.5, 0.5]` 的 palm span 上，max drift = 1.0 canonical unit、mean grid drift = 0.6 canonical unit。

因此 mirror mismatch 是 **semantic frame inversion**，不是一般 small-noise problem。`anatomical hand side`、camera/selfie mirroring convention、`mirrored_for_model` 與 inverse-applied state 必須有完整 lineage；缺失時，side-specific / fine-region mapping 應 fail closed。

## Traditional interpretation boundary

中國與西方 source normalization 結論維持不變：

- Cheiro 只代表 Western tradition；
- `SXQ-640` / `TQ-V5` / `TGKD` 為中國傳統 provenance anchors；
- `SXQ-640` 與 `TQ-V5` 高度近似段落不能機械視為獨立 corroboration；
- `天／人／地紋 ↔ heart/head/life` 與 `玉柱紋 ↔ fate line` 仍是 `PROHIBITED_ASSUMPTION`；
- CV detector class 不取得 Chinese terminology authority；
- traditional source 不取得 image observation authority。

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
- frame-level uncertainty 必須能涵蓋多-anchor error，而不能只看單 landmark confidence。

## Validation completed so far

已完成：

1. 中國傳統 source provenance baseline；
2. source-specific rule-family normalization；
3. Palm Observation Fact draft v2；
4. 代表性真實照片 field-coverage / fail-closed review；
5. upstream preprocessing / rectification implementation review；
6. source-neutral normalization contract draft；
7. repository Cold invariant probe：11 passed / 0 failed；
8. controlled three-anchor perturbation direction-grid sweep；
9. mirror-convention failure magnitude check。

## Remaining evidence gaps

目前仍不足以 promotion 到 production：

1. 尚未量化 **real-image landmark repeatability**；
2. 尚未建立 camera / selfie mirroring auto-reconciliation contract；
3. 尚未建立 same-image controlled transform consistency（rotate / scale / crop / mirror 後 inverse 回原座標）；
4. `palm-line-reader` aggregate Dice 不足以建立本專案 detector acceptance threshold，也缺 per-case / cross-device validation；
5. branch / island / star / minor lines / mounts 等 detector evidence 仍不足；
6. Bagua / palm-palace projection geometry 尚未 source-specifically formalize；
7. named patterns / illustrated marks 仍有大量 unresolved mapping；
8. 尚未建立 production numeric tolerance / landmark-version compatibility matrix；
9. 尚未建立 Palmistry behavioral regression，證明正式加入後不影響 Tarot / Meihua / Liuyao routing。

## Adoption decision

目前所有外部來源、schema、normalization contract、synthetic probes 與 sensitivity sweep 仍為：

**REFERENCE-ONLY / DRAFT｜僅供參考／草案**

production method set 不變。

下一個合理 research node 是：**real-image landmark repeatability / transform-consistency study**。優先用 public/free-licensed palm images，在固定 detector/version 下做 controlled rotate / scale / crop / mirror，再 inverse transform 回原座標，比對 L0/L5/L17 displacement；只有取得真實影像 repeatability evidence 後，才值得討論 production numeric admission tolerance 或正式 normalization implementation owner。
