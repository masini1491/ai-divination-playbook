# Device / Capture-condition Repeatability — Predeclared Research Plan

Status: **REFERENCE-ONLY / PREDECLARED EMPIRICAL PLAN / NO PRODUCTION THRESHOLD / NO BIOMETRIC IDENTITY CLAIM**

## Purpose

本 node承接已 boundedly closed 的：

- observation uncertainty-composition contract；
- MediaPipe `1.0.1` vs `1.0.0` runtime-only 2D portability；
- capture / mirroring / anatomical-side deterministic lineage contract。

下一個 empirical question是：

> 在固定 detector runtime/model與明確 capture-lineage下，同一隻手以不同實體拍攝裝置、不同 session重拍時，raw landmark / anchor / canonical geometry的 repeatability分布如何？

本研究不是 biometric identification、authentication或跨人員 matching研究。

## Research boundary

本 node只研究 observation repeatability，不回答：

- 這些 geometry能不能識別一個人；
- 哪個 device「比較準」；
- production admission threshold；
- Palmistry interpretation truth；
- medical / physiological inference。

Dataset person / hand labels只用於已知 repeated-capture grouping，不作 identity inference。

## Primary variable

第一輪主要變因：

```text
physical capture device
```

必須固定：

```text
same explicit anatomical hand
same detector runtime
same Hand Landmarker model bytes
same detector options
same EXIF-normalization policy
same model-mirror policy
same geometry contract
```

Capture pose / distance / illumination在第一輪 baseline block內盡量控制；capture-condition perturbations另分 block，不與 pure device comparison混在同一 primary contrast。

## Minimum study design

### Devices

至少兩個不同實體拍攝裝置：

```text
D1
D2
```

Device record只保存研究所需欄位，例如：

```text
device_id: D1 | D2
manufacturer/model: optional research note
camera_role: rear | front | webcam | other
```

不得保存 serial、IMEI、MAC、account id或其他 device-unique identifier。

### Anatomical hand

同一 participant固定同一隻手完成整個 primary block。

Side authority來源：

```text
explicit_bodily_self_report
```

記錄：

```text
anatomical_side = left | right
side_authority = explicit_bodily_self_report
```

Detector handedness不得取代此欄位。

### Sessions and captures

Primary minimum：

```text
2 devices
× 3 sessions
× 5 captures per device per session
= 30 image entries
```

Session應在不同時間重新擺位；不要求不同日期，但至少要真正中斷並重新建立 capture setup，避免把 burst frame當 repeated capture。

每一 capture都需重新放下再抬手 / 重新 framing，不使用 video連續抽幀代替。

## Primary baseline capture block

兩個 device都使用相同操作目標：

```text
palm-facing camera
near-frontal
fingers naturally open
whole palm + wrist base + MCP region visible
no accessory covering palm ROI
no deliberate hand pressing/stretching
ordinary diffuse indoor light
no beauty filter / portrait blur / AI enhancement if controllable
native still-photo mode
```

Distance不要求毫米級精密，但兩 device應使用同一 nominal distance target；建議第一輪使用約 `35 cm`，並以 capture note記錄而不是把 nominal number當 ground truth。

Background盡量簡單且與手掌有對比。

## Capture-lineage record required per image

每一 image entry至少保存：

```text
file_id
source_file_sha256
session_id
capture_index
device_id
camera_role
anatomical_side
side_authority
preview_mirrored: true | false | unknown | not_applicable
stored_file_mirror_state: mirrored | not_mirrored | unknown
exif_orientation_present: true | false
exif_orientation_code: 1..8 | unknown
exif_transform_applied: true | false
mirrored_for_model: true | false
inverse_model_mirror_applied: true | false | not_applicable
capture_condition_block
```

若某 capture-lineage欄位無法知道，使用 `unknown`，不得由 detector handedness反推。

## EXIF / metadata minimization

本研究可以讀取 task-relevant EXIF orientation，但不保存完整 EXIF dump。

不得寫入研究 artifact：

- GPS；
- exact capture location；
- camera serial；
- user/account identifiers；
- unrelated EXIF metadata。

若 source file含這些資料，分析 pipeline只抽取 orientation等 task-required欄位。

## Detector lock

第一輪 detector contract固定：

```text
MediaPipe Tasks runtime = 1.0.1
Hand Landmarker model SHA256 = fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1
running_mode = IMAGE
num_hands = 2
min_hand_detection_confidence = 0.5
min_hand_presence_confidence = 0.5
min_tracking_confidence = 0.5
```

Runtime只選一個，不在此 node比較版本。

Controller必須先建立單一 normalized RGB pixel representation，再餵同一 locked runtime；不得讓 device comparison混入不同 decoder / transform path。

## Geometry outputs

沿用 current normalization contract：

