---
name: ai-divination-playbook
description: Project gateway for activating the current ai-divination-playbook governance in Agent Skills-compatible hosts. Use when a task should be handled by this repository's Playbook. This adapter only hands off to repository bootstrap and canonical routing; it does not define methods or policy.
compatibility: Requires access to the ai-divination-playbook project repository. Repository canonical governance controls retrieval, runtime, evidence, storage, and fail-closed behavior.
metadata:
  playbook-adapter-role: agent-skills-discovery-activation-shim
  playbook-authority: none
  playbook-repository: masini1491/ai-divination-playbook
  playbook-bootstrap: AGENTS.md
  playbook-chat-init: CHAT_INIT.md
  playbook-index: PLAYBOOK_INDEX.json
  playbook-load-pack: CHATGPT_LOAD_PACK.json
---

# Gateway

This file is a non-authoritative Agent Skills interoperability shim. It exists only so a compatible host can discover and activate the repository Playbook. It must not become a second current-state policy source or a method router.

## Activation handoff

1. Locate the project repository root for `masini1491/ai-divination-playbook`.
2. Read the repository-root `AGENTS.md` and follow its current governance.
3. Continue through `CHAT_INIT.md` and use `PLAYBOOK_INDEX.json` / `CHATGPT_LOAD_PACK.json` only as the canonical bootstrap permits.
4. Before method-specific judgment, read the canonical owner selected by the existing Playbook routing.
5. If the host cannot satisfy a capability or authority gate required by the canonical governance, stop or fail closed at that canonical boundary rather than inventing an adapter fallback.

## Authority boundary

Do not treat this `SKILL.md` as authority for method selection, interpretation, stochastic runtime behavior, deterministic engines or providers, repository retrieval or freshness, bounded loading, reading lifecycle or records, privacy or storage, or behavioral regression. Those responsibilities remain with the existing canonical owners.

This gateway contains no scripts, bundled references, assets, method aliases, runtime implementation, provider implementation, or storage implementation. If this adapter conflicts with current repository governance, current canonical governance wins and the adapter must narrow or stop.