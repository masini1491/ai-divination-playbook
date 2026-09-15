# AGENTS.md

Project AI mode: ChatGPT-Only

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
| Stochastic Draw / Cast | `RUNTIME_DRAW.md` + `runtime/casting/randomizer.py` |
| Reading lifecycle / durable record | `READING_LIFECYCLE.md` / `READING_RECORD.md` |
| Tarot × Meihua reconciliation | `CROSS_VALIDATION.md` |
| User-visible output | `CHATGPT_OUTPUT.md` |
| Behavioral regression | `BEHAVIORAL_EVAL.md` + `evals/regression_matrix.json` |
| Machine routing | `PLAYBOOK_INDEX.json` |

## Runtime / engine boundary

Canonical stochastic implementation：

```text
runtime/casting/randomizer.py
```

目前只擁有 Tarot draw、Meihua A/B cast、Liuyao three-coin Raw Cast；不解讀。

六爻 deterministic path：

```text
fixed Raw Cast
→ tools/liuyao_calendar.py
→ tools/liuyao_engine.py
→ tools/liuyao_runtime.py
→ LIUYAO.md
```

Astrology production path：

```text
raw birth data / user-supplied structured facts
→ optional tools/astrology_place_resolver.py
→ tools/astrology_provider.py and/or tools/astrology_transit_provider.py
→ Astrology Fact Bundle 1.0
→ tools/astrology_runtime.py
→ ASTROLOGY.md
```

責任邊界：

- Randomizer 只擁有 stochastic Raw Cast authority。
- Liuyao calendar / engine / runtime 只建立 deterministic method facts／composition；`LIUYAO.md` 擁有 judgment、用神與 interpretation governance。
- Astrology resolver / providers 只做 admitted deterministic input resolution／calculation；`tools/astrology_runtime.py` 是 Fact Gate，`ASTROLOGY.md` 擁有 interpretation / source-admission / unsupported-factor governance。
- language model 不得把手算結果冒充 deterministic engine fact。
- research probe、legacy adapter、external calculator 不因存在而取得 production authority。
- user-supplied Astrology facts 必須保留 `user_asserted` provenance。

## Repository / Git identity

- Repository：`masini1491/ai-divination-playbook`
- GitHub account / commit author：`masini1491`
- Commit email：`10146979+masini1491@users.noreply.github.com`

若 local Git 尚未設定 author identity，只做 repository-local 設定；除非使用者明確要求，不修改 global Git identity。不得保存 token、password、API key 或其他 credential。

## GitHub repository retrieval

**Pre-retrieval invariant：** before any current GitHub repository-content claim, GitHub connector capability must be established. GitHub public page／URL preview／search snippet／raw URL 等 alternate transport 不能 bootstrap 或驗證 current repo authority。若 connector unavailable／permission blocked 且 current content materially required，直接 `ACCESS BLOCKED`；不得先引用、摘要或聲稱已確認 alternate transport 所見的 Repo 規則。

所有 GitHub-hosted repository identity、ref、commit、tree、diff、file、section、workflow、external GitHub reference acquisition 一律使用 GitHub connector / GitHub Connect。

禁止以以下方式替代 GitHub repository retrieval：

```text
GitHub public HTML
raw.githubusercontent.com
generic Web search
Python direct HTTP / requests / urllib
curl / wget
git clone
memory / stale cache pretending to be current GitHub authority
```

若 connector unavailable／permission blocked，而 current task materially 依賴 GitHub current content：

```text
minimum exact read recovery
→ still unavailable
→ ACCESS BLOCKED
```

已由 canonical owner 專門治理的 local verified runtime reuse（例如 `RUNTIME_DRAW.md` 的 Randomizer fixed cache）不是新的 GitHub acquisition，可依其 owner 規則 reuse。

Connector retrieval capability ≠ Python execution authority ≠ repository write authority ≠ Reading Record storage authority。

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

正式說明與規則預設繁體中文；technical identifiers 保留原文。

## AI bootstrap / bounded-read discipline

Fresh session 依序：

```text
resolve repository + current ref to exact commit when currentness matters
→ read AGENTS.md
→ use CHATGPT_LOAD_PACK.json at the same resolved revision for eligible ordinary/stochastic profiles
→ read selected method / research canonical owner
→ load only task-required exceptions
→ STOP
```

規則：

