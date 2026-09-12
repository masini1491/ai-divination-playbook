# Palm Detector-to-Detector Agreement Plan

Status: **REFERENCE-ONLY / PREDECLARED / RUNTIME ARTIFACT GATE CLOSED / READY FOR FIRST EXECUTION**

本 Cold plan 凍結 Palmistry observation research 的下一個獨立 evidence node：**detector-to-detector agreement**。

本研究不是 biometric verification，也不是 palmprint identity matching。目的只是在同一張 full-hand source image 上，比較兩個彼此獨立的 hand-landmark implementations 對 source-neutral palm geometry 的觀察差異。

## Research question

在已經 permission-qualified 的 MOHI bounded sample 上：

> 同一張手掌照片交給 pinned MediaPipe Hand Landmarker 與一個獨立的 21-keypoint hand pose model 時，兩者對 wrist / MCP anchors、canonical palm basis 與 21-landmark geometry 的 disagreement 有多大？

這個 node 要回答的是 **observation implementation uncertainty**，不是「哪個 detector 才是真實手掌」。

## Why this node is independent of device-repeatability

MPD-v2 / XJTU-UP 的 device-repeatability 主線目前仍等待 dataset-level permission closure，因此不可先下載或跑 inference。

Detector agreement 不需要那些 datasets；MOHI 已有明確 research / teaching permission，而且目前 150 image entries 的 provenance、runtime compatibility 與 duplicate audit 都已閉合。

因此本研究可在不擴張 MPD-v2 / XJTU-UP authority 的前提下獨立進行。

## Detector A: existing MediaPipe baseline

沿用 MOHI 已經固定並實際執行過的 baseline：

```text
MediaPipe 1.0.1
Hand Landmarker model SHA256:
fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1

running_mode = IMAGE
num_hands = 2
min_hand_detection_confidence = 0.5
min_hand_presence_confidence = 0.5
min_tracking_confidence = 0.5
max working dimension = 1600
```

既有 MOHI result 已證明 150 / 150 image entries 均得到 exactly one candidate。

MediaPipe handedness 仍只當 detector metadata，不取得 anatomical handedness authority。

## Detector B: MMPose / RTMPose-m Hand5

### Selected implementation

第二 detector 選用：

```text
Repository: open-mmlab/mmpose
Release: v1.3.2
Resolved tag commit:
5408bc76f5b848cf925a0d1857899011d8c5b497

Config:
configs/hand_2d_keypoint/rtmpose/hand5/
rtmpose-m_8xb256-210e_hand5-256x256.py

Official checkpoint:
rtmpose-m_simcc-hand5_pt-aic-coco_210e-256x256-74fb594_20230320.pth
```

MMPose repository software license is Apache-2.0.

目前 inspected source 沒有把 external checkpoint binary 的 license 單獨再表述一次，因此本研究不宣稱「repository Apache-2.0 automatically relicenses every external checkpoint artifact」。執行時只使用官方 project 提供的 checkpoint 作 local research inference，不重新散布 checkpoint。

### Why RTMPose-Hand5 is suitable

這個 model 是獨立於 MediaPipe 的 implementation / model family，並以 combined hand datasets 訓練：

```text
COCO-WholeBody Hand
OneHand10K
FreiHand
RHD
Halpe Hand
```

Model output 為 21 個 2D hand keypoints，meta definition 為：

```text
0  = wrist
5  = forefinger1
17 = pinky_finger1
```

在現有 canonical contract 中對應：

```text
L0  = wrist
L5  = index-finger MCP-side root
L17 = little-finger MCP-side root
```

因此可以建立 deterministic semantic correspondence，不需要從 detector output 推測 palm class 或 real identity。

## Frozen RTMPose input adapter

### No upstream hand detector

本研究**不使用** MMPose demo 中的 RTMDet hand detector，也不使用 MediaPipe result 產生 RTMPose crop。

MMPose `inference_topdown()` 在 `bboxes=None` 時，官方 API 會直接使用：

```text
[0, 0, image_width, image_height]
```

作單一 top-down bounding box。

因此 frozen adapter 為：

```text
raw MOHI full-hand image
→ full-image bbox only
→ MMPose TopdownAffine / 256×256 model input
→ RTMPose 21-keypoint output
→ framework-mapped raw-image keypoint coordinates
→ existing canonical palm basis
```

這避免：

```text
MediaPipe → crop → RTMPose
```

這種會污染 detector independence 的路徑。

### RTMPose config behavior

保留 official config，不為結果調參：

```text
input_size = 256 × 256
flip_test = True
mean = [123.675, 116.28, 103.53]
std  = [58.395, 57.12, 57.375]
bgr_to_rgb = True
```

