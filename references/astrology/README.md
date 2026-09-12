# Astrology Research｜占星研究線

Status: **REFERENCE-ONLY / RESEARCH｜僅供參考／研究中**

Reviewed Playbook baseline: `masini1491/ai-divination-playbook@6bd58ea5bb61849c2464f4e485bc4f7917f64862`

本目錄建立 Astrology（星座／本命星盤／行運星象）的 Cold research surface。它只整理外部來源、計算／資料／解讀責任邊界與 evidence architecture，**不建立 production Astrology method capability，也不修改目前正式 method routing**。

## 1. Scope

本研究線目前關注：

```text
zodiac / placements
natal chart
transits / transit-to-natal
houses / angles / aspects
retrograde / motion state
structured chart facts
interpretation retrieval / synthesis boundary
```

「星座」在此不是獨立 stochastic method；它優先被視為 Astrology chart facts 的簡化投影，例如 Sun sign / Moon sign / Ascendant。完整本命盤與行運則需要更完整的時間、地點、計算設定與 provenance。

目前不納入 production：

- 不新增 `ASTROLOGY.md` canonical method owner；
- 不修改 `CHAT_INIT.md`；
- 不修改 `PLAYBOOK_INDEX.json`；
- 不修改 `METHOD_ROUTING.md`；
- 不建立 Astrology cross-validation semantics；
- 不宣稱 Astrology 已可由一般占問 router 自動選用；
- 不把外部 repo 的 interpretation corpus 或程式碼直接複製成 canonical rule。

## 2. Current research decomposition

研究先分四個責任層：

```text
birth / event input + provenance
→ astronomical / ephemeris fact
→ derived chart fact
→ tradition-specific projection
→ interpretation / synthesis
```

核心要求：

1. 天文位置、宮位、相位等可 deterministic 計算的內容，不由 language model 自由手算後冒充 engine fact。
2. tropical / sidereal、house system、ayanamsa、node type、orb policy 等設定必須成為 provenance，而不是隱藏預設。
3. 出生時間未知時，不把 houses / angles 或其他 time-sensitive facts 當作已知。
4. astronomical fact 與 astrological tradition claim 分層；「程式能算」不等於「解讀主張已被證實」。
5. interpretation 只能消費已建立的 facts 與明確來源，不得反向補造缺失 chart facts。

詳細分層見 [`EVIDENCE_ARCHITECTURE.md`](EVIDENCE_ARCHITECTURE.md)。

## 3. Initial source families

第一輪來源刻意涵蓋不同責任：

- ephemeris / astronomy engine；
- structured chart-data implementation；
- transit / timing search implementation；
- retrieval-first AI interpretation architecture；
- permissive-license alternative calculation path。

Exact reviewed revisions、license evidence、可借鑑範圍與 not-adopted boundary 見 [`SOURCE_REGISTRY.md`](SOURCE_REGISTRY.md)。

## 4. Promotion is explicitly out of scope

本輪只建立 evidence/source architecture。任何未來 production admission 至少還需要獨立驗證：

```text
source / license audit
→ deterministic calculation candidate
→ reproducibility / comparison evidence
→ birth-time / timezone / location uncertainty contract
→ chart configuration provenance contract
→ Structured Astrology Fact draft
→ interpretation-source / tradition boundary
→ behavioral regression
→ explicit admission decision
```

完成上述研究也**不自動**代表必須進 production router。

## 5. Parallel-work boundary

建立本目錄時，`references/palmistry/**` 有另一條平行研究線進行中。本研究 branch 只修改：

```text
references/astrology/**
```

Palmistry、root canonical owners、router 與 index 均不在本次 mutation scope。
