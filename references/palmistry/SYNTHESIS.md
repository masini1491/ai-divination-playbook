# Palmistry Research Synthesis｜手相參考收斂

Status: **REFERENCE-ONLY｜僅供參考**

本檔只收斂 external / Cold evidence，不建立 production Palmistry capability，也不修改 `METHOD_ROUTING.md`、`PLAYBOOK_INDEX.json`、`CHAT_INIT.md` 或既有 Tarot / Meihua / Liuyao contract。

## Architecture conclusion

目前 evidence 支持：

```text
Scene / Target Selection Gate
→ Task-specific Image Quality Gate
→ Model Adapter
→ Raw-image Observation Geometry
→ Canonical Palm Coordinates
→ Palm Observation Fact
→ Tradition-specific Projection
→ Tradition-specific Interpretation
→ User-visible synthesis
```

責任邊界：

- detector preprocessing / mirror / resize 是 adapter implementation detail；
- detector output 要能 inverse 回 raw-image geometry，才可進 canonical observation；
- anatomical hand side 與 detector handedness / `mirrored_for_model` 分開；
- observation fact 與 tradition interpretation 分開；
- frame-level uncertainty 不能只看單 landmark confidence；
- traditional source 不取得 image observation authority；
- CV detector class 不取得 Chinese terminology authority。

## Source-neutral coordinate frame

Draft anchors：`L0 wrist`、`L5 index MCP`、`L17 little MCP`。wrist→MCP midpoint 定義 longitudinal axis；little→index MCP 的正交分量定義 transverse axis；palm height / width normalization。此 frame 只代表 geometry，不代表 Western line label 或中國掌宮。

Ideal synthetic invariant probe：`11 passed / 0 failed`。

Controlled simultaneous-anchor sensitivity sweep：

| Per-anchor bound | Axis angle | Width error | Height error | Max canonical drift |
|---:|---:|---:|---:|---:|
| 0.25% | 0.2865° | 0.500% | 0.500% | 0.527% |
| 0.50% | 0.5729° | 1.001% | 1.000% | 1.059% |
| 1.00% | 1.1458° | 2.005% | 2.000% | 2.135% |
| 2.00% | 2.2906° | 4.019% | 4.000% | 4.341% |
| 5.00% | 5.7106° | 10.112% | 10.000% | 11.445% |

這些只是 configured-grid synthetic evidence，不是 production thresholds。若 detector-only mirror 漏 inverse，在 canonical `x∈[-0.5,0.5]` frame 上可形成 100% max drift；mirror lineage 因此是 admission gate，不是 optional metadata。

## Real-image MediaPipe evidence

Pinned research baseline：

```text
MediaPipe 1.0.1
Python 3.12.14
OpenCV 5.0.0
Hand Landmarker float16/1
model SHA256 fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1
```

### Case A — single palm

`Right Hand Palm.png` / CC BY-SA 4.0。Max canonical drift：same pixels `0%`、rotate +10° `7.3708%`、rotate -10° `4.7228%`、scale 0.75× `1.0967%`、scale 1.25× `2.4488%`、crop 3% `1.6727%`、horizontal mirror `2.9833%`。Mirror handedness `Right → Left`。

### Case B — overlapping two-palm scene

`Open Palm of the Left Hand, Fingers.jpg` / CC BY-SA 4.0。Scene 視覺上有兩掌，但 baseline 與 transforms 都只回 1 candidate。Max canonical drift：same pixels `0%`、rotate +10° `2.1408%`、rotate -10° `8.8829%`、scale 0.75× `4.0574%`、scale 1.25× `1.6918%`、crop 3% `9.2687%`、horizontal mirror `77.3400%`。Mirror handedness `Left → Right`；不能解讀為 anatomical-side evidence。

### Public multi-hand bounded screen

[`MULTI_HAND_FIXTURE_SCREEN.md`](MULTI_HAND_FIXTURE_SCREEN.md) 用相同 pinned runtime/model 與固定 `0.5` thresholds 篩選 4 個視覺上有 2–3 hands 的 public scenes，baseline candidate counts 為 `0 / 1 / 1 / 0`。因此：

```text
visually multiple hands
!=
pinned detector returns multiple candidates
```

沒有為了湊 `>=2` 而降低 threshold。

### Case C — upstream MediaPipe multi-hand fixture

[`UPSTREAM_MULTI_HAND_ASSOCIATION.md`](UPSTREAM_MULTI_HAND_ASSOCIATION.md) 使用 MediaPipe 官方 `right_hands.jpg` test fixture：upstream revision `8dd04551858308f3003ace87632d7308d6a62212`、fixture SHA256 `4b5134daa4cb60465535239535f9f74c2842aba3aa5fd30bf04ef5678f93d87f`、research run `34614749960`。

我們自己的 pinned Python runtime 得到 baseline 2 candidates，7 個 controlled variants 也全部 2 candidates。Candidate index 會在 rotate / crop / mirror 後從 baseline index `0` 變成 selected index `1`，所以 list position 不能當 scene-local identity。

