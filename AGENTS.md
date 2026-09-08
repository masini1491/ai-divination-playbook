# AGENTS.md

## 儲存庫用途

本儲存庫是一套可重用、公開的實戰手冊，用於設計低歧義的塔羅與梅花易數題目、方法選擇、牌陣、占問生命週期、ChatGPT Runtime Draw、正式 Reading Record、交叉驗證方法，以及控制 ChatGPT 的出題與解讀輸出。

本儲存庫**不是**私人占卜日誌，也**不是**個人預測資料庫。

## 權威與文件 ownership

- `main` 是目前可信來源（source of truth）。
- `CHAT_INIT.md`：新聊天室最小 bootstrap／routing；同時維護 repository access、Playbook freshness 與長聊天室 handoff gate。
- `PLAYBOOK_INDEX.json`：machine-readable routing-only manifest；只做 stable capability／owner discovery，不保存 current state 或 policy wording。
- `SESSION_HANDOFF.md`：長聊天室最低充分 checkpoint adapter；不是 Reading Record 或 authority。
- `METHOD_ROUTING.md`：使用者未指定方法時，依主要 judgment function 選 Tarot／Meihua／Both；包含 single-method sufficiency、Both responsibility 與 tie-breaker gate。
- `INPUT_CONTRACT.md`：抽牌／起卦前需要保存的輸入契約與 draw/cast provenance。
- `QUESTION_DESIGN.md`：問題拆解、牌位功能與高頻題型模式。
- `READING_LIFECYCLE.md`：新題／承接／補占／重占／現實更新／完成／回測。
- `READING_RECORD.md`：正式長期紀錄的 stable identity、lifecycle status、六層證據、information-integrity guards 與 append-only 保存契約；不規定私人 Vault 的目錄結構。
- `RUNTIME_DRAW.md`：ChatGPT／AI 何時可以實際執行程式抽牌／起卦、canonical tool、source acquisition、provenance 與 fail-closed fallback。
- `TAROT.md`：塔羅特有的牌位、牌陣與解讀規則。
- `MEIHUA.md`：梅花特有的起卦、體用、主互變、動爻、外應與應期規則。
- `CROSS_VALIDATION.md`：Tarot × Meihua 的分工、reconciliation 與 evidence lineage／independence guard。
- `CHATGPT_OUTPUT.md`：ChatGPT 最終出題、解讀、copy-ready 與 pre-send output contract。
- `BEHAVIORAL_EVAL.md`：低頻 cold-start／regression 行為驗證 scenarios；只驗證 Agent 是否遵守 canonical rules，不取代各主文件 authority，也不在一般占問預設載入。
- `evals/regression_matrix.json`：Behavioral Eval change-class → scenario selection metadata；selection-only。
- `tools/behavioral_eval.py`：只做 eval run record／regression matrix 的 deterministic metadata validation，不做 LLM semantic grading。
- `tools/playbook_check.py`：Playbook 結構一致性的 deterministic checker；檢查 local Markdown links／anchors、`PLAYBOOK_INDEX.json` owner／section／adapter／runner、`CHAT_INIT.md` routed owner，以及 `BEHAVIORAL_EVAL.md` ↔ regression matrix scenario closure。
- `tests/test_playbook_check.py`：`tools/playbook_check.py` 的單元測試；涵蓋正常 repo、manifest section drift、behavioral matrix drift 與缺失 routed owner。
- `CASE_STUDIES/`：匿名化、低頻載入的失敗案例與方法演進。
- `references/`：外部來源 dossier；不自動取得主規則權威。

Runtime Draw 的 RNG／抽牌／起卦**實作**不在本 Repo 維護；canonical implementation 是 `masini1491/tarot-plum-randomizer/randomizer.py`。本 Repo 只維護治理與使用契約，避免演算法重複造成 drift。

穩定 policy 只保留一個 canonical owner；routing/index/adapter 不複製完整 normative policy，也不得成為第二份 current state database。

## 儲存庫與 Git 身分設定

- Repository：`masini1491/tarot-meihua-question-playbook`
- GitHub 帳號：`masini1491`
- Git commit author name：`masini1491`
- Git commit author email：`10146979+masini1491@users.noreply.github.com`
- 若 local Git 尚未設定 author identity，只做 repository-local 設定：

```bash
git config user.name "masini1491"
git config user.email "10146979+masini1491@users.noreply.github.com"
```

除非使用者明確要求，不修改 global Git identity；不得保存 token、password、API key 或其他 credential。

## 語言規則

