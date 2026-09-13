# AGENTS.md

Project AI mode: ChatGPT-Only

## 儲存庫用途

本儲存庫是一套可重用、公開的 AI 占卜方法與治理 Playbook，用於：

- 自然語言占問 → method routing；
- 明確 research intent → bounded research-line discovery；
- 低歧義 Input Contract／Question Design；
- Tarot／Meihua／Liuyao／Astrology method-specific contract；
- ChatGPT Runtime Draw / Cast governance；
- deterministic Astrology place resolution + natal/transit calculation + Fact Gate governance；
- Reading lifecycle、Reading Record、Reality Update、Backtest；
- cross-validation／derived synthesis 的 evidence boundary；
- ChatGPT user-visible output governance。

本儲存庫**不是**私人占卜日誌，也**不是**個人預測資料庫。

## 權威與文件 ownership

- `main`：目前 canonical source of truth。
- `CHAT_INIT.md`：fresh-session bootstrap、repository access、Playbook freshness、task routing、session handoff gate。
- `PLAYBOOK_INDEX.json`：machine-readable routing-only capability／owner index；不是 policy/state authority。
- `SESSION_HANDOFF.md`：最低充分 handoff checkpoint adapter；不是 Reading Record authority。
- `METHOD_ROUTING.md`：未指定方法時，依 judgment function 選目前正式支援的方法；Astrology v1 只接受 explicit user override，不參與 ordinary auto-routing。
- `RESEARCH_ROUTING.md`：使用者明確指定 Astrology research / Palmistry 等已登錄 research line 時的 research owner discovery、authority boundary 與 ordinary-router separation；不是 production method router。
- `INPUT_CONTRACT.md`：題目、method input 與 provenance contract。
- `QUESTION_DESIGN.md`：題目拆解、position responsibility、高頻題型。
- `READING_LIFECYCLE.md`：新題／承接／補占／重占／Reality Update／completion／backtest。
- `READING_RECORD.md`：durable reading identity、evidence layers、append-only、storage boundary。
- `RUNTIME_DRAW.md`：ChatGPT／AI stochastic draw/cast 的 runtime capability、canonical source、cache、provenance、fail closed。
- `TAROT.md`：Tarot-specific contract。
- `MEIHUA.md`：Meihua-specific contract。
- `LIUYAO.md`：Liuyao judgment responsibility、Raw Cast → Structured Method Fact、interpretation、engine fail-closed contract。
- `ASTROLOGY.md`：Astrology Production v1 method owner；explicit-request activation、place resolution、natal/transit providers、Fact Gate、admitted interpretation policy 與 unsupported-factor boundary。
- `ASTROLOGY_PRODUCTION_ADMISSION_V1.json`：Astrology v1 machine-readable production-admission manifest；不是 research source database。
- `ASTROLOGY_PROVIDER_ADMISSION_V1.json`：Astrology natal provider 的 dependency/input/calculation/provenance admission manifest。
- `ASTROLOGY_TRANSIT_PROVIDER_ADMISSION_V1.json`：Astrology transit event-search provider 的 bounded calculation admission manifest。
- `ASTROLOGY_PLACE_RESOLVER_ADMISSION_V1.json`：Astrology offline city/locality resolver 的 dependency/data-license/resolution admission manifest。
- `tools/astrology_place_resolver.py`：offline city/locality → coordinates + IANA timezone input-resolution owner；不取得天文 authority。
- `tools/astrology_provider.py`：admitted raw-birth-data natal provider；使用 pinned MIT Astronomy Engine + project-owned house/aspect derivation產生 Astrology Fact Bundle 1.0，不解讀。
- `tools/astrology_transit_provider.py`：admitted bounded transit event-search provider；搜尋 exact transit-to-natal aspects、stations、tropical ingresses/re-ingresses，不解讀。
- `tools/astrology_runtime.py`：Astrology Fact Bundle 1.0 production gate；驗證 provider/supplied facts 是否可進 interpretation，不重新計算天文位置。
- `CROSS_VALIDATION.md`：目前正式 Tarot × Meihua reconciliation 與 evidence lineage／independence guard。
- `CHATGPT_OUTPUT.md`：最終出題、解讀、Copy-ready、Pre-Send output contract。
- `BEHAVIORAL_EVAL.md`：低頻 cold-start／behavioral regression scenarios。
- `evals/regression_matrix.json`：change-class → scenario selection metadata。
- `tools/behavioral_eval.py`：eval run record／matrix deterministic validation；不做 semantic grading。
- `tools/playbook_check.py`：structure/link/router/index consistency checker。
- `tests/test_playbook_check.py`：checker unit + repository-root integration tests。
- `tools/liuyao_engine.py`：zero-dependency deterministic Liuyao structural engine；只產生 Structured Method Fact，不解讀。
- `tools/liuyao_calendar.py`：zero-dependency Liuyao calendar fact provider；只產生月建／日辰／旬空等 deterministic calendar facts，不解讀。
- `tools/liuyao_runtime.py`：把已固定 Raw Cast、calendar facts 與 structural engine 組合成完整 deterministic runtime payload，並提供 derived human presentation；不選用神、不解讀。
- `tools/liuyao_engine_adapter.py`：legacy / fallback external-engine adapter；不是目前 production structural owner。
- `references/`：Cold external source dossier；不自動取得 policy authority。Astrology research evidence可被 production manifest bounded-admit，但 research 檔案本身不因此改成 production owner。
- `CASE_STUDIES/`：Cold anonymized failure cases。

