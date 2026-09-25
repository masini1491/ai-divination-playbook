# Astrology Transit｜行運解讀契約

Status: **PRODUCTION V1 MODE OWNER**

本檔是 `ASTROLOGY.md` 下的 Transit mode policy owner；不取代 root method owner，也不擁有 deterministic event-search mechanics。

## 1. Entry / Baseline

```text
ASTROLOGY.md
→ reading_mode = transit
→ admitted natal baseline
→ admitted transit event facts
→ ASTROLOGY_TRANSIT.md
```

Transit calculation由 `tools/astrology_transit_provider.py` 執行；exact search span、root tolerance、scan steps、station/ingress algorithms、supported scopes與not-admitted boundary以 `ASTROLOGY_TRANSIT_PROVIDER_ADMISSION_V1.json` 為 machine truth。

若 request提供 admitted raw birth input但尚無 natal baseline，先由 production orchestrator / admitted natal provider建立 natal bundle並通過 natal runtime Fact Gate，再進 transit provider；不得從零用模型心算 transit-to-natal geometry。

## 2. Transit Interpretation Scope

只解讀 `ASTROLOGY_TRANSIT_PROVIDER_ADMISSION_V1.json` 與 production manifest當前 admitted 的 transit event facts；本 mode owner不重複保存 exact event-family enum。

能算出 admitted event不等於 pair-specific meaning已 admitted；semantic admission仍由 root source policy與 production manifest決定。

## 3. Exactness / Motion / Repetition

```text
natal baseline
→ deterministic transit event search
→ exactness / motion / repetition
→ admitted timing claim
→ conditional synthesis
```

Interpretation必須保留：

- canonical event time以provider fact為準；
- local civil time只能由 explicit IANA timezone衍生；
- repeated passage保留 `passage_index / passage_count`；
- retrograde造成多次 exact roots不得合併成一筆；
- exact geometry ≠ outcome certainty。

## 4. Timing Semantics

Timing window是 symbolic / methodological interpretation window，不是現實事件保證。

禁止把 transit直接寫成必然：

- death / pregnancy；
- medical diagnosis / outcome；
- accident；
- legal outcome；
- investment result；
- job loss；
- relationship ending。

高風險現實決策仍以專業與可觀察 evidence為主。

## 5. Transit Interpretation Order

```text
1. establish admitted natal baseline
2. fix bounded search window + targets
3. deterministic transit event search；house ingress uses admitted natal cusp facts and exact birth time only
4. runtime Fact Gate
5. preserve exact / motion / repeated-passage state
6. retrieve only admitted timing / semantic claims
7. conditional timing synthesis
8. separate symbolism from observable reality
```

不要為了「完整」把整段search window全部事件傾倒；只選與使用者原題直接相關的最低充分 events。

## 6. Transit Unsupported / Uncertainty

- unadmitted pair-specific meaning → `unsupported_factor`；
- transit-house **calculation** only admits exact-birth-time natal charts with all 12 admitted house cusps and bounded search windows; approximate/unknown birth time must fail closed；
- transit-house deterministic calculation includes both bounded cusp-crossing search and explicit point-in-time `house_context`; both require exact birth time and all 12 admitted natal cusps；
- point-in-time context must use explicit UTC `house_context_utc` inside the bounded request window; it is not inferred from an unrelated search endpoint；
- transit-house semantic interpretation remains unsupported unless a separate source-backed claim family is admitted；
- sidereal ingress、topocentric geometry等超出 admitted scope時不得模型補算；
- user-supplied transit facts若未獨立驗證，要保留 `user_asserted` provenance；
- deterministic event fact與 symbolic meaning必須分層表達。

共通 source / safety / recording / handoff rule回到 `ASTROLOGY.md`。
