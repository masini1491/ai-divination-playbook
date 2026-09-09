# Reading Record｜正式占卜紀錄格式

本章只處理一件事：**一個已完成抽牌／起卦並形成解讀的占問，若需要跨聊天室保存、後續承接、現實更新或回測，應如何留下可追蹤、可稽核、不可事後漂移的正式紀錄。**

本章不負責：

- 題目輸入欄位 → `INPUT_CONTRACT.md`
- 新題／承接／補占／重占／completion → `READING_LIFECYCLE.md`
- Tarot／Meihua／Liuyao 方法解讀 → 對應 method owner
- Runtime stochastic provenance → `RUNTIME_DRAW.md`
- ChatGPT 最終輸出 → `CHATGPT_OUTPUT.md`

核心原則：

> **Record schema 負責忠實保存當時發生了什麼，不負責重新解釋它。**

> **Original interpretation 不因後來知道結果而覆寫；Reality Update 與 Retrospective Interpretation 必須追加成新層。**

## 1. 何時需要正式 Reading Record

不是每次聊天都必須存檔。符合以下任一情況時，才值得建立正式紀錄：

- 使用者明確要求保存；
- 有 `horizon`／`completion_rule`，未來需要現實驗證；
- 是 follow-up／conditional branch 的 parent；
- 之後可能 Backtest；
- 多人物／多時間窗／多方法比較需保留原始契約；
- 要跨聊天室延續同一 judgment node；
- 需要保留 Runtime Draw / Cast 或 deterministic engine provenance。

純即時反思、一次性聊天且沒有後續價值時，不要求為形式建立長期紀錄。

## 2. Stable Record Identity｜固定紀錄身分

正式紀錄應有穩定、唯一的 `reading_id`。

例如：

```text
reading_id: 20260904-career-001
reading_id: 20260904-relationship-002
```

外部儲存系統可使用更長流水號或 UUID；重點是後續引用同一筆紀錄時不靠檔名猜測。

若承接既有紀錄：

```yaml
parent_reading_id: <id or null>
```

若關係不是單純 parent/child：

```yaml
related_readings:
  - reading_id: <id>
    relation: conditional_branch
  - reading_id: <id>
    relation: comparison_peer
```

`relation` 只記錄 lineage，不自動授予方法論上的承接權；承接是否合法仍由 `READING_LIFECYCLE.md` 判斷。

### 2.1 Container / synthesis / provenance guards

- 多人物／多題／多時間窗若可獨立詢問、驗證、更新、補占或回測，必須各自保留 `reading_id` 與 question identity。
- `container_id`、batch id、group label 只作 presentation／transport pointer，不合併 child reading authority。
- Cross-validation、summary、ranking、comparison、digest、回顧表等預設是 **derived synthesis**；不得覆寫底層 Contract、Method Fact、Reality Update，也不得在沒有新的 draw/cast／現實 observation 時製造新的 source-fact identity。
- Derived synthesis 若需長期保存，應能回到各 source `reading_id`。
- Provenance 只保存實際可證明的 precision；未知欄位保持 `unknown`／`unavailable`／`unverified`，不得補造。

核心原則：**Container may group readings; it does not merge their identity or authority. Derived synthesis may add interpretation; it does not manufacture source facts.**

## 3. Lifecycle Status｜目前狀態

正式紀錄應保存 machine-readable `status`：

```text
interpreted
waiting_for_reality
resolved
unresolved
superseded_contract
reflective_only
```

- `interpreted`：已解讀，但不一定需要等待現實。
- `waiting_for_reality`：預測／時間／條件題，尚未到 completion 或 horizon 判定點。
- `resolved`：已可由現實判定。
- `unresolved`：期限已到或需判定，但現實證據不足。
- `superseded_contract`：原契約有明確缺陷，已建立修正版；舊紀錄保留。
- `reflective_only`：純反思／象徵探索，不建立未來現實驗證責任。

狀態轉移由 `READING_LIFECYCLE.md` 判斷；本檔只保存結果。

## 4. Minimum Metadata｜最低 metadata

Record schema v2：

```yaml
record_schema_version: "2"
reading_id: "..."
created_at: "<ISO-8601 with timezone>"
method: "tarot | meihua | liuyao | tarot+meihua | ..."
question_type: "..."
subject: "..."
horizon: "... | N/A"
completion_rule: "... | N/A"
status: "..."
parent_reading_id: null
```

`method` 保存實際使用的方法 identity；未來新增正式 method 時可使用其 canonical method id，不需要為列舉本身再升 schema。

若已有完整 Input Contract，不必在 metadata 重複所有細節；正文保存原題、context、exclusions、positions／casting contract 即可。

## 5. Six Evidence Layers｜六層證據

正式紀錄仍固定六層；v2 只把 Layer 2 泛化為 **METHOD FACT**，不增加第七層。

### Layer 1 — QUESTION / CONTRACT FACT

保存結果出現前已固定的內容：

- 原始題目；
- `subject`；
- `horizon`；
- `completion_rule`；
- `context_facts`；
- `exclusions`；
- Tarot positions／Meihua casting contract／Liuyao casting contract；
- multi-method 時各方法 responsibility。