### Runtime / engine boundary

Stochastic implementation 不在本 Repo 維護：

```text
masini1491/divination-casting-randomizer/randomizer.py
```

目前擁有：

```text
Tarot draw
Meihua A/B cast
Liuyao three-coin Raw Cast
```

六爻 production deterministic path：

```text
fixed Raw Cast
→ tools/liuyao_calendar.py
→ tools/liuyao_engine.py
→ tools/liuyao_runtime.py
→ LIUYAO.md
```

Astrology Production v1 natal path：

```text
raw birth data
→ optional tools/astrology_place_resolver.py  # city/locality only; fail closed on ambiguity
→ explicit local wall time + IANA timezone + coordinates
→ tools/astrology_provider.py
→ Astrology Fact Bundle 1.0
→ tools/astrology_runtime.py
→ ASTROLOGY.md
```

Astrology Production v1 transit path：

```text
admitted natal Astrology Fact Bundle
+ bounded UTC search window / moving bodies / natal targets / major aspects
→ tools/astrology_transit_provider.py
→ transit Astrology Fact Bundle 1.0
→ tools/astrology_runtime.py
→ ASTROLOGY.md
```

Alternative admitted fact path：

```text
user-supplied structured export / verified existing record
→ Astrology Fact Bundle 1.0
→ tools/astrology_runtime.py
→ ASTROLOGY.md
```

責任邊界：

- Randomizer 只擁有 stochastic Raw Cast authority。
- `liuyao_calendar.py` 只擁有 calendar fact calculation authority。
- `liuyao_engine.py` 只擁有 structural chart calculation authority。
- `liuyao_runtime.py` 只做 deterministic composition 與 derived presentation，不取得 interpretation / yongshen authority。
- `LIUYAO.md` 才擁有 judgment responsibility、用神 responsibility 與 interpretation governance。
- `astrology_place_resolver.py` 只做 city/locality input resolution；同名多地、not-found 都 fail closed；不自動挑人口最大地點，也不取得天文 authority。
- `astrology_provider.py` 擁有 admitted natal astronomical/house/aspect calculation authority；不解讀、不搜尋 transit events。
- `astrology_transit_provider.py` 擁有 admitted bounded transit exact-event search authority；canonical event time 是 UTC；不做 event-outcome interpretation。
- `astrology_runtime.py` 只驗證 Astrology facts 與 production config；任何 provider output 也不得繞過它。
- `ASTROLOGY.md` 擁有 Astrology v1 interpretation / source-admission / unsupported-factor governance。
- research 階段 `pyswisseph` probes 與 external calculators 不因存在而取得 production authority。
- user-supplied Astrology facts 必須保留 `user_asserted` provenance。
- `references/ichingshifa.md` 與 `tools/liuyao_engine_adapter.py` 保留作歷史／fallback／reference surface，不覆蓋目前 production lightweight path。

