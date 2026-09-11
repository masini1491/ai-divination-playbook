# Real-image Landmark Repeatability Study｜真實影像地標重複性研究

Status: **REFERENCE-ONLY / CASE A+B EXECUTED｜僅供參考／A+B 已執行**

Evidence baseline: `masini1491/ai-divination-playbook@66697df63e122451136364157d66abf5c88440bc`

Companion tools:

- [`real_image_repeatability_probe.py`](real_image_repeatability_probe.py) — detector-agnostic metric harness。
- [`mediapipe_repeatability_runner.py`](mediapipe_repeatability_runner.py) — Cold MediaPipe research runner；不是 production owner。

本研究把 synthetic normalization / sensitivity work 接到真實掌心照片：

```text
public/free-licensed palm image
→ pinned detector/runtime/model
→ controlled rotate / scale / crop / mirror
→ detect L0 / L5 / L17
→ inverse transform back to baseline-image coordinates
→ anchor drift as palm-width fraction
→ canonical-frame drift
```

本輪取得的數字是 **specific detector + specific model + specific image + specific transform** 的 research evidence；不是 MediaPipe 一般 accuracy 宣稱，也不是 production tolerance。

## 1. Execution provenance

實際 detector study 透過一次性 GitHub Actions research workflow 執行，原因是本地 container 無法取得 MediaPipe runtime/model binary。研究 workflow 在結果擷取後不保留於 final tree。

成功 research run：

```text
GitHub Actions run: 34611890893
head: 66697df63e122451136364157d66abf5c88440bc
runner image: ubuntu-24.04 / 20260907.300.1
Python: 3.12.14
MediaPipe: 1.0.1
OpenCV: 5.0.0
```

Pinned model：

```text
https://storage.googleapis.com/mediapipe-models/hand_landmarker/
hand_landmarker/float16/1/hand_landmarker.task
SHA256: fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1
```

同一 evidence commit 的 normal `Validate Playbook` workflow 亦成功完成（run `34611890817`）。

## 2. Measurement contract

`real_image_repeatability_probe.py` 接收：

```text
baseline L0 / L5 / L17
variant L0 / L5 / L17
known inverse image transform
optional handedness label
```

輸出：

- max / mean anchor displacement ÷ baseline palm width；
- palm-axis angle drift；
- palm-width / palm-height relative error；
- canonical 5×5 palm grid max drift；
- handedness label 是否相對 baseline 改變。

Harness synthetic self-test：

```text
exact rotate+translate + exact inverse
→ max anchor drift = 0
→ max canonical drift = 0

injected 1% wrist displacement
→ recovered max anchor drift = 1.0000%
→ max canonical drift ≈ 1.2532%
```

因此以下 real-image drift 不是 inverse-transform harness 自己製造的已知 round-trip error。

## 3. Case A — single right palm

Source: Wikimedia Commons — `Right Hand Palm.png`

License: CC BY-SA 4.0

Source SHA256：

```text
2456fd263914f7b6c9109edc5056d994c7ca140fad3c567d2edf0f5422a42e22
```

Image geometry：

```text
source: 4011 × 2553 (H×W)
working baseline: 1600 × 1018
scale: 0.3989030167040638
baseline MediaPipe candidates: 1
baseline handedness label: Right
```

### Case A results

| Variant | Max anchor drift | Mean anchor drift | Axis error | Width error | Height error | Max canonical drift | Handedness changed |
|---|---:|---:|---:|---:|---:|---:|---|
| same-pixels rerun | 0.0000% | 0.0000% | 0.0000° | 0.0000% | 0.0000% | 0.0000% | no |
| rotate +10° | 7.7876% | 4.0247% | 2.3574° | 1.4627% | 3.1190% | 7.3708% | no |
| rotate -10° | 4.9099% | 2.7330% | 1.6336° | 0.1099% | 2.7399% | 4.7228% | no |
| scale 0.75× | 1.5502% | 1.1984% | 0.3636° | 1.2164% | 0.1863% | 1.0967% | no |
| scale 1.25× | 2.0721% | 1.7510% | 0.3431° | 2.1027% | 0.5699% | 2.4488% | no |
| crop 3% | 1.7821% | 1.5323% | 0.5408° | 1.0019% | 0.8306% | 1.6727% | no |
| horizontal mirror | 4.2577% | 2.3765% | 0.8753° | 2.3900% | 1.9661% | 2.9833% | yes |

### Case A conclusion

- identical pixels + fixed runtime/model 在本 run 中 deterministic；
- exact inverse transform **不會**讓 detector landmarks 自動變成 invariant；
- 此 fixture 對 ±10° rotation 的 sensitivity 明顯高於 scale / crop；
- +10° 與 -10° 並不對稱，因此不能假設 transform error 只由角度絕對值決定；
- mirror 經 inverse 回 baseline coordinates 後仍有約 2.98% canonical drift；handedness label 由 `Right` 變 `Left`。

這些只描述 Case A，不推廣成 MediaPipe 一般性排序。

## 4. Case B — overlapping two-palm scene

Source: Wikimedia Commons — `Open Palm of the Left Hand, Fingers.jpg`

License: CC BY-SA 4.0

Source SHA256：

