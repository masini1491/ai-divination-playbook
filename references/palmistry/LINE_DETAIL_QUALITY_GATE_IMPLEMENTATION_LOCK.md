# Principal-line Line-detail Quality Gate — Implementation Lock

Status: **REFERENCE-ONLY / PRE-EXECUTION IMPLEMENTATION LOCK / NO RESULT INSPECTED**

## Purpose

本文件在 `LINE_DETAIL_QUALITY_GATE_PLAN.md` 之後、任何 MOHI quality-gate result 執行之前，固定第一版 executable implementation contract。

Runner：

```text
references/palmistry/line_detail_quality_gate_runner.py
```

Pinned runner blob SHA：

```text
d0f5580af5f10942c9227cb7522df1f430dd3467
```

本 lock 不代表 runner 已通過 full MOHI execution；它只凍結 execution 前的實作選擇，避免看到結果後再改 degradation / descriptor / primary-source accounting。

## Frozen upstream evidence

Runner hard-lock：

```text
frozen manual annotation SHA256
= 51c4886e20cb9aee2d660fe1ca39f25b927398261478c013090ab5d611858041

frozen anatomical-audit result SHA256
= 6f95828b70b388028a46ee1879835d432d9dd695bdbbdd1f2656b6ebf3572284

frozen spatial-control raw SHA256
= ba65456e3c7c3a645a4000c721961d0f600b46541ffc7e7566525b99a55f87e7

manual-reference comparison tolerance
= 8 px in corrected 512×512 frame
```

Full execution 必須先 reproduce 每張 source 的 corrected baseline input SHA 與 baseline model-mask SHA；任何 drift 直接 stop。

## Primary / sentinel accounting

Primary quantitative set 固定為：

```text
P002/S1/01.jpg
P003/S1/01.jpg
P004/S1/01.jpg
P005/S1/01.jpg
P006/S1/01.jpg
P007/S1/01.jpg
P008/S1/01.jpg
P009/S1/01.jpg
P010/S1/01.jpg
```

共 9 張。

`P001/S1/01.jpg` 只能透過 explicit `--include-p001-sentinel` 加入 descriptive execution。即使加入，runner 也**不計算 P001 manual-reference quality metric**，因為其 frozen manual trace 已被 observer 回報為 reference-quality-confounded。

因此：

```text
primary execution = 9 × 10 conditions = 90 inferences
optional sentinel = 1 × 10 conditions = 10 additional inferences
```

P001 永遠不進 primary aggregate。

## Frozen condition contract

每張 primary source 固定十個 512×512 conditions：

```text
baseline
blur sigma 1.5 px
blur sigma 3.0 px
blur sigma 6.0 px
resolution 256→512
resolution 128→512
resolution 64→512
contrast factor 0.75
contrast factor 0.50
contrast factor 0.25
```

### Gaussian blur

在 final 512×512 RGB frame 執行 isotropic Gaussian blur。

Kernel：

```text
radius = ceil(3 × sigma)
kernel = 2 × radius + 1
border = BORDER_REFLECT_101
```

### Resolution destruction

```text
512 → target side：INTER_AREA
 target → 512：INTER_LINEAR
```

不 crop、不 rotate、不 translate、不 mirror。

### Contrast compression

```text
I' = 127.5 + factor × (I - 127.5)
```

先於 float domain 計算，之後才 clip 到 8-bit legal range；保留 formal clipping fraction。

## Descriptor implementation

固定保存：

```text
laplacian_variance
= variance of 3×3 CV_32F Laplacian on grayscale 0..255

tenengrad_mean_squared_gradient
= mean(Sobel_x² + Sobel_y²), 3×3, grayscale 0..255

sobel_mean_gradient_magnitude
= mean(sqrt(Sobel_x² + Sobel_y²)), grayscale 0..255

rms_contrast_0_1
= grayscale standard deviation / 255

gray mean / std
RGB channel mean / std
formal clipping fraction
```

這些 descriptors 是 manipulation / observability evidence features，不是 admission threshold。

不得在 result inspection 後刪除較弱 descriptor，只留下相關性最高者。

## Frozen comparison contract

對 P002–P010：

1. 每個 manual reference class 都與 model `heart/head/life` 三類比較；
2. correct-class 仍為 primary comparison；
3. best-wrong class / wrong-class-exceeds-correct 也保留，禁止 post-hoc relabel；
4. 保存：
   - model-on-reference coverage；
   - reference-on-model coverage；
   - harmonic coverage；
   - median model→reference distance；
   - median reference→model distance；
5. model self-repeatability 另外保存 degraded mask vs source baseline mask 的 class Dice / IoU；
6. foreground / class presence 與 pixel count 分開保存。

Manual-reference agreement 是 primary evidence；baseline-model Dice 只是 secondary implementation stability evidence。

## Summary contract

Primary summary 依每個 condition × class 報：

- model presence count；
- correct harmonic coverage distribution；
- directional coverage distributions；
- nearest-distance distributions；
- best-wrong harmonic distribution；
- wrong-class-exceeds-correct count；
- baseline-mask Dice / IoU；
- appearance-transition count；
- quality-descriptor distributions。

不把這些量壓成單一總 confidence。

## Dry-run gate

第一次 full MOHI execution 前必須先執行：

```text
--dry-run
```

Dry-run 使用 synthetic non-MOHI RGB fixture，只驗證：

- 10-condition generation；
- 512×512 geometry preservation；
- descriptor finite/schema；
- ONNX inference contract；
- mask digest / class-presence extraction；
- manual-distance comparison code path。

Dry-run 結果不屬於 MOHI evidence，也不能用來調整 degradation levels。

## Stop rules

Full execution 必須 stop if：

- frozen annotation / audit-result / spatial-result SHA drift；
- source set/order drift；
- corrected baseline input SHA 無法 reproduce；
- baseline mask SHA 無法 reproduce；
- primary P002–P010 任一 manual class 不再是 frozen `observable`；
- condition 改變 512×512 geometry；
- logits / descriptor 出現 non-finite；
- execution accounting 不等於 9 primary sources × 10 conditions。

不得透過 threshold sweep、sharpening、denoising、morphology cleanup 或 source removal rescue failure。

## Evidence boundary

本 implementation lock 不建立：

- production blur threshold；
- production `line_detail` cutoff；
- universal camera-quality score；
- model correctness on degraded images；
- Palmistry interpretation validity。

Palmistry 維持 **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**。