```text
L0  = wrist
L5  = index MCP
L17 = little MCP
M   = midpoint(L5, L17)
ey  = normalize(M - L0)
raw_ex = L5 - L17
ex = orthogonalized index-side axis
width  = dot(L5 - L17, ex)
height = norm(M - L0)
```

至少輸出：

```text
raw landmark pairwise distance summaries
L0/L5/L17 anchor distance
axis-angle difference
width relative difference
height relative difference
canonical landmark mean distance
canonical landmark max distance
```

Handedness label / score只作 metadata，不進 anatomical-side authority。

## Pair families

### P1 — within-device / within-session

同一 device、同一 session的 5 captures：

```text
C(5,2) = 10 pairs per device/session
2 devices × 3 sessions × 10 = 60 pairs
```

用途：估計短時間 repeated-capture baseline。

### P2 — cross-device / within-session

同一 session的 D1五張與 D2五張 all-pairs：

```text
5 × 5 = 25 pairs per session
3 sessions × 25 = 75 pairs
```

用途：觀察 device change是否引入比 within-device baseline更大的 geometry spread。

不把 capture index `01`與另一 device `01`視為自然 matched pair，除非未來 protocol另外建立同步 capture procedure。

### P3 — within-device / cross-session

同一 device在三個 session間：

```text
3 session-pairs × 25 image-pairs × 2 devices = 150 pairs
```

用途：分離 session/reposition effect與 device effect。

## Primary summaries

各 pair family至少報：

```text
n
mean
median
p10
p90
p95
min
max
std
```

並依 metric分開，不壓成一個 universal repeatability score。

另報：

```text
candidate-count distribution
unresolved-target count
anatomical-side provenance completeness
capture-lineage unknown counts
per-device / per-session summaries
```

## Device-effect descriptive contrasts

第一輪只做 descriptive comparison，不選 cutoff。

至少比較：

```text
P2 cross-device within-session
vs
P1 within-device within-session
```

以及：

```text
P2 cross-device within-session
vs
P3 within-device cross-session
```

可以報 ratio / delta of medians or means，但不得從同一小樣本 post-hoc產生 production acceptance threshold。

## Capture-condition extension blocks

只有 primary 30-image baseline block完成後才進下一層。

可分別新增 single-variable blocks，例如：

```text
distance: near / baseline / far
illumination: diffuse baseline / dim / uneven
pose: frontal / mild oblique
camera role: rear / front
```

每個 extension一次只改一個主要因素；不把 blur、distance、light、pose同時混在一個 label。

Front-camera block必須額外記錄：

```text
preview_mirrored
stored_file_mirror_state
EXIF orientation
```

以 empirical驗證前一個 B3 deterministic contract在真實 app/device pipeline中的 lineage assumptions。

## Stop / exclusion rules

Formal run前 predeclare以下 fail-closed exclusions：

1. source file SHA重複時，保留 manifest entry但 primary independent-source summary只取一個 representative；
2. anatomical side未由 explicit/trusted source確認 → side-dependent analysis unresolved，但 source-neutral geometry可保留；
3. model-only transform lineage unknown → detector-derived mapped geometry unresolved；
4. EXIF normalization state不明且會影響 coordinate frame → geometry unresolved；
5. palm ROI materially cropped / severe occlusion → 該 capture標記 quality insufficient，不用降低門檻 rescue；
6. detector candidate count為 0 → observation unresolved，不補點；
7. multi-hand target無法可靠指定 → target unresolved，不用 candidate index猜。

## Data-quality fields

每張 capture至少人工/程序保存：

```text
palm completeness
focus state
lighting state
glare state
material occlusion
pose / foreshortening state
```

這些只作 descriptive stratification，不在第一輪建立 production quality threshold。

## Predeclared closure criterion

B2第一輪可 boundedly close「two-device controlled baseline characterization」必須同時滿足：

```text
2 devices present
3 true repositioned sessions
5 captures/device/session
all 30 source entries accounted for
capture-lineage fields recorded or explicitly unknown
raw source SHA frozen before substantive inspection
locked detector/model provenance reproduced
P1/P2/P3 summaries completed
no production threshold inferred
```

Closure只代表：

> 這個 bounded two-device repeated-capture sample的 device/session geometry variability已被量測與描述。

不代表 arbitrary device家族、所有 camera app或 production portability已驗證。

## Artifacts expected

預期流程：

```text
DEVICE_CAPTURE_REPEATABILITY_PLAN.md
DEVICE_CAPTURE_REPEATABILITY_CAPTURE_PROTOCOL.md
→ private/local 30-image source set + manifest
→ formal runner implementation lock
→ static review
→ formal execution
→ raw-result SHA freeze
→ substantive results
→ bounded node closure / roadmap update
```

第三方或真實使用者照片不得 commit進 public repo。

## Boundary

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**。
