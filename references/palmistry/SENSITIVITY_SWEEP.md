# Palm Normalization Sensitivity Sweep｜掌面正規化敏感度掃描

Status: **REFERENCE-ONLY / DRAFT｜僅供參考／草案**

Baseline: `masini1491/ai-divination-playbook@41f2a89a1c2e09cb5059fb788331d267a4bd2958`

Companion executable: [`normalization_sensitivity_probe.py`](normalization_sensitivity_probe.py)

本文件量化 draft palm basis 對 `L0 / L5 / L17` landmark 誤差與 mirror-convention error 的敏感度。它只提供 synthetic research evidence，不建立 production tolerance。

## 1. Method

Baseline synthetic palm：

```text
L0  wrist       = (0, 0)
L5  index MCP   = (2, 4)
L17 little MCP  = (-2, 4)
```

因此 baseline palm width = 4、palm height = 4。

對每個 perturbation level：

```text
0.25%, 0.5%, 1%, 2%, 5% of palm width
```

每個 anchor 使用 16 個等角方向；simultaneous sweep 對三個 anchors 做：

```text
16 × 16 × 16 = 4096
```

組 deterministic direction-grid combinations。

Evaluation region 使用 canonical palm rectangle：

```text
x = -0.5, -0.25, 0, 0.25, 0.5
y = 0, 0.25, 0.5, 0.75, 1
```

共 25 個 evaluation points。

重要限制：以下 maxima 只是**configured 16-direction grid 的 deterministic maxima**，不是連續方向空間的數學全域 worst-case bound。

## 2. Simultaneous three-anchor sweep

本地以 companion probe 執行得到：

| Per-anchor perturbation bound | Max palm-axis angle error | Max width scale error | Max height scale error | Max canonical point drift | Max mean point drift |
|---:|---:|---:|---:|---:|---:|
| 0.25% | 0.2865° | 0.500% | 0.500% | 0.527% | 0.250% |
| 0.50% | 0.5729° | 1.001% | 1.000% | 1.059% | 0.500% |
| 1.00% | 1.1458° | 2.005% | 2.000% | 2.135% | 1.000% |
| 2.00% | 2.2906° | 4.019% | 4.000% | 4.341% | 2.003% |
| 5.00% | 5.7106° | 10.112% | 10.000% | 11.445% | 5.075% |

### Interpretation

在這個對稱 synthetic geometry 中，小誤差區間大致呈近線性傳遞；但多 anchor 誤差可疊加。

因此不能用：

```text
one anchor ≈ 1% error
```

推論整個 canonical frame 也只有 1% error。

以此 fixture 為例，三個 anchors 各允許 1% palm-width bounded perturbation 時，direction-grid 最大 canonical point drift 已約 2.135%。

5% anchor-level perturbation 時，最大 drift 約 11.445%，已足以讓細 region / boundary mapping 顯著不穩定。

這仍不能直接轉成 production acceptance threshold，因為真實 landmark error distribution、correlation、pose、camera 與 palm shape 尚未被驗證。

## 3. Single-anchor sensitivity at 1%

| Anchor | Max axis-angle error | Max width error | Max height error | Max canonical point drift |
|---|---:|---:|---:|---:|
| `L0 / wrist` | 0.5729° | 0.005% | 1.000% | 1.282% |
| `L5 / index MCP` | 0.2865° | 1.001% | 0.500% | 1.041% |
| `L17 / little MCP` | 0.2865° | 1.001% | 0.500% | 1.041% |

這支持目前 draft geometry 的角色分工：

- `L0` 對 longitudinal axis / palm-height 更敏感；
- `L5 / L17` 對 transverse scale / palm-width 更敏感；
- 三者都不是可忽略的 anchor。

這只是本 fixture 的 sensitivity shape，不代表所有真實手型具有相同數值。

## 4. Mirror-convention failure

若 detector-only mirror 應該 inverse 卻被漏掉，等價於 canonical：

```text
x → -x
```

在 `x ∈ [-0.5, 0.5]` 的 palm span 上：

```text
max canonical point drift  = 1.0 canonical unit = 100%
mean grid drift            = 0.6 canonical unit = 60%
```

因此 mirror convention mismatch 不是一般 small-noise problem，而是**semantic frame inversion**。

這使以下 gate 成為必要條件，而不是 optional metadata：

```text
anatomical hand side
camera/selfie mirroring convention
model mirrored_for_model state
inverse mirror applied state
```

只要上述 lineage 不完整，fine side-specific / region-specific mapping 應 fail closed。

## 5. What is now supported

現在已有 executable synthetic evidence 支持：

1. ideal geometry invariance probe 的公式沒有明顯 transform bug；
2. anchor noise 會可量化地傳入 axis、scale 與 canonical position；
3. multi-anchor errors 會疊加，不能只看單 landmark confidence；
4. mirror convention error 的影響量級遠高於一般小 landmark perturbation；
5. future admission gate 應考慮 **frame-level uncertainty**，而不是只保存每個 landmark 的 confidence。

## 6. What is still not supported

本 sweep **沒有**建立：

- MediaPipe 在同一張真實 palm image 的 repeatability distribution；
- 同一手不同拍攝距離、旋轉、光照、鏡頭的 landmark repeatability；
- left/right hand 的實際 error asymmetry；
- different hand-shape aspect ratio sensitivity；
- camera/selfie mirroring auto-detection correctness；
- perspective / foreshortening 下的 perturbation distribution；
- segmentation line endpoint uncertainty；
- production numeric threshold。

因此不能說：

```text
MediaPipe error < 1% => production-safe
```

也不能把 2.135% 當 production cutoff。

## 7. Research implication

下一個最有價值的 node 已從純 synthetic math 轉為：

**real-image landmark repeatability study**。

建議最小設計：

```text
same public/free-licensed palm image
→ repeated detector runs / deterministic-version check
→ controlled image transforms (scale / rotate / crop / mirror)
→ compare L0/L5/L17 after transform inversion
→ express anchor displacement as palm-width fraction
→ feed observed displacement into this sensitivity framework
```

若同一 detector/version 本身 deterministic，下一層再做：

```text
same hand / multiple captures
→ pose / distance / lighting / device variation
```

這一層完成前，Palmistry 仍維持：

**REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**
