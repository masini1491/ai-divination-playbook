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
- The GitHub Action `chatgpt-mcp-selective-sync.yml` triggers **only** for the
  source and policy allowlist, the release script, and relevant integration tests.
  It verifies contracts, generates the release, and commits only generated files
  using the built-in GitHub Actions token. No third-party API key is required.
- A Git-linked Vercel project with **Root Directory** `integrations/chatgpt-mcp`
  automatically deploys the generated release commit. The `ignoreCommand`
  skips non-release changes. An unrelated palmistry change does not update
  this directory or pass the workflow's path filter.

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
