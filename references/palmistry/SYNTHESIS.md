# Palmistry Research Synthesis｜手相參考收斂

Status: **REFERENCE-ONLY｜僅供參考**

Reviewed evidence baseline: `masini1491/ai-divination-playbook@66697df63e122451136364157d66abf5c88440bc`

本檔只收斂外部研究與 Cold validation，不建立 production Palmistry capability，也不修改 `METHOD_ROUTING.md`、`PLAYBOOK_INDEX.json`、`CHAT_INIT.md` 或既有 Tarot / Meihua / Liuyao contract。

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

## Source-neutral coordinate decision

[`NORMALIZATION_CONTRACT_DRAFT.md`](NORMALIZATION_CONTRACT_DRAFT.md) 使用 draft anchors：

```text
L0  wrist
L5  index MCP
L17 little MCP
```

wrist→MCP midpoint 定義 longitudinal axis；little→index MCP 的正交分量定義 transverse axis；palm height / width normalization。此 frame 只代表 geometry，不代表 Western line label 或中國掌宮。

`normalization_probe.py` 已用 ideal synthetic fixtures executable-validated：

```text
11 passed, 0 failed
```

涵蓋 translation / rotation / uniform-scale invariance、mirror/chirality、crop/resize inverse、missing/degenerate anchors fail closed、target selection 與 perspective gate。

## Synthetic sensitivity evidence

[`SENSITIVITY_SWEEP.md`](SENSITIVITY_SWEEP.md) 對 L0/L5/L17 做 16-direction / 每層 4096 simultaneous combinations：

| Per-anchor bound | Axis angle | Width error | Height error | Max canonical drift |
|---:|---:|---:|---:|---:|
| 0.25% | 0.2865° | 0.500% | 0.500% | 0.527% |
| 0.50% | 0.5729° | 1.001% | 1.000% | 1.059% |
| 1.00% | 1.1458° | 2.005% | 2.000% | 2.135% |
| 2.00% | 2.2906° | 4.019% | 4.000% | 4.341% |
| 5.00% | 5.7106° | 10.112% | 10.000% | 11.445% |

這些只是 configured-grid maxima，不是 production thresholds。

若 detector-only mirror 漏 inverse，在 canonical `x∈[-0.5,0.5]` frame 上可形成 100% max drift；所以 mirror lineage 是 admission gate，不是 optional metadata。

## Real-image MediaPipe evidence

[`REAL_IMAGE_REPEATABILITY.md`](REAL_IMAGE_REPEATABILITY.md) 現已取得兩個 public real-image controlled-transform studies。

Pinned runtime/model：

```text
MediaPipe 1.0.1
Python 3.12.14
OpenCV 5.0.0
Hand Landmarker float16/1
model SHA256 fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1
```

Research run `34611890893` 成功；同 evidence commit 的 normal `Validate Playbook` run `34611890817` 亦成功。

### Case A — single palm

`Right Hand Palm.png` / CC BY-SA 4.0。

Same-pixels rerun = 0 drift。Controlled transform max canonical drift：

```text
rotate +10°       7.3708%
rotate -10°       4.7228%
scale 0.75×       1.0967%
scale 1.25×       2.4488%
crop 3%           1.6727%
horizontal mirror 2.9833%
```

Mirror 後 handedness label `Right → Left`。

### Case B — overlapping two-palm scene

`Open Palm of the Left Hand, Fingers.jpg` / CC BY-SA 4.0。

Scene 視覺上有兩掌，但 MediaPipe baseline 與所有 transforms 都只回 1 candidate，因此此 fixture **沒有真正 exercised multi-candidate target-selection branch**。

Same-pixels rerun = 0 drift。Controlled transform max canonical drift：

```text
rotate +10°        2.1408%
rotate -10°        8.8829%
scale 0.75×        4.0574%
scale 1.25×        1.6918%
crop 3%            9.2687%
horizontal mirror 77.3400%
```

Mirror 後 handedness `Left → Right`；inverse 後三 anchors centroid只粗略移約 14 px，但 axis error ≈27.93°、width error ≈35.90%。這比較像 foreground palm landmark geometry 在 mirror + overlap context 下失穩，而不是單純 candidate 跳到很遠的另一掌；但只有三 anchors 且 detector只輸出一個 candidate，不能宣稱 scene-local identity continuity 已證明。

## Multi-hand fixture bounded screen

[`MULTI_HAND_FIXTURE_SCREEN.md`](MULTI_HAND_FIXTURE_SCREEN.md) 進一步用相同 pinned model/runtime 與固定 `0.5` detection/presence thresholds 篩選 public multi-hand scenes；`num_hands=4`，max working dimension 1600 px。

四個視覺上有 2–3 hands 的 fixtures 實際 baseline candidate counts：

