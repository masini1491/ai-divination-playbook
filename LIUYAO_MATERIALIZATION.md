# Liuyao Deterministic Tool Materialization｜按需載入契約

Status: **TASK-SPECIFIC CANONICAL CONTRACT**

本檔只在 `LIUYAO.md` 已固定 Raw Cast、但 local deterministic tools cache 缺失／失效而本題仍需要 Structured Method Fact 時載入。普通六爻解讀若 verified deterministic tools 已可執行，不為形式讀本檔。

本檔不取得 stochastic cast、question routing、用神 selection 或 interpretation authority；這些仍由 `RUNTIME_DRAW.md`、`METHOD_ROUTING.md`、`LIUYAO.md` 等既有 owners 管理。

## 1. Canonical deterministic tool set

```text
tools/liuyao_calendar.py
tools/liuyao_engine.py
tools/liuyao_runtime.py
```

`liuyao_runtime.py` 會從同一目錄載入 `liuyao_calendar.py` 與 `liuyao_engine.py`。若執行 integrated runtime，三支檔案必須共同 materialize；若只有 engine 可被 byte-for-byte 驗證並執行，仍應先產生不依賴 calendar 的 structural facts，再讓 calendar-dependent layer獨立 fail closed。

Canonical source authority 永遠是上述三支 `.py`；`runtime/liuyao/CHATGPT_DETERMINISTIC_TOOL_BUNDLE.json` 只是由 canonical source 產生、由 CI 驗證同步的 **derived transport cache**，不成為第二份 calculation authority。

## 2. Local miss is not source unavailability

Raw Cast 已固定且本題需要 Structured Method Fact 時，**local filesystem / cache miss 本身不等於 engine unavailable**。

若 GitHub Connect exact-commit retrieval 與 Python execution capability 都可用，必須先嘗試 canonical deterministic tools 的 byte-preserving materialization，再決定是否進 `LIUYAO.md §9` fail closed。

不得把下列情況單獨當成 unavailable：

```text
/mnt/data 當下沒有 liuyao_*.py
沒有 automatic connector object bridge
Python sandbox 不能自己連 GitHub
上一輪只 materialize 了 Randomizer core.py
```

## 3. Preferred cold-start path｜single deterministic transport bundle

Verified local cache MISS／invalid 後，Free ChatGPT 類型的 connector→Python handoff **優先取得同一 resolved exact commit 的**：

```text
runtime/liuyao/CHATGPT_DETERMINISTIC_TOOL_BUNDLE.json
```

這個 bundle 把三支 canonical deterministic tools 的 exact bytes 依 manifest 順序串接、zlib 壓縮、base64 編碼，再切成 bounded ASCII chunks；每個 chunk、完整 archive 與解出的每支 source file 都有獨立驗證 identity。

最低流程：

```text
fixed Raw Cast + original cast_timestamp
→ probe verified local Liuyao deterministic-tool cache
→ cache MISS / invalid
   → GitHub Connect resolve current Playbook to exact commit
   → fetch same-commit CHATGPT_DETERMINISTIC_TOOL_BUNDLE.json
   → validate schema / authority / contract / source paths
   → transfer chunks in index order
   → verify each chunk encoded_length + SHA-256
   → concatenate only verified chunks
   → verify encoded_size
   → base64 decode → zlib decompress
   → verify archive decoded_size + SHA-256
   → slice files by manifest offset / byte_size
   → verify each file SHA-256 + Git blob identity
   → write all three verified files into one local directory
   → write + read back cache marker
   → import / execute tools/liuyao_runtime.py
→ Structured Method Fact fixed
→ return to LIUYAO.md interpretation
```

Chunk mismatch 時，不直接 fail closed：依 bundle 的 `chunk_retry_limit`，只 fresh-read **同一 exact commit bundle 的失敗 chunk**；已 PASS chunk 不重取、不改 ref、不以 memory／舊聊天室 payload 補洞。任何 archive 或 per-file identity 未 PASS 前不得 write-as-verified、import 或 execute。

Bundle manifest 的 `source_files` 順序同時定義 archive unpack order。解出的 file bytes 必須逐檔與 manifest 的 SHA-256 與 Git blob identity 相符；bundle 能成功解壓並不等於 file verification 已通過。

### 3A. Bundle unavailable / unusable fallback

若同 commit bundle 無法取得、格式無法驗證，或 host 無法完成 bundle payload handoff，但 GitHub Connect 仍可讀 canonical source，才退回 direct exact-source materialization：

```text
GitHub Connect exact commit
→ retrieve tools/liuyao_calendar.py / liuyao_engine.py / liuyao_runtime.py
→ byte-preserving full-file bridge
   OR bounded exact source ranges
→ complete reassembly
→ per-file canonical Git blob / SHA verification
→ write/import only after PASS
```

