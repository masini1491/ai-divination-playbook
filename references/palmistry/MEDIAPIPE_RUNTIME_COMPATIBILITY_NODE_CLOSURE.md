# MediaPipe Runtime Compatibility — Bounded Node Closure

Status: **REFERENCE-ONLY / RUNTIME-ONLY SUBNODE CLOSED / MODEL-VERSION PORTABILITY STILL OPEN / NO PRODUCTION PROMOTION**

## Purpose

本文件關閉 MediaPipe `1.0.1` vs `1.0.0` 的第一輪 runtime-only 2D geometry portability子節點。

Closure只回答：

> 在 controlled reconstructed environment中，固定同一 Hand Landmarker model artifact、同一 RGB pixel bytes與同一 detector options時，runtime package `1.0.1`與`1.0.0`是否改變本 Palmistry observation pipeline使用的 candidate count、2D hand landmarks、L0/L5/L17 anchors、canonical palm geometry與 handedness label。

它不關閉 model artifact version compatibility，也不建立 production upgrade policy。

## Evidence chain

```text
MEDIAPIPE_RUNTIME_MODEL_COMPATIBILITY_PLAN.md
→ MEDIAPIPE_RUNTIME_COMPATIBILITY_CANDIDATE_LOCK.md
→ MEDIAPIPE_RUNTIME_PROVENANCE_RECONCILIATION.md
→ mediapipe_runtime_identity_probe.py
→ MEDIAPIPE_RUNTIME_IDENTITY_PROBE_STATIC_REVIEW.md
→ MEDIAPIPE_RUNTIME_PHASE0_SYSTEM_DEPENDENCY_BLOCKER.md
→ MEDIAPIPE_RUNTIME_PHASE0_RESULT_FREEZE.md
→ mediapipe_runtime_mohi_compare_runner.py
→ MEDIAPIPE_RUNTIME_MOHI_COMPARISON_IMPLEMENTATION_LOCK.md
→ MEDIAPIPE_RUNTIME_MOHI_RUNNER_STATIC_REVIEW.md
→ MEDIAPIPE_RUNTIME_MOHI_RESULT_FREEZE.md
→ MEDIAPIPE_RUNTIME_MOHI_RESULTS.md
```

Historical-runtime provenance uncertainty was preserved instead of silently treating a local environment as the original MOHI runtime。

## Formal raw-result identity

```text
MOHI runtime-only result SHA256
bcee8126b3c5ce4b01a7dcf921edac627961351423121e6a975c2462142ade9d
```

Execution accounting：

```text
150 manifest entries
148 primary unique source-byte representatives
2 duplicate source-byte groups
150 inferences under MediaPipe 1.0.1
150 inferences under MediaPipe 1.0.0
stop = false
```

## Closure evidence

Primary 148 unique-source representatives：

```text
candidate count agreement = 148 / 148
candidate transitions     = 1 -> 1 for all 148
resolved geometry         = 148 / 148
unresolved geometry       = 0
handedness label agreement= 148 / 148
```

Tracked 2D / canonical metrics：

```text
raw_21_mean
raw_21_median
raw_21_max
anchor_mean
anchor_max
axis_angle_deg
width_rel
height_rel
canonical_mean
canonical_max
```

For every metric：

```text
mean   = 0
median = 0
p90    = 0
p95    = 0
min    = 0
max    = 0
std    = 0
```

All per-person/session group means for raw / anchor / axis / canonical geometry were also `0.0`。

Both byte-identical duplicate groups reproduced exact candidate structures within each runtime。

## Closure decision

The first controlled runtime-only portability question is **boundedly closed**：

> No runtime-dependent difference was observed between MediaPipe `1.0.1` and `1.0.0` for the tracked 2D/canonical observation outputs under the exact pinned model / pixel / environment contract used by this experiment。

Because the entire tracked delta distribution is exact zero, this closure does not require inventing a numeric compatibility cutoff。

## What remains open

This closure does **not** answer：

### Model artifact portability

The Hand Landmarker model bytes were held fixed。Different model artifact revisions remain untested。

### Future / broader runtime versions

No claim is made for arbitrary MediaPipe versions beyond this `1.0.1` vs `1.0.0` pair。

### z / ancillary field portability

The formal geometry summary is 2D x/y + derived canonical geometry。Normalized z and ancillary score exactness were not promoted into this closure because current canonical Palmistry observation geometry is 2D and handedness score is non-authoritative metadata。

If later schema use depends materially on z or score magnitude, they require their own explicit validation。

### Device / OS / capture portability

The two comparison environments deliberately shared one WSL/Linux runtime family and one prepared-pixel contract。This does not close multi-device, multi-OS, camera-pipeline, lighting, pose, exposure or distance repeatability。

### Historical runtime forensic identity

Historical MOHI artifact provenance remains less specific than the controlled reconstruction；the closure is about the controlled experiment, not a claim that the old local run was executed in exactly the reconstructed environment。

## Research-roadmap consequence

`B1 MediaPipe runtime / model version compatibility` should no longer be represented as one undifferentiated open item。

It should be split into：

```text
B1a runtime package 1.0.1 vs 1.0.0, pinned model
→ BOUNDEDLY CLOSED

B1b Hand Landmarker model artifact version portability
→ OPEN

B1c broader/future runtime families
→ OPEN / lower priority until needed
```

With uncertainty composition already boundedly closed, the next observation-portability work should prioritize capture/device lineage rather than repeat this same runtime pair。

## Boundary

Closure here does not establish production Palmistry support、general MediaPipe certification、anatomical truth、biometric identity、Palmistry predictive validity or production upgrade safety。

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**。
