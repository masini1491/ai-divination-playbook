# AI Divination ChatGPT MCP (selective release)

This directory is the deployable FastAPI MCP service for **three explicitly
allowlisted divination methods only:** Tarot, Meihua, Liuyao. It is **not** the
whole `ai-divination-playbook` repository, and must not automatically admit
Palmistry, Astrology, Zi Wei or new methods simply because they appear on main.

## Authority and release flow

- Canonical sources: five source files in `runtime/casting/` and `tools/` plus
  eleven approved method-owner markdown documents in `release_profile.json`.
- Generator: `python tools/build_chatgpt_mcp_release.py` (repo root).
- Output: hash-pinned files inside this directory. `source_manifest.json`,
  `source_integrity.json`, `policy_pack.json` are generated, never hand-edited.
- The GitHub Action `chatgpt-mcp-selective-sync.yml` runs on the narrow
  source, policy, and integration allowlist. It validates the candidate and
  generates exact-commit runtime/policy files, but **never pushes main**.
  Instead it creates an isolated `automation/mcp-release-<source-sha>` branch
  and Draft PR with only generated files.
- PRs created using the built-in `GITHUB_TOKEN` do not automatically trigger
  `pull_request` Actions. The release job explicitly dispatches
  `validation.yml` for the candidate branch. This requires `actions: write`,
  `pull-requests: write`, and repository permission for Actions to create PRs.
  No third-party token is needed; inability to create or validate the PR
  is a **release blocker**, not authorization to push main.
- A Git-linked Vercel project with **Root Directory** `integrations/chatgpt-mcp`
  deploys Production when generated release paths or MCP service code change;
  unrelated files outside the MCP deployment allowlist are skipped by `ignoreCommand`. The generated-only Draft PR
  must receive the intended CI checks and be deliberately approved/merged
  before Production is eligible. Enforce Required Status Checks and PR reviews
  in GitHub before promoting this process to routine use. Vercel READY alone
  is not a functional MCP smoke-test result.
- Palmistry, Astrology and Zi Wei remain outside the allowlist.

## Repeated casts / multiple independent questions

- For two to **twelve** independent user-requested readings, call `batch_divination` with stable anonymized labels. Each item independently selects Tarot, Meihua or Liuyao (or server auto-routing), so interleaved order such as Tarot → Liuyao → Meihua → Tarot is supported. For more than 12, use successive batches without reusing old receipts. The server pre-validates all labels and completion rules before any random cast.
- Every successful label receives its own **compact original stochastic-choice receipt**, timestamp and SHA-256, with an invocation-unique `batch_id`, per-receipt `receipt_id`, index and source identity. The original random choices are kept; redundant derivable line metadata is intentionally omitted to reduce ChatGPT transport/context pressure. For Liuyao, all six 6/7/8/9 raw lines **and the original three-coin values for each line** are retained, along with the cast timestamp. Meihua keeps original A/B, Tarot keeps all actual cards. These are sufficient to reconstruct deterministic method facts later without random recasting.
- Policy text is NOT repeated with each item: after storing receipts, read the pinned method owner and `CHATGPT_OUTPUT.md` once per distinct method using `get_interpretation_policy`.
- Multiple batch calls can be interleaved with single `auto_divination` or deterministic `derive_meihua`/`derive_liuyao` calls. Tests additionally run the *actual bundled hash-verified engines* and the local MCP HTTP transport with a fixed, nonrandom test source, checking that 12 receipts remain independently reconstructible. Preserve the per-batch IDs and the receipt hashes across those calls. An unchanged label in a later batch is NOT the same reading.
- The interleaving regression sends **ten distinct MCP HTTP tools/call invocations** (four two-item batches, three compact independent auto casts, two deterministic derivations, one owner read). That gives **eleven new casts across all three methods** and rechecks each saved receipt after every later tool invocation; this complements the separate 12-casts-in-one-batch regression. These are fixed-test-source engine calls, not personal divinations.
- The service remains `storage=none`: if an original receipt is lost or truncated by the ChatGPT client, **it cannot be restored**. A partial failure returns all prior receipts; never rerun completed labels. Never claim a batch is complete unless all expected labeled receipts are present.
- This new tool does not make calls transactional across RNG failures: a failed current label may have consumed randomness. Do not automatically retry it without explicit user authorization.

## ChatGPT web plugin release acceptance

After a reviewed squash merge and **explicit authorization** for normal Production deployment, verify the existing connected **AI Divination Private – Git Sync** plugin from a fresh ChatGPT web conversation. Do not update or replace the legacy plugin. Do not mistake a READY Preview for a Production release.

