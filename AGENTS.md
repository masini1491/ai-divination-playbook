# AGENTS.md
## Baseline
Shared AI Development Playbook: `masini1491/ai-development-playbook`
Playbook baseline: `main`
Project AI mode: ChatGPT-Only

Shared reporting contract: declared Playbook baseline → `REPORTING.md`
Applicability: substantive user-facing engineering / repository-maintenance replies only; activation-independent and does not replace `CHATGPT_OUTPUT.md` for divination question delivery or interpretation output.
## 儲存庫用途與權威

本儲存庫是可重用、公開的 AI 占卜方法與治理 Playbook，涵蓋 method routing、Input Contract／Question Design、Tarot／Meihua／Liuyao／Astrology、Runtime Draw / Cast、deterministic fact providers、Reading lifecycle／record、cross-validation 與 ChatGPT output governance。

本儲存庫**不是**私人占卜日誌，也**不是**個人預測資料庫。

權威原則：

- `main` 是目前 canonical source of truth。
- 穩定 policy 只保留一個 canonical owner；routing、index、runtime cache 或 generated artifact 不得成為第二份 current-state database。
- `CHAT_INIT.md` 是 fresh-session bootstrap／repository access／freshness／task routing／handoff owner。
- `PLAYBOOK_INDEX.json` 是 machine-readable routing-only capability／owner index；不是 policy authority。
- `CHATGPT_LOAD_PACK.json` 是由 canonical owners 產生的 **derived retrieval cache**；只用來減少 cold-start GitHub reads，不取得 policy authority。若 cache 與 canonical owner 發生任何衝突，以 canonical owner 為準。
- 詳細 capability → owner mapping 由 `PLAYBOOK_INDEX.json` 維護，`AGENTS.md` 不複製完整 ownership catalogue。

### 核心 canonical owners

| Responsibility | Owner |
| --- | --- |
| Fresh-session bootstrap / GitHub access / freshness / handoff gate | `CHAT_INIT.md` |
| Ordinary method selection | `METHOD_ROUTING.md` |
| Explicit research-line routing | `RESEARCH_ROUTING.md` |
| Input / provenance contract | `INPUT_CONTRACT.md` |
| Question decomposition / positions | `QUESTION_DESIGN.md` |
| Tarot / Meihua / Liuyao / Astrology | `TAROT.md` / `MEIHUA.md` / `LIUYAO.md` / `ASTROLOGY.md` |
| Stochastic Draw / Cast | `RUNTIME_DRAW.md` |
| Reading lifecycle / durable record | `READING_LIFECYCLE.md` / `READING_RECORD.md` |
| Tarot × Meihua reconciliation | `CROSS_VALIDATION.md` |
| User-visible output | `CHATGPT_OUTPUT.md` |
| Behavioral regression | `BEHAVIORAL_EVAL.md` + `evals/regression_matrix.json` |
| Machine routing | `PLAYBOOK_INDEX.json` |

## Runtime / engine boundary

Implementation topology 由 direct owners 維護，`AGENTS.md` 只保留最低 routing boundary：

- stochastic → `RUNTIME_DRAW.md`；`runtime/casting/core.py` 是 canonical core，`runtime/casting/randomizer.py` 是 full API / CLI adapter，正式 entrypoint 為 `core.execute_stochastic()`。
- Liuyao deterministic facts → `LIUYAO.md` + `tools/liuyao_calendar.py` / `tools/liuyao_engine.py` / `tools/liuyao_runtime.py`。
- Astrology deterministic facts → `ASTROLOGY.md` + admitted resolver / provider / Fact Gate。
- language model 不得把手算冒充 deterministic engine/provider fact；research probe、legacy adapter、external calculator 不因存在而取得 production authority；user-supplied Astrology facts 保留 `user_asserted` provenance。

## Repository / Git identity

`masini1491/ai-divination-playbook`；author：`masini1491`。其餘 Git identity 只於 maintenance 依 shared baseline處理。

## GitHub repository retrieval

Current GitHub repository authority is **GitHub Connect-only**；bootstrap／access／freshness細節由 `CHAT_INIT.md` 擁有。Alternate public/raw/Web/HTTP/clone transport不得取代 current Repo authority；required connector authority無法建立時 fail closed。

Retrieval capability ≠ connector→runtime handoff ≠ Python execution ≠ repository write ≠ Reading Record storage authority。

## 隱私與公開安全

不得提交：

- 真實姓名或可識別感情／關係細節；
- 可對應特定個人的出生日期、時間、地點；
- 健康、性相關私人紀錄；
- 私人公司未公開人事、薪資、客戶、專案資訊的可識別組合；
- 未去識別化截圖／聊天紀錄；
- secrets／credentials；
- 未授權第三方內容的大段複製。

`SESSION_HANDOFF.md` 只保存模板；真實 Reading Record 永遠不得寫入本公開 Playbook。

**Private inference egress：** private Context 的 disclosure permission 不隨 model／provider／router 或 Task 自動轉移；destination materially 改變時重新核准 disclosure scope，否則 minimize／redact 或 STOP。

正式說明與規則預設繁體中文；technical identifiers 保留原文。

## AI bootstrap / bounded-read discipline

Fresh session：

```text
resolve repo/ref when currentness matters
→ read AGENTS.md
→ apply CHAT_INIT.md activation / load-pack gate
→ same-revision CHATGPT_LOAD_PACK.json when eligible
→ selected method / research owner
→ task-required exceptions only
→ STOP
```

最低 invariants：

1. `CHATGPT_LOAD_PACK.json` 只是 derived cache；canonical owner 永遠優先。Pack miss／conflict／profile不涵蓋時 fallback `CHAT_INIT.md` + task owner。
2. 已指定 method或已有 Draw/Cast/Astrology facts時，保留既有 identity/facts；不為形式 reroute、redraw、recast、recompute。
3. AI 代抽／代起才進 `RUNTIME_DRAW.md`；cache/acquisition/materialization/handoff細節只由該 owner決定，language-model generation ≠ Runtime fact。
4. material/question/lifecycle/record需求才載 `INPUT_CONTRACT.md`／`QUESTION_DESIGN.md`／`READING_LIFECYCLE.md`／`READING_RECORD.md`。
5. `BEHAVIORAL_EVAL.md`、`references/`、`CASE_STUDIES/`預設 Cold；exact owner已知就直讀。
6. old chat／memory 不得覆蓋 current reality、原始 Input Contract、method facts或 current canonical rule。

## 維護與 validation

- 優先修改既有 canonical owner；不在 README／AGENTS／CHAT_INIT／index／load pack／method owner間複製完整 normative policy。
- Generated artifacts（含 `CHATGPT_LOAD_PACK.json`）只由 canonical generator產生；loader budget是 repository-payload proxy，不等同 wall-clock latency。
- Runtime stochastic implementation只在 `runtime/casting/**` 維護；external references仍需 source/ref/license/adopted-scope boundary。
- 變更 bootstrap／routing／Runtime／method owner／Reading lifecycle/record／output或 loader semantics時，依 `BEHAVIORAL_EVAL.md` + regression matrix選最低充分 regression。
- Repository maintenance的 generic GitHub operation、Action Contract Closure與validation procedure由已啟動的 shared development baseline + canonical CI workflow擁有；project-specific local overrides仍優先。

## 外部參考

Declared `masini1491/ai-development-playbook` common baseline 依上方 adoption／activation contract 處理。其他公開 Tarot／Meihua／Liuyao／Astrology／Qimen／AI methodology repository 仍只是 external references；所有 GitHub source acquisition 只走 GitHub connector，其他外部規則不會自動成為本 Repo authority。
