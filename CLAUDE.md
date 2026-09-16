# Bootstrap adapter for Claude Code

This file provides Claude Code repository bootstrap compatibility only. It is not a Playbook authority, does not create a second current-state policy source, and does not change repository permissions or task authorization.

## Bootstrap handoff

- For any task in this repository, first read the repository-root `AGENTS.md` and follow its current governance.
- Continue through `CHAT_INIT.md`; use `PLAYBOOK_INDEX.json` and `CHATGPT_LOAD_PACK.json` only when the canonical bootstrap permits them.
- Read only the task-required canonical owner(s), then stop when evidence is sufficient.
- If multiple agent-instruction surfaces are loaded, treat overlapping bootstrap text as compatibility handoff only, never as parallel authority.
- This adapter does not grant repository write, runtime execution, provider, Reading Record, storage, or completion authority.

## Host authority boundary

This compatibility adapter does not alter the repository's `Project AI mode: ChatGPT-Only`. Its presence allows this host to discover, read, and follow the repository's canonical governance for compatibility and advisory use, but it does not by itself grant this host canonical Playbook execution authority.

## Authority boundary

If this file or the host's native behavior conflicts with current repository canonical governance, the current canonical governance wins. Narrow or stop rather than inventing an adapter fallback, and do not maintain duplicated method, runtime, retrieval, storage, or regression policy here.