不得因 MOHI outcome 修改 model input size、flip-test、crop rule 或 checkpoint。

## Runtime artifact lock gate

在任何 MOHI RTMPose inference 前，必須先完成並 durable-record：

```text
MMPose == 1.3.2
exact Python version
exact PyTorch version
exact mmcv version
exact mmdet version
exact mmengine version
official checkpoint SHA256
execution device / backend
```

MMPose v1.3.2 upstream dependency ranges目前為：

```text
mmcv >= 2.0.0, < 3.0.0
mmdet >= 3.0.0, < 3.3.0
mmengine >= 0.4.0, < 1.0.0
```

這些 range 不是 reproducibility lock。必須在結果 inspection **之前**解析成 exact runtime versions。

Checkpoint 也必須先從 official OpenMMLab artifact 取得、計算完整 SHA256、寫回本 plan 或其 execution record，之後才可開始 MOHI inference。

`DETECTOR_AGREEMENT_RUNTIME_LOCK.md` 現已 durable-record 並實際驗證：

```text
Platform: Linux / WSL2 / x86_64 / glibc 2.35
Python: 3.9.18
NumPy: 1.26.4
OpenCV package: 4.10.0.84
cv2.__version__: 4.10.0
PyTorch: 1.13.1
TorchVision: 0.14.1
MMCV: 2.0.0
MMDetection: 3.2.0
MMEngine: 0.10.4
MMPose: 1.3.2
setuptools: 80.9.0
MKL: 2020.2
Intel OpenMP: 2023.0.0
chumpy: 0.70
CPU backend
pip check: clean
```

Official checkpoint full SHA256 已閉合：

```text
b74fb5941684fe13c337b8d4fce644293e12903fed5407f8b27921f107dc6003
```

`torch.load(..., map_location="cpu")` 已成功讀取 checkpoint，top-level keys 為 `meta` / `state_dict`。

最後的 frozen-config MMPose model-construction + checkpoint weight-load smoke test 也已在任何 MOHI image 前完成：

```text
resolved installed frozen config = YES
init_model(config, checkpoint, device="cpu") = PASS
model type = TopdownPoseEstimator
device = cpu
MODEL LOAD = PASS
```

因此 runtime artifact gate 已閉合。後續可在不改變任何 frozen protocol 的前提下開始第一輪 MOHI RTMPose execution。

## Frozen source sample

重用既有 MOHI bounded source package，不重新擴張 dataset acquisition：

```text
10 dataset person IDs
3 sessions
5 image entries / session
150 image entries
```

既有 source ZIP SHA256：

```text
6309f2390b0013858928c6c77344b4aa869edc8c0aeb9a61db93b73ae83feec2
```

### Duplicate-aware analysis unit

Integrity audit 已知兩組 byte-identical source duplicates：

```text
P005/S1/01.jpg == P005/S3/02.jpg
P001/S3/03.jpg == P001/S3/05.jpg
```

因此 frozen analysis 分成兩層：

1. **150 image entries**：全部做 decode / execution / output-integrity accounting；
2. **148 unique source-byte representatives**：作 primary cross-detector disagreement distribution。

Unique representative 選法必須 deterministic：

```text
group by source SHA256
→ sort sample_path lexicographically
→ keep first path in each SHA group
```

不得看 detector 結果後再挑 representative。

兩組 duplicate entries 額外作 deterministic duplicate-consistency check；byte-identical source 若在同一 pinned runtime 產生 material 不一致 output，先視為 runtime / serialization integrity 問題，而不是 biological variation。

## Output-validity contract

MediaPipe 與 RTMPose 的 output contract 不同：

- MediaPipe 是 candidate-producing detector；
- RTMPose 在 fixed full-image top-down ROI 下會回傳一個 pose estimate。

因此不得把兩者的「candidate count」直接當同一種 usable-rate metric。

RTMPose geometry 只在以下條件成立時納入 agreement calculation：

```text
source decoded
21 keypoints present
all required 2D coordinates finite
L0 / L5 / L17 present
canonical basis non-degenerate
raw-image mapping available
```

RTMPose keypoint scores全部保存並 descriptive report，但**不在 first study 用 post-hoc score threshold 排除影像**。

若低 score 與 disagreement 有關，只能當 descriptive association，不能在看結果後創造 acceptance cutoff。

## Frozen semantic mapping

對 21 landmarks 使用 index-preserving semantic correspondence：

```text
0: wrist
1..4: thumb chain
5..8: index / forefinger chain
9..12: middle chain
13..16: ring chain
17..20: little / pinky chain
```

