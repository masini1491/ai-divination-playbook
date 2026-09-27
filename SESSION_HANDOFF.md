# Session Handoff｜長聊天室最低充分交接

> **Role**：把 `CHAT_INIT.md` 的 `Session Continuity / Handoff Gate` 轉成可直接使用的薄 checkpoint adapter。
>
> **Authority boundary**：handoff 只是一個 retrieval／recovery index，不是現實 truth、Reading Record、抽牌結果、補占授權或 repository write permission。

## When to use

只在長 session 已出現 material stale-premise／retrieval risk，或即將進入高影響 judgment boundary 且 current session health 可能影響 correctness 時使用。

不要只因聊天很長、訊息很多或主觀覺得 Context 可能快滿就建立 handoff；除非產品真的暴露可信 context meter，否則不得捏造 token／百分比。

## Compact payload

```json
{
  "handoff_version": 1,
  "playbook": {
    "repository": "masini1491/ai-divination-playbook",
    "ref": "main",
    "observed_head": "<40-char SHA or UNKNOWN>"
  },
  "active_readings": [
    {
      "reading_id": "<id or UNKNOWN>",
      "subject": "<minimum non-sensitive label>",
      "status": "<interpreted / waiting_for_reality / resolved / ...>",
      "horizon": "<value or N/A>",
      "completion_rule": "<value or N/A>",
      "source_pointer": "<private record pointer or conversation-local pointer>"
    }
  ],
  "confirmed_reality": ["<only current confirmed facts needed next>"],
  "symbolic_working_branches": ["<conditional premise; never rewrite as confirmed fact>"],
  "superseded_assumptions": ["<only if forgetting it would cause regression>"],
  "unresolved_functions": ["<what the current readings did not answer>"],
  "canonical_pointers": [
    {
      "path": "<Playbook file>",
      "section": "<optional exact section>"
    }
  ],
  "next_safe_action": "<interpret / wait for reality / design follow-up / STOP>",
  "stop_conditions": ["<material evidence or authority condition requiring STOP>"]
}
```

Unknown values保持 `UNKNOWN`／pending，不為了讓 checkpoint 看起來完整而猜值。

## Privacy / Storage Boundary

- Checkpoint 若包含真實人物、感情、健康、性、工作等私人占卜內容，預設只留在 conversation／使用者合法私人紀錄庫；**不得寫入本公開 Playbook**。
- 若需要 durable Reading Record，依 `READING_RECORD.md`，並使用 Playbook 之外的合法儲存目的地。
- `subject` 若會出現在可分享 handoff payload，優先使用最低充分代稱；不要因 handoff 方便而擴張 private-to-public exposure。

## Rehydration procedure

Fresh session 必須：

`Confirm current Playbook ref / HEAD → read current CHAT_INIT.md → follow canonical pointers → resolve active reading identities from actual source → reconcile confirmed reality / symbolic branches / superseded assumptions → continue only the currently authorized judgment function`

具體規則：

- current canonical Playbook 與 handoff 衝突時，current canonical rule 優先；handoff 不覆蓋 authority。
- 已確認現實事實若有新的可靠 evidence，更新 current reality；但不得回頭改寫舊 reading 的 Original Interpretation。
- symbolic working branch 仍只是條件前提；fresh session 不得因 handoff 重述就升格成 confirmed fact。
- `reading_id`／source pointer 能命中正式私人紀錄時，回原 source；不要只靠 checkpoint summary 冒充完整 Reading Record。
- Handoff 不構成重新抽牌理由；是否為 new judgment node／合法 follow-up 仍由 `READING_LIFECYCLE.md` 決定。
- 若 current Playbook HEAD 已前進，依 `CHAT_INIT.md` 的 Playbook Freshness Probe 做 bounded material-delta reconciliation，不因任何 commit 就全文重載。

## Repository-maintenance durable checkpoint adapter

當 intent 是 repository maintenance／research maintenance／GitHub workflow，而不是私人 reading continuation，且 `REPOSITORY_ARCHITECTURE.md` 已為該 method opt-in exact continuity thread時，可在一個 **material logical action closure** 後追加一筆 sanitized durable checkpoint event。

Durable event只保存 control state：

```json
{
  "continuity_version": 1,
  "repository": "masini1491/ai-divination-playbook",
  "ref": "main",
  "producer_observed_revision": "<40-char SHA>",
  "work_identity": "<backlog item / PR / stage / bounded task>",
  "current_result_pointer": "<canonical file / PR / workflow run / artifact pointer>",
  "validation_boundary": "<PASS / unresolved blocker / exact condition>",
  "next_authorized_action": "<bounded action or STOP>"
}
```

不適用欄位可省略；不得為完整感補猜。Event不是 self-contained transcript。

### Durable event trigger

只有以下條件同時成立才 append：

1. current project governance已採用對應 exact continuity thread，且 current actor具有 comment write authority；
2. logical repository action已完成必要 canonical read-back；
3. fresh session continuation state materially改變。

通常一個 logical action closure最多一筆。不要為 HEAD probe、read/search、branch creation、中間 commit、CI polling或同一 action內的每個 validation step逐筆記錄。

### Public-safety boundary

Durable continuity thread位於公開 repository，因此 event只能含 sanitized technical coordination state。不得寫入：

- 真實人物或可識別 private subject；
- 出生日期／時間／地點組合；
- 感情、健康、性、工作或其他私人 reading內容；
- private conversation摘要；
- secrets、tokens、未公開公司／客戶／專案資訊；
- 長 diff、完整 log、整份 backlog或可由 canonical source重取的大段資料。

私人 reading continuity仍使用上方 transient checkpoint／合法私人儲存；不得因 repository continuity feature存在就改變其 egress boundary。

### Durable rehydration

Fresh maintenance session：

```text
resolve current repository/ref/HEAD
→ resolve exact method continuity Issue from PLAYBOOK_INDEX.json
→ bounded-read latest relevant checkpoint comment(s)
→ compare producer_observed_revision/work_identity with current authority
→ bounded reconcile material delta
→ read only referenced current backlog / owner / validation evidence
→ continue currently authorized action or STOP
```

- checkpoint revision是 provenance，不是 pin；
- HEAD一致時可 reuse仍適用的 verified context，不為形式全文重讀；
- HEAD不同時只做 bounded material-delta reconciliation；
- stale／out-of-order event不得覆蓋 current canonical state；
- event不建立 work admission、completion acceptance、repository source-write authority或新 method capability。

## Persistence boundary

Transient reading handoff預設是 conversation-level／private-storage scoped。Repository-maintenance durable checkpoint只有在 `REPOSITORY_ARCHITECTURE.md` 明確採用的 exact continuity thread內才允許持久化。

本檔只維護 handoff / checkpoint adapter結構，不保存任何使用者實際 handoff payload或 durable event history。

核心原則：**Transient handoff preserves private reading continuity；durable repository checkpoints preserve only sanitized current-working pointers；兩者都不取代 current canonical authority。**
