# Association Ambiguity Stress｜候選關聯模糊壓力測試

Status: **REFERENCE-ONLY / SYNTHETIC-COMPOSITE STRESS EXECUTED｜僅供參考／合成壓力測試已執行**

## Purpose

Case C 已證明 pinned MediaPipe 在官方 `right_hands.jpg` fixture 上可穩定輸出 2 candidates，且 inverse-mapped `L0/L5/L17` geometry 能在 candidate index 重排後找回 scene-local target；但 Case C 的 best-vs-second-best separation 約 `3.93–3.97 palm widths`，屬於非常容易的 association 正例。

本輪不降低 detector confidence thresholds，也不再搜尋一般照片；改用同一 upstream fixture 建立**受控 synthetic twin-hand composite**，把同一被 detector 偵測到的手複製一份並沿水平方向逐步靠近 baseline target，觀察：

```text
candidate count
best association distance
second-best association distance
best-vs-second-best separation
candidate reorder / collapse
```

這是 detector stress instrumentation，不代表自然拍攝分布，也不是 biometric identity 或 production threshold。

## Provenance / runtime

```text
research run: 34615812360
head: 61208e9bd2e1eac55714188fc098cc9da3dd5f12
fixture: MediaPipe right_hands.jpg
fixture SHA256: 4b5134daa4cb60465535239535f9f74c2842aba3aa5fd30bf04ef5678f93d87f
model: Hand Landmarker float16/1
model SHA256: fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1
MediaPipe: 1.0.1
OpenCV: 5.0.0
Python: 3.12.14
confidence thresholds: detection/presence/tracking = 0.5 / 0.5 / 0.5
```

The source fixture and model checksum were verified before the sweep.

## Composite method

1. Run MediaPipe on upstream `right_hands.jpg`.
2. Select the largest normalized landmark bbox as source hand.
3. Build a research-only hand layer from the 21 detected landmarks using a dilated, feathered convex-hull mask.
4. Place one copy on a white canvas as the fixed baseline target.
5. Place a second identical copy at a controlled horizontal offset measured in the isolated baseline palm width `W`.
6. Run MediaPipe independently on every composite.
7. Compare every returned candidate against the isolated baseline target using mean `L0/L5/L17` distance divided by baseline palm width.

The isolated baseline composite itself returned one hand candidate. Its measured palm width was approximately `111.24 px`.

## Sweep result

| Requested copy separation | Detector candidates | Best mean distance | Second-best distance | Score separation |
|---:|---:|---:|---:|---:|
| 2.50 W | 2 | 3.071% | 250.615% | 247.544% |
| 2.00 W | 2 | 4.891% | 200.667% | 195.775% |
| 1.50 W | **1** | 149.659% | — | — |
| 1.25 W | **2** | 11.294% | 124.553% | 113.259% |
| 1.00 W | **1** | 99.425% | — | — |
| 0.75 W | **1** | 74.368% | — | — |
| 0.50 W | **1** | 49.391% | — | — |
| 0.35 W | **1** | 33.888% | — | — |
| 0.25 W | **1** | 25.050% | — | — |
| 0.15 W | **1** | 15.184% | — | — |
| 0.00 W | **1** | 0.761% | — | — |

## Key finding: collapse precedes near-tie

The stress sweep did **not** produce a smooth transition from large score gap to a two-candidate near-tie. Instead, the detector frequently collapsed two visible synthetic copies into one candidate before the association scores became close.

Most importantly, detector behavior was **not monotonic** with geometric separation:

```text
2.50W → 2 candidates
2.00W → 2 candidates
1.50W → 1 candidate
1.25W → 2 candidates
1.00W → 1 candidate
0.75W and below → 1 candidate
```

Therefore the current evidence rejects a simple assumption such as:

```text
smaller hand separation
→ monotonically smaller association score gap
→ eventual near-tie
```

A production-like admission gate must be prepared for candidate disappearance / reappearance as a first-class uncertainty signal.

## 1.25 W recovery case

At requested `1.25W`, MediaPipe briefly returned two candidates again:

```text
best mean distance      ≈ 11.294%
second-best distance    ≈ 124.553%
score separation        ≈ 113.259%
```

This is still not a near-tie. The best candidate was labeled `Left` while the second candidate was labeled `Right`, despite the source hand being copied from one image patch. This reinforces the existing rule that detector handedness under synthetic overlap / composition is not anatomical-side authority.

## Fail-closed implication

Current evidence supports a qualitative admission principle:

```text
expected multi-target scene
+ detector candidate-count instability / collapse
→ association unresolved
→ fail closed for target-specific fine geometry
```

This principle does **not** yet define a production numeric threshold. The sweep is synthetic-composite evidence and only one source hand/model/runtime was tested.

A missing second candidate must not be interpreted as evidence that the second hand vanished from the scene, nor may the remaining candidate automatically inherit target identity.

## What this validates

- candidate disappearance / reappearance can happen under controlled proximity stress;
- candidate-count behavior can be non-monotonic;
- association uncertainty cannot be represented only by best-vs-second-best score separation because sometimes there is no second detector candidate to score;
- candidate count and association score evidence should be preserved separately;
- fail-closed logic needs an explicit unresolved state for candidate collapse.

## What remains unresolved

This run does **not** establish:

- a natural-image near-tie distribution;
- a production minimum candidate separation in image space;
- a production minimum best-vs-second-best score gap;
- whether another composition method, hand shape, orientation, device, or model version would collapse at the same distances;
- a complete ambiguity contract when two candidates remain but score separation is genuinely small;
- cross-capture or biometric identity continuity.

## Next research node

The next bounded node should separate two ambiguity families:

```text
A. candidate-count instability
   → characterize disappearance / reappearance across controlled occlusion and proximity

B. retained-two-candidate ambiguity
   → seek a controlled case where 2 candidates remain while score separation becomes materially smaller
```

The admission contract should be designed from both families before any threshold is considered.

## Adoption decision

Palmistry remains:

**REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**

No production router, method index, interpretation rule, or numeric threshold is changed by this stress study.