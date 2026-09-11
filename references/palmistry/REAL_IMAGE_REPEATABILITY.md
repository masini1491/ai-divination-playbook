# Real-image Landmark Repeatability Study｜真實影像地標重複性研究

Status: **REFERENCE-ONLY / PARTIALLY EXECUTED｜僅供參考／部分執行**

Baseline: `masini1491/ai-divination-playbook@776934ab5ea6a688ebf91a98c71511ded70657ef`

Companion harness: [`real_image_repeatability_probe.py`](real_image_repeatability_probe.py)

本研究節點的目標是把上一輪 synthetic sensitivity framework 接到真實掌心照片的 hand-landmark detector output：

```text
public/free-licensed palm image
→ fixed detector/version
→ controlled rotate / scale / crop / mirror variants
→ detect L0 / L5 / L17 on every variant
→ inverse transform back to baseline-image coordinates
→ express landmark displacement as palm-width fraction
→ measure canonical-frame drift
```

本輪**沒有**產生 real-image detector accuracy / repeatability 數值。原因與邊界如下；這是刻意 fail closed，不是把人工目測或其他模型輸出冒充 detector evidence。

## 1. Candidate image set

沿用 [`PHOTO_VALIDATION.md`](PHOTO_VALIDATION.md) 已審核的公開真實照片，不把影像複製進 repository：

### Case A — single right palm

- Wikimedia Commons: `Right Hand Palm.png`
- License: CC BY-SA 4.0
- Purpose: single-target, near-frontal geometry case

### Case B — two palms, left emphasized

- Wikimedia Commons: `Open Palm of the Left Hand, Fingers.jpg`
- License: CC BY-SA 4.0
- Purpose: multi-hand target-selection / mirror-convention case

真正執行 detector study 時，應以 source URL + license + immutable local checksum（研究環境產生）識別 fixture；repo 仍不保存真實 palm image。

## 2. Detector/runtime reconciliation

### MediaPipe path

`samuelwbarber/palm-line-reader@bc48939f4deee6d8ff842bfde499396dab9c4830` 的 `pipeline/` 確實包含：

```text
hand_landmarker.task
```

其 GitHub object metadata：

```text
size = 7,819,105 bytes
blob = 0d53faf3786146e95c5bc010c48029ff16b7fa59
```

但目前執行容器：

- 沒有 `mediapipe` Python runtime；
- Python package installation 無 network access；
- GitHub connector 可確認 binary object metadata，但此工作流不能 materialize binary model 到 container；
- 一般外部 binary/model download 也被環境隔離。

所以不能在本輪真實執行 MediaPipe Hand Landmarker。

### OpenPose fallback review

為避免把研究卡死在單一 detector，本輪也檢視 `CMU-Perceptual-Computing-Lab/openpose@5c5d96523ef917bd30301245fdc8343937cae48d`。

官方 hand constants 明確定義：

```text
HAND_NUMBER_PARTS = 21
HAND_PROTOTXT = hand/pose_deploy.prototxt
HAND_TRAINED_MODEL = hand/pose_iter_102000.caffemodel
```

而 hand topology 包含：

```text
0→5
0→17
```

因此 `0 / 5 / 17` 可作 wrist / index-ray base / little-ray base 的同 topology anchors，適合拿來做 detector-agnostic normalization experiment。

但目前容器同樣無法取得 OpenPose trained caffemodel，因此也沒有真實執行 OpenPose inference。

## 3. Harness added

新增 [`real_image_repeatability_probe.py`](real_image_repeatability_probe.py)。它不是 detector；它只負責**接收 detector 已輸出的 landmarks + known inverse image transform**，然後計算：

- max / mean anchor displacement as palm-width fraction；
- palm-axis angle drift；
- palm-width / palm-height scale drift；
- canonical 5×5 grid 的 max coordinate drift；
- handedness label 是否相對 baseline 改變。

Input contract 概念：

