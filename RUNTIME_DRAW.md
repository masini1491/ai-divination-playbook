# ChatGPT Runtime Draw｜程式抽牌／起卦治理

本章是 ChatGPT／AI 在具有實際程式執行能力時，**自行執行塔羅抽牌或梅花起卦**的主要 authority。

本章不實作 RNG，也不複製抽牌程式。Canonical implementation 由：

- `masini1491/tarot-plum-randomizer/randomizer.py`

維護。

核心原則：

> **Language-model generation ≠ random draw。**
>
> 模型能說出牌名，不代表已完成隨機抽牌；宣稱 Runtime Draw 必須有真正的 runtime execution result。

## Section Router｜依 Runtime 任務只讀最低必要段落

本檔可以按 section 漸進式讀取，不要求每次全文載入：

- **普通 ChatGPT 代抽／代起卦** → 第 1～6 節 + 第 11～12 節；依方法只讀 Tarot 或 Meihua contract。
- **需要版本／timestamp／完整 provenance／audit** → 再讀第 7～10 節。
- **判斷同題能否重抽、補占或 copy-ready vs runtime** → 第 13～14 節，並依需要讀 `READING_LIFECYCLE.md`。
- **維護或驗證 canonical Randomizer** → 第 3、7～9、15 節；實際測試仍屬 Randomizer repo responsibility。
- **正式保存 Runtime Draw** → 第 8～11 節 + `READING_RECORD.md`。

若目前 task 已能由 exact section 唯一處理，直接讀該 section；router 用於降低載入成本，不是額外 ceremony。

## 1. 何時可以使用 Runtime Draw

只有同時符合以下條件時，ChatGPT 才可宣告「自行抽牌／起卦」：

1. 使用者明確要求 ChatGPT 自己抽，或上下文已授權由 ChatGPT 代為抽牌／起卦。
2. 本次 execution environment 具有可實際執行 Python 的能力。
3. 能取得並執行 `tarot-plum-randomizer` 的 canonical Python implementation，或已有與該 implementation 明確同步且可驗證的本地副本。
4. 題目、牌位／起卦契約已在結果出現前固定。
5. 執行結果可以被保留為 `DRAW / CAST FACT`，而不是只留下模型重述。

若只是模型「隨機想一組牌」，不得標記為 Runtime Draw。

## 2. Runtime Capability Gate

ChatGPT 在第一次需要自行抽牌時，應做最低充分 capability check：

- Python 是否可執行；
- canonical `randomizer.py` 是否可取得／已載入；
- 必要標準庫是否可用；
- 程式能否完成一次 bounded smoke test。

不要為了能力盤點去掃描所有 runtime、compiler 或 sandbox 套件；只驗證本次真正需要的 Python capability。

若 execution environment 不可觀察或不可執行，不得因模型「通常能跑 Python」就假設本次可用。

## 3. Canonical Runtime Source

Runtime Draw 的 canonical implementation 是：

```text
masini1491/tarot-plum-randomizer/randomizer.py
```

Playbook 只保存治理規則，不另外維護一份 Python 抽牌程式，避免 Web、Python、Playbook 三份演算法 drift。

### 3.1 Source Acquisition Layering｜取得 canonical script 的優先序

`repository retrieval capability` 與 `Python runtime network capability` 是不同層級；Python sandbox 無法直接連 GitHub，不代表 ChatGPT 無法透過 repository-native connector 取得 canonical source。

當本次需要載入 `randomizer.py` 時，依最低充分順序：

1. 若目前環境已有可直接讀取 GitHub repository 的 **connected GitHub tool／connector**，優先用它取得指定 `main`／ref 的 canonical `randomizer.py` 與可得的 source commit evidence。
2. 取得 source 後，可將該檔案 materialize／寫入 ChatGPT 自己的 temporary／ephemeral runtime workspace，再由 Python 執行；temporary copy 只是 execution input，不會變成新的 canonical implementation。
3. 若 GitHub connector 不可用，再評估 GitHub public/raw/Web access；只有在必要時才要求 Python runtime 自己具備外網／DNS／HTTPS 能力。
4. 若已有本地副本，只有其來源與 canonical version 能被可靠確認時才可使用；未確認 freshness 的 cached copy 不得覆蓋較新的 canonical GitHub evidence。
5. Connector 能讀 repository ≠ Python runtime 能連網 ≠ repository write authority。這三種 capability 不得互相推導。
6. 若任何取得路徑只拿到不完整、截斷或無法確認為 canonical target 的 source，視為 acquisition gap，不能因「看起來像 randomizer」就執行並宣稱 canonical Runtime Draw。