穩定 policy 只保留一個 canonical owner；routing/index/runtime 不複製完整 normative policy，也不得成為第二份 current state database。

## 儲存庫與 Git 身分設定

- Repository：`masini1491/ai-divination-playbook`
- GitHub 帳號：`masini1491`
- Git commit author name：`masini1491`
- Git commit author email：`10146979+masini1491@users.noreply.github.com`

若 local Git 尚未設定 author identity，只做 repository-local 設定：

```bash
git config user.name "masini1491"
git config user.email "10146979+masini1491@users.noreply.github.com"
```

除非使用者明確要求，不修改 global Git identity；不得保存 token、password、API key 或其他 credential。

## GitHub Connect 讀取規則

所有 **GitHub-hosted repository retrieval** 一律走 GitHub connector / GitHub Connect。這是 project-wide 規則，不只適用於本 Repository。

包括：

- 本 Repo 的 branch／tag／commit／tree／diff／file／section；
- `divination-casting-randomizer`；
- Liuyao／Astrology provider／Qimen／未來 method engine；
- `references/` 中任何 GitHub external source；
- repo rename、freshness、comparison、license、release 或 source audit。

禁止把以下當成 GitHub repository retrieval fallback：

```text
GitHub public HTML
raw.githubusercontent.com
generic Web search
Python direct HTTP / requests / urllib
curl / wget
git clone
memory / stale unverified cache
```

若 GitHub connector unavailable，而 current task materially 依賴 GitHub current content：

```text
minimum connector/read recovery
→ still unavailable
→ ACCESS BLOCKED
```

不要改走 public/raw/Web。

例外只有已由其他 canonical owner 明確治理的**本地 verified runtime reuse**：例如 `RUNTIME_DRAW.md` 的 Randomizer deterministic cache。這種情況沒有新的 GitHub acquisition，因此可直接 reuse；一旦真的需要重新取得 GitHub source，仍只能走 GitHub connector。

GitHub retrieval capability 不代表 Python execution、repository write 或 Reading Record storage authority。

完整 repository access policy 由 `CHAT_INIT.md` 擁有；AGENTS 只保留 project-wide 摘要，不複製全部 recovery semantics。

## 語言規則

- 正式說明、規則、案例與 reference 摘要預設繁體中文。
- 程式欄位、檔名、API、GitHub repository、schema key、draw/cast id 等 technical identifiers 保留原文。
- 外部來源以繁中摘要，不把大段第三方文字直接搬進 canonical rules。

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

## AI 讀取紀律