1. Call `runtime_status` on **Git Sync**, not the legacy plugin. Expect `mcp_runtime_version=1.3.0-private-policy-parity`, `interpretation_policy_version=canonical-owner-parity-v1`, `verified=true`, and the pinned canonical `runtime_source_commit`. The old runtime can report the SAME `source_commit` and policy hash but has no interpretation version; these fields distinguish the code release.
2. Confirm that `get_interpretation_policy` is available in the ChatGPT web tool catalogue. If missing after Production is READY, refresh/reconnect **only this Git Sync plugin** through ChatGPT's plugin settings, then recheck. Do not assume the tool manifest refreshes instantly.
3. With a fixed existing cast and `existing_cast=true` plus a known `method_override`, confirm a no-draw result includes both the full method owner and full `CHATGPT_OUTPUT.md`, with source identity. Never generate new random cards solely for a smoke test.
4. For the three methods, read the full canonical owners via `get_interpretation_policy`, verify hashes and excluded methods, and separately carry out the paired model interpretation review. Report factual/policy availability separately from human-language interpretation equivalence.

The service only provides verified method facts and canonical interpretation source material. ChatGPT still synthesizes natural language; consistency depends on following the returned rules and the model's behavior.

## Interpretation policy parity (Tarot / Meihua / Liuyao)

- `auto_divination` default policy output contains the **complete pinned method owner** (`TAROT.md`, `MEIHUA.md` or `LIUYAO.md`) and **complete `CHATGPT_OUTPUT.md`**. Other shared policy excerpts remain bounded to reduce token cost; partial text is always labeled.
- The advertised `get_interpretation_policy(method, owner, offset, max_chars)` retrieves exact original text for shared allowlisted owners or that method's own owner (eleven approved files in total) in bounded contiguous chunks. Cross-method document requests are rejected; for legitimate two-method reconciliation, fetch each method's owner under its correct method and consult the shared `CROSS_VALIDATION.md`. Follow `next_offset` to exhaustion and verify stable `source_commit`, `owner` and `sha256` across chunks before claiming full coverage.
- Apply `QUESTION_DESIGN.md` and `INPUT_CONTRACT.md` when contract/position/horizon design materially matters; `READING_LIFECYCLE.md` for follow-ups/recasts; `READING_RECORD.md` for user-managed records; `CROSS_VALIDATION.md` for admitted cross-method reconciliation. Do not imply those owners were read solely because the MCP bundled them.
- Existing fixed Tarot cards / Meihua / Liuyao facts: call `auto_divination(existing_cast=true, method_override=<known method>)` to obtain full pinned method and output rules **without any new draw/cast**. Unknown methods preserve the no-redraw guard but cannot claim that a matching method rule was loaded.
- `include_policy_excerpts=false` is compact evidence mode, **not** permission to interpret without loading required canonical rules.
- Policy integrity is checked **before** invoking a new stochastic draw: a missing/tampered owner pack blocks casting instead of creating a partial reading. The loaded policy pack must contain **exactly the approved eleven owners**, match the engine source manifest's repository/commit, and retain valid SHA-256 **and Git blob SHA-1** for each owner.
- Transport smoke tests verify that complete method/output owners and exact SHA-pinned paginated rules reach the MCP caller, and that invalid owner requests or failed policy integrity do not yield a new cast.
- This service still produces method facts, not deterministic natural-language interpretations. Rule-access parity does not imply identical prose, validity of predictions, or reading-record persistence.

## Safety and guarantees

Canonical sources are read from an *exact Git commit* (not a moving HTTP URL)
with Git blob IDs, SHA-256 and sizes checked. The adapter fails closed on
hash/version violations. Selected policy-owner text is bundled verbatim and
short, explicitly marked excerpts accompany tool results; this is not a claim
that a single reading loads or enforces every section of the entire Playbook.
New methods require a reviewed change to profile, generator, server and tests.

Source-version equality means provenance and method rule sync, **not** identical
random draws, identical free-form LLM wording, or automatic Plugin UI refresh.

### Local check

```sh
python -m unittest discover -s tests/chatgpt_mcp -v
python tools/build_chatgpt_mcp_release.py
python tools/build_chatgpt_mcp_release.py --check
```

A Vercel deployment becoming READY is only a build result; actual `tools/list`
and `auto_divination` smoke tests are required before remapping an existing
user-facing plugin to the new service. The legacy MCP endpoint is not modified
by this repository change.