推薦概念流程：

```text
GitHub connector / repository-native read
→ canonical randomizer.py + source evidence
→ temporary runtime copy
→ Python smoke test
→ Runtime Draw
```

若 ChatGPT 取得的是 repo 某個 commit 的檔案，應在內部 provenance 中保留該 commit SHA。GitHub 的 commit time 只代表**該程式版本提交時間**，不是抽牌時間。

若未能確認來源版本，可記 `runtime_source_commit: unknown`，但不得捏造 SHA。

## 4. Tarot Runtime Contract

Runtime Tarot 必須維持 Randomizer 的 canonical contract：

- 完整 78 張牌；
- 單題 1～24 張；
- 同一題不重複；
- 每個 question identity 都重新建立完整牌組並重新洗牌；
- 正／逆位固定啟用且每張獨立抽取；
- 多人物／多題平行抽牌時，每題是獨立 draw identity，不共用上一題剩餘牌組。

例如四個人物各抽 5 張，應形成四次獨立 shuffle，而不是一次洗牌後連抽 20 張分組。

## 5. Meihua Runtime Contract

若使用 Runtime Draw 起梅花，維持 canonical 雙數契約：

- A、B 各為 `000～999`；
- `A % 8` → 上卦；
- `B % 8` → 下卦；
- `(A+B) % 6` → 動爻；
- 八卦餘 0 → 坤；
- 動爻餘 0 → 第 6 爻。

Runtime result 中的 A／B、本卦、上下卦與動爻視為該次 canonical casting input。解讀端不得在看到卦象後重新取數、改用時間起卦或替換 A／B。

## 6. Preferred Invocation

有 Python runtime 時，建議直接執行 Randomizer CLI。

單題塔羅：

```text
python randomizer.py tarot --count 6 --format json --source-commit <SHA>
```

梅花：

```text
python randomizer.py plum --format json --source-commit <SHA>
```

塔羅＋梅花：

```text
python randomizer.py both --count 6 --format json --source-commit <SHA>
```

多題：

```text
python randomizer.py batch --counts 5,5,6,3 --format json --source-commit <SHA>
```

AI integration 優先使用 JSON，避免把人類排版重新解析成機械欄位。

## 7. Version Semantics｜版本語意

`algorithm_version` 只代表**抽牌／起卦演算法契約**。只有下列內容真的改變時才升版：

- 牌組或抽牌範圍；
- RNG／rejection sampling／shuffle 邏輯；
- 正逆位產生方式；
- 梅花 A/B 與取卦公式；
- 其他會改變實際抽取分布或結果契約的核心方法。

若只是新增 timestamp、commit provenance、JSON 欄位或其他輸出 metadata，不應升 `algorithm_version`；這類變化使用獨立的 `schema_version`。

目前 canonical Randomizer：

```text
algorithm_version: 1
schema_version: 2
```

因此使用者可見仍可寫：

```text
Canonical Randomizer v1
```

不需要因 provenance schema 更新而顯示 v2。

## 8. Draw Timestamp｜抽牌時間

Runtime Draw 應保存實際程式執行當下的 timestamp：

```text
generated_at_utc: <UTC ISO-8601>
generated_at_taipei: <Asia/Taipei ISO-8601, UTC+08:00>
timezone: Asia/Taipei
```

規則：

- `generated_at_utc` 由 runtime 在執行當下取得 UTC。
- `generated_at_taipei` 由同一 timestamp 轉成 `Asia/Taipei`。
- GitHub commit timestamp 只能當版本 provenance，不能替代 draw timestamp。
- 若 Runtime 無法可信取得時間，標示 unavailable，不要自行補一個看似合理的時間。

這些欄位主要用於內部／JSON provenance。使用者可見回覆不需要預設顯示 UTC、GitHub commit time 或 SHA。

## 9. Internal Provenance｜內部來源紀錄

Runtime Draw 至少在工具輸出或正式紀錄中保存：