- 實際使用先讀 `CHAT_INIT.md`，再依 task bounded-read minimum canonical owners。
- 所有 GitHub-hosted repository read/search/ref/diff 只用 GitHub connector；不得改走 public/raw/Web。
- machine consumer 可選 `PLAYBOOK_INDEX.json` 做 owner discovery；命中後仍回 canonical Markdown owner。
- 使用者明確要求 production Astrology reading 時讀 `ASTROLOGY.md`；Astrology v1 不參與 ordinary auto-routing。
- 使用者明確指定 research intent 時讀 `RESEARCH_ROUTING.md` → named research owner；research pointer 不加入 ordinary method auto-selection。
- 方法未指定且屬 ordinary reading 才讀 `METHOD_ROUTING.md`；若使用者已指定 method 或已有實際 Draw / Cast Fact / Astrology Fact Bundle，不為形式重新 routing。
- `BEHAVIORAL_EVAL.md`、`references/`、`CASE_STUDIES/`、Historical Context 預設 Cold；明確 research intent 只 bounded-load 對應 research owner與必要 evidence，不因此掃完整 `references/`。
- AI 要自行抽／起 stochastic method 才載入 `RUNTIME_DRAW.md`。
- 選到 Liuyao 才載入 `LIUYAO.md`；需要完整 structured chart 時才執行 `tools/liuyao_runtime.py` 的 deterministic path。
- Astrology raw birth data 若只有 city/locality 名稱，可先用 `tools/astrology_place_resolver.py`；歧義或不支援的地址粒度必須 fail closed，不由模型猜座標或 timezone。
- Astrology natal raw birth data 有 exact/approximate time、IANA timezone 與 coordinates 時，可交給 `tools/astrology_provider.py`；其輸出仍必須通過 `tools/astrology_runtime.py`。模型本身不得手算。
- Astrology transit 需要 exact event 時，可由 `tools/astrology_transit_provider.py` 消費 admitted natal bundle；search span 必須在 provider boundary 內，輸出仍須 runtime gate。
- 只有保存／跨聊天室／Backtest／audit 才載入 `READING_RECORD.md`。
- 只有 material session-health risk 才載入 `SESSION_HANDOFF.md`。
- exact section／owner 已唯一時直接讀 target，不為 routing 增加 ceremony。
- old chat／memory 不得覆蓋 current reality、original Input Contract、Draw/Cast Fact、Astrology Fact Bundle 或 current canonical rule。

## 維護風格

- 優先修改既有 canonical owner；只有形成獨立 retrieval intent 才新增文件。
- 新 method 的正確擴充順序：

```text
judgment gap
→ method owner
→ casting / deterministic engine or fact-gate authority
→ routing
→ runtime / provenance
→ behavioral regression
→ user-facing docs
→ explicit admission decision
```

- research-line discoverability 不等於 method adoption；`RESEARCH_ROUTING.md` / `PLAYBOOK_INDEX.json` pointer 不得繞過上述順序。
- 不因 Repo 名稱泛化就宣稱未定義方法已支援。
- Runtime stochastic implementation 變更優先改 Randomizer repo；Playbook 只同步 governance contract。
- deterministic calculation 必須有單一清楚 owner；不得讓 language model 手算結果冒充 engine fact，也不得讓 legacy adapter / research probe 覆蓋 current production owner。
- External GitHub reference 納入前，一律用 GitHub connector 取得並記錄 source/ref、license、採用範圍、not-adopted boundary。
- 不在 README、AGENTS、CHAT_INIT、PLAYBOOK_INDEX 與 method owner 間複製完整 normative policy。
- `CROSS_VALIDATION.md` 目前只擁有已正式定義的 reconciliation；新增 method 或 research line 不代表自動獲得 pairwise cross-validation semantics。
- 任何改變 `CHAT_INIT.md`、`METHOD_ROUTING.md`、`RESEARCH_ROUTING.md`、`RUNTIME_DRAW.md`、method owner、Reading Record、cross-validation、session continuity 等 Agent behavior 的 contract，依 `BEHAVIORAL_EVAL.md`／`evals/regression_matrix.json` 做最低充分 regression。
- 任何會修改 canonical owner 名稱／heading、`CHAT_INIT.md` routing、`PLAYBOOK_INDEX.json`、Behavioral Eval scenario ID、regression matrix 或 local Markdown link 的變更，至少執行：

```text
python tools/playbook_check.py .
```

- 修改 checker 本身時至少執行：

```text
python -m unittest tests.test_playbook_check
python tools/playbook_check.py .
```

- repository CI 應至少執行 full unit-test discovery 與 root structural checker，避免 fixture-only tests 全綠但 canonical root 已漂移。
- 純 Markdown 修改至少檢查 routing、heading、link、ownership、authority boundary 是否矛盾。

## 外部參考

可引用公開 Tarot／Meihua／Liuyao／Astrology／Qimen／AI methodology repository，但所有 GitHub source acquisition 只走 GitHub connector。外部規則不會自動成為本 Repo authority；整併時必須保留 premise、流派差異、license、authority boundary 與 not-adopted items。