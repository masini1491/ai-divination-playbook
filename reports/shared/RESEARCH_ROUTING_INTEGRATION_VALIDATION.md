# Research Routing Integration Validation

Status: **REFERENCE-ONLY / RESEARCH INTEGRATION / NOT PRODUCTION-ROUTABLE**

Baseline main: `1f1d952a2c29b8dd7ead3c15c0935666e971852f`

## Purpose

驗證 root-level research discoverability integration 沒有把 Astrology / Palmistry 誤升級成 production methods，也沒有破壞既有 ordinary method routing。

本輪 integration surface：

```text
CHAT_INIT.md
→ RESEARCH_ROUTING.md（only for explicit research intent）
→ references/astrology/README.md | references/palmistry/README.md
```

Machine discovery：

```text
PLAYBOOK_INDEX.json
→ research.routing
→ research.astrology
→ research.palmistry
```

Production method selection 仍由 `METHOD_ROUTING.md` 單獨擁有。

## Case A — ordinary unspecified reading stays production-routed

Stimulus：

```text
我想占這件事接下來最可能怎麼發展。
```

Expected routing：

```text
CHAT_INIT.md
→ METHOD_ROUTING.md
→ production method selection
```

Astrology / Palmistry 不得因已存在 research dossier 或 index pointer 而成為候選。

Existing behavioral guard：`TAROT-BEH-002`。

## Case B — explicit Astrology intent stays research

Stimulus：

```text
用占星看我的本命盤／近期行運。
```

Expected routing：

```text
CHAT_INIT.md
→ RESEARCH_ROUTING.md
→ references/astrology/README.md
→ minimum relevant Astrology research contracts / evidence
```

Required boundary：

```text
REFERENCE-ONLY / RESEARCH / NOT PRODUCTION-ROUTABLE
```

禁止：

- 未經使用者要求先改成 Tarot / Meihua / Liuyao；
- 因 typed validators / regressions 存在就宣稱 Astrology production-ready；
- 把 astronomical fact、tradition projection、interpretation authority 混成一層。

## Case C — explicit Palmistry intent stays research and may fail closed

Stimulus：

```text
用手相／手掌照片幫我分析。
```

Expected routing：

```text
CHAT_INIT.md
→ RESEARCH_ROUTING.md
→ references/palmistry/README.md
→ minimum relevant observation / interpretation evidence
```

Current evidence boundary：

```text
formal S2 collection = pending
formal S3 collection = pending
formal B2 closure = open
```

因此若任務需要尚未取得的正式實拍 evidence，應停在該 evidence gap；不得自行改用 production method，也不得把 pilot / Cold evidence冒充 production threshold。

## Case D — mixed production + research remains two responsibility planes

Stimulus：

```text
用塔羅看這件事，另外再用占星研究角度補充。
```

Expected handling：

```text
production reading
→ production method owner

research analysis
→ RESEARCH_ROUTING.md → Astrology owner
```

Unless a future canonical reconciliation contract explicitly exists：

- 不稱為正式 cross-validation；
- research conclusion 不成為 production source fact；
- production reading 不替 research line 補造缺失 facts。

## Machine routing validation

`PLAYBOOK_INDEX.json` new pointers are routing-only：

```text
research.routing    → RESEARCH_ROUTING.md
research.astrology  → references/astrology/README.md
research.palmistry  → references/palmistry/README.md
```

`kind` is `research-router` / `reference`, not `method`.

Index pointer existence does not change production authority.

## Ownership boundary

This integration intentionally does **not** modify：

```text
METHOD_ROUTING.md
TAROT.md
MEIHUA.md
LIUYAO.md
RUNTIME_DRAW.md
CROSS_VALIDATION.md
Astrology core semantics
Palmistry observation experiments / thresholds
```

`RESEARCH_ROUTING.md` owns only explicit research-line discovery / boundary semantics.

## Validation boundary

Repository structural validation can prove owner/link/index/router consistency, but it does not itself prove semantic model behavior.

A green root workflow therefore means：

```text
structural integration passes repository checks
```

not：

```text
Astrology / Palmistry are production-ready
research claims are scientifically validated
all behavioral scenarios were executed by CI
```

Existing `TAROT-BEH-001` / `002` remain the behavioral reference for repo-only activation and ordinary unspecified routing.

## Conclusion

The integration is valid only if all of the following remain true：

```text
explicit research intent → research router
ordinary unspecified reading → production method router
research pointer ≠ production admission
Palmistry B2 real-photo gap remains open
Astrology remains REFERENCE-ONLY
```

**Current conclusion: root discoverability may be integrated without changing the production method set.**
