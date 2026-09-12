# Device / Capture First-upload Pilot — Results

Status: **REFERENCE-ONLY / TWO-DEVICE REPEATED-REPOSITION PILOT RESULTS / NOT FORMAL THREE-SESSION B2 CLOSURE / NO PRODUCTION AUTHORITY**

## Purpose

本文件記錄第一批 two-device / repeated-reposition 左手 pilot 在 raw-result freeze 之後的 substantive geometry inspection。

本結果只回答已在 `DEVICE_CAPTURE_REPEATABILITY_FIRST_UPLOAD_ADMISSION.md` admission 的 bounded pilot questions：

- 同一 physical device 內 repeated-reposition still captures 的 geometry spread；
- Google Pixel 5 與 Google Pixel 10 Pro 之間的 same-collection cross-device spread；
- ordinal `B1/B2/B3` 的 diagnostic-only 變化。

本文件**不**把 `B1/B2/B3` 升格成 `S1/S2/S3`，也不建立 formal three-session B2 closure。

## Evidence chain

```text
DEVICE_CAPTURE_REPEATABILITY_FIRST_UPLOAD_ADMISSION.md
→ DEVICE_CAPTURE_REPEATABILITY_FIRST_UPLOAD_SOURCE_FREEZE.md
→ DEVICE_CAPTURE_FIRST_UPLOAD_PILOT_IMPLEMENTATION_LOCK.md
→ DEVICE_CAPTURE_FIRST_UPLOAD_PILOT_RUNNER_STATIC_REVIEW.md
→ DEVICE_CAPTURE_FIRST_UPLOAD_PILOT_RESULT_FREEZE.md
→ 本 results document
```

## Frozen artifact identity

Substantive inspection只針對已 freeze 的 private/local artifact：

```text
B2_left_first_upload_pilot_raw.json
size_bytes = 210926
SHA256 = fda53f7f9cbee5ee1322fe7b13fe7128f3a953a6b17e999fc1aaf69d526387e3
```

Source / model provenance：

```text
source archive SHA256 = b5854b545f3ff0193b51cc02278efdbca25e1e3d1147a8559c7bb042ff2b7ca0
MediaPipe Tasks runtime = 1.0.1
Hand Landmarker model SHA256 = fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1
anatomical_side = left
side_authority = explicit_bodily_self_report
```

Device mapping：

```text
D1 = Google Pixel 5
D2 = Google Pixel 10 Pro
```

## Accounting result

Formal raw artifact reports：

```text
source_entries = 30
unique_source_sha256 = 30
duplicate_groups = 0
D1 = 15
D2 = 15
candidate_count 1 = 30 / 30
usable_entries = 30
unresolved_entries = 0
```

Pair accounting：

```text
within-device = 105 pairs/device = 210 total
cross-device = 15 × 15 = 225
all expected pairs resolved
```

Detector handedness metadata was `Left` for all 30 entries and pairwise label agreement was 1.0, but this remains metadata only and does not replace explicit anatomical-side authority。

## 1. Within-device repeated-reposition result

Lower values mean less pairwise spread for these difference metrics. Means are descriptive only; no production cutoff is inferred。

| Metric | D1 Pixel 5 mean | D2 Pixel 10 Pro mean | Lower mean |
| --- | ---: | ---: | --- |
| `raw_21_mean` | 0.069925 | 0.065878 | D2 |
| `raw_21_median` | 0.069877 | 0.063859 | D2 |
| `raw_21_max` | 0.133034 | 0.116885 | D2 |
| `anchor_mean` | 0.071787 | 0.061791 | D2 |
| `anchor_max` | 0.109447 | 0.082818 | D2 |
| `axis_angle_deg` | 8.459° | 4.446° | D2 |
| `width_rel` | 0.085002 | 0.072467 | D2 |
| `height_rel` | 0.083919 | 0.067744 | D2 |
| `canonical_mean` | 0.066262 | 0.076860 | D1 |
| `canonical_max` | 0.196397 | 0.225449 | D1 |

### Tail behavior

Selected p95 values：

| Metric | D1 p95 | D2 p95 |
| --- | ---: | ---: |
| `raw_21_mean` | 0.156542 | 0.109645 |
| `anchor_mean` | 0.142167 | 0.114598 |
| `axis_angle_deg` | 28.921° | 12.209° |
| `width_rel` | 0.217954 | 0.160561 |
| `height_rel` | 0.194101 | 0.163082 |
| `canonical_mean` | 0.118940 | 0.128126 |
| `canonical_max` | 0.350969 | 0.344203 |

### Bounded interpretation

在本 pilot 中，D2 Pixel 10 Pro 的 mean 在所有 **8 個 pre-canonical / raw-or-scale metrics** 都低於 D1；差異尤其明顯於：

```text
axis_angle_deg:  D1 8.459°  vs D2 4.446°
anchor_mean:     D1 0.071787 vs D2 0.061791
anchor_max:      D1 0.109447 vs D2 0.082818
height_rel:      D1 0.083919 vs D2 0.067744
```

相反地，經 canonical normalization 後，D1 Pixel 5 在兩個 canonical metrics 的 mean 較低：

```text
canonical_mean: D1 0.066262 vs D2 0.076860
canonical_max:  D1 0.196397 vs D2 0.225449
```

因此本 pilot 不支持「某一支手機在所有層級全面較穩」的敘述。

## 2. Pooled within-device vs cross-device

