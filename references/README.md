# 外部 GitHub 參考索引

此目錄保存外部 GitHub 專案的**來源摘要、可借鑑方法、採用狀態、差異與授權注意事項**。

核心規則仍以本 Repo 根目錄文件為準；這裡不是第二套規則來源。

## 使用原則

每個來源檔盡量回答：

1. 這個 Repo 是什麼？
2. 哪些內容與「問題設計／牌位契約／起卦治理／ChatGPT 輸出治理」直接相關？
3. 哪些已被本手冊吸收？
4. 哪些不採用或只列為候選？
5. 授權上能否直接複製內容，還是只能概念性參考？
6. 該來源的 authority boundary 與 do-not-assume 是什麼？

若來源會持續更新，建議在 dossier 中保存 reviewed revision／日期或 commit，以便日後判斷差異與 freshness。

## 已收錄

### 塔羅

- [`arcanite.md`](arcanite.md) — 問題分類、牌位特定語意、結構化內容到 LLM 敘事整合。
- [`metaphysics-synthesis-skill.md`](metaphysics-synthesis-skill.md) — 塔羅輸入檢查、抽牌紀律、牌陣選擇、解讀順序、逆位紀律。
- [`tarot-mcp.md`](tarot-mcp.md) — AI 牌陣推薦、自訂牌陣、歷史紀錄、依問題背景選擇解讀。
- [`tarot-prompt.md`](tarot-prompt.md) — 結構化問題／牌面／牌位／背景輸入。
- [`tarot-api.md`](tarot-api.md) — 牌組／牌陣／牌面資料分離的工具架構參考。
- [`veiled-stars.md`](veiled-stars.md) — 長期塔羅紀錄、原始事實／解讀／回顧分層與 append-only history。

### 梅花易數

- [`muyen-meihua-yishu.md`](muyen-meihua-yishu.md) — 起卦來源、雙數算法、重卦紀律、主互變、體用、外應、應期與方法學限制。
- [`metaphysics-synthesis-skill.md`](metaphysics-synthesis-skill.md) — 梅花輸入檢查、證據階層、外應與應期約束。
- [`plum-yi.md`](plum-yi.md) — 簡化取卦 App 的工具化方向。

### AI／ChatGPT 方法治理

- [`ai-development-playbook.md`](ai-development-playbook.md) — canonical policy owner、Progressive Reading、scope control、Completion Evidence Guard、證據層級、最低充分輸出與 One Question = One Copy Surface。
- [`yifortune.md`](yifortune.md) — 單一入口、progressive disclosure、Agent 主動 routing 與最小必要提問。
- [`t-ai-skills.md`](t-ai-skills.md) — truth layer／interpretation layer 分離、統一 machine envelope 與 unavailable/graceful degradation。
- [`metaphysics-synthesis-skill.md`](metaphysics-synthesis-skill.md) — 多方法 router、輸入完整度與系統間邊界。

### 手相（研究階段）

- [`palmistry/README.md`](palmistry/README.md) — Palmistry Cold reference index；分開 observation / CV 與 tradition-specific interpretation source，尚未進 production routing。

## 採用標記

來源檔內保留英文狀態碼作為固定識別字，旁邊一律附繁中語意：

- **ADOPTED｜已採用**：已整併成主規則。
- **ADAPTED｜調整後採用**：吸收概念，但改寫成符合本手冊的規則。
- **REFERENCE-ONLY｜僅供參考**：保留參考，不直接成為規則。
- **REJECTED｜不採用**：明確不採用，並記錄原因。

若來源日後更新，不應自動覆寫本手冊；先比較差異，再決定是否修改主規則。
