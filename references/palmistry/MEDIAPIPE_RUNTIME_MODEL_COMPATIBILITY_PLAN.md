# MediaPipe Runtime / Hand-Landmarker Model Compatibility — Predeclared Plan

Status: **REFERENCE-ONLY / PREDECLARED RESEARCH PLAN / NO PRODUCTION THRESHOLD**

## Purpose

本 Cold plan 凍結 Palm Observation geometry 的 runtime/model portability 問題：

> 在相同 source images、raw-frame policy、thresholds、target-selection rule 與 canonical geometry contract 下，改變 MediaPipe runtime 或 Hand Landmarker model artifact 時，candidate count、21 landmarks、L0/L5/L17 anchors、palm axis / width / height 與 handedness metadata 會漂移到什麼程度？

本研究不是 detector benchmark，也不決定 production runtime。

## Why this node remains open

目前核心 Palmistry geometry evidence高度依賴既有 pinned baseline：

```text
MediaPipe runtime reported by research evidence = 1.0.1
Python                                      = 3.12.14
OpenCV                                      = 5.0.0
Hand Landmarker model SHA256
= fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1
```

已完成的 MOHI、GTEA、transform、detector-agreement studies 都證明：

- raw-frame policy 會 materially 影響 geometry interpretation；
- detector choice 會影響 palm scale / canonical shape；
- candidate count、handedness metadata 與 target association 不能假設跨 implementation invariant。

因此 runtime/model version drift 必須成為 explicit provenance，而不能被視為 harmless dependency update。

## Upstream release observation motivating an EXIF gate

Public upstream source：

```text
repository: google-ai-edge/mediapipe
GitHub release: v1.0.0
published: 2026-07-28
```

該 release note 同時記錄：

- internal MediaPipe version bump to `0.10.36`；
- Python Task API新增 EXIF orientation support。

因此本研究**不得**假設：

```text
GitHub release tag
== installed Python package version string
== identical raw-frame orientation behavior
```

特別是目前本 repo evidence 記錄的 runtime string為 `1.0.1`，所以正式 compatibility execution 前必須先完成 runtime identity reconciliation，而不是只靠字串名稱推定 upstream revision。

## Phase 0 — Runtime identity reconciliation gate

任何 cross-version inference 前，先 durable-record baseline與 comparison runtime：

```text
python version
mediapipe.__version__
installed distribution metadata
wheel filename / source channel when available
wheel or installed-package artifact digest when reproducibly obtainable
platform / architecture
OpenCV version
NumPy version
MediaPipe Tasks Python API import path
upstream tag / commit mapping if defensibly resolvable
```

若 installed package version無法一對一映射到 upstream tag / commit：

```text
upstream_revision = unresolved
```

而不是猜測。

### Raw-frame identity check

每個 runtime先對固定 JPEG fixture記錄：

- file byte SHA256；
- decoded image `[h,w]`；
- EXIF orientation presence；
- Task API input path；
- whether API implicitly applies orientation；
- geometry frame supplied to detector。

若不同 runtime把同一 source bytes解讀到不同 pixel frame，必須先標為：

```text
raw_frame_policy_mismatch
```

不能直接把 landmark delta解讀成 detector geometry disagreement。

這一點延續 detector-agreement EXIF diagnostic 的既有教訓。

## Study decomposition

Runtime compatibility與 model compatibility必須分開。

### Study A — Runtime-only comparison

Hold fixed：

```text
same Hand Landmarker model bytes
same model SHA256
same source image bytes
same explicit decoded pixel frame
same running mode
same num_hands
same detection / presence / tracking thresholds
same target-association logic
same canonical L0/L5/L17 geometry implementation
```

Vary only：

```text
MediaPipe runtime / package identity
```

### Study B — Model-only comparison

Hold fixed：

```text
same MediaPipe runtime
same source images
same raw-frame policy
same detector options / thresholds
same association / geometry code
```

Vary only：

```text
Hand Landmarker model artifact
```

Study B只能在 comparison model具有清楚的 official artifact identity、full SHA256與相容 task contract後開啟。

若找不到合法、可重現、task-compatible的 alternative model artifact，Study B維持 `BLOCKED`，不得拿未知模型替代。

## Comparison target selection

### Baseline

Baseline固定使用 repo既有研究 runtime/model identity，不重定義 threshold。

### Comparison runtime

**本 plan 不預先猜一個 package version。**

先完成 Phase 0 identity reconciliation，再選一個明確可安裝、可固定 bytes / metadata、且能載入相同 Hand Landmarker artifact的 comparison runtime。

優先順序：

1. 與 baseline相鄰、可重現的 released runtime；
2. 若相鄰版不可安裝，再選最近可重現 release；
3. 不使用 nightly / mutable latest。

Comparison runtime identity必須在看 MOHI/GTEA comparison results以前另行 lock。

## Primary source set

第一輪 runtime-only compatibility優先 reuse permission-qualified MOHI full-hand evidence：