Primary canonical anchors：

```text
0, 5, 17
```

如果 execution 時發現 upstream checkpoint / config 的 semantics 與 inspected meta definition 不一致，立即 STOP；不得手動重排來救結果，除非在任何 result inspection 前由 authoritative metadata 證明 mapping correction。

## Frozen per-image agreement metrics

對每一個 primary unique source image，以同一 raw-image coordinate frame 比較 MediaPipe 與 RTMPose：

### Raw-image normalized landmarks

沿用既有 MOHI normalization：

```text
x_norm = x / raw_width
y_norm = y / raw_height
```

對應 index 的 Euclidean delta：

```text
d_i = ||MP_i(norm) - RTM_i(norm)||
```

報告：

- 21-point mean / median / max delta；
- per-keypoint delta distributions；
- L0/L5/L17 anchor mean / max delta。

### Canonical palm basis disagreement

每個 detector 各自用自己的 L0/L5/L17 建立既有 source-neutral basis，再比較：

- canonical-axis angle delta；
- palm width relative difference；
- palm height relative difference；
- canonical 21-landmark mean delta；
- canonical 21-landmark max delta；
- per-keypoint canonical delta。

Canonical coordinate formula與 `NORMALIZATION_CONTRACT_DRAFT.md` / existing MOHI metric path 保持一致，不新增 alternative basis。

### RTMPose score diagnostics

另外 descriptive report：

- 21-keypoint score mean / median / min；
- L0 / L5 / L17 score；
- score 與 cross-detector delta 的 descriptive relationship。

不做 hypothesis fishing，不從這個 bounded sample 推 score cutoff。

## Frozen aggregation order

```text
source integrity
→ runtime / model artifact integrity
→ 150-entry execution accounting
→ duplicate consistency
→ 148 unique-source per-image agreement
→ per-keypoint distributions
→ per-person / per-session heterogeneity
→ pooled descriptive summaries
→ only then qualitative interpretation
```

先保留 per-image / per-keypoint evidence，不得只報一個 pooled mean。

## Directional research questions

本研究是 descriptive，不預設 pass/fail threshold，但在結果 inspection 前固定問題：

1. L0/L5/L17 是否比 fingertip / distal joints 有較小 cross-detector disagreement？
2. 以各 detector 自己 anchors 建 basis 後，canonical disagreement 是否小於 raw normalized disagreement？
3. 某些 palm classes / sessions 是否對 detector choice 特別敏感？
4. RTMPose keypoint score 與 disagreement 是否有明顯 descriptive relationship？
5. 兩個 detector 對 palm width / height / axis orientation 的差異有多大？

任何 observed pattern 都只屬 bounded MOHI + pinned runtimes。

## Stop rules

在 inference 前或 execution 中停止，如果：

- actual runtime identity drift from the closed runtime lock;
- frozen config / checkpoint identity 不再等於已驗證 artifact；
- full-image `inference_topdown()` adapter 無法保留 raw-image output mapping；
- 21-keypoint semantics 無法 authoritative 對應；
- 執行需要 MediaPipe-derived crop 或其他會破壞 detector independence 的補救。

在結果產生後停止 interpretation，如果：

- source SHA / manifest 與既有 MOHI integrity record 不一致；
- runtime artifact identity 與 pre-run lock 不一致；
- duplicate source bytes 產生無法解釋的 material nondeterminism；
- geometry 需要看 outcome 才臨時改 mapping / crop / score threshold。

## Prohibitions

Do **not**:

- 將 cross-detector agreement 解讀為 biometric identity continuity；
- 把其中一個 detector 當 ground truth；
- 用 MediaPipe crop 餵 RTMPose；
- 加入 RTMDet hand detector 改變本 first-study design；
- 看結果後調 keypoint-score threshold；
- 看結果後排除難例；
- 因 disagreement 大就修改 canonical anchors；
- 建立 production admission threshold；
- 把 checkpoint 或 MOHI source images commit 進本 repo；
- 宣稱 MOHI detector agreement 可外推到所有 smartphone images。

## Evidence boundary

若本 study 成功執行，只能建立：

> 在 permission-qualified MOHI bounded sample 上，MediaPipe 1.0.1 Hand Landmarker 與 pinned MMPose / RTMPose-Hand5 對 source-neutral 2D palm geometry 的 bounded detector-to-detector disagreement distribution。

它仍不建立：

- detector ground truth accuracy；
- universal hand-landmark invariance；
- device-to-device repeatability；
- long-term longitudinal stability；
- principal-line segmentation repeatability；
- biometric identity / authentication claims；
- production Palmistry tolerance。

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**.