這層不能因後續結果或現實發展而回改。

### Layer 2 — METHOD FACT

Layer 2 區分兩種 authority：

```text
2A — RAW DRAW / CAST FACT
2B — STRUCTURED METHOD FACT（方法需要時）
```

#### 2A — Raw Draw / Cast Fact

保存 stochastic 或使用者提供的原始 method input fact。

Tarot：

```text
牌位 → 牌名 → 正／逆位
```

Meihua：

```text
raw input / A / B
```

Liuyao：

```text
raw_lines: [6|7|8|9] × 6
line_order: bottom-to-top
coin values / faces（若 runtime payload 有提供）
```

Raw Fact 一旦固定，不因後續 calculator、engine、解讀或喜好而修改。

#### 2B — Structured Method Fact

只有方法真的需要 deterministic derivation／engine calculation 時才保存；不為形式硬填。

Meihua 可包含：

```text
本卦／互卦／變卦
動爻
體用（若依 canonical rule 可確定）
```

Liuyao 可包含由 deterministic engine 實際產生且本題使用的欄位，例如：

```text
ben_gua
changed_lines
zhi_gua
najia
five_elements
six_relatives
shi_ying
six_spirits
fu_shen
calendar_context
```

Tarot 通常沒有 2B；沒有內容就標 `N/A` 或省略 subsection。

**Structured Method Fact 不等於 Interpretation。** deterministic calculation／mapping 進 Layer 2B；象徵判讀、用神選擇後的 judgment、outcome／obstacle／timing 結論仍進 Layer 3。

若某 method 需要 engine，而 engine unavailable：保留 2A，將 2B 標成 unavailable；不得重抽、手算後冒充 deterministic output，或把缺失 structured fact 靜默塞進 Interpretation。

### Layer 3 — ORIGINAL INTERPRETATION

保存當時第一次正式解讀：

- 逐牌／逐層／逐方法判讀；
- 當時主結論；
- 事前次級／條件分支；
- 當時認定的驗證訊號；
- 當時已明確保留的不確定性。

不得在知道後續結果後重寫這一層。

### Layer 4 — REALITY UPDATE

只保存後來實際發生或可驗證的新事實，並標日期／來源。

Reality Update 不偷塞新的象徵解讀；現實層與解讀層分開。

### Layer 5 — RETROSPECTIVE INTERPRETATION

知道後續現實後重新看牌／卦／盤所得的新理解放這一層，並明確標示為事後重讀，不冒充原始預測。

### Layer 6 — BACKTEST JUDGMENT

依 `READING_LIFECYCLE.md` 的 Backtest Gate 對照：

- 原題／契約品質；
- 原 Method Fact 是否支持；
- 當時主結論；
- 事前次級分支；
- 實際結果；
- 命中／偏移／污染／UNRESOLVED。

Backtest 是評估層，不覆蓋前五層。

核心規則：**Interpretation is not reality evidence; retrospective insight is not original prediction.**

## 6. Append-Only｜後續更新以追加為主

已建立的正式紀錄原則上採 append-only：

- 新 Reality Update → 追加；
- 新 Retrospective Interpretation → 追加；
- 新 Backtest → 追加；
- 原始 Contract／Method Fact／Original Interpretation → 不因後來結果覆寫。

只有 typo、格式錯誤或明確資料轉錄錯誤可以修正，且應留下最小 correction note；不能藉「修正」改變當時結論。

若原題契約本身有缺陷，依 `READING_LIFECYCLE.md` 建立修正版 reading；舊紀錄標 `superseded_contract`，不要刪除。

## 7. Provenance｜Runtime 與 deterministic engine 分離

若使用 Runtime Draw / Cast，保存實際可驗證的 stochastic provenance，例如：

```yaml
casting_provenance:
  tool: divination-casting-randomizer
  algorithm_version: "<version or unknown>"
  schema_version: "<version or unknown>"
  source_commit: "<SHA or unknown>"
  generated_at_utc: "<ISO-8601 or unavailable>"
  generated_at_taipei: "<ISO-8601 or unavailable>"
```

Tarot 可使用等價的 `draw_provenance`；外部儲存系統可採 method-neutral `runtime_provenance`，但不得讓欄位語意變模糊。

若方法需要 deterministic engine，另保存：

```yaml
engine_provenance:
  engine_name: "<name>"
  engine_source_ref: "<commit/version/ref or unknown>"
  structured_fact_fields_used:
    - "..."
```

**Randomizer / stochastic source provenance 與 deterministic engine provenance 必須分離。** 已知 Randomizer commit 不代表 engine commit 已知；反之亦然。

詳細 stochastic source 規則由 `RUNTIME_DRAW.md` 維護；Liuyao structured fact boundary 由 `LIUYAO.md` 維護。

## 8. Human-Readable First｜人可讀，AI 也可解析

推薦格式是薄 front matter + Markdown 正文，而不是把整篇紀錄變成大型 YAML。