```text
Mehndi hands.jpg                                  0
25.12.2018 Vierfingerfurche, beidseitig.JPG       1
Givinghandsandredpushpin.jpg                       1
Three open palms ... henna.jpg                     0
```

成功 screening runs：`34613331865`、`34613479425`、`34613728619`。

因此現在有直接 detector evidence 支持：

```text
visually multiple hands
!=
pinned detector returns multiple candidates
```

這表示 multi-candidate target-selection gate 不能靠 scene description 或人工目測推定；必須先觀察 detector 真正輸出的 candidate set。

此輪依 bounded-discovery / evidence-gap stop rule停止公開圖片擴張。沒有為了得到 `>=2` candidates 而降低 confidence thresholds，因為那會改變目前的實驗 baseline，也不足以建立 production admission rule。

下一次要恢復 multi-candidate association research，優先使用來源可控、已知能穩定觸發 ≥2 candidates 的 fixture strategy，例如 purpose-built/public test fixture、合適的 upstream MediaPipe multi-hand test fixture，或具同意且專為兩手完整分離拍攝的小型 controlled capture。

## Cross-case conclusions

現在可以用 real-image evidence 支持：

1. **same-pixels deterministic 不等於 transform invariant**；
2. exact inverse transform 只能消除已知 image-space transform，不能消除 detector本身對 transform 的 sensitivity；
3. rotation error具 image/context-specific asymmetry，不能以單一角度 tolerance預測；
4. crop / scale也能改變 landmark geometry；
5. mirror handedness output 是 detector convention，不是 anatomical fact；
6. overlapping-hand context 可以大幅放大 mirror instability；
7. synthetic sensitivity numbers不能直接當 real-image cutoff；
8. production-like quality gate需要 detector consistency / frame uncertainty evidence；
9. human-visible hand count 不能替代 detector candidate evidence；
10. multi-candidate fixture acquisition 本身需要可重現的 admission contract，而不是無限搜尋或降低 threshold。

## Traditional interpretation boundary

中國與西方 source normalization維持：

- Cheiro 只代表 Western tradition；
- `SXQ-640` / `TQ-V5` / `TGKD` 為中國傳統 provenance anchors；
- `SXQ-640` 與 `TQ-V5` 的近似段落不能機械視為獨立 corroboration；
- `天／人／地紋 ↔ heart/head/life`、`玉柱紋 ↔ fate line` 仍為 `PROHIBITED_ASSUMPTION`；
- named pattern 必須保留 source / anatomical scope / geometry basis。

## Validation completed

1. 中國傳統 source provenance baseline；
2. source-specific rule-family normalization；
3. Palm Observation Fact draft v2；
4. public real-photo field-coverage / fail-closed review；
5. upstream preprocessing / rectification implementation review；
6. source-neutral normalization contract；
7. ideal synthetic invariant probe：11/11 PASS；
8. controlled landmark perturbation sensitivity sweep；
9. mirror-convention failure magnitude check；
10. detector-agnostic repeatability harness self-test PASS；
11. pinned MediaPipe real-image Case A controlled-transform study；
12. pinned MediaPipe overlapping-hand Case B controlled-transform study；
13. public multi-hand fixture bounded screen（4 fixtures；candidate counts `0/1/1/0`）；
14. normal repository validation workflow PASS for the prior real-image evidence baseline；本次 final evidence commit另以其當次 workflow 結果為準。

## Remaining evidence gaps

目前仍不足以 promotion：

1. 一個來源可控、baseline 可重現地輸出 ≥2 detector candidates 的 multi-hand fixture，才能真正驗 target association / ambiguity；
2. 多張不同 hand shapes / capture contexts 的 transform-consistency distribution；
3. same hand / multiple captures 的 pose / distance / lighting / device repeatability；
4. camera/selfie mirroring reconciliation 與 anatomical side contract；
5. MediaPipe model/runtime version compatibility；
6. detector-to-detector agreement；
7. branch / island / star / minor lines / mounts 等 detector evidence；
8. palm-line segmentation uncertainty 與 landmark-frame uncertainty 的合成方式；
9. Bagua / palm-palace source-specific projection geometry；
10. named patterns / illustrated marks unresolved mapping；
11. production numeric admission thresholds；
12. Palmistry behavioral regression，證明 promotion 不影響 Tarot / Meihua / Liuyao routing。

## Adoption decision

所有 Palmistry external sources、schema、normalization contracts、synthetic probes、MediaPipe runners與 real-image results 仍為：

**REFERENCE-ONLY / DRAFT｜僅供參考／草案**

production method set 不變。

下一個合理 research node 不再是 open-ended Commons 圖片搜尋，而是先取得**來源可控、已知可重現地產生 ≥2 candidates** 的 fixture strategy，再驗 scene-local matching / ambiguity fail-closed；之後才做 multiple captures / devices。現在仍不建立 production threshold，也不 promotion Palmistry routing。
