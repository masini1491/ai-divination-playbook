# Palmistry｜手相方法架構（Cold Scaffold）

> Status: **architecture scaffold / not production-routable**
>
> 本檔先建立手相能力的責任邊界與未來擴充位置；目前**不代表 Playbook 已正式支援手相占讀**。`METHOD_ROUTING.md`、`PLAYBOOK_INDEX.json`、`CHAT_INIT.md` 的 production method set 仍以 Tarot / Meihua / Liuyao 為準。

## 1. Loading Boundary｜預設不進 Hot Path

本 owner 預設為 Cold：

- 普通 Tarot / Meihua / Liuyao 占問不得載入本檔；
- 不因 repository 名稱是 `ai-divination-playbook` 就自動讀取本檔；
- 只有使用者明確要求手相、或 maintainer 正在做 Palmistry capability work 時，才讀取本檔；
- `references/palmistry/` 同樣預設 Cold，不進一般占問 context。

目的：加入新方法時，不增加既有方法的固定 context 成本，也不讓手相規則污染既有 method judgment。

## 2. Responsibility Split｜Observation 與 Interpretation 分離

Palmistry 不應直接採用「看到照片 → 立刻解讀」的單層流程。預定架構為：

```text
Palm image / user-provided visual input
→ Image Quality Gate
→ Objective Observation
→ Palm Observation Fact
→ Palmistry Interpretation
→ User-visible synthesis
```

責任邊界：

- **Image Quality Gate**：只判斷影像是否足以觀察需要的掌紋／掌型特徵。
- **Objective Observation**：只描述可見特徵，不混入命理解釋。
- **Palm Observation Fact**：把已觀察特徵結構化，作為後續解讀的 evidence layer。
- **Palmistry Interpretation**：才依已採用的手相規則解讀。
- **User-visible synthesis**：把 observation 與 interpretation 清楚區分後輸出。

不得把 interpretation 反推成「影像上一定存在」的 observation。

## 3. Planned Observation Surface｜未來結構化欄位

未來若正式實作，Observation Fact 至少應能容納：

```text
handedness / hand side
image quality / occlusion
palm shape / proportions
finger proportions
major-line visibility
heart line
head line
life line
fate line (if observable)
branches / forks / breaks / islands / intersections
confidence / unknown / not-observable
```

這裡只定義資料責任方向，不先固定 schema、閾值或傳統判讀規則；那些需要後續 source review 與 validation 才能 canonicalize。

## 4. Evidence Boundary｜影像事實不等於玄學結論

必須維持至少三層：

```text
Visual Evidence
→ Observation Fact
→ Traditional / symbolic interpretation
```

規則：

- 可見線條、比例、分叉等屬 observation；
- 「代表感情、性格、人生走向」等屬 interpretation；
- interpretation 不得冒充可驗證的影像事實；
- 影像不清楚時使用 `unknown` / `not observable`，不得補畫、腦補或假定存在；
- 不把手相結果表述成醫療診斷、健康檢查、身份辨識或生物特徵認證。

## 5. Tool / Model Boundary｜CV 工具不是解讀 authority

未來可使用 computer vision / segmentation / landmark detection 協助產生 observation，但：

- CV model 只取得它被驗證能穩定取得的 feature；
- model output 不自動取得 Palmistry interpretation authority；
- external GitHub project、dataset、paper 或 rule set 預設都是 `REFERENCE-ONLY`；
- source 被放入 `references/palmistry/` 不等於被採用為 canonical rule；
- 若沒有可靠 observation capability，允許 AI 直接描述自己能清楚看到的特徵，但必須保留 confidence / uncertainty boundary。

## 6. Runtime Boundary｜不使用 stochastic Draw / Cast

Palmistry 的主要輸入是既有手掌影像／可見特徵，不是 stochastic divination fact，因此目前規劃：

```text
Palmistry
≠ Tarot draw
≠ Meihua number cast
≠ Liuyao three-coin cast
```

除非未來另有被明確採用的混合方法，Palmistry 不進 `RUNTIME_DRAW.md` 的 stochastic path，也不呼叫 `divination-casting-randomizer` 來製造掌紋事實。

## 7. Promotion Gate｜何時才能進 production routing

在把 Palmistry 加入 `METHOD_ROUTING.md` 或 `PLAYBOOK_INDEX.json` 前，至少需要完成：

1. Palmistry judgment responsibility 已能與 Tarot / Meihua / Liuyao 清楚區分；
2. canonical observation schema / fact boundary 已定義；
3. 採用的 interpretation sources / rules 已完成 source、license、流派與 not-adopted boundary review；
4. image-quality / uncertainty / fail-closed 規則已定義；
5. 至少有最小 behavioral regression coverage，證明加入後不影響既有 method routing；
6. structural validation 通過後，才更新 routing / index / user-facing docs。

在此 Gate 完成前：

```text
PALMISTRY.md = Cold scaffold
METHOD_ROUTING.md = unchanged
PLAYBOOK_INDEX.json = unchanged
README production support list = unchanged
```

## 8. External Reference Location

Palmistry 相關 GitHub / paper / dataset / implementation evidence 放在：

```text
references/palmistry/
```

該目錄只做 Cold source dossier；reference existence、技術可行性、模型表現或看起來合理的傳統規則，都不會自動升格成 canonical Playbook capability。