```markdown
---
record_schema_version: "2"
reading_id: "20260909-engineering-225"
created_at: "2026-09-09T15:30:00+08:00"
method: "liuyao"
question_type: "completion"
subject: "示例事件"
horizon: "2026-09-30"
completion_rule: "明確事件完成"
status: "waiting_for_reality"
parent_reading_id: null
---

# 示例事件｜六爻

## Layer 1 — Question / Contract Fact
...

## Layer 2 — Method Fact

### 2A — Raw Draw / Cast Fact
...

### 2B — Structured Method Fact
...

## Layer 3 — Original Interpretation
...

## Layer 4 — Reality Update
尚無。

## Layer 5 — Retrospective Interpretation
尚無。

## Layer 6 — Backtest Judgment
尚未到判定點。
```

真正重要的是 identity、status、六層 evidence、method-fact authority boundary 與 append-only history。

## 9. Record Schema Version｜紀錄 schema 版本

目前：

```text
record_schema_version: 2
```

v2 相對 v1 的 material change：

- `method` 不再只列 Tarot／Meihua；正式支援 Liuyao 與未來 canonical methods。
- Layer 2 從單一 `DRAW / CAST FACT` 泛化為 `METHOD FACT`，區分 Raw Fact 與 Structured Method Fact。
- stochastic runtime provenance 與 deterministic engine provenance 明確分離。

### v1 compatibility

既有 `record_schema_version: "1"` 紀錄仍是合法歷史紀錄，**不要求批次 migration、重寫、重抽或補造 metadata**。

```text
v1 record
→ 保留原文
→ current lookup 仍可使用
→ 只有新 reading 使用 v2
→ 舊 reading 後續需要 audit／backtest 時，按原有 evidence precision 處理
```

不要把 v2 欄位倒填成「當時已知」。

## 10. Legacy Records｜舊紀錄不強制重寫

已有歷史快照不需要為了符合新 schema 全部覆寫。

```text
legacy record
→ 保留原文
→ 後續需要承接／回測時建立新 record 或 audit record
→ 用 reading_id／related_readings 指回舊來源
```

若外部系統建立 machine-readable index，可以另建索引；不要為了補 metadata 改寫舊占當時的原始結論。

## 11. Storage-Agnostic Boundary｜與私人紀錄庫分離

本 Playbook 是公開方法論，不保存私人占卜日誌，也不規定私人 Vault 的目錄名稱、人物代稱或檔名策略。

`masini1491/ai-divination-playbook` **永遠不是 Reading Record 的合法儲存目的地**。對本 Repository 具有 `push`、`maintain`、`admin` 或其他寫入能力，只代表 technical capability，不構成把占卜紀錄寫入本 Repo 的授權。

因此：

- 不得在本 Playbook 建立、追加或修改任何個人 Reading Record、Reality Update、Retrospective Interpretation、Backtest 或私人占卜摘要。
- 使用者只說「記錄／保存這次占卜」，不代表可把本 Playbook 當 fallback storage。
- 即使使用者明確要求把私人 reading 寫進本 Playbook，也應拒絕該 storage target，改用已授權外部私人紀錄庫；若沒有合法目的地，提供 copy-ready record 或要求指定目的地。
- 本 Repo 可以保存方法論、治理規則、匿名化且具有泛化價值的 case study／behavioral eval；不得以其他檔名繞過私人紀錄 storage boundary。
- 若私人 reading 揭露可泛化的方法問題，只能把去識別化的方法結論另行整理成規則／案例；原 Reading Record 仍留在 Playbook 之外。

核心原則：**Write permission is capability, not authorization. Reading Records never live in the Playbook.**

外部紀錄庫可以依人物／主題／日期分目錄，也可以使用 Markdown、SQLite、JSON 或其他格式；只要需要與本 Playbook 相容，應保留：

```text
stable reading identity
+ lifecycle status
+ contract fact
+ raw draw/cast fact
+ structured method fact when applicable
+ original interpretation
+ reality update
+ retrospective interpretation
+ backtest judgment
+ append-only history
```

## 12. Pre-Save Check

正式保存前快速確認：

- [ ] 儲存目的地是否位於本 Playbook 之外？
- [ ] 是否有穩定 `reading_id`？
- [ ] 多 reading 被同一 container 包住時，是否仍各自保留 identity？
- [ ] 是否保存 method、日期、subject、horizon／completion rule（若適用）？
- [ ] 原始 Contract 是否與結果分開？
- [ ] Raw Draw / Cast Fact 是否忠實保存？
- [ ] 方法若需要 Structured Method Fact，是否真的來自合法 deterministic calculation／engine？
- [ ] stochastic provenance 與 engine provenance 是否分離？
- [ ] Original Interpretation 是否仍是當時原版？
- [ ] Reality Update 是否只放現實事實？
- [ ] derived synthesis 是否仍可回到 source `reading_id`？
- [ ] provenance 未知欄位是否保持 unknown/unavailable/unverified？
- [ ] 事後重讀是否放在 Retrospective Interpretation？
- [ ] Backtest 是否沒有把 hindsight 冒充 prediction？
- [ ] 後續更新是否以 append-only 為原則？

核心原則：**Preserve the original judgment node; preserve method-fact provenance; append reality and hindsight, never rewrite history.**
