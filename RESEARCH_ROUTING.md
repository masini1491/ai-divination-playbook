# Research Routing｜研究線導向

本檔只負責**明確 research intent 的 owner discovery、authority boundary 與最低載入路徑**。

它不是 production method router，也不把 `references/**` 內的研究線自動升級成正式占卜方法。

目前 production method selection 仍由 `METHOD_ROUTING.md` 負責。Astrology 已有 bounded production v1，但只有 explicit-request activation；普通未指定方法的 auto-routing 仍是：

```text
Tarot
Meihua
Liuyao
Tarot + Meihua（只有既有 canonical reconciliation contract 適用時）
```

## Research Line Registry｜研究線登錄

目前 root 可發現的 research lines：

### Astrology

Research owner：[`references/astrology/README.md`](references/astrology/README.md)

Production owner：[`ASTROLOGY.md`](ASTROLOGY.md)

Research intent examples：

```text
研究星座／本命星盤來源
維護 Astrology research dossier
比較不同 engine / house-system / tradition evidence
檢查 claim registry / source admission
Astrology chart fact architecture research
```

Research authority：

```text
REFERENCE-ONLY / RESEARCH EVIDENCE
```

Astrology research v1 已完成並保留歷史 evidence。它**不因 production v1 已 admission 就回頭改寫成 production source of truth**；production authority 由 `ASTROLOGY.md` + `ASTROLOGY_PRODUCTION_ADMISSION_V1.json` 另外擁有。

若使用者說：

```text
用占星幫我看
看我的本命盤
看這段行運
```

這是 production reading intent，**不要進本 research router**，直接交給 `ASTROLOGY.md`。

### Zi Wei Dou Shu / 紫微斗數

Owner：[`references/ziwei/README.md`](references/ziwei/README.md)

Intent examples：

```text
紫微斗數 calculation / source / tradition research
比較不同排盤 engine / 四化 / 閏月 / 子時 / 年界規則
維護 Zi Wei evidence / profile / validation architecture
研究一般使用者載入 ChatGPT 後的 default profile
```

Current authority：

```text
REFERENCE-ONLY / RESEARCH-ONLY / NOT PRODUCTION-ROUTABLE
```

目前已建立 deterministic calculation、source/tradition、profile divergence，以及 interpretation architecture / provenance-preserving composition / future admission 的研究架構。研究 default candidate 以「一般使用者載入 ChatGPT 後的主觀貼合／命中感」為產品目標之一，但 Tarot 覆核只屬 research decision evidence；**不等於科學驗證、客觀預測效度或唯一正統來源**。

不得因本 research line 已有 default candidate，就加入 `METHOD_ROUTING.md`、ordinary auto-selection、production cross-validation 或 production runtime。

### Palmistry

Owner：[`references/palmistry/README.md`](references/palmistry/README.md)

Intent examples：

```text
手相／掌紋 research
手掌照片 observation research
palm geometry / principal lines
Palmistry source / tradition research
```

Current authority：

```text
REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE
```

目前 observation / normalization / repeatability 研究已累積多個 bounded evidence nodes；formal device/capture repeatability 仍等待真正分離的實拍 collection，未完成 production admission。

## Explicit Research Intent Gate｜明確研究意圖

只有下列情形進本 router：

- 使用者明確要求 Astrology **research**、來源／架構／evidence／repo 維護；
- 使用者明確指定 Zi Wei Dou Shu／紫微斗數 research line；
- 使用者明確指定 Palmistry／手相 research line；
- 使用者要求維護、驗證、比較或繼續上述 research dossier；
- machine consumer 已由 `PLAYBOOK_INDEX.json` 命中 `research.*` capability。

Astrology production reading 不屬於這個 gate。

最低路徑：

```text
explicit research intent
→ RESEARCH_ROUTING.md
→ named research README / owner
→ only the minimum relevant research contracts / evidence
→ output with research authority preserved
```

不得因使用者明確指定 research task，又先把問題改寫成 production Tarot / Meihua / Liuyao / Astrology reading。

## Ordinary Reading Boundary｜普通占問邊界

使用者只說：

```text
幫我占……
這件事怎麼發展？
她怎麼想？
月底前會不會完成？
```

而沒有指定 Astrology 時，**不要**載入本檔來擴張候選方法。

應直接回到：

```text
CHAT_INIT.md
→ METHOD_ROUTING.md
→ production method owner
```

Astrology production v1 仍不因 repository 有 research dossier 就成為 ordinary auto-routing candidate。

若使用者明確指定 production Astrology：

```text
CHAT_INIT.md
→ ASTROLOGY.md
→ Astrology Fact Gate
```

Zi Wei Dou Shu 與 Palmistry 仍不得因有 research dossier而成為 ordinary auto-routing candidate。

## Research Routing ≠ Production Admission

下列推論一律禁止：

```text
research README exists
→ therefore production supported

PLAYBOOK_INDEX has research pointer
→ therefore METHOD_ROUTING may auto-select it

research validator/test passes
→ therefore scientific/predictive validity established

research result is detailed
→ therefore may silently create production rule
```

Astrology v1 的 production admission 是另外的 explicit decision，記錄於：

```text
ASTROLOGY.md
ASTROLOGY_PRODUCTION_ADMISSION_V1.json
```

它不改變這項原則，也不為其他 research line 建立捷徑。

Research pointer 只代表：

```text
this repository knows where the bounded research owner lives
```

不代表：

```text
production method authority
runtime authority
scientific validity
cross-validation authority
user-facing predictive certainty
```

## Explicit Research Request with Incomplete Capability

如果 research line 尚缺必要 fact / engine / image / permission / validation：

1. 保留 research identity；
2. 依該 research owner fail closed 在缺失層；
3. 可說明需要的最小 additional evidence；
4. 不因 research capability gap 就自行改成 production reading；
5. 若使用者另行要求 production method，才建立新的 distinct reading / task identity。

## Mixed Production + Research Request

同一 request 同時要求 production method 與 research line 時，預設保持兩個責任面：

```text
production reading
→ production method owner

research analysis
→ RESEARCH_ROUTING.md → research owner
```

例如 Astrology：

```text
production interpretation → ASTROLOGY.md
source / architecture audit → references/astrology/**
```

除非已有獨立 canonical reconciliation contract，否則不得把兩者稱為正式 cross-validation，也不得把 research conclusion 未經 admission 直接當成 production source fact。

## Promotion Boundary

任何尚未 production-admitted 的 research line 未來要進 production，仍必須依 repository governance 走完整 adoption sequence：

```text
judgment gap
→ method owner
→ deterministic / runtime authority
→ routing
→ provenance
→ behavioral regression
→ user-facing docs
→ explicit admission decision
```

Astrology v1 是這個 sequence 的一個 bounded implementation，不是繞過 sequence 的例外。

修改本檔或 `PLAYBOOK_INDEX.json` 的 research pointer **不能跳過上述 sequence**。

核心原則：

> **Research routing makes evidence discoverable without making it authoritative beyond its admitted layer. Production Astrology and Astrology research are distinct intents; ordinary unspecified readings stay on the ordinary production router.**
