# 外部參考入口

外部 GitHub 來源的詳細整理已移到 [`references/`](references/) 目錄。

本檔保留作為根目錄入口，避免主規則與來源摘要混在一起。

## 目前主要來源

### 塔羅

- [`references/arcanite.md`](references/arcanite.md) — 問題分類、牌位語意、結構化內容到 LLM 敘事整合。
- [`references/metaphysics-synthesis-skill.md`](references/metaphysics-synthesis-skill.md) — 輸入檢查、抽牌紀律、牌陣選擇、解讀順序、逆位紀律。
- [`references/tarot-mcp.md`](references/tarot-mcp.md) — 牌陣推薦、自訂牌陣、歷史紀錄。
- [`references/tarot-prompt.md`](references/tarot-prompt.md) — 結構化問題／牌面／牌位／背景輸入。
- [`references/tarot-api.md`](references/tarot-api.md) — 牌面資料／牌陣／解讀欄位的分層架構參考。

### 梅花易數

- [`references/muyen-meihua-yishu.md`](references/muyen-meihua-yishu.md) — 起卦來源、雙數算法、重卦紀律、主互變、體用、外應、應期與方法學限制。
- [`references/metaphysics-synthesis-skill.md`](references/metaphysics-synthesis-skill.md) — 輸入檢查、證據角色、外應與應期約束。
- [`references/plum-yi.md`](references/plum-yi.md) — 工具化取卦介面參考。

### 共通 AI 開發治理 baseline

- [`references/ai-development-playbook.md`](references/ai-development-playbook.md) — `masini1491/ai-development-playbook` 的 declared baseline、conditional activation 與本 Repo local overrides；不是 ordinary divination reference。

完整索引與採用標記見 [`references/README.md`](references/README.md)。

## 權威原則

Declared common AI engineering baseline 依 `AGENTS.md` / `CHAT_INIT.md` 的 adoption 與 activation contract處理；其餘外部來源只提供研究證據與可借鑑方法。本 Repo 的 project-specific正式規則仍以本地 canonical owners為準。

來源更新時：

1. 先更新對應 `references/*.md`。
2. 比較新內容是否真的改善本手冊。
3. 只有確認值得採用後，才修改主規則。
4. 不讓外部 Repo 的流派選擇、實作細節或授權內容自動變成本手冊的權威。