```text
63a836d188b30341e6db0b751dcf64a9cc8129c1409b99df1ee843e45cc7a976
```

Image geometry：

```text
source: 3024 × 4032 (H×W)
working baseline: 1200 × 1600
scale: 0.3968253968253968
scene visually contains two overlapping palms
baseline MediaPipe candidates: 1
baseline selected handedness label: Left
```

重要：雖然 scene 有兩隻手，MediaPipe 在 baseline 與本組所有 transforms 都只回傳 **1 candidate**。因此此 case 能測「複雜／重疊 scene 下 detector transform consistency」，但**不能宣稱已驗證 multi-candidate target selection**。

### Case B results

| Variant | Max anchor drift | Mean anchor drift | Axis error | Width error | Height error | Max canonical drift | Handedness changed |
|---|---:|---:|---:|---:|---:|---:|---|
| same-pixels rerun | 0.0000% | 0.0000% | 0.0000° | 0.0000% | 0.0000% | 0.0000% | no |
| rotate +10° | 2.0970% | 1.6808% | 0.2982° | 1.0672% | 1.1963% | 2.1408% | no |
| rotate -10° | 8.4448% | 3.7368% | 3.8073° | 1.5980% | 2.5284% | 8.8829% | no |
| scale 0.75× | 3.3349% | 2.5779% | 1.4808° | 0.0867% | 0.5670% | 4.0574% | no |
| scale 1.25× | 1.7600% | 1.5179% | 0.4854° | 0.1343% | 0.3007% | 1.6918% | no |
| crop 3% | 7.6500% | 4.2483% | 2.2669° | 2.1814% | 4.3393% | 9.2687% | no |
| horizontal mirror | 35.2223% | 27.0413% | 27.9349° | 35.9024% | 2.0861% | 77.3400% | yes |

### Case B mirror failure analysis

Mirror case 很重要：

```text
baseline handedness label = Left
mirrored handedness label = Right
max canonical drift       = 77.34%
```

把 mirrored L0/L5/L17 inverse 回 baseline image 後，三 anchor centroid 與 baseline centroid只相差約 **14 px**，仍落在前景大掌的粗略位置；但 palm-frame shape 本身嚴重改變：

```text
axis error  ≈ 27.93°
width error ≈ 35.90%
```

這不像單純整個 candidate 跳到遠處另一掌；較符合「同一 foreground region 的 landmark geometry 在 mirror + overlapping-hand context 下失穩」的樣子。然而本 runner只保存三個 canonical anchors，且 detector只回一個 candidate，因此**不能證明 scene-local identity continuity**。Production-like判斷必須 fail closed，而不是把這組 mirror geometry 當可靠 observation。

## 5. Cross-case findings

本輪現在有真實影像 evidence 支持：

1. **same pixels deterministic != transform invariant**。
2. detector transform error 可以遠高於前一輪 synthetic 1% anchor-noise example。
3. rotation sensitivity 具有 image/context-specific asymmetry；Case A 是 +10°較差，Case B 是 -10°較差。
4. crop 本身也可能改變 detector landmark geometry；Case B crop 3% 的 canonical drift 約 9.27%。
5. mirrored handedness label flip 是 detector output convention change；它不能直接改寫 anatomical hand-side fact。
6. overlapping-hand scene 可讓 mirror transform 出現極大 geometry instability，即使 inverse transform math 正確。
7. frame-level quality / uncertainty gate 必須使用 detector consistency evidence，不能只看單一 frame 的 landmark confidence。

## 6. Multi-hand target-selection boundary

`mediapipe_repeatability_runner.py` 已實作 research-only scene-local candidate matching：

```text
baseline target = largest normalized hand bbox
variant candidates
→ inverse each candidate L0/L5/L17 to baseline coordinates
→ compare mean anchor distance to baseline target
→ choose minimum-distance candidate
→ preserve second-best distance / separation
```

此機制只允許**同一來源影像的已知 transform**之 scene-local association，不是 biometric identity，也不能跨照片認人。

Case B 因 detector 始終只回一個 candidate，尚未真正 exercised「兩候選排序／ambiguity」分支。下一個 fixture 必須讓 detector 在 baseline 確實輸出 ≥2 hands，才能驗這個 gate。

## 7. What remains unresolved

仍不足以 promotion：

- 至少一個 detector 實際輸出 ≥2 candidates 的 multi-hand fixture；
- 多張不同真實掌型與 capture context 的 transform-consistency distribution；
- same hand / multiple captures 的 pose、distance、lighting、device repeatability；
- MediaPipe version / model-version compatibility matrix；
- detector-to-detector agreement；
- palm-line segmentation endpoint uncertainty 如何與 landmark-frame uncertainty 合成；
- production numeric admission thresholds。

因此目前**不能**把例如 2%、5% 或 10% drift 設成 production cutoff。

## 8. Adoption decision

Palmistry 狀態維持：

**REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**

本輪把 evidence gap 從「沒有真實 detector 數值」推進到「已有兩個 public real-image transform studies，但 sampling / multi-candidate / cross-capture evidence仍不足」。下一個合理 research node 是新增真正被 detector 辨識為 ≥2 hands 的 public fixture，驗 candidate association / ambiguity fail-closed；之後再擴到多 capture / cross-device，而不是直接設 production threshold。