- 正式說明、規則、案例與參考摘要預設使用繁體中文。
- 程式欄位、檔名、API 名稱、GitHub repository、schema key、seed、draw id 等技術識別字保留原文。
- 外部來源以繁中摘要，不直接把原文語氣搬進主規則。

## 隱私與公開安全

不得提交：

- 真實姓名或可識別的感情／關係細節；
- 可對應特定個人的出生日期、時間與地點；
- 健康、性相關私人紀錄；
- 私人公司名稱與未公開人事、薪資、客戶或專案資訊之組合；
- 未經去識別化的截圖、聊天紀錄或其他私人來源材料；
- secrets、credentials 或未授權第三方內容的大段複製。

案例只保留足以說明方法問題的最低必要結構。`SESSION_HANDOFF.md` 只保存模板，不保存任何使用者實際 handoff payload；真實 Reading Record 永遠不得寫入本 Playbook。

## AI 讀取紀律

- 實際使用先讀 `CHAT_INIT.md`，再依 task 只讀最低必要 canonical sections。
- machine consumer 可選讀 `PLAYBOOK_INDEX.json` 找 stable owner pointer，但 index 命中後仍要回 canonical Markdown owner 判斷語意。
- 使用者未指定 Tarot／Meihua／Both，而 workflow 需要決定占卜方法時，才載入 `METHOD_ROUTING.md`；若方法已由使用者指定或已有既存牌面／卦象，不為形式重跑 method routing。
- 不因某文件存在就預設完整載入；`BEHAVIORAL_EVAL.md`、`CASE_STUDIES/`、`references/`、Historical Context 預設是 Cold。
- 只有使用者要求 ChatGPT 自己抽牌／起卦，或 workflow 明確需要 AI Runtime Draw 時才載入 `RUNTIME_DRAW.md`；一般使用者自行抽牌不付這段 Context 成本。
- 只有使用者要求保存、跨聊天室承接、正式回測／audit，或 workflow 明確需要建立長期 Reading Record 時才載入 `READING_RECORD.md`；一般即時解讀不付這段 Context 成本。
- 只有 session-health material risk 需要 fresh-session recovery 時才讀 `SESSION_HANDOFF.md`；聊天很長本身不是載入理由。
- 只有使用者要求 cold-start／regression validation，或本次規則變更需要驗證 AI 實際行為時，才載入 `BEHAVIORAL_EVAL.md`；不要把 eval scenario 當作日常 workflow instruction。
- 若 exact section／問題身份已能唯一命中 owner，可直接 bounded-read，不為 routing 做額外 ceremony。
- 舊聊天室、memory 或歷史占卜不得覆蓋 current reality、原 Input Contract 或目前主規則。

## 維護風格

- 優先修改既有 canonical owner；只有形成獨立 retrieval intent 才新增文件。
- 新案例若揭露可泛化失敗模式，先判斷應更新哪個主規則，再新增匿名案例。
- 不在 README、AGENTS、CHAT_INIT、PLAYBOOK_INDEX 與主題文件間複製完整 normative policy。
- Runtime implementation 變更優先修改 Randomizer repo；Playbook 只在 governance contract 改變時同步。
- 修改 `CHAT_INIT.md`、`METHOD_ROUTING.md`、`RUNTIME_DRAW.md`、`READING_RECORD.md`、`CROSS_VALIDATION.md` 或 session continuity 等會改變 Agent 行為的 contract 後，依 `BEHAVIORAL_EVAL.md`／`evals/regression_matrix.json` 判斷最低充分 behavioral regression；不為純文字排版強制 full suite。
- 可機械判斷的 routing／matrix／record metadata 可以交給 deterministic tool；需要 interpretation／judgment 的規則不得假裝由簡單 validator 決定。
- 任何會修改 canonical owner 名稱／heading、`CHAT_INIT.md` routing、`PLAYBOOK_INDEX.json`、Behavioral Eval scenario ID、regression matrix 或 local Markdown link 的變更，至少執行 `python tools/playbook_check.py .`。
- 修改 `tools/playbook_check.py` 本身時，至少執行 `python -m unittest tests.test_playbook_check`；若 checker contract 同時變更，再跑一次 repository-level `python tools/playbook_check.py .`。
- 純 Markdown 修改至少檢查 routing、heading、link 與 ownership 是否矛盾；新增 canonical／validation surface 後確認可由 `CHAT_INIT.md`／`PLAYBOOK_INDEX.json` 等預期 discovery path 命中，不依賴模型猜檔名。

## 外部參考

可引用公開的塔羅／梅花易數／AI 方法論 GitHub 專案，但外部規則不會自動成為本儲存庫權威。整併時記錄前提、流派差異、authority boundary、授權與不採用項目。
