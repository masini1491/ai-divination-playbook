# kentang2017/ichingshifa｜六爻 deterministic engine reference

## Source

- Repository: `kentang2017/ichingshifa`
- Checked ref: `ac1a3f8d89708acc8d547868fc9634c8e2c61d67`
- License file: MIT-style permission notice

## Relevant capability

本 Playbook 研究／採用它的原因不是使用其隨機起卦，而是它能把**既有六爻 6/7/8/9 input**轉成後續六爻結構資料。

公開 README/API 顯示：

```text
mget_bookgua_details(lines)
```

接受六位 `6/7/8/9` 字串，例如：

```text
789789
```

作為 manual line-value input；Repository 亦包含納甲、五行、六親、六獸／六神、世應、伏神、農曆／干支等能力。

## Adopted boundary

目前採用為 **preferred deterministic engine reference**：

```text
divination-casting-randomizer
→ 產生 canonical raw 6/7/8/9

ichingshifa-style deterministic engine
→ 接收已固定 raw lines
→ 建立本卦／之卦與需要的六爻結構 fact

ai-divination-playbook
→ method routing + interpretation governance
```

Randomizer 的 raw cast authority 不交給外部 engine。

## Not adopted

目前不採用：

- `ichingshifa` 自己的 random / yarrow cast 作為本 Playbook 預設六爻 stochastic source；
- time-based casting 取代已固定的 canonical three-coin Raw Cast Fact；
- 外部程式中的自然語言吉凶文案直接升格為本 Playbook interpretation authority；
- 未經驗證就假設任一版本輸出 schema 永久穩定。

## Integration caution

完整納甲排盤可能依賴日期／時間 context。若本題使用月建、日辰、六神、旬空等欄位，應使用同一次 cast 的實際 timestamp 並保存 engine provenance。

若 runtime 無法執行所需 dependencies，保留 Randomizer Raw Cast Fact，並在 `LIUYAO.md` 的 Structured Method Fact Gate fail closed；不得手算後冒充 engine output。