Pooled within-device 210 pairs 與 cross-device 225 pairs：

| Metric | Within-device mean | Cross-device mean | Descriptive change |
| --- | ---: | ---: | ---: |
| `raw_21_mean` | 0.067901 | 0.089385 | +31.6% |
| `anchor_mean` | 0.066789 | 0.087282 | +30.7% |
| `axis_angle_deg` | 6.453° | 6.344° | -1.7% |
| `width_rel` | 0.078734 | 0.074844 | -4.9% |
| `height_rel` | 0.075831 | 0.075144 | -0.9% |
| `canonical_mean` | 0.071561 | 0.076762 | +7.3% |
| `canonical_max` | 0.210923 | 0.221174 | +4.9% |

Cross-device raw / anchor location spread is therefore larger in this collection, while axis / width / height differences are not uniformly larger than pooled within-device spread。

Canonical-space cross-device means are only modestly above pooled within-device means in this pilot. This supports the bounded observation that the current canonical normalization **reduces the relative cross-device separation seen in raw / anchor location metrics**. It does not prove arbitrary-device invariance or portability。

### Cross-device distribution summary

Selected cross-device metrics：

| Metric | mean | median | p95 | max |
| --- | ---: | ---: | ---: | ---: |
| `raw_21_mean` | 0.089385 | 0.086293 | 0.151266 | 0.187965 |
| `anchor_mean` | 0.087282 | 0.087108 | 0.135205 | 0.176155 |
| `axis_angle_deg` | 6.344° | 4.484° | 24.002° | 33.922° |
| `width_rel` | 0.074844 | 0.063542 | 0.178000 | 0.295743 |
| `height_rel` | 0.075144 | 0.061015 | 0.180508 | 0.246445 |
| `canonical_mean` | 0.076762 | 0.074119 | 0.124804 | 0.163295 |
| `canonical_max` | 0.221174 | 0.210090 | 0.374558 | 0.473416 |

## 3. Ordinal B1 / B2 / B3 diagnostics

`B1/B2/B3` remain **ordinal diagnostic strata only, not sessions**。

Cross-device selected means：

| Metric | B1 | B2 | B3 |
| --- | ---: | ---: | ---: |
| `raw_21_mean` | 0.085477 | 0.092956 | 0.087287 |
| `anchor_mean` | 0.073230 | 0.094178 | 0.092116 |
| `axis_angle_deg` | 10.268° | 4.741° | 3.414° |
| `canonical_mean` | 0.073389 | 0.077051 | 0.073866 |
| `canonical_max` | 0.217080 | 0.205111 | 0.204289 |

The only clear ordinal pattern in these selected summaries is the lower cross-device axis-angle spread after B1：

```text
10.268° → 4.741° → 3.414°
```

However, `raw_21_mean`、`anchor_mean`、`canonical_mean` do not show a common monotonic improvement pattern. Therefore this pilot does **not** establish a general warm-up effect or temporal stabilization rule。

## 4. Are these effectively frozen-pose duplicates?

No。

The evidence does not support treating the 30 images as burst-like duplicates：

- 30 / 30 source byte hashes are unique；
- all 30 are usable single-candidate captures；
- within-device geometry spreads are materially non-zero；
- pooled within-device axis-angle has mean 6.453°、p95 24.518°、max 34.962°；
- user-provided collection semantics state the hand was lowered and re-raised / repositioned before each still。

The bounded description remains **repeated-reposition still-capture pilot**。

## 5. Device decision

### If one device must be chosen for acquisition / pose stability

**Choose D2 — Google Pixel 10 Pro for this pilot context.**

Reason：D2 has lower mean spread across every pre-canonical metric in the locked analysis, including raw landmark spread、anchor spread、axis angle、width and height relative variation. The strongest practical contrast is axis orientation：

```text
Pixel 5      mean axis-angle = 8.459°
Pixel 10 Pro mean axis-angle = 4.446°
```

Thus, if the operational criterion is **stable capture geometry before canonical normalization**, D2 is the bounded pilot preference。

### If the criterion is downstream canonical geometry only

**D1 — Google Pixel 5 is better on the two canonical mean metrics in this pilot.**

```text
canonical_mean: 0.066262 vs 0.076860
canonical_max:  0.196397 vs 0.225449
```

This means the capture-stage winner and canonical-stage winner differ. The result should not be collapsed into an unconditional statement that one camera is universally superior。

### Research use

For formal B2 device/capture characterization, retain **both devices**. Choosing D2 for convenience would answer a different single-device question and would not close the planned two-device node。

## 6. Scope and non-claims

This result is bounded by：

```text
one participant
one explicitly reported left hand
2 physical phone devices
15 captures/device
one short collection block/device
same general environment
MediaPipe Tasks 1.0.1
one pinned Hand Landmarker model
2D x/y geometry metrics
```

It does not establish：

- formal three-session B2 closure；
- arbitrary phone / camera portability；
- session-held-out device effect；
- production cutoff；
- z-coordinate portability；
- detector handedness anatomical authority；
- biometric identity or authentication performance；
- superiority of Pixel 5 or Pixel 10 Pro outside this bounded collection；
- production routing。

No threshold is selected from these observed distributions。

## Result disposition

**Pilot characterization: COMPLETE for the admitted first-upload scope.**

**Formal B2 device/capture repeatability node: OPEN.**

To close formal B2, the existing predeclared three-session design still requires true separated / reset sessions rather than relabeling ordinal blocks from this collection。

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**。
