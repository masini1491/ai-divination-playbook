# ChatGPT Runtime Draw｜程式抽牌／起卦治理

本章是 ChatGPT／AI 在具有實際程式執行能力時，**自行執行目前已支援之 stochastic draw / cast** 的主要 authority。

Canonical implementation：

```text
masini1491/divination-casting-randomizer/randomizer.py
```

目前 canonical Randomizer 已實作：

```text
Tarot
Meihua
Liuyao three-coin raw cast
```

本章不維護 RNG implementation，也不負責六爻納甲排盤。六爻完整 method-specific contract 見 `LIUYAO.md`。

核心原則：

> **Language-model generation ≠ random draw / cast。**
>
> 模型能說出牌名、數字或 6/7/8/9，不代表已完成隨機抽牌／起卦；宣稱 Runtime Draw / Cast 必須有真正的 runtime execution result。

## Section Router｜依 Runtime 任務只讀最低必要段落

- **普通 ChatGPT 代抽／代起卦** → §1～6 + §11～12；依方法只讀實際需要的 method contract。
- **需要版本／timestamp／完整 provenance／audit** → 再讀 §7～10。
- **判斷同題能否重抽、補占或 copy-ready vs runtime** → §13～14 + 必要時 `READING_LIFECYCLE.md`。
- **維護或驗證 canonical Randomizer** → §3、§7～9、§15；實際 tests 屬 Randomizer repo responsibility。
- **正式保存 Runtime Draw / Cast** → §8～11 + `READING_RECORD.md`。

## 1. 何時可以使用 Runtime Draw / Cast

只有同時符合以下條件時，ChatGPT 才可宣告「自行抽牌／起卦」：

1. 使用者明確要求 ChatGPT 自己抽／起，或 Default Interaction Profile 已授權代抽／代起卦；
2. 本次 execution environment 具有可實際執行 Python 的能力；
3. 能取得並執行 canonical `divination-casting-randomizer`，或已有明確同步且可驗證的 runtime copy；
4. 題目、牌位／起卦契約已在結果出現前固定；
5. 執行結果可以保存為 `DRAW / CAST FACT`。

若只是模型「隨機想一組結果」，不得標記為 Runtime Draw / Cast。

## 2. Runtime Capability Gate

### 2.1 Deterministic Cache Slot｜先查固定位置，再決定是否抓 GitHub

普通 Runtime Draw / Cast 的第一個 source-related action 必須是 local cache probe。

優先 slot：

```text
/mnt/data/divination-casting-runtime/randomizer.py
/mnt/data/divination-casting-runtime/verification.json
```

若 `/mnt/data` 不可寫，唯一 fallback：

```text
<runtime-workspace>/.divination-casting-runtime/randomizer.py
<runtime-workspace>/.divination-casting-runtime/verification.json
```

不得靠 conversation memory 猜 path，不做 broad filesystem search，也不自行發明第三個 cache locator。

### 2.2 Mandatory Reuse Probe

在任何 GitHub source acquisition、raw download 或 materialize 前，依固定 slot 檢查：

- `randomizer.py` 存在且可 import／execute；
- `verification.json` 存在且可解析；
- marker `runtime_copy_sha256` 與檔案 hash 一致；
- `runtime_source_commit` 為 exact SHA，或明確標記 weaker provenance；
- `algorithm_version`、`schema_version` 與程式一致；
- 本次方法所需最低 invariant 通過。

目前最低 method-specific invariants：

```text
Tarot
→ 78 張且唯一

Meihua
→ A/B contract 與 8×8 hexagram mapping 可成立

Liuyao
→ method=liuyao 可執行
→ 6 lines
→ bottom-to-top
→ 每爻 value ∈ {6,7,8,9}
→ 6/9 changing, 7/8 static
→ three-coins raw fields 可解析
```

Probe PASS：

- 直接用 cached script fresh execution；
- 本次 draw / cast 禁止 GitHub fetch、raw download、重新 materialize；
- 不跑完整 smoke／full invariant suite；
- 每個新 question identity 都 fresh shuffle / fresh cast，絕不重用上一題結果。

只有以下 trigger 才能在 PASS 後重新確認 Randomizer source：

- 使用者明確要求 Randomizer 最新版／重新同步；
- 有 concrete evidence 顯示 Randomizer source 已更新；
- 使用者要求完整 provenance，而 marker 無法提供必要 source identity；
- local verification FAIL／無法完成。

**Playbook HEAD 更新本身不是 Randomizer freshness trigger。**

### 2.3 First Acquisition

Cache FAIL／absent／unavailable 時才做：

```text
Python capability
→ resolve Randomizer moving ref to exact commit
→ acquire exact revision randomizer.py
→ bounded smoke test
→ write fixed cache + verification marker
→ fresh draw / cast
```

Marker 最低包含：

