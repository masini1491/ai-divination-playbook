# Upstream Multi-hand Association Study｜上游多手候選關聯研究

Status: **REFERENCE-ONLY / CASE C EXECUTED｜僅供參考／Case C 已執行**

## Purpose

前一輪 public-image bounded screen 顯示：人眼看到 2–3 隻手，並不代表 pinned MediaPipe 會輸出多個 candidates。為了真正執行 `mediapipe_repeatability_runner.py` 內的 scene-local candidate association branch，本輪改用 MediaPipe 自己的 multi-hand test fixture，而不是繼續 open-ended 圖片搜尋。

## Upstream provenance

Upstream repository / revision：

```text
google-ai-edge/mediapipe
8dd04551858308f3003ace87632d7308d6a62212
```

MediaPipe 官方 Python test 將：

```text
_TWO_HANDS_IMAGE = 'right_hands.jpg'
```

並在 `HandLandmarkerOptions(..., num_hands=2)` 下明確驗證：

```text
self.assertLen(detection_result.handedness, 2)
```

C++ `hand_landmarker_graph_test.cc` 同樣使用 `right_hands.jpg`，設定 `kMaxNumHands = 2`，並 `ASSERT_EQ(landmarks.size(), kMaxNumHands)`。

Fixture 由 MediaPipe `mediapipe_files()` / `third_party/external_files.bzl` 從 GCS test assets 取得：

```text
right_hands.jpg
SHA256: 4b5134daa4cb60465535239535f9f74c2842aba3aa5fd30bf04ef5678f93d87f
```

`mediapipe/tasks/testdata/vision/BUILD` 對 package 宣告：

```text
licenses = ["notice"]  # Apache 2.0
```

License boundary：這足以支持 MediaPipe testdata package 的 Apache-2.0 build licensing；但本輪未找到 `right_hands.jpg` 單獨的作者／拍攝 provenance。因此本 repository **不複製圖片本體**，只保存 upstream revision、GCS identity、checksum、實驗輸出與限制。

## Runtime baseline

```text
GitHub Actions research run: 34614749960
head: 6f207ba554a359e37402b38650f0b729824786e6
runner: ubuntu-24.04
Python: 3.12.14
MediaPipe: 1.0.1
OpenCV: 5.0.0
Hand Landmarker model: float16/1
model SHA256: fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1
num_hands: 2
min detection/presence/tracking confidence: 0.5 / 0.5 / 0.5
```

Both fixture checksum and model checksum were verified inside the run before accepting the evidence.

## Baseline result

Image geometry：

```text
382 × 720 (H×W)
no research downscale applied
baseline candidate count = 2
```

Both candidates were labeled `Right` by the detector.

Normalized landmark bbox areas：

```text
candidate 0 = 0.3112108763
candidate 1 = 0.3106376311
```

The research runner selects the largest bbox as the scene-local baseline target, then associates transformed candidates by minimum mean inverse-mapped L0/L5/L17 distance to that baseline target.

This is **same-source-image scene-local association only**. It is not biometric identity and must not be used to recognize a person across captures.

## Association results

All seven controlled variants returned **2 candidates**, so the best-vs-second-best branch was actually exercised every time.

| Variant | Candidates | Selected index | Best mean anchor distance | Second-best distance | Separation | Max canonical drift | Handedness changed |
|---|---:|---:|---:|---:|---:|---:|---|
| same-pixels rerun | 2 | 0 | 0.0000% | 397.3044% | 397.3044% | 0.0000% | no |
| rotate +10° | 2 | 1 | 3.3253% | 395.8929% | 392.5676% | 5.9313% | no |
| rotate -10° | 2 | 1 | 2.8716% | 397.2671% | 394.3955% | 6.4146% | no |
| scale 0.75× | 2 | 0 | 0.7345% | 397.8279% | 397.0934% | 0.8897% | no |
| scale 1.25× | 2 | 0 | 0.7066% | 397.3751% | 396.6685% | 0.6691% | no |
| crop 3% | 2 | 1 | 2.3551% | 396.6983% | 394.3432% | 3.3916% | no |
| horizontal mirror | 2 | 1 | 4.8491% | 399.2808% | 394.4317% | 12.2287% | yes |

Important behavior：candidate **index is not stable identity**. The baseline target is index `0`, but rotate ±10°, crop 3%, and horizontal mirror return the corresponding best target at index `1`. Therefore a production-like pipeline must not persist detector list position as hand identity.

## Geometry results

Controlled-transform frame drift for the selected scene-local target：

| Variant | Max anchor drift | Mean anchor drift | Axis error | Width error | Height error | Max canonical drift |
|---|---:|---:|---:|---:|---:|---:|
| same-pixels rerun | 0.0000% | 0.0000% | 0.0000° | 0.0000% | 0.0000% | 0.0000% |
| rotate +10° | 6.1875% | 3.3253% | 0.4521° | 2.0362% | 4.8746% | 5.9313% |
| rotate -10° | 4.4196% | 2.8716% | 2.0112° | 3.1414% | 2.0831% | 6.4146% |
| scale 0.75× | 1.0985% | 0.7345% | 0.1942° | 0.0806% | 1.0298% | 0.8897% |
| scale 1.25× | 0.8047% | 0.7066% | 0.0438° | 0.3648% | 0.3134% | 0.6691% |
| crop 3% | 3.3163% | 2.3551% | 0.4285° | 2.9493% | 2.7342% | 3.3916% |
| horizontal mirror | 9.7688% | 4.8491% | 3.2410° | 3.3170% | 3.1953% | 12.2287% |

Mirror changes the selected handedness label from `Right` to `Left`, reinforcing the existing rule that detector handedness / mirror convention is separate from anatomical hand-side fact.

## What this validates

Case C now provides real detector evidence that:

1. a controlled fixture can reproducibly enter the `>=2 candidates` branch;
2. candidate ordering can change under ordinary image transforms;
3. inverse-mapped L0/L5/L17 geometry can recover the intended scene-local target despite list reordering on this fixture;
4. best and second-best association distances can be preserved as explicit uncertainty evidence;
5. same-pixels deterministic behavior still holds on this fixture;
6. multi-candidate target selection must use actual candidate geometry, not candidate index or human-visible hand count.

## What this does **not** validate

The fixture is an easy association case: best-vs-second-best separation remains approximately `3.93–3.97 palm widths` for every transformed variant. Therefore this does **not** prove the ambiguity fail-closed gate under near-tie conditions.

Still unresolved：

- a stress fixture / controlled perturbation where two candidates become geometrically similar enough that association separation shrinks materially;
- a predeclared ambiguity admission rule and threshold derived from broader evidence;
- candidate disappearance / appearance across transforms;
- same-hand multi-capture / device / lighting repeatability;
- cross-detector association agreement;
- production numeric thresholds.

No threshold such as 2%, 5%, 10%, or any particular separation value is promoted from this single Case C.

## Next research node

The next bounded node is **association ambiguity stress**, not more ordinary multi-hand discovery.

Preferred direction：

```text
known two-candidate fixture
→ controlled perturbation that reduces target/candidate geometric separation
→ preserve best + second-best inverse-mapped distances
→ characterize ranking stability / swaps / candidate loss
→ fail closed when association evidence becomes unresolved
```

Only after that should a candidate ambiguity rule be considered for a production admission contract.

## Adoption decision

Palmistry remains:

**REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**

This study changes evidence state only. It does not modify `PALMISTRY.md`, `METHOD_ROUTING.md`, `PLAYBOOK_INDEX.json`, or the production Tarot / Meihua / Liuyao method set.