```text
cards_source: chatgpt-runtime
runtime_tool: tarot-plum-randomizer-python
runtime_algorithm_version: <algorithm_version>
runtime_schema_version: <schema_version>
runtime_source_commit: <known commit SHA or unknown>
generated_at_utc: <tool output>
generated_at_taipei: <tool output>
timezone: Asia/Taipei
```

梅花則另外保存：

```text
casting_source: chatgpt-runtime
raw_input: A, B
```

`chatgpt-runtime` 表示「ChatGPT 實際執行 canonical runtime tool」，不是「ChatGPT 自己用語言生成結果」。

Provenance precision 必須如實保存：若只確認 source path、未確認 commit，就保留 `unknown`；若 runtime timestamp unavailable，就標 unavailable。單一 provenance 欄位已知，不代表其他欄位也已驗證。

## 10. 使用者可見的標準 Runtime Draw

預設保持簡潔，不把內部 audit metadata 全部印出來。

推薦格式：

```text
### Runtime Draw｜YYYY/MM/DD HH:MM

1. 牌位：**牌面**
2. 牌位：**牌面**
...

Canonical Randomizer v1，使用完整 78 張牌與獨立正逆位隨機。
```

其中：

- 標題時間取自 `generated_at_taipei`，顯示到分鐘即可；
- 不預設顯示 UTC；
- 不預設顯示 GitHub commit time；
- 不預設顯示 commit SHA；
- 若使用者要求完整稽核／provenance，再展開內部欄位。

若是梅花，可在結尾改成對應說明，例如：

```text
Canonical Randomizer v1，採雙數 A/B 起卦契約。
```

若塔羅＋梅花同時使用，可同時簡述兩套 canonical contract。

## 11. DRAW / CAST FACT 與解讀分離

Runtime tool 的原始結果先固定，再開始解讀。

順序：

```text
Question Contract fixed
→ Runtime execution
→ Raw result captured
→ DRAW / CAST FACT fixed
→ Interpretation
```

不得邊解牌邊要求程式重抽，也不得看到不喜歡的結果後重新執行同一題。

若使用者要求保存紀錄，應優先保留實際 tool output 或等價結構化資料，而不是只保存最後的自然語言解讀。

## 12. Fail-Closed Fallback

如果 Runtime Draw 在本次環境不可用、canonical script 無法取得、程式執行失敗或結果無法可信解析：

- 不得假裝已執行；
- 不得由語言模型自行產生牌名來冒充抽牌；
- 不得偷偷改用另一套未宣告 RNG；
- 應改用 Web `tarot-plum-randomizer`，或請使用者自行抽牌後提供結果。

若 runtime 部分成功，例如 Tarot 成功、梅花失敗，應分開標示，不能把整組宣稱為完整 Runtime Draw。

## 13. Runtime Draw 不改變補占紀律

能快速執行 Python，不代表可以快速重抽。

所有：

- 同題／新題判斷；
- 承接前占；
- 條件世界；
- 補占／重占；
- 多人物 question identity；

仍必須服從 `READING_LIFECYCLE.md`。

**Execution availability does not create divination authority。** 有能力執行，只代表技術上可以抽，不代表方法論上已允許重抽。

## 14. Runtime Draw 與 Copy-ready 的關係

若使用者要求「你幫我出題，我自己抽」，依 `CHATGPT_OUTPUT.md` 提供 copy-ready 題目，不自動執行 Runtime Draw。

若使用者要求「你直接幫我抽」，才進入本章 Runtime Gate。

若使用者同時要求：

> 幫我設計題目並直接抽牌

應先完成題目／牌位契約，再執行；不能先抽牌再倒推題目。

## 15. 最低驗證

Canonical runtime tool 更新後，建議至少驗證：

- 78 張牌唯一；
- 單題無重複牌；
- count boundary 正確；
- 多題各自形成獨立 draw；
- 梅花 A/B 與動爻範圍正確；
- 64 卦 mapping 完整；
- JSON 可被正常解析；
- `generated_at_utc` 與 `generated_at_taipei` 代表同一瞬間；
- 台灣時間 offset 為 `+08:00`；
- metadata-only 變更不會誤升 `algorithm_version`。

測試屬於 Randomizer repo 的 implementation responsibility；本 Playbook 只要求 Runtime Draw 不應依賴未驗證、來源不明的臨時抽牌片段。