```json
{
  "verified": true,
  "cache_locator_version": 2,
  "runtime_source_path": "masini1491/divination-casting-randomizer/randomizer.py",
  "runtime_source_ref": "main",
  "runtime_source_commit": "<exact immutable commit SHA or unknown>",
  "runtime_copy_sha256": "<sha256>",
  "algorithm_version": "<version>",
  "schema_version": "<version>",
  "supported_methods": ["tarot", "plum", "liuyao"],
  "tarot_deck_size": 78
}
```

Marker 只屬 temporary execution state，不是 canonical authority，也不是 Reading Record evidence。

核心原則：

> **Fresh question means fresh RNG, not fresh program acquisition。**

## 3. Canonical Runtime Source

Canonical implementation：

```text
masini1491/divination-casting-randomizer/randomizer.py
```

Playbook 不另維護一份抽牌／起卦程式。

### 3.1 Source Acquisition Layering

`repository retrieval capability`、`Python network capability`、`repository write authority` 是三件不同的事，不得互相推導。

只有 §2 允許 source acquisition 時：

1. connected GitHub tool／connector 優先 resolve `main` → exact commit SHA；
2. 優先取得 exact revision 的 `randomizer.py`，避免 mixed snapshot；
3. 寫入 fixed cache slot；
4. bounded smoke test；
5. marker 保存 ref + exact commit；
6. connector 不可用才考慮 public/raw/Web；
7. 取得到的 source 若截斷／不完整／無法確認 canonical target，視為 acquisition gap。

若 exact commit 無法確認但 source 可可靠取得，且本次不要求 immutable audit，可令：

```text
runtime_source_commit: unknown
```

不得拿 `main` 字串冒充 SHA。

## 4. Tarot Runtime Contract

Runtime Tarot：

- 完整 78 張；
- 單題 1～24 張；
- 同題不重複；
- 每個 question identity fresh full-deck shuffle；
- 每張正／逆位獨立；
- 多題／多人物彼此獨立 draw identity。

## 5. Meihua Runtime Contract

Runtime Meihua：

- A、B 各為 `000～999`；
- `A % 8` → 上卦；
- `B % 8` → 下卦；
- `(A+B) % 6` → 動爻；
- 八卦餘 0 → 坤；
- 動爻餘 0 → 第 6 爻。

A/B 與由 canonical algorithm 得出的本卦／上下卦／動爻形成該次 Cast Fact；不得看到結果後重新取數或改用別種起卦。

## 5A. Liuyao Runtime Contract｜三錢 Raw Cast

Runtime Liuyao 預設使用 Randomizer 的 canonical three-coin method：

```text
每爻 3 枚獨立公平二元抽樣
陰 = 2
陽 = 3

6 = 老陰，changing
7 = 少陽，static
8 = 少陰，static
9 = 老陽，changing

六爻：初爻 → 上爻（bottom-to-top）
```

Runtime output 中以下內容形成 **Raw Cast Fact**：

```text
cast_method
line_order
coin_mapping
每爻 coin_values / coin_faces
每爻 value 6/7/8/9
每爻 yin_yang
每爻 changing
```

重要 boundary：

> **Raw Cast Fact ≠ 完整六爻納甲盤。**

Randomizer 只擁有 stochastic casting authority。若需要本卦／之卦／納甲／六親／世應／六神／伏神／月日條件，依 `LIUYAO.md` 進入 Structured Method Fact Gate，由 deterministic engine 建立。

Raw Cast 成功、engine 失敗時，不重起卦；保留 raw 6/7/8/9，fail closed 在 structured layer。

## 6. Preferred Invocation

固定 cache slot可用時：

```text
# Tarot
python /mnt/data/divination-casting-runtime/randomizer.py tarot --count 6 --format json --source-commit <SHA>

# Meihua
python /mnt/data/divination-casting-runtime/randomizer.py plum --format json --source-commit <SHA>

# Liuyao three-coin raw cast
python /mnt/data/divination-casting-runtime/randomizer.py liuyao --method coins --format json --source-commit <SHA>

# Current legacy Tarot + Meihua command
python /mnt/data/divination-casting-runtime/randomizer.py both --count 6 --format json --source-commit <SHA>
```

若使用 workspace fallback，換成：

```text
<runtime-workspace>/.divination-casting-runtime/randomizer.py
```

AI integration 優先 JSON。

## 7. Version Semantics｜版本語意

`algorithm_version` 代表 stochastic draw / cast algorithm contract。改變實際抽樣分布、核心 shuffle/casting rule 或新增會改變 canonical stochastic method contract 的方法時才升版。

`schema_version` 代表 output metadata / shape。

目前 canonical Randomizer（Liuyao three-coin 已加入）：

```text
algorithm_version: 2
schema_version: 4
```

因此使用者可見可寫：

```text
Canonical Randomizer v2
```

## 8. Draw / Cast Timestamp

Runtime 每次執行保存：

