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

## 3. Acquisition / materialization flow

```text
fixed Raw Cast + original cast_timestamp
→ probe verified local Liuyao deterministic-tool cache if present
→ cache MISS / invalid
   → GitHub Connect resolve the same Playbook revision to exact commit
   → retrieve canonical Liuyao tool source from that exact commit
   → materialize byte-for-byte into one local directory
   → verify each reconstructed file against GitHub canonical blob identity
   → only after verification import / execute canonical tool
→ tools/liuyao_runtime.py composes calendar + structural facts
→ Structured Method Fact fixed
→ return to LIUYAO.md interpretation
```

若 host 有可觀察、byte-preserving 的 connector→Python full-file bridge，可直接傳完整 canonical file。

若沒有 automatic object bridge，但 GitHub Connect 可做 bounded exact line reads，允許 **model-mediated bounded source transport**，條件是：

- 來源固定在同一 resolved exact commit；
- 只搬運 canonical source text，不理解後重寫、不翻譯、不補 code；
- chunks 必須依原始行序完整重組，不得省略中段；
- 重組後以 Git blob identity 驗證 canonical bytes；必要時可再加 SHA-256／byte-count 驗證；
- hash / blob identity 未 PASS 前不得 import 或執行；
- mismatch 時只 fresh-read 同 commit 的失敗 chunk／range；不得改用 memory、舊聊天室、其他 ref 或模型重寫 source 補洞。

## 4. Verified local cache

允許 verified local cache reuse。Cache marker 至少應能綁定：

```text
source_repository
source_path(s)
exact_source_commit
canonical_file_hash_or_blob_identity
local_copy_identity
verified = true
```

不得因聊天重開就假設舊 cache 仍有效；也不得因 local cache 不存在就直接宣告 source 不存在。

若 local cache identity 與當次 required source identity 不一致，視為 cache MISS，走 §3 acquisition；不以 stale cache 冒充 current source。

## 5. Unavailable classification

只有以下情況才可把 deterministic layer 判定為 unavailable：

- GitHub Connect 無法取得所需 exact-commit canonical source；
- Python execution capability 不可用；
- host 無法建立任何 admitted byte-preserving handoff，而 bounded exact source transport 亦不可行；
- bounded retries 後仍無法通過完整 source reassembly / canonical blob-hash verification；
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
→ canonical repository source acquisition authority

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

> **Local deterministic-tool miss ≠ deterministic source unavailable。先完成可驗證 acquisition / handoff / execution capability gate，再決定 fail closed。**