Direct-source fallback 同樣要求：

- 來源固定在同一 resolved exact commit；
- 只搬運 canonical source text，不理解後重寫、不翻譯、不補 code；
- chunks/ranges 依原始順序完整重組，不得省略中段；
- mismatch 只 fresh-read 同 commit 的失敗 range；不得改用 memory、舊聊天室、其他 ref 或模型重寫 source 補洞。

如果 integrated runtime materialization 不可行，但 `liuyao_engine.py` 已被 byte-for-byte 驗證且 Python 可執行，仍應先產生不依賴 calendar 的 structural facts；calendar-dependent layer 再獨立 fail closed。

## 4. Verified local cache

允許 verified local cache reuse。Bundle contract 預設 cache directory / marker 為：

```text
/mnt/data/divination-liuyao-runtime/
bundle_verification.json
```

Marker 至少應綁定：

```text
verified = true
repository
materialized_source_commit
last_checked_repository_head
bundle_contract
archive_sha256
files[]: path + sha256 + git_blob_sha + local_copy_identity
```

marker 寫入後應 fresh read-back 驗證必要欄位與 local copies；沒有可觀察的 marker/read-back evidence 不宣稱 persistent verified cache 已建立。

不得因聊天重開就假設舊 cache 仍有效；也不得因 local cache 不存在就直接宣告 source 不存在。

`materialized_source_commit` 表示目前三支 local tool bytes 的 provenance；`last_checked_repository_head` 只是最近一次 current repository observation。兩者可以不同，不得因 Playbook HEAD 前進就把 local executable provenance回填成新 HEAD。

### 4A. Identity-first deterministic refresh

只有存在合法 freshness trigger時才做 current repository identity probe：

```text
verified Liuyao deterministic cache
→ cheap current HEAD/ref probe
→ compare materialized_source_commit ... current HEAD
→ inspect only:
   tools/liuyao_calendar.py
   tools/liuyao_engine.py
   tools/liuyao_runtime.py
→ all unchanged
   → reuse verified local files
   → update last_checked_repository_head only
   → MUST NOT fetch deterministic bundle / rematerialize / rerun full acquisition
→ any changed / renamed / compare incomplete / source commit unavailable
   → exact current per-file identity verification
   → all bytes unchanged → reuse cache
   → any bytes changed / identity inconclusive → §3 acquisition
```

Repository其他檔案的 commit不構成 Liuyao deterministic-tool refresh trigger。只有 owned source paths的 material identity改變，或 identity無法可信證明一致時，才重新 acquisition / materialization。

local cache identity真正失配時才視為 MISS；current HEAD與 `materialized_source_commit` 不同本身不是 MISS。

## 5. Unavailable classification

只有以下情況才可把 deterministic layer 判定為 unavailable：

- GitHub Connect 無法取得所需 exact-commit bundle，且 canonical source fallback 亦無法取得；
- Python execution capability 不可用；
- host 無法建立任何 admitted byte-preserving handoff，而 bundle 與 bounded exact source transport 都不可行；
- bounded retries 後仍無法通過 bundle chunk/archive/per-file verification，且 direct-source fallback 也無法通過；
- canonical source 實際 import / execution 失敗，且失敗不是可用同一 source bounded recover 的暫時 materialization 錯誤。

當 structural layer 最終仍 unavailable：

```text
保留原 Raw Cast
保留原 cast_timestamp
記錄 acquisition / verification / execution gap
→ LIUYAO STRUCTURED FACT UNAVAILABLE
→ 回 LIUYAO.md §9
```

不得重抽、重卦、改用現在時間，亦不得由 language model 手算納甲、六親、世應後冒充 engine output。

## 6. Authority boundary

```text
GitHub Connect
→ canonical repository source / derived bundle acquisition authority

CHATGPT_DETERMINISTIC_TOOL_BUNDLE.json
→ CI-generated derived transport cache only

this contract
→ deterministic tool handoff / verification / cache boundary only

tools/liuyao_calendar.py
→ deterministic calendar facts only

tools/liuyao_engine.py
→ deterministic structural facts only

tools/liuyao_runtime.py
→ deterministic composition / presentation only

LIUYAO.md
→ judgment responsibility + yongshen responsibility + interpretation governance
```

核心原則：

> **Transport merge, not source merge。共享 stochastic `core.py` 保持純粹；六爻 deterministic source 保持分層，但 cold start 優先以一個可驗證 bundle 搬運。**

> **Local deterministic-tool miss ≠ deterministic source unavailable。先完成可驗證 acquisition / handoff / execution capability gate，再決定 fail closed。**