```text
generated_at_utc
generated_at_taipei
timezone: Asia/Taipei
```

GitHub commit time 只代表 source provenance，不是 draw / cast time。

對 Liuyao，如果 downstream deterministic engine 使用月建、日辰、六神、旬空等時間相關欄位，應使用**同一次 Raw Cast 的實際 timestamp**作為時間基準，不得事後另挑時間。

## 9. Internal Provenance

共同最低欄位：

```text
casting_source / cards_source: chatgpt-runtime
runtime_tool: divination-casting-randomizer-python
runtime_algorithm_version
runtime_schema_version
runtime_source_ref
runtime_source_commit
generated_at_utc
generated_at_taipei
timezone
```

Meihua 另存：

```text
raw_input: A, B
```

Liuyao 另存：

```text
cast_method: three-coins
raw_lines: [6|7|8|9] × 6
line_order: bottom-to-top
```

六爻 deterministic engine provenance 與 Randomizer provenance 必須分開保存；見 `LIUYAO.md`。

## 10. 使用者可見標準格式

預設簡潔，不把全部 audit metadata 印出來。

Tarot：

```text
### Runtime Draw｜YYYY/MM/DD HH:MM
...
Canonical Randomizer v2。
```

Meihua：

```text
### Runtime Cast｜YYYY/MM/DD HH:MM
A / B / 本卦 / 動爻
Canonical Randomizer v2，採雙數 A/B 起卦。
```

Liuyao：

```text
### Runtime Cast｜YYYY/MM/DD HH:MM
初爻：7 少陽
二爻：8 少陰
...
上爻：9 老陽（動）

Canonical Randomizer v2，採三錢六爻，初爻至上爻。
```

若完整 Liuyao structured chart 已成功，再由 `LIUYAO.md` 決定要顯示哪些盤面欄位；不要把 engine metadata 混進 Randomizer result label。

## 11. DRAW / CAST FACT 與解讀分離

順序：

```text
Question Contract fixed
→ Runtime execution
→ Raw result captured
→ DRAW / CAST FACT fixed
→ Structured Method Fact（若方法需要）
→ Interpretation
```

不得邊解讀邊重抽／重起。

對 Liuyao：

```text
Raw Cast Fact
→ 永久保留該次 6/7/8/9
→ engine 只補 structured facts
→ engine 不得重新起卦
```

## 12. Fail-Closed Fallback

若 Runtime Draw / Cast 不可用、canonical script 無法取得、execution 失敗或 result 無法可信解析：

- 不得假裝執行；
- 不得由模型自行生成牌／數／六爻；
- 不得偷換未宣告 RNG；
- 改用 `divination-casting-randomizer` Web UI，或請使用者自行抽／起後提供結果。

若 Liuyao Raw Cast 已成功但 deterministic engine unavailable：

```text
保留 Raw Cast Fact
→ 不重起
→ 依 LIUYAO.md 標記 Structured Fact unavailable
```

不要因 engine 缺失就偷偷改成另一方法。

## 13. Runtime Availability 不改變補占紀律

Python 很快，不代表同題可以快速重抽。

同題／新題、承接、條件世界、補占／重占、多人物 identity 仍由 `READING_LIFECYCLE.md` 決定。

> **Execution availability does not create divination authority。**

## 14. Runtime Draw 與 Copy-ready

使用者要求「幫我出題，我自己抽／起」：

→ `CHATGPT_OUTPUT.md` copy-ready，不自動 Runtime。

使用者要求「你直接幫我抽／起」：

→ 本章 Runtime Gate。

若同時要求設計題目並代抽／代起：

```text
先固定題目／position／completion rule
→ 才執行 Runtime
```

## 15. 最低驗證

Canonical Randomizer 更新後至少驗證：

### Common

- JSON 可解析；
- UTC / Taipei timestamp 為同一瞬間；
- Taipei offset `+08:00`；
- algorithm / schema version 語意正確；
- fixed cache locator / marker / SHA reuse 正常；
- cache PASS 後不重抓 source；
- new question identity fresh RNG；
- cache FAIL 才 source acquisition。

### Tarot

- 78 張唯一；
- count boundary；
- 單題無重複；
- 多題獨立 shuffle；
- orientation 合法。

### Meihua

- A/B `000～999`；
- moving line 1～6；
- 64 卦 mapping 完整。

### Liuyao

- 恰好六爻；
- 初爻至上爻；
- 每爻 3 coin values；
- coin value ∈ {2,3}；
- line value ∈ {6,7,8,9}；
- 6/9 changing、7/8 static；
- 三錢理論分布維持：6=1/8、7=3/8、8=3/8、9=1/8；
- Runtime output 不偷偷產生納甲等 deterministic engine facts。

測試屬於 Randomizer repo implementation responsibility；本 Playbook 只要求 runtime provenance、authority boundary 與 fail-closed 行為成立。
