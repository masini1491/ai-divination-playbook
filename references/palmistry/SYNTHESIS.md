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

Draft anchors：

```text
L0  wrist
L5  index MCP
L17 little MCP
```

wrist→MCP midpoint 定義 longitudinal axis；little→index MCP 的正交分量定義 transverse axis；palm height / width normalization。此 frame 只代表 geometry，不代表 Western line label 或中國掌宮。

Ideal synthetic invariant probe：

```text
11 passed / 0 failed
```

Controlled simultaneous-anchor sensitivity sweep：

| Per-anchor bound | Axis angle | Width error | Height error | Max canonical drift |
|---:|---:|---:|---:|---:|
| 0.25% | 0.2865° | 0.500% | 0.500% | 0.527% |
| 0.50% | 0.5729° | 1.001% | 1.000% | 1.059% |
| 1.00% | 1.1458° | 2.005% | 2.000% | 2.135% |
| 2.00% | 2.2906° | 4.019% | 4.000% | 4.341% |
| 5.00% | 5.7106° | 10.112% | 10.000% | 11.445% |

這些只是 configured-grid synthetic evidence，不是 production thresholds。

若 detector-only mirror 漏 inverse，在 canonical `x∈[-0.5,0.5]` frame 上可形成 100% max drift；mirror lineage 因此是 admission gate，不是 optional metadata。

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

`Right Hand Palm.png` / CC BY-SA 4.0。

Max canonical drift：

```text
same pixels        0.0000%
rotate +10°        7.3708%
rotate -10°        4.7228%
scale 0.75×        1.0967%
scale 1.25×        2.4488%
crop 3%            1.6727%
horizontal mirror  2.9833%
```

Mirror handedness `Right → Left`。

### Case B — overlapping two-palm scene

`Open Palm of the Left Hand, Fingers.jpg` / CC BY-SA 4.0。

Scene 視覺上有兩掌，但 baseline 與 transforms 都只回 1 candidate。Max canonical drift：

```text
same pixels         0.0000%
rotate +10°         2.1408%
rotate -10°         8.8829%
scale 0.75×         4.0574%
scale 1.25×         1.6918%
crop 3%             9.2687%
horizontal mirror  77.3400%
```

Mirror handedness `Left → Right`。這組巨幅 mirror instability 不能被解讀為 anatomical-side evidence。

### Public multi-hand bounded screen

[`MULTI_HAND_FIXTURE_SCREEN.md`](MULTI_HAND_FIXTURE_SCREEN.md) 用相同 pinned runtime/model 與固定 `0.5` thresholds 篩選 4 個視覺上有 2–3 hands 的 public scenes，baseline candidate counts 為：

```text
0 / 1 / 1 / 0
```

因此已有直接 detector evidence 支持：

```text
visually multiple hands
!=
pinned detector returns multiple candidates
```

沒有為了湊 `>=2` 而降低 threshold。

### Case C — upstream MediaPipe multi-hand fixture

[`UPSTREAM_MULTI_HAND_ASSOCIATION.md`](UPSTREAM_MULTI_HAND_ASSOCIATION.md) 使用 MediaPipe 官方 `right_hands.jpg` test fixture：

```text
upstream revision: 8dd04551858308f3003ace87632d7308d6a62212
fixture SHA256: 4b5134daa4cb60465535239535f9f74c2842aba3aa5fd30bf04ef5678f93d87f
research run: 34614749960
```

官方 Python / C++ tests 都明確把它當 two-hand fixture；我們自己的 pinned Python runtime 亦得到：

```text
baseline candidates = 2
all 7 controlled variants = 2 candidates
```

這使 scene-local best-vs-second-best branch 首次由 real detector output 真正 exercised。

Association evidence：

| Variant | Selected index | Best mean distance | Second-best | Separation |
|---|---:|---:|---:|---:|
| same-pixels | 0 | 0.0000% | 397.3044% | 397.3044% |
| rotate +10° | 1 | 3.3253% | 395.8929% | 392.5676% |
| rotate -10° | 1 | 2.8716% | 397.2671% | 394.3955% |
| scale 0.75× | 0 | 0.7345% | 397.8279% | 397.0934% |
| scale 1.25× | 0 | 0.7066% | 397.3751% | 396.6685% |
| crop 3% | 1 | 2.3551% | 396.6983% | 394.3432% |
| mirror | 1 | 4.8491% | 399.2808% | 394.4317% |

