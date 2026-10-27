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
