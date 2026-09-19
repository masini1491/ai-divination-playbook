# Meihua Deterministic Materialization｜梅花衍生事實契約

Status: **TASK-SPECIFIC CANONICAL CONTRACT**

本檔只在 `MEIHUA.md` 已固定有效 Cast Fact，但互卦／變卦／體用尚未取得而本題需要完整 Structured Method Fact 時載入。它不取得 stochastic casting、question routing 或 interpretation authority。

## 1. Canonical deterministic source

```text
tools/meihua_engine.py
```

輸入必須是同一個已固定 Cast Fact 的 A/B；若同時提供上／下卦、本卦、動爻，engine 只把它們當 assertion 驗證。一旦 assertion 與 A/B 不一致，**fail closed**；不得改寫原 Cast Fact，也不得重新起卦。

## 2. Fixed derivation convention

本 Repo 採以下 deterministic convention：

- 六爻 bit order：bottom-to-top。
- 互卦：二三四爻成下互，三四五爻成上互。
- 變卦：只翻轉既有動爻的陰陽。
- 體用：動爻所在經卦為「用」，另一個靜經卦為「體」。
- 八卦五行：乾兌金、震巽木、坎水、離火、坤艮土。
- 生克輸出只形成 structural relation：比和／體生用／用生體／體剋用／用剋體；吉凶與原題 interpretation 仍由 `MEIHUA.md` 決定。

傳統依據以《梅花易數》卷一至卷三的互卦、觀梅、體用與五行規則為 source family；本 Repo 將其固定成上述可重現 convention。

## 3. Deterministic pipeline

```text
existing Cast Fact
A/B + 上卦/下卦 + 本卦 + 動爻
→ tools/meihua_engine.py
→ verify Cast Fact consistency
→ derive 互卦
→ derive 變卦
→ derive 體/用 + 五行 relation
→ Structured Meihua Fact
→ MEIHUA.md interpretation
```

engine failure 時：

```text
保留原 Cast Fact
→ MEIHUA STRUCTURED FACT UNAVAILABLE
→ 不重卦
→ 不用 language-model 手算冒充 verified fact
```

## 4. Regression fixture

Canonical regression fixture：

```text
A = 074
B = 803
上卦 = 兌
下卦 = 離
本卦 = 澤火革
動爻 = 初爻
```

Expected deterministic facts：

```text
互卦 = 天風姤（乾上巽下）
變卦 = 澤山咸（兌上艮下）
體 = 兌（金）
用 = 離（火）
體用五行 = 用剋體
```

這個 fixture 只驗 deterministic downstream；不得因此重新 stochastic cast。

## 5. Transport / cache boundary

Canonical authority 永遠是 `tools/meihua_engine.py`。若存在 `runtime/meihua/CHATGPT_DETERMINISTIC_TOOL_BUNDLE.json`，它只能是由 canonical source 產生並由 CI 驗證同步的 **derived transport cache**。

Local cache MISS 不等於 deterministic source unavailable。GitHub Connect 可取得 exact-commit source／bundle且 Python 可執行時，先完成 byte-preserving acquisition / verification，再判斷 unavailable。

核心原則：

> **Preserve Cast Fact, derive downstream deterministically, interpret last.**