1. `CHATGPT_LOAD_PACK.json` 只可作 **derived hot-path cache**。它可以取代 eligible ordinary/stochastic profiles 中重複的 `CHAT_INIT.md` / `METHOD_ROUTING.md` / `RUNTIME_DRAW.md` / `CHATGPT_OUTPUT.md` hot-section retrieval，但不能取代 selected method owner、research owner、Reading Record owner或其他 task-specific canonical authority。Explicit Astrology / research 若不在 pack profile，直接 bounded-read canonical path，不為形式載入 pack。
2. Load pack 必須從與本次 resolved Playbook revision 相同的 GitHub revision 取得；同 revision 下由 CI 的 generator check 保證 canonical excerpts 同步，不為形式再逐一重抓來源 sections。
3. Pack 缺失、無法解析、profile 不涵蓋本題、或出現 ambiguity/conflict 時，直接 fallback 到 `CHAT_INIT.md` 與相關 canonical owner；不得猜。
4. 使用者已指定 method，或已有實際 Draw / Cast Fact / Astrology Fact Bundle 時，不為形式重新 routing、重抽、重卦、重算或換方法。
5. 未指定 ordinary method 才走 `METHOD_ROUTING.md` Fast Path；production Astrology 只接受 explicit request，不參與 ordinary auto-routing。
6. explicit research intent 走 `RESEARCH_ROUTING.md` → named research owner；research pointer 不取得 production method authority。
7. stochastic method 由 AI 代抽／代起才需要 `RUNTIME_DRAW.md` contract；language-model generation ≠ Runtime Draw / Cast。
8. 只有 material contract gap 才讀 `INPUT_CONTRACT.md`；需要拆題／牌位／時間窗設計才讀 `QUESTION_DESIGN.md`。
9. 只有承接／補占／重占／Reality Update／completion／backtest 才讀 `READING_LIFECYCLE.md`；只有保存／跨聊天室／audit 才讀 `READING_RECORD.md`。
10. `BEHAVIORAL_EVAL.md`、`references/`、`CASE_STUDIES/`、Historical Context 預設 Cold。
11. exact owner／section 已唯一時直接讀 target，不增加 discovery ceremony。
12. old chat／memory 不得覆蓋 current reality、原始 Input Contract、Draw/Cast Fact、Astrology Fact Bundle 或 current canonical rule。

## 維護與 validation

- 優先修改既有 canonical owner；只有形成獨立 retrieval intent 才新增文件。
- 不在 README、AGENTS、CHAT_INIT、PLAYBOOK_INDEX、load pack 與 method owner 間人工複製完整 normative policy。
- `CHATGPT_LOAD_PACK.json` 必須由 `tools/build_chatgpt_load_pack.py` 產生；禁止手動把它提升為 authority。
- loader performance budget 由 `tools/chatgpt_load_benchmark.py` + `evals/chatgpt_load_budget.json` 驗證；benchmark 是 deterministic retrieval-cost proxy，不宣稱等同產品 wall-clock latency。
- 新 method / research line discoverability 不等於 production adoption；不得繞過 method owner、runtime/fact gate、behavioral regression 與 explicit admission。
- Runtime stochastic implementation 變更只在本 Repo `runtime/casting/**` 維護；legacy Randomizer repository 只保留 compatibility / rollback / historical provenance responsibility。
- External GitHub reference 納入前，使用 GitHub connector 記錄 source/ref、license、adopted scope、not-adopted boundary。
- 改變 `CHAT_INIT.md`、routing、Runtime、method owner、Reading Record、cross-validation、session continuity 或 loader semantics 時，依 `BEHAVIORAL_EVAL.md` / `evals/regression_matrix.json` 做最低充分 regression。
- 改變 canonical owner 名稱／heading、routing、`PLAYBOOK_INDEX.json`、Behavioral Eval scenario ID、regression matrix 或 local Markdown link，至少執行：

```text
python tools/playbook_check.py .
```

- 修改 loader cache / profiles / hot-section heading 時至少執行：

```text
python tools/build_chatgpt_load_pack.py --check
python tools/chatgpt_load_benchmark.py --check
python -m unittest tests.test_chatgpt_load_pack tests.test_chatgpt_load_benchmark
```

- 修改 checker 本身時至少執行：

```text
python -m unittest tests.test_playbook_check
python tools/playbook_check.py .
```

- repository CI 應執行 full unit-test discovery、root structural checker、load-pack sync check 與 loader budget check。

## 外部參考

可引用公開 Tarot／Meihua／Liuyao／Astrology／Qimen／AI methodology repository；所有 GitHub source acquisition 仍只走 GitHub connector。外部規則不會自動成為本 Repo authority。