```text
10 dataset person IDs
3 sessions
5 captures / session
150 image entries
```

已知 byte-identical duplicate groups仍按既有 integrity record保存，不冒充 150 unique independent photos。

### Analysis units

分兩層：

1. **execution accounting**：150 image entries；
2. **primary distribution**：148 unique source-byte representatives。

Byte-identical duplicates另用於 deterministic reproduction check。

## Frozen detector options

沿用既有 MOHI baseline：

```text
running mode = IMAGE
num_hands = 2
min detection = 0.5
min presence  = 0.5
min tracking  = 0.5
```

不得因 comparison runtime candidate count改變而調 threshold。

## Primary comparison metrics

### 1. Candidate-count agreement

每張記錄：

```text
baseline candidate count
comparison candidate count
count equal: yes/no
```

Aggregate：

- exact candidate-count agreement rate；
- `0↔1`, `1↔2`, `0↔2` transition counts；
- no post-hoc source exclusion。

### 2. Candidate association

若兩 runtime都只有一個 candidate，直接比較。

若任一 runtime回傳多 candidate：

- 不用 candidate list index當 identity；
- 使用既有 scene-local geometry association rule或 explicit best/second accounting；
- association unresolved時，target-specific fine geometry fail closed。

### 3. Raw 21-landmark disagreement

對 resolved one-to-one target比較：

- per-landmark raw x/y normalized delta；
- 21-point mean / median / max Euclidean delta；
- L0/L5/L17 anchor mean / max delta。

Raw normalization contract必須與既有 detector-agreement study一致，避免換 scale後假裝可直接比較。

### 4. Canonical frame disagreement

每個 runtime各自由 L0/L5/L17建構 canonical frame，保存：

- palm-axis angle delta；
- palm-width relative difference；
- palm-height relative difference；
- canonical 21-landmark mean / max delta。

Canonical metric不得與 raw normalized metric直接比較大小，因為 scale不同。

### 5. Handedness metadata behavior

記錄：

- label；
- score若可得；
- baseline/comparison label agreement。

但 handedness只作 detector metadata，不取得 anatomical-side authority。

### 6. Duplicate determinism

對既知 byte-identical groups，兩個 runtime各自檢查 exact reproduction：

```text
same source bytes
→ same runtime
→ keypoints / scores是否 exact equal
```

這是 implementation determinism evidence，不是 independent recapture repeatability。

## Predeclared directional questions

### Q1. Candidate count是否跨 runtime保持？

若 150 entries並非全部 count-equal，完整保存 transition；不得把 transition frame排除後只比較成功子集。

### Q2. L0/L5/L17是否比 full 21-point更穩定？

沿用 detector-agreement教訓：不得因 anchors定義 canonical frame就用 canonical-space結果替 anchors背書。

先看 raw normalized anchor disagreement，再看 full set。

### Q3. Palm axis是否比 width / height更 portable？

既有 MediaPipe-vs-RTMPose evidence顯示 axis與scale可呈不同 disagreement regime；runtime-only study需重新回答，不能直接外推。

### Q4. EXIF/raw-frame handling是否造成 apparent giant drift？

任何 suspicious ~90° axis change、swapped image dimensions或 systematic orientation shift，先診斷 frame policy，不先解讀為 runtime detector regression。

### Q5. Handedness metadata是否改變？

任何 label shift保留為 metadata compatibility evidence，但不等於 anatomical side改變。

## Summary reporting

Primary 148 unique-source distribution至少報：

- candidate-count agreement；
- raw 21-point mean / median / max delta summaries；
- anchor mean / max delta；
- axis-angle delta；
- width / height relative difference；
- canonical 21-point mean / max delta；
- handedness agreement；
- per-person / per-session descriptive heterogeneity。

150-entry execution accounting與148 unique-source primary analysis不得混寫。

## No automatic compatibility threshold

第一輪只建立 distribution，不建立：

```text
runtime delta < X => compatible
model delta < Y => compatible
```

也不得用 baseline自身 within-session variation直接當 cutoff，因為：

```text
recapture variation
!= runtime-version variation
!= detector-to-detector variation
```

這三種 uncertainty source必須分開保存。

## Stop rules

Stop if：

- baseline runtime/model identity不能重現；
- comparison runtime identity unresolved到無法 durable-record；
- same model bytes無法被兩 runtime共同載入，卻仍試圖稱為 runtime-only study；
- raw-frame orientation policy不同且無法顯式 reconciliate；
- thresholds / num_hands / running mode被迫改變；
- source package / manifest integrity drift；
- target association需要 candidate index identity；
- comparison必須靠 post-hoc source removal才完成。

## Evidence boundary

有利結果只支持：

> 在指定 source set、model bytes、options與 raw-frame contract下，兩個 pinned runtime產生相近 observation geometry。

不支持：

- 所有未來 MediaPipe版本自動相容；
- anatomical ground truth；
- production upgrade policy；
- biometric identity；
- Palmistry interpretation validity。

Palmistry維持 **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**。