Key finding：**candidate list index is not stable identity**。Baseline target 是 index `0`，但 rotate / crop / mirror 後 scene-local best match 會出現在 index `1`。因此 target association 必須靠 geometry / uncertainty evidence，而不能靠 detector list position。

Case C geometry max canonical drift：

```text
same pixels         0.0000%
rotate +10°         5.9313%
rotate -10°         6.4146%
scale 0.75×         0.8897%
scale 1.25×         0.6691%
crop 3%             3.3916%
horizontal mirror  12.2287%
```

Mirror handedness again `Right → Left`。

Case C 是乾淨 association 正例：best-vs-second-best separation 約 `3.93–3.97 palm widths`。因此**不能**宣稱 ambiguity fail-closed 已驗證；near-tie / candidate-loss stress 還沒做。

## Cross-case conclusions

現在可以用 executable / real-image evidence 支持：

1. same-pixels deterministic 不等於 transform invariant；
2. exact inverse transform 只能消除已知 image-space transform，不能消除 detector sensitivity；
3. rotation error具 image/context-specific asymmetry；
4. crop / scale 也能改變 landmark geometry；
5. detector handedness / mirror output 不是 anatomical hand-side fact；
6. overlapping-hand context 可以大幅放大 mirror instability；
7. synthetic sensitivity numbers不能直接當 real-image cutoff；
8. human-visible hand count不能替代 detector candidate evidence；
9. candidate list index不能當 scene-local hand identity；
10. best / second-best inverse-mapped distance與 separation應被保留為 association uncertainty evidence；
11. Case C 證明 association可成功，但因 separation太大，尚未驗 near-tie ambiguity fail-closed。

## Traditional interpretation boundary

中國與西方 source normalization維持：

- Cheiro 只代表 Western tradition；
- `SXQ-640` / `TQ-V5` / `TGKD` 為中國傳統 provenance anchors；
- `SXQ-640` 與 `TQ-V5` 的近似段落不能機械視為獨立 corroboration；
- `天／人／地紋 ↔ heart/head/life`、`玉柱紋 ↔ fate line` 仍為 `PROHIBITED_ASSUMPTION`；
- named pattern 必須保留 source / anatomical scope / geometry basis。

## Remaining evidence gaps

目前仍不足以 promotion：

1. association ambiguity stress：near-tie、candidate reorder、candidate disappearance / appearance；
2. predeclared ambiguity admission contract與可辯護 threshold；
3. 多張不同 hand shapes / capture contexts 的 transform-consistency distribution；
4. same hand / multiple captures 的 pose / distance / lighting / device repeatability；
5. camera/selfie mirroring reconciliation 與 anatomical side contract；
6. MediaPipe model/runtime version compatibility；
7. detector-to-detector agreement；
8. branch / island / star / minor lines / mounts 等 detector evidence；
9. palm-line segmentation uncertainty 與 landmark-frame uncertainty 的合成方式；
10. Bagua / palm-palace source-specific projection geometry；
11. named patterns / illustrated marks unresolved mapping；
12. production numeric admission thresholds；
13. Palmistry behavioral regression，證明 promotion 不影響 Tarot / Meihua / Liuyao routing。

## Adoption decision

所有 Palmistry external sources、schema、normalization contracts、synthetic probes、MediaPipe runners與 real-image results 仍為：

**REFERENCE-ONLY / DRAFT｜僅供參考／草案**

production method set 不變。

下一個合理 bounded research node：**association ambiguity stress**。使用已知 two-candidate fixture，透過受控 perturbation 讓 best / second-best separation 縮小，觀察 ranking stability、swap、candidate loss，並驗 fail-closed evidence contract。現在仍不建立 production threshold，也不 promotion Palmistry routing。