Best-vs-second-best separation 約 `3.93–3.97 palm widths`；Case C 因而是乾淨 association 正例，但不是 ambiguity stress case。

### Association ambiguity stress

[`ASSOCIATION_AMBIGUITY_STRESS.md`](ASSOCIATION_AMBIGUITY_STRESS.md) 以 Case C 來源手建立 synthetic twin-hand composite，固定 detector thresholds，不做 threshold tuning。Research run `34615812360`。

Requested duplicate separation 與 detector candidate count：

```text
2.50W → 2
2.00W → 2
1.50W → 1
1.25W → 2
1.00W → 1
0.75W → 1
0.50W → 1
0.35W → 1
0.25W → 1
0.15W → 1
0.00W → 1
```

在仍保留兩 candidates 的三個點：

| Requested separation | Best mean distance | Second-best | Score gap |
|---:|---:|---:|---:|
| 2.50W | 3.071% | 250.615% | 247.544% |
| 2.00W | 4.891% | 200.667% | 195.775% |
| 1.25W | 11.294% | 124.553% | 113.259% |

因此本輪沒有觀察到「兩 candidates 保留且逐步形成 near-tie」；更早出現的是 candidate collapse，而且 collapse / recovery 非單調（`1.50W→1` 但 `1.25W→2`）。

這支持新的 fail-closed evidence rule：

```text
expected multi-target scene
+ detector candidate-count instability / collapse
→ association unresolved
→ target-specific fine geometry fail closed
```

但這仍是 qualitative research principle，不是 production numeric threshold。缺少第二 candidate 時，不得把 remaining candidate 自動視為 target identity 的延續。

## Cross-case conclusions

目前 executable / real-image / stress evidence 支持：

1. same-pixels deterministic 不等於 transform invariant；
2. exact inverse transform 只能消除已知 image-space transform，不能消除 detector sensitivity；
3. rotation / crop / scale error具有 image/context dependency；
4. detector handedness / mirror output 不是 anatomical hand-side fact；
5. overlapping-hand context可極大放大 mirror instability；
6. synthetic sensitivity numbers不能直接當 real-image cutoff；
7. human-visible hand count不能替代 detector candidate evidence；
8. candidate list index不能當 scene-local hand identity；
9. best / second-best inverse-mapped distance與 separation應被保留；
10. association uncertainty不能只靠 score gap，因為第二 candidate可能直接消失；
11. candidate-count instability / disappearance / reappearance本身是獨立的 uncertainty signal；
12. hand proximity與 detector ambiguity不是單調函數，不能建立簡單的距離→confidence規則。

## Traditional interpretation boundary

中國與西方 source normalization維持：

- Cheiro 只代表 Western tradition；
- `SXQ-640` / `TQ-V5` / `TGKD` 為中國傳統 provenance anchors；
- `SXQ-640` 與 `TQ-V5` 的近似段落不能機械視為獨立 corroboration；
- `天／人／地紋 ↔ heart/head/life`、`玉柱紋 ↔ fate line` 仍為 `PROHIBITED_ASSUMPTION`；
- named pattern 必須保留 source / anatomical scope / geometry basis。

## Remaining evidence gaps

目前仍不足以 promotion：

1. retained-two-candidate ambiguity：需要真正較小 best-vs-second-best gap 的 stress case；
2. candidate-count instability 在自然影像、多手型與不同 occlusion pattern 的分布；
3. predeclared ambiguity admission contract與可辯護 threshold；
4. 多張不同 hand shapes / capture contexts 的 transform-consistency distribution；
5. same hand / multiple captures 的 pose / distance / lighting / device repeatability；
6. camera/selfie mirroring reconciliation 與 anatomical side contract；
7. MediaPipe model/runtime version compatibility；
8. detector-to-detector agreement；
9. branch / island / star / minor lines / mounts 等 detector evidence；
10. palm-line segmentation uncertainty 與 landmark-frame uncertainty 的合成方式；
11. Bagua / palm-palace source-specific projection geometry；
12. named patterns / illustrated marks unresolved mapping；
13. production numeric admission thresholds；
14. Palmistry behavioral regression，證明 promotion 不影響 Tarot / Meihua / Liuyao routing。

## Adoption decision

所有 Palmistry external sources、schema、normalization contracts、synthetic probes、MediaPipe runners與 real-image results 仍為：

**REFERENCE-ONLY / DRAFT｜僅供參考／草案**

production method set 不變。

下一個 bounded research node 應拆成兩條：

```text
A. candidate-count instability
   → controlled occlusion / proximity 下的 disappearance / reappearance

B. retained-two-candidate ambiguity
   → 尋找仍保留兩 candidates 但 score gap 明顯縮小的 controlled case
```

在兩類 evidence 都足夠前，不建立 production threshold，也不 promotion Palmistry routing。
