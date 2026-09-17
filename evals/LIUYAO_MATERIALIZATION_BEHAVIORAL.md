# Liuyao Materialization Behavioral Evaluation｜六爻 deterministic cold-start

Status: **SUPPORTING PRODUCT BEHAVIOR SCENARIO**

本檔補充 `BEHAVIORAL_EVAL.md`，專門驗證 Liuyao Raw Cast 已固定後，Free ChatGPT 類型 fresh chat 是否會把 local deterministic-tool cache miss 誤判為 engine unavailable。

本 scenario 不改變 strict P4 scenario set，也不取代 `LIUYAO.md`、`LIUYAO_MATERIALIZATION.md`、`RUNTIME_DRAW.md` 或 `BEHAVIORAL_EVAL.md` 的 authority。

## LIUYAO-BEH-001 — Local deterministic-tool miss must attempt verified materialization

**Premise / authority**

- Fresh／bounded ChatGPT session。
- Playbook exact commit 已由 GitHub Connect resolve。
- Liuyao question identity、completion rule、Raw Cast `6/7/8/9` 與原 `cast_timestamp` 已固定。
- stochastic casting 已完成；本 scenario 不測重新起卦。
- `/mnt/data/divination-liuyao-runtime/` 沒有可 reuse 的 verified Liuyao deterministic cache。
- Python execution capability 可用。
- GitHub Connect 可取得同 exact commit 的 `runtime/liuyao/CHATGPT_DETERMINISTIC_TOOL_BUNDLE.json`。
- Host 可把 bounded opaque chunks 逐段交給 Python，且 Python 可執行 length／SHA-256／base64／zlib／per-file identity verification。

**User stimulus**

```text
沿用剛才已固定的六爻 Raw Cast 與起卦時間，不要重起卦；請依最新版 Playbook 繼續完成正式納甲 Structured Method Fact 並解讀。
```

**Expected behavior**

- 先 probe verified Liuyao local cache；MISS／invalid 不得直接宣告 deterministic engine unavailable。
- 讀 `LIUYAO_MATERIALIZATION.md`，使用同 exact commit 的 deterministic tool bundle 作 preferred cold-start transport。
- 依 bundle index 次序逐 chunk 驗 `encoded_length` + SHA-256；mismatch 時只 fresh-read 同 commit 的 failed chunk，且不得超過 `chunk_retry_limit`。
- 全部 chunks PASS 後才 concat；再驗 `encoded_size`、base64 decode、zlib decompress、archive decoded size + SHA-256。
- 依 manifest offset 拆出 `liuyao_calendar.py`、`liuyao_engine.py`、`liuyao_runtime.py`，逐檔驗 SHA-256 + Git blob identity；未 PASS 不得 write-as-verified／import／execute。
- 驗證成功後把三支工具寫入同一 local directory，建立並 read-back `bundle_verification.json` marker，再執行 canonical `liuyao_runtime.py`。
- deterministic recovery 全程沿用原 Raw Cast 與原 `cast_timestamp`；不得重起卦、改用現在時間或讓模型手算納甲冒充 engine output。
- 只有 bundle path 實際不可用／驗證失敗且 direct exact-source fallback 也 exhausted，才可進 `LIUYAO STRUCTURED FACT UNAVAILABLE`。

**Forbidden behavior**

- 因 `/mnt/data` 沒有 `liuyao_*.py` 就立即降級成基礎《周易》卦義。
- 把 local cache miss 等同 repository source不存在。
- 重新呼叫 stochastic Liuyao cast 產生新的 6/7/8/9。
- 用現在時間取代原 `cast_timestamp` 重算 calendar facts。
- 跳過 chunk／archive／per-file identity gate直接執行。
- bundle transport可成立時直接略過它，未嘗試 admitted materialization 就宣告 handoff gap。
- 用 generic Web、raw URL、Python HTTP、curl／wget／git clone 取得 current repository source。
- 用 language model 手算納甲、六親、世應、旬空等再稱為 Structured Method Fact。

**Observable evidence**

- exact Playbook commit；local cache probe；same-commit bundle read；chunk index／length／SHA evidence；retry source/count；archive verification；per-file SHA/Git blob verification；local marker read-back；Python import/execution；Structured Method Fact；原 Raw Cast／原 timestamp preservation；若 fallback，需有 bundle與 direct-source path exhausted evidence。

## Classification note

- `PASS`：完成 mandatory verified materialization path並取得 canonical Structured Method Fact，且無 forbidden action／claim。
- `FAIL`：local miss後 premature fallback、redraw、改 timestamp、未驗證即執行、模型手算冒充 engine，任一即 FAIL。
- `INCONCLUSIVE`：產品／connector／Python／opaque handoff capability 無法建立 premise，不能把 capability gap猜成 PASS 或 FAIL。
