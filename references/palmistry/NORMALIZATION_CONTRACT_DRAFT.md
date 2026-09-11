# Palm ROI / Coordinate Normalization Contract Draft

Status: **REFERENCE-ONLY / DRAFT｜僅供參考／草案**

Reviewed target baseline: `masini1491/ai-divination-playbook@c40fb0149c2fc01e0d9c91218cf56d8ce71383b7`

本檔收斂「原始手掌照片 → target hand → model-specific preprocessing → source-neutral palm coordinates」的第一版 deterministic contract。它不是 production runtime，也不建立 Palmistry method authority。

## 1. Research question

目前真正需要固定的是：

```text
raw image
→ select target hand
→ preserve anatomical chirality
→ obtain hand landmarks
→ model-specific crop / rotate / warp / mirror（optional）
→ detector output
→ invert model transform back to raw-image geometry
→ canonical palm coordinates
→ Palm Observation Fact
```

核心要求：**model input coordinates 不得直接等同 canonical observation coordinates。**

## 2. Upstream findings

### 2.1 `samuelwbarber/palm-line-reader`

Reviewed revision: `bc48939f4deee6d8ff842bfde499396dab9c4830`

其 shipped ONNX model contract 本身相對清楚：

- input `RGB NCHW 512×512`；
- ImageNet mean / std normalization；
- plain resize to 512×512；training 沒有 letterbox；
- output 為 4-class logits：background / heart / head / life；
- per-pixel argmax 取得 mask；
- `model_meta.json` 記錄 held-out foreground Dice `0.8098`。

Browser module `web/palmLines.js` 只會把 caller 給的 source **直接拉伸成 512×512**。它自己不建立 hand ROI，也不做 letterbox；註解明確要求 caller 最好提供 reasonably square hand/palm crop。

另一方面，`pipeline/hand_preprocess.py` 的檔頭明確說：原本在 VM 上的 preprocessing file 沒有 recover，現在版本是 reconstruction。該 reconstruction：

- MediaPipe Hand Landmarker，`num_hands=1`；
- 用 wrist landmark 0 → middle-MCP landmark 9 做 fingers-up rotation；
- 以全部 landmarks bounding box + fixed `100 px` margin crop；
- 可依 MediaPipe handedness label mirror 成固定方向；
- 程式自己提醒 MediaPipe handedness 假設 selfie/mirrored input，因此這個 Left/Right label 只能當 consistent training label，不能當 anatomical handedness ground truth。

因此：

```text
shipped segmentation I/O contract = usable technical reference
reconstructed crop / handedness preprocessing = reference only
```

不能把 reconstruction 冒充原 student model 的完整歷史 preprocessing authority。

### 2.2 `yeonsumia/palmistry`

Reviewed revision: `17610c3f031ee312d3352116eefff9b833e9cafb`

`code/rectification.py` 的實際流程：

1. `cv2.flip(image, 1)`；
2. MediaPipe `max_num_hands=1`；
3. 取得 21 個 landmarks；
4. 把 21 點 fit 到一組 hard-coded `pts_target_normalized`；
5. `cv2.findHomography(..., cv2.RANSAC, 5.0)`；
6. `warpPerspective` 回原 image width / height。

後續 pipeline 還包含：

- HSV-based skin/background heuristic；
- 固定 threshold `[0,20,80] → [50,255,255]`；
- resize 到 256×256；
- principal-line segmentation；
- skeleton / graph grouping；
- K-means based line classification；
- measurement 階段再次跑 MediaPipe，依 landmarks 算 heart/head/life 的 length threshold。

這證明「landmark-guided rectification → detector → geometry」是可行 decomposition，但 hard-coded 21-point template、5 px RANSAC threshold、skin HSV threshold 與 downstream cluster centers 都是**project-specific implementation choices**，不是可直接升格的 canonical palm coordinate system。

## 3. Canonical coordinate principle

Canonical observation coordinates 應：

- 不依賴 Western heart/head/life labels；
- 不依賴中國掌宮／八卦術語；
- 不因 detector 需要 mirror 而改變 anatomical chirality；
- 不把某個 model 的 256 / 512 / 1024 pixel grid 當 semantic coordinates；
- 對 translation / in-plane rotation / uniform scale 有 deterministic invariance；
- perspective correction 若不可靠，可以 fail closed，而不是強行 warp。

## 4. Draft palm basis

第一版 source-neutral 2D palm basis 只使用較穩定的 palm anchors：

```text
L0  = wrist
L5  = index-finger MCP
L17 = little-finger MCP
M   = midpoint(L5, L17)
```

定義：

```text
ey = normalize(M - L0)                  # wrist → distal palm
raw_ex = L5 - L17                       # ulnar → radial / index side
ex = normalize(raw_ex - dot(raw_ex, ey) * ey)
```

並確保 `ex` 朝 index-finger MCP 方向。

尺度：

```text
palm_width  = dot(L5 - L17, ex)
palm_height = norm(M - L0)
```

任一 raw-image point `P` 的 draft canonical coordinate：

```text
x = dot(P - L0, ex) / palm_width
y = dot(P - L0, ey) / palm_height
```

直觀上：

- wrist 約 `(0, 0)`；
- MCP midpoint 約 `(0, 1)`；
- index MCP 約 `(+0.5, 1)`；
- little MCP 約 `(-0.5, 1)`。

這個 basis 的目標是建立**幾何 observation frame**，不是把掌面強行變成方形圖片。

## 5. Why canonical facts should not require image warping

