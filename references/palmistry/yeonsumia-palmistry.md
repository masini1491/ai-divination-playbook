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

## Rectification implementation review

`code/rectification.py` 的 current implementation：

1. 先 `cv2.flip(image, 1)`；
2. MediaPipe Hands 設 `max_num_hands=1`；
3. 使用 21 個 hand landmarks；
4. 將全部 21 點 fit 到 hard-coded `pts_target_normalized`；
5. `cv2.findHomography(..., cv2.RANSAC, 5.0)`；
6. `cv2.warpPerspective` 回原 image width / height。

這是一個可重現的 project implementation，但下列都屬**project-specific choice**：

- hard-coded 21-point target template；
- RANSAC threshold `5.0`；
- source-image pre-flip；
- full-hand homography 使用所有 finger landmarks。

因 finger articulation 會改變 distal landmarks，而 Palmistry 主要 observation region 是 palm，本 Playbook 不把「21 點全部 fit 到單一 template」自動升格成 canonical palm coordinate definition。

## Downstream implementation coupling

`code/tools.py` 還使用 HSV heuristic 做 background removal：

```text
lower = [0, 20, 80]
upper = [50, 255, 255]
```

並把 rectified image resize 到固定 256×256。

`code/classification.py`：

- 對 segmentation skeleton 建 graph；
- 依方向 / length heuristic 列舉 candidate lines；
- 以 24-dimensional feature + K-means cluster centers 選三條線。

`code/measurement.py` 則再次跑 MediaPipe，用 landmarks 計算 heart/head/life 的 line-length threshold，再接 palmistry-style文字敘述。

因此整條 pipeline 的 detection / classification / measurement 與該資料集、固定 template、cluster centers、threshold 有明顯耦合。

## Authority boundary

本來源沒有建立可追溯的傳統手相 interpretation authority；它的主要價值是 computer-vision / geometry pipeline。

不得因 repository 名稱或 README 使用 `Palmistry` 就推定其 line class / length measurement 已經證明任何性格、命運、健康或事件預測規則。

尤其 `measurement.py` 的 interpretation strings 不應取得 rule authority；其 value 在於「landmark-relative measurement 可以如何被實作」，而不是其中的 fortune statements。

## Limitations / do-not-assume

- README 展示 pipeline，但本輪沒有建立跨資料集 accuracy / robustness evidence；
- hard-coded 21-point homography target 不等於 source-neutral palm coordinate system；
- HSV skin/background threshold 不應預設對所有膚色、lighting、camera processing 有效；
- pre-flip / handedness convention 必須與 anatomical side 分離；
- 不把 model output 自動當 ground-truth Palm Observation Fact；
- 不把 line length 本身直接映射成 interpretation；那層必須由獨立 tradition source 負責。

## Adoption

**REFERENCE-ONLY**

保留為 observation pipeline / rectification 研究參考，不升格為 canonical detector、coordinate system 或 interpretation rule。
