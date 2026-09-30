# Astrology Place Resolver Materialization｜占星地名解析按需載入契約

Status: **TASK-SPECIFIC CANONICAL CONTRACT**

本檔只在 explicit Astrology production 使用 `place`／`country` name input，且 installed admitted resolver／compatible verified resolver cache 無法直接完成解析時載入。它擁有 **place-resolution recovery / query-bounded shard materialization**；不擁有 astronomical provider selection、planet/house calculation、interpretation 或 research authority。

## 1. Activation / ordering

Place resolution 是 provider-independent input resolution，必須在 natal/transit provider selection 之前完成：

```text
named place / country input
→ admitted resolver available?
   ├─ yes → deterministic place resolution
   └─ no  → this contract
            → query-bounded exact-commit resolver transport
            → verified coordinates + IANA timezone
→ only then provider selection
   ├─ ChatGPT known-time + host swisseph PASS → swiss-host-natal-v1
   └─ otherwise → Astronomy Engine portable path
```

這條 recovery **不因 Swiss 已 PASS 而停用**。ChatGPT host 有 `swisseph` 但沒有 `geonamescache` 時，仍必須先完成本檔的 admitted location resolution；不得改用 generic web geocoding、GeoNames public search page、模型記憶或手填近似座標來冒充 resolver PASS。

Explicit `coordinates + timezone_name` input不需要本檔，直接走 core/provider path。

## 2. Canonical authority

Resolver admission：

```text
ASTROLOGY_PLACE_RESOLVER_ADMISSION_V1.json
tools/astrology_place_resolver.py
```

Query-bounded transport identity：

```text
dataset: astrology-place-geonamescache-v1
profile: 500
main manifest: data/astrology/place/v1/MANIFEST.json
data ref: refs/heads/data/astrology-place-v1
exact data commit: d18be87abe762433e43e844f33f4b43f7fad9f3b
aggregate digest: 6e542fd50c4d821d783c74c2f392bea087df68666ba1781970df66d47dc719a0
```

資料源是 admitted `geonamescache==3.0.2` / GeoNames-derived corpus；此 transport 只建立 location-resolution facts，不取得 astronomical authority。

## 3. Fast path

For a place/country request，先檢查 admitted resolver runtime／已驗證 query result or shard cache 是否仍符合 exact data-commit + profile identity；compatible 時直接 reuse。只有 resolver/runtime/cache真的 unavailable 或 identity不足時才進 query-bounded transport。

The original whole-package / model-mediated A-MAT-2 transport remains rejected. A separate query-bounded shard transport is production-admitted for the default profile `500` only。

Taiwan full administrative locality input must first apply the same method-owned policy used by `tools/astrology_place_resolver.py`：

```text
same-commit runtime/astrology/TW_ADMIN_LOCALITY_V1.json
→ bounded 台→臺 script normalization
→ exact county/city prefix match
→ exact county/city × township/district hierarchy validation
→ valid pair: query = validated township/district, effective country = TW
→ invalid/mismatched pair: fail closed
```

The policy file is input-normalization evidence only; it never supplies coordinates. After normalization, the admitted GeoNames alias/candidate transport remains the sole coordinate/timezone resolution path. Do not fetch the whole GeoNames corpus and do not use fuzzy contains search。

```text
normalize query = strip then casefold
→ SHA-256(normalized query), first 3 hex
→ GitHub Connect exact-data-commit alias shard
→ exact alias lookup
→ optional ISO alpha-2 country filter
→ if zero routes: fail closed NOT_FOUND
→ if multiple surviving routes: fail closed with first 10 deterministic candidates
→ for one selected geoname id, SHA-256(decimal geoname id), first 3 hex
→ GitHub Connect exact-data-commit candidate shard
→ exact geoname-id lookup
→ return admitted resolver fields
```

Path derivation follows the manifest：

```text
profiles/500/aliases/{first_hex}/{remaining_two_hex}.json
profiles/500/candidates/{first_hex}/{remaining_two_hex}.json
```

Every retrieval MUST use the exact admitted data commit, not the moving data branch. Missing path、malformed schema、profile mismatch、missing alias/id 或 identity mismatch全部 fail closed。GitHub Connect 不暴露 connector-internal cache/network-byte/latency telemetry；不得自行推測。

## 4. Output / provenance

成功解析只可輸出 admission manifest 允許的 resolver fields，例如：

```text
geoname_id
name
country_code
admin1_code
latitude
longitude
timezone_name
population
```

Production handoff 必須保留 resolver id/version、exact data commit/profile、query normalization/country filter 與 selected geoname identity。之後 provider 只消費已解析的 coordinates + IANA timezone；不得把 provider identity 反推成 location-resolution evidence。

## 5. Fail closed / profile boundary

Profiles `1000`、`5000`、`15000` 可由 installed `geonamescache` resolver 支援，但 **not admitted for shard materialization transport**。若使用者明確要求這些 profile 而 installed resolver unavailable，要求 explicit coordinates + IANA timezone 或回報 resolver-specific limitation；never silently substitute profile 500。

禁止：

```text
resolver MISS
→ generic web / public GeoNames search / map search
→ copy coordinates
→ claim production resolver PASS
```

也不得把 resolver dependency miss升格成整個 Astrology deterministic runtime unavailable。

## 6. Cross-provider regression case

此案例是正式 anti-regression boundary：

```text
execution surface: ChatGPT
request: exact/approximate known-time natal
location input: 苗栗縣頭份市
host swisseph probe: PASS
installed geonamescache: MISS

EXPECTED:
→ do NOT use generic web
→ apply Taiwan admin normalization
→ use exact admitted profile-500 alias/candidate shards
→ resolve coordinates + Asia/Taipei with resolver provenance
→ then select swiss-host-natal-v1
→ Astrology Fact Gate
```

Swiss capability PASS只回答 astronomical provider capability；不能跳過 location-resolution authority。

## 7. Authority boundary

```text
GitHub Connect → exact shard acquisition authority
ASTROLOGY_PLACE_RESOLVER_ADMISSION_V1.json → resolver/materialization admission truth
this contract → resolver recovery / query-bounded transport owner
ASTROLOGY_PROVIDER_ROUTING_V1.json → astronomical provider preference/fallback
ASTROLOGY_MATERIALIZATION.md → portable Astronomy core materialization only
ASTROLOGY.md → method / interpretation governance
```
