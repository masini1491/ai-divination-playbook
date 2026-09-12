# Principal-line Line-detail Quality Gate — Runner Static Review

Status: **REFERENCE-ONLY / PRE-EXECUTION STATIC REVIEW / NO MOHI RESULT EXECUTED**

## Scope

本文件只做 source-level contract review，對照：

- `LINE_DETAIL_QUALITY_GATE_PLAN.md`
- `LINE_DETAIL_QUALITY_GATE_IMPLEMENTATION_LOCK.md`
- `line_detail_quality_gate_runner.py`

不宣稱 `py_compile`、ONNX dry-run、full MOHI execution 或 CI 已通過。

## Review result

Source-level contract alignment：**PASS**。

### 1. Frozen provenance hard-lock — PASS

Runner 直接固定：

```text
annotation SHA256
51c4886e20cb9aee2d660fe1ca39f25b927398261478c013090ab5d611858041

audit result SHA256
6f95828b70b388028a46ee1879835d432d9dd695bdbbdd1f2656b6ebf3572284

spatial result SHA256
ba65456e3c7c3a645a4000c721961d0f600b46541ffc7e7566525b99a55f87e7

tolerance
8 px
```

Full execution 前會驗證這些 provenance，並要求 baseline input / mask SHA 重現既有 spatial evidence。

### 2. Primary source accounting — PASS

Runner primary set 固定為 `P002`–`P010` 的 `S1/01` 共 9 張。

`P001/S1/01.jpg` 只有 explicit `--include-p001-sentinel` 才執行，而且 source code 明確不對 P001 計算 manual-reference quality metric。

因此 P001 不會意外進入 primary aggregate。

### 3. Degradation contract — PASS

Runner condition set與 plan 一致：

```text
baseline
Gaussian blur sigma 1.5 / 3.0 / 6.0 px
resolution 256 / 128 / 64 → 512
contrast factor 0.75 / 0.50 / 0.25
```

未加入 plan 明確排除的：

- JPEG compression；
- glare patch；
- uneven illumination；
- crop / occlusion；
- rotation / geometric scale；
- denoising / sharpening rescue；
- threshold sweep；
- morphology cleanup。

### 4. Geometry preservation — PASS

每個 degradation 都在 final 512×512 RGB frame 執行，runner 會 fail if output shape 不再等於 baseline geometry。

這使 frozen manual reference coordinates 可在第一輪 quality study 中合法重用。

### 5. Descriptor contract — PASS

Runner 保存：

- Laplacian variance；
- Tenengrad mean squared gradient；
- Sobel mean gradient magnitude；
- RMS contrast；
- grayscale mean / std；
- RGB mean / std；
- formal clipping fraction。

沒有 source-level 自動挑選「表現最好」的 descriptor，也沒有建立 threshold。

### 6. Manual-reference comparison — PASS

對 primary P002–P010，每個 manual reference class 都與三個 model classes 比較。

保存：

- correct-class coverage；
- all-class comparisons；
- best-wrong class；
- wrong-class-exceeds-correct；
- nearest-distance metrics。

因此 degraded output 若出現 class shift，不會被 post-hoc relabel 隱藏。

### 7. Model self-repeatability is secondary — PASS

Runner另算 degraded mask vs source baseline mask 的 class Dice / IoU 與 foreground overlap，但 manual-reference agreement 與 self-repeatability 是分開保存。

這符合：

```text
model self-consistency != observation correctness
```

### 8. Presence cannot self-certify quality — PASS

Output 同時保留：

- class presence；
- pixel count；
- manual-reference agreement；
- image-quality descriptors。

沒有 `model present => quality sufficient` 的 shortcut。

### 9. Summary accounting — PASS

Primary summary固定依 condition × class 報：

- 9-source model-presence count；
- harmonic / directional coverage distribution；
- distance distribution；
- best-wrong distribution；
- wrong-class-win count；
- baseline-mask Dice / IoU；
- appearance-transition count；
- descriptor distribution。

未定義單一總 confidence。

### 10. Pre-execution dry-run gate exists — PASS

Runner提供 `--dry-run`，以 non-MOHI synthetic fixture exercise：

- condition generation；
- descriptor path；
- ONNX inference；
- mask digest / presence extraction；
- manual-distance comparison path。

但截至本 review，**dry-run 尚未執行**。

## Items that remain runtime-dependent

以下不能靠 source review 宣稱完成：

1. Python syntax / import environment 實際可執行；
2. pinned local ONNX model可正常載入；
3. synthetic dry-run 10 conditions 全部完成；
4. MOHI ZIP / frozen MediaPipe / spatial / annotation / audit-result artifacts均在本機可讀；
5. 90 primary inferences是否完成且 `stop=false`；
6. output JSON 是否成功寫出並可 SHA256 freeze。

因此下一個 evidence action仍是：

```text
local dry-run
→ record dry-run evidence
→ full 90-condition execution
→ hash result before interpretation
```

在完成 dry-run以前，不把 runner描述成 runtime-validated。

## Boundary

本 static review 只證明 implementation source 與 predeclared contract 對齊；不建立 quality threshold、production admission rule 或 Palmistry interpretation validity。

Palmistry 維持 **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**。