```json
{
  "baseline": {
    "landmarks": {
      "0": [0, 0],
      "5": [0, 0],
      "17": [0, 0]
    },
    "handedness": "right"
  },
  "variants": [
    {
      "name": "rotate+10deg",
      "landmarks": {
        "0": [0, 0],
        "5": [0, 0],
        "17": [0, 0]
      },
      "inverse_transform": [
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1]
      ],
      "handedness": "right"
    }
  ]
}
```

`inverse_transform` 必須把 variant detector coordinates 映回 baseline-image coordinates。這樣 harness 不需要知道 detector 是 MediaPipe、OpenPose 或其他 future adapter。

## 4. Harness self-test

本輪已在 local container 執行：

```text
python real_image_repeatability_probe.py --self-test
```

結果：

```text
exact-rotate-translate
max_anchor=0.0000%
max_canonical=0.0000%

exact-plus-wrist-noise
max_anchor=1.0000%
axis_deg≈0.525343
max_canonical≈1.2532%

summary: real-image repeatability harness self-test PASS
```

這證明：

1. known affine transform + exact inverse 可以 round-trip 回 0 drift；
2. 注入 1% palm-width wrist displacement 後，harness 能回推出 1% anchor drift；
3. frame-level drift calculation 能對 synthetic injected error 產生非零 propagation。

它**沒有**證明任何真實 detector repeatability。

## 5. Controlled transform study contract

當 detector runtime 可用時，Case A 最小 study 應至少包含：

```text
baseline
rotate +10°
rotate -10°
uniform scale 0.75×
uniform scale 1.25×
crop with safe palm margin
horizontal mirror
```

每個 variant 必須保存：

```text
image transform matrix
inverse transform matrix
detector identity + immutable version/model identity
target hand selection rule
reported handedness
L0/L5/L17 raw detector coordinates
```

然后 inverse 回 baseline coordinates 再比較。

Case B 另驗：

- multi-hand target 是否在 transform 後仍選到同一 anatomical hand；
- mirror 後 handedness label / camera convention 是否可 reconciliation；
- 若 target identity 或 mirror lineage 無法可靠維持，該 case fail closed，不計入 numeric repeatability aggregate。

## 6. Required result classes

未來 real-image 結果不能只報平均值。至少要分：

```text
same-pixels deterministic rerun
controlled affine transform consistency
controlled mirror consistency
multi-hand target-selection consistency
```

如果同一張完全相同 pixels、相同 detector/version 的 repeated inference 已 deterministic，第一類可以只記 deterministic fact；真正重要的是 transform consistency。

## 7. What this round establishes

目前可建立的 evidence：

- real-image repeatability 的 metric / interchange contract 已可執行；
- harness 對 exact transform round-trip 的 self-test PASS；
- harness 能把 detector landmark displacement 換算成 palm-width fraction，並接到既有 canonical sensitivity frame；
- MediaPipe binary/model 在 upstream repo 的存在可確認，但目前 execution environment 缺 runtime / binary materialization path；
- OpenPose 可作 topology-compatible fallback reference，但本環境同樣缺可執行 model weights。

## 8. What remains unresolved

仍**沒有**建立：

- MediaPipe real-image L0/L5/L17 transform consistency；
- OpenPose real-image transform consistency；
- real-image handedness stability；
- same-photo crop / rotate / scale / mirror numeric drift；
- detector-to-detector agreement；
- production admission tolerance。

所以目前不能宣稱：

```text
real-image repeatability validated
```

只能宣稱：

```text
real-image repeatability harness validated;
detector execution blocked by environment;
real-image numeric evidence pending
```

## 9. Adoption decision

Palmistry 狀態維持：

**REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**

下一個研究節點不應再擴充 synthetic math；應取得一個可固定版本、可本地執行的 hand-landmark runtime/model，然後直接用本 harness 跑 Case A / B controlled-transform study。完成前不建立 production numeric threshold，也不 promotion Palmistry routing。