Palm line / mark path 可以：

```text
raw pixel geometry
→ project point-by-point into palm basis
```

不需要先把整張照片 warp 成 canonical bitmap。

好處：

- 避免 interpolation 改變細線；
- 避免 full homography 被 finger articulation 拉扯；
- raw geometry 與 canonical geometry 可同時保存；
- detector 若有自己的 preprocessing，仍能透過 inverse transform 回到 raw geometry。

因此 canonical coordinate transform 與 detector image rectification 是兩個責任。

## 6. Model-adapter transform chain

若 detector 需要特定 crop / rotate / mirror / resize：

```text
raw image
→ target-hand crop
→ optional rotation / rectification
→ optional detector-only mirror
→ detector resize
→ detector output
→ inverse detector resize
→ inverse mirror
→ inverse rectification / crop mapping
→ raw-image geometry
→ canonical palm basis
```

每個 adapter 至少應保存：

```text
adapter_id
input_image_size
crop_rect / ROI mapping
rotation / affine / homography matrix（若有）
mirrored_for_model
resize target
inverse_available
landmark source / version
```

如果 transform 無法可靠 inverse，該 detector output 不得成為 canonical geometry authority。

## 7. Chirality guard

`hand_side` 與 `mirrored_for_model` 必須分開。

```text
anatomical hand side = observation fact
model mirror         = implementation detail
```

禁止：

```text
MediaPipe label == anatomical hand side
```

除非 calling pipeline 已明確記錄 camera / selfie mirroring convention 並完成 handedness reconciliation。

若 detector 需要把所有右手 mirror 成左手形狀，output 必須在進 canonical basis 前 unmirror。

## 8. Homography admission gate

Full homography 只在 material perspective distortion 且有足夠 stable palm anchors 時考慮。

不得因「MediaPipe 有 21 landmarks」就預設把全部 21 點 fit 到一個固定 template 最適合掌紋 observation；finger tips / joints 會受 articulation 影響，而掌紋主要位於 palm region。

若採用 homography，至少保存：

- anchor set；
- inlier / residual evidence；
- target template identity；
- transform matrix；
- inverse matrix；
- warp quality / failure state。

若 perspective correction evidence 不足：

```text
geometry may remain observable
fine region mapping = unresolved / fail closed
```

## 9. Segmentation-output boundary

以 `palm-line-reader` 為例，argmax mask 只給 class index，**沒有自動提供 per-pixel confidence**。若需要 confidence，必須從 logits / softmax 額外產生，而不是把 argmax 當 confidence。

另外：

- aggregate held-out foreground Dice `0.8098` 不是單張照片 accuracy guarantee；
- `student_int8.onnx` upstream 自己標示 thin lines visibly lossier；
- model class `heart/head/life` 仍只是 Western tool-local classification；
- 任何 output 都不能直接變成 `天／人／地紋`。

## 10. Deterministic synthetic probe

已新增 [`normalization_probe.py`](normalization_probe.py)，只位於 Cold research surface，**不是 `tools/` production owner**。

Probe 為 standard-library-only，直接實作本 draft basis 與最小 inverse-transform helpers。首次驗證結果：

```text
11 passed, 0 failed
```

已固定的 synthetic properties：

| Case | Result |
|---|---|
| anchor expectations | PASS |
| translation invariance | PASS |
| in-plane rotation invariance | PASS |
| uniform-scale invariance | PASS |
| image mirror with anatomical landmark labels preserved | PASS |
| detector-only mirror + inverse | PASS |
| crop + resize + inverse | PASS |
| missing L0/L5/L17 | fail closed / PASS |
| degenerate palm height / width axis | fail closed / PASS |
| multiple hands | only selected target accepted / PASS |
| material foreshortening without reliable rectifier | fine mapping blocked / PASS |

Probe 使用 `TOL = 1e-9` 作理想 synthetic arithmetic 的 comparison tolerance。這只證明目前公式在理想點集下的 deterministic 性質，不是 camera / landmark noise 的 production tolerance。

### What this probe proves

目前可以把以下從「reasoning expectation」提升成 executable research evidence：

- translation / in-plane rotation / uniform scale 不改 canonical coordinates；
- anatomical landmark identity 保留時，鏡像不會反轉 canonical index-side semantic direction；
- detector-only mirror 與 crop/resize 可以要求明確 inverse round-trip；
- anchor 不完整、basis 退化、target 未選定會 fail closed；
- material perspective distortion 沒有可靠 rectifier 時，不允許 fine source-region mapping。

### What it does not prove

它**沒有**證明：

- MediaPipe landmarks 在真實照片上的 repeatability；
- selfie / camera mirroring convention 已可自動 reconciliation；
- 1e-9 適合作 production tolerance；
- detector segmentation geometry 在 inverse transform 後仍達到某個 accuracy threshold；
- perspective rectifier 已可靠；
- cross-device robustness 已建立。

## 11. Adoption decision

本輪仍只建立 research contract + executable research probe：

**REFERENCE-ONLY / DRAFT**

尚未建立：

- production normalization implementation；
- production deterministic repository tool；
- landmark-version / camera-mirroring compatibility matrix；
- real-image landmark perturbation tolerance；
- cross-device repeatability；
- detector accuracy acceptance threshold。

下一個合理 research node 是對 L0/L5/L17 做**controlled perturbation / mirror-convention sensitivity sweep**，量化 landmark noise 對 canonical coordinate 的影響，再討論 numeric admission tolerance 或正式 implementation owner。
