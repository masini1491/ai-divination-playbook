# Palm Line Segmentation — Evidence Node Closure

Status: **REFERENCE-ONLY / BOUNDED EVIDENCE NODE CLOSED / NO PRODUCTION PROMOTION**

## Scope

本文件收斂 principal-line segmentation 這一個 bounded research node，回答的窄問題是：

> shipped `heart_line / head_line / life_line` 三類，在目前 frozen MOHI sample 與既定 corrected adapter 下，是否具有可辯護的 class-specific spatial alignment，而不是只做 generic crease activation？

本節點不回答 Palmistry interpretation validity，也不建立 production runtime。

## Evidence chain now available

目前已完成並保留的 evidence chain：

1. corrected adapter diagnosis：`C_G1_M0` 在 frozen 10-image sample 上恢復三類輸出；
2. implementation repeatability：小型幾何 / appearance perturbation 下大致維持三類；
3. content-dependence control：low-pass / flat-color destructive controls 使 foreground 消失；
4. spatial-structure control：spatial shuffle 幾乎使 foreground collapse，支持 coherent crease-like spatial arrangement materially important；
5. blind single-observer manual audit：人工 reference 在 model comparison 前完成、freeze、hash；
6. result artifact 亦在 substantive inspection 前 freeze / hash；
7. post-hoc P001 quality caveat 與 leave-P001-out sensitivity analysis，未改動 frozen annotation 或 frozen comparison result。

Pinned artifacts：

```text
annotation SHA256 = 51c4886e20cb9aee2d660fe1ca39f25b927398261478c013090ab5d611858041
result SHA256     = 6f95828b70b388028a46ee1879835d432d9dd695bdbbdd1f2656b6ebf3572284
spatial control   = ba65456e3c7c3a645a4000c721961d0f600b46541ffc7e7566525b99a55f87e7
```

## Primary manual-audit result

Frozen 10-image audit, 8 px tolerance：

| class | mean harmonic coverage | median | wrong-class exceeds correct |
|---|---:|---:|---:|
| `heart_line` | 0.9036458631 | 0.9735923680 | 0 / 10 |
| `head_line` | 0.9137675861 | 0.9572269111 | 0 / 10 |
| `life_line` | 0.7906154111 | 0.8158573054 | 0 / 10 |

這支持 shipped class identity 在此 bounded sample 中具有 class-specific spatial meaning；結果不符合「完全忽略 class identity 的 generic crease detector」這個較弱解釋。

## P001 post-hoc sensitivity

Observer 在 model result 已 freeze 並 inspect 後回報：`P001/S1/01.jpg` 過於模糊，人工 trace 有部分依推測完成。

因此 P001 不可作為 clean model-failure case。原始 frozen audit 保持不變，另做 descriptive leave-P001-out sensitivity：

| class | primary mean n=10 | leave-P001-out mean n=9 |
|---|---:|---:|
| `heart_line` | 0.9036458631 | 0.9620089169 |
| `head_line` | 0.9137675861 | 0.9428548314 |
| `life_line` | 0.7906154111 | 0.8224475929 |

P001 本身也沒有 wrong-class win，因此排除它不改變 class-specificity 的 qualitative conclusion。

## Closure decision

對本節點原本的 bounded research question，目前 evidence 已足夠支持以下窄結論：

> 在目前 10-image MOHI sample、corrected `C_G1_M0` geometry、single-observer blind trace 與 8 px comparison tolerance 下，`heart_line / head_line / life_line` segmentation outputs 與相對應的人工主要掌褶 reference 呈現 class-specific spatial alignment。

因此 **不需要再為了同一個 bounded question 追加本機 model rerun**。既有 frozen overlays 可做 post-freeze qualitative review，但不是本節點 closure 的必要條件。

## What remains unresolved

若未來要把 segmentation evidence 強化到更高層級，最有價值的新增 evidence 不是重跑同一批數字，而是：

1. 第二位 independent annotator，先報 inter-observer agreement，再與 model 比較；
2. 更清楚、更多 capture contexts 的 cross-image / cross-session line segmentation repeatability；
3. 外部 dataset / device / lighting 的 bounded generalization；
4. line-mask uncertainty 與 landmark-frame uncertainty 的 composition；
5. explicit admission / quality gate，尤其對 blur / partial visibility / crop failure；
6. 任何 Western `heart/head/life` 到 Chinese Palmistry terminology 的映射都必須另外有 tradition-specific authority，不能由 CV class 自動取得。

## Adoption boundary

本 closure **不**使 palm-line-reader 成為 canonical Palmistry engine，也不修改 ordinary reading Hot Path。

允許的收斂只有：

```text
palm-line-reader
→ REFERENCE-ONLY observation implementation evidence
→ 可作為 Palm Observation Fact research backend candidate
```

仍不得推論：

- medical anatomical truth；
- Palmistry fortune validity；
- population-wide accuracy；
- production readiness；
- production cutoff；
- biometric identity / authentication；
- `heart/head/life` 自動等於中國手相術語。

Palmistry 維持 **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**。
