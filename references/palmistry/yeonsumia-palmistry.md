# Source Dossier｜yeonsumia/palmistry

Status: **REFERENCE-ONLY｜僅供參考**

Repository: `yeonsumia/palmistry`

Reviewed revision: `17610c3f031ee312d3352116eefff9b833e9cafb`

License: Apache-2.0

## What it is

`Fortune On Your Hand: View-Invariant Machine Palmistry` 是一個 principal-line detection pipeline。README 將流程拆成：

```text
palm rectification
→ principal-line detection
→ line classification
→ line-length measurement
```

其 palm rectification 使用 MediaPipe landmarks，principal-line detection 使用 deep-learning model，分類使用 K-means，並以 landmarks 輔助量測主線長度。

## Relevant value

適合作為未來 Palmistry observation layer 的 pipeline decomposition 參考：

- tilted / rotated palm normalization；
- landmark-guided rectification；
- principal-line segmentation；
- line classification；
- geometric measurement。

這類 decomposition 與本 Playbook 的 `Objective Observation → Palm Observation Fact` 邊界相容。

## Authority boundary

本來源沒有建立可追溯的傳統手相 interpretation authority；它的主要價值是 computer-vision / geometry pipeline。

不得因 repository 名稱或 README 使用 `Palmistry` 就推定其 line class / length measurement 已經證明任何性格、命運、健康或事件預測規則。

## Limitations / do-not-assume

- README 展示 pipeline，但本輪沒有建立跨資料集 accuracy / robustness evidence。
- 不把其 model output 自動當作 ground-truth Palm Observation Fact；若未來 reuse，仍需本專案自己的 image-quality / confidence / fail-closed contract。
- 不把 line length 本身直接映射成 interpretation；那層必須由獨立 tradition source 負責。

## Adoption

**REFERENCE-ONLY**

保留為 observation pipeline 參考，不升格為 canonical detector 或 interpretation rule。
