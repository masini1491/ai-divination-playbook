# MediaPipe Runtime-only MOHI Comparison — Implementation Lock

Status: **REFERENCE-ONLY / PRE-EXECUTION IMPLEMENTATION LOCK / NO MOHI CROSS-RUNTIME RESULT INSPECTED**

## Purpose

本 lock 固定 controlled reconstructed MediaPipe `1.0.1` vs `1.0.0` MOHI runtime-only comparison 的第一輪 implementation。

Runner：

```text
references/palmistry/mediapipe_runtime_mohi_compare_runner.py
Git blob = b4cd51d0b7c793ab5107e6b84047521d40fdee0d
```

在本 lock 建立時，尚未執行正式 150-entry cross-runtime study，也沒有任何 MOHI cross-runtime metric 可供 inspection。

## Frozen upstream identities

```text
MOHI ZIP SHA256
6309f2390b0013858928c6c77344b4aa869edc8c0aeb9a61db93b73ae83feec2

Hand Landmarker model SHA256
fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1

Phase-0 MediaPipe 1.0.1 identity artifact SHA256
cc31a3d5120663f36b5f6ae47206d53465a38cdf861dd8d3b0f6f46cc023f357

Phase-0 MediaPipe 1.0.0 identity artifact SHA256
e1fb2836891b863bbe8fd5edb311c00482cd7e6c1d950d3666bf2bed330d7485
```

## Runtime-only variable

Controller要求：

```text
Python = 3.12.14 on both sides
NumPy  = 2.5.3 on both sides
OpenCV = 5.0.0 on both sides
non-MediaPipe pip package list = exact-equal
model bytes = exact-equal
input pixel bytes = exact-equal per image
```

Only intended runtime package difference：

```text
baseline   mediapipe = 1.0.1
comparison mediapipe = 1.0.0
```

## Source accounting lock

Runner硬鎖：

```text
manifest entries = 150
unique source-byte representatives = 148
10 dataset person IDs
```

且 byte-identical duplicate groups必須精確重現：

```text
P005/S1/01 == P005/S3/02
P001/S3/03 == P001/S3/05
```

若 source-byte grouping不同，execution停止，不做 post-hoc exclusion。

## Shared raw-frame contract

JPEG source bytes只在 controller 解碼一次：

```text
ZIP bytes
→ cv2.imdecode(..., IMREAD_UNCHANGED)
→ full-frame resize only when max dimension > 1600
→ INTER_AREA
→ explicit GRAY/BGR/BGRA → RGB conversion
→ contiguous uint8 RGB
→ SHA256 over C-order pixel bytes
→ .npy prepared array
```

同一 prepared `.npy` array 由 `1.0.1` 與 `1.0.0` worker共同消費。

EXIF orientation只被 diagnostic-record；runtime workers不得各自從 filename / JPEG bytes decode，因此 EXIF/file-loader behavior不能混入 runtime geometry delta。

## Detector option lock

兩 worker相同：

```text
running_mode = IMAGE
num_hands = 2
min_hand_detection_confidence = 0.5
min_hand_presence_confidence = 0.5
min_tracking_confidence = 0.5
```

不得因任一 runtime candidate count不同而調 threshold。

## Candidate association lock

禁止 candidate list index取得 cross-runtime identity authority。

第一輪 association：

```text
1 vs 1
→ direct one-to-one

2 vs 2
→ evaluate both complete assignments
→ cost = mean raw-normalized L0/L5/L17 anchor distance
→ retain best / second / gap
→ exact-or-numeric tie within 1e-15 => unresolved

candidate-count mismatch
→ unresolved

0 vs 0
→ no target; no fine geometry metric
```

本輪不建立 empirical near-tie cutoff；best/second gap完整保存供後續 interpretation。

## Geometry metric lock

Raw 21-landmark metric使用 detector normalized x/y frame：

```text
per-landmark Euclidean delta in [x/image_width, y/image_height] coordinate pair
raw_21_mean / median / max
L0/L5/L17 anchor mean / max
```

Canonical geometry重新依 `NORMALIZATION_CONTRACT_DRAFT.md` 實作：

```text
L0 = wrist
L5 = index MCP
L17 = little MCP
M = midpoint(L5,L17)
ey = normalize(M-L0)
raw_ex = L5-L17
ex = normalize(raw_ex - dot(raw_ex,ey)*ey), toward index side
width = dot(L5-L17, ex)
height = norm(M-L0)
```

保存：

```text
palm-axis angle delta
projected width relative difference
height relative difference
canonical 21-landmark mean / max delta
```

這裡刻意不 reuse 舊 `mohi_mediapipe_repeatability.py` 的 `norm(L5-L17)` width denominator，避免重複已知 implementation discrepancy。

## Handedness lock

保存 label / score與 cross-runtime label agreement；handedness仍只是 detector metadata，不是 anatomical-side authority。

## Duplicate determinism lock

每個 runtime內部對已知 byte-identical groups檢查：

```text
input pixel SHA exact equal
candidate count exact equal
candidate structures / float outputs exact equal
```

失敗會被保存為 implementation determinism evidence，不會被刪除或當作 independent recapture variation。

## Summary layers

正式 JSON同時保留：

```text
all 150 execution entries
primary 148 unique-source representatives
per-person / per-session primary descriptions
duplicate determinism
per-entry candidate outputs
per-entry association accounting
```

Primary distribution不得把 150 entries冒充 150 independent unique photos。

## Result discipline

正式 execution 後：

1. 先核對 execution accounting；
2. 先對完整 raw result JSON 做 SHA256；
3. 先建立 result-freeze evidence；
4. 才 inspection aggregate / per-entry substantive metrics。

不得先看結果後再調 association、threshold、source exclusion或 compatibility cutoff。

## No threshold

第一輪不產生：

```text
delta < X => compatible
```

也不把 MOHI recapture repeatability直接拿來當 runtime compatibility cutoff。

## Stop rules

Runner fail closed if：

- ZIP/model/Phase-0 artifact SHA drift；
- Python / NumPy / OpenCV identity drift；
- non-MediaPipe pip package list drift；
- manifest != 150；
- unique source bytes != 148；
- duplicate groups drift；
- byte-identical sources decode to different prepared pixels；
- worker input pixel SHA differs from controller；
- model bytes differ；
- runtime version differs；
- canonical basis degenerates for a resolved matched target。

Candidate-count disagreement本身不是 execution stop；它是研究結果，該 entry fine geometry fail closed。

## Boundary

本 implementation lock 不建立 compatibility result、production upgrade policy、anatomical truth、biometric identity或 Palmistry interpretation validity。

Palmistry維持 **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**。
