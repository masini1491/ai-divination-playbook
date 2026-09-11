# Retained Two-candidate Near-tie Stress｜雙候選保留近似平手壓力測試

Status: **REFERENCE-ONLY / SYNTHETIC-COMPOSITE STRESS EXECUTED｜僅供參考／合成壓力測試已執行**

## Purpose

前一輪 [`ASSOCIATION_AMBIGUITY_STRESS.md`](ASSOCIATION_AMBIGUITY_STRESS.md) 已觀察到 candidate disappearance / reappearance，但大多在 score 真正接近前就先 collapse 成 1 candidate。本輪專門補另一個 ambiguity family：**兩 candidates 都保留，但兩者對 baseline target 都同樣合理**。

## Runtime / provenance

```text
research run: 34616780936
head: d82e02572dd7e64ea8027a9dca5b2033a2fd1e36
fixture: MediaPipe right_hands.jpg
fixture SHA256: 4b5134daa4cb60465535239535f9f74c2842aba3aa5fd30bf04ef5678f93d87f
model: Hand Landmarker float16/1
model SHA256: fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1
MediaPipe: 1.0.1
OpenCV: 5.0.0
Python: 3.12.14
confidence thresholds: detection/presence/tracking = 0.5 / 0.5 / 0.5
```

## Evidence boundary

依 engineering playbook 的 provisional-vs-settled guard，本檔刻意分開：

- `requested pair separation = 2.00W`、`requested center bias`：**composition input / pre-execution design parameter**；
- detector candidate count、observed pair distance、best/second scores、score gap：**post-detector observation**。

不得把 requested `2.00W` 當成 detector 實際量到的 pair distance。

## Composition method

從 Case C upstream fixture 偵測出的同一隻 source hand 建立 hand layer，在白底 canvas 上放兩份 identical copies：

```text
copy A <—— fixed requested pair span ——> copy B
                     ↑
             pair center bias sweep
                     ↑
             isolated baseline target
```

Requested pair separation 固定 `2.00W`，pair center 相對 baseline target 由 `-0.30W` 掃到 `+0.30W`。每一張 composite 都重新執行 MediaPipe；沒有沿用前一張 landmarks，也沒有降低 confidence threshold。

## Results

所有 11 個 bias points 都保留 **2 candidates**。

| Requested center bias | Candidates | Observed pair distance | Best distance | Second-best | Score gap | Best index |
|---:|---:|---:|---:|---:|---:|---:|
| -0.30W | 2 | 204.003% | 70.961% | 133.240% | 62.279% | 0 |
| -0.20W | 2 | 202.028% | 79.029% | 123.324% | 44.295% | 0 |
| -0.15W | 2 | 203.552% | 84.729% | 119.150% | 34.422% | 0 |
| -0.10W | 2 | 203.485% | 90.584% | 113.180% | 22.597% | 0 |
| -0.05W | 2 | 203.509% | 94.042% | 109.691% | 15.649% | 0 |
| **0.00W** | **2** | **202.158%** | **99.014%** | **103.389%** | **4.375%** | **0** |
| +0.05W | 2 | 204.251% | 99.656% | 104.861% | 5.205% | **1** |
| +0.10W | 2 | 202.569% | 92.338% | 110.284% | 17.946% | 1 |
| +0.15W | 2 | 202.878% | 87.908% | 115.119% | 27.211% | 1 |
| +0.20W | 2 | 202.205% | 83.531% | 118.763% | 35.232% | 1 |
| +0.30W | 2 | 202.007% | 72.674% | 129.519% | 56.845% | 1 |

## Key finding: retained-two-candidate ambiguity was exercised

At requested center bias `0.00W`:

```text
candidate count            = 2
observed candidate pair    ≈ 2.0216W
best mean distance         ≈ 0.9901W
second-best mean distance  ≈ 1.0339W
score gap                  ≈ 0.04375W
```

The two detector candidates both survive and are almost symmetrically plausible relative to the isolated baseline target. The best-vs-second score gap is only about **4.375% of baseline palm width** in this synthetic case.

At requested bias `+0.05W`, both candidates still survive but the best candidate index changes from `0` to `1`; score gap remains only about **5.205%**. Therefore the sweep also shows a real detector **ranking swap** across a small composition perturbation while candidate count remains stable.

This is the ambiguity family that Case C and the previous collapse sweep had not exercised.

## Fail-closed implication

Current evidence now supports two distinct unresolved states:

```text
A. expected multi-target scene + candidate collapse / count instability
   → association unresolved

B. >=2 candidates retained + materially small best-vs-second gap / ranking instability
   → association unresolved
```

Both should fail closed for target-specific fine geometry until a defensible admission contract exists.

However **4.375% is not a production threshold**. It is one observed synthetic-composite point under one model/runtime/source hand. No numeric cutoff is promoted by this study.

## What this validates

- retained-two-candidate near-tie can be constructed without lowering detector thresholds;
- two candidates can remain detectable while association scores become close;
- best candidate ranking can swap while candidate count stays at 2;
- candidate count and score separation are complementary uncertainty evidence;
- requested composition geometry must remain separate from detector-observed geometry.

## What remains unresolved

- natural-image distribution of retained-two-candidate score gaps;
- whether `4.375%` is common, rare, or meaningful outside this synthetic fixture;
- repeated runs / different hand shapes / orientations / model versions;
- a defensible production admission threshold;
- same-hand multiple-capture continuity and cross-detector agreement.

## Next research node

The ambiguity evidence families are now both demonstrated synthetically. The next higher-value node is no longer to push the synthetic gap lower. It is to test whether these two uncertainty signals reproduce in **natural or controlled real captures** and across detector/runtime variants before considering any numeric admission contract.

## Adoption decision

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**. No production router, method index, interpretation rule, or numeric threshold changes in this study.