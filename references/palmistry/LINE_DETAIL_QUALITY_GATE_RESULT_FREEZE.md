# Principal-line Line-detail Quality Gate — Result Freeze

Status: **REFERENCE-ONLY / FORMAL EXECUTION ARTIFACT FROZEN / SUBSTANTIVE RESULT NOT YET INTERPRETED**

## Purpose

本文件只固定 `LINE_DETAIL_QUALITY_GATE_PLAN.md` 正式 primary execution 的 artifact identity 與 execution accounting。

在此 freeze record 建立前，不以本文件記錄或解讀 `summary_primary_by_condition` 的 substantive quality-study metrics；後續 interpretation 必須以本次 frozen JSON SHA256 為唯一正式結果 artifact。

## Repository / execution identity

正式 execution 前，user-side local repository 已更新並驗證於：

```text
bc57e9bf2184f2038b51513113f52e7fe152aee4
```

Executed runner：

```text
references/palmistry/line_detail_quality_gate_runner.py
```

Formal raw artifact：

```text
/home/user/palm-detector-study/results/MOHI_line_detail_quality_gate.json
```

## Frozen formal result artifact

SHA256：

```text
2ec6542d353a1ab8336476868be2cecf7e71f2e27cdb01e36f154b2ab065a4b7
```

此 hash 在正式 execution 完成、只讀 execution accounting 後計算。

後續任何 summary / per-source interpretation 都必須先確認 artifact bytes 仍與此 SHA256 一致。

## Execution accounting

Observed formal execution：

```text
primary_sources        = 9
sentinel_sources       = 0
conditions_per_source  = 10
primary_inferences     = 90
sentinel_inferences    = 0
stop                    = false
p001_sentinel_included = false
```

Completed primary files：

```text
P002/S1/01.jpg
P003/S1/01.jpg
P004/S1/01.jpg
P005/S1/01.jpg
P006/S1/01.jpg
P007/S1/01.jpg
P008/S1/01.jpg
P009/S1/01.jpg
P010/S1/01.jpg
```

因此 primary accounting reproduces the predeclared contract：

```text
9 sources × 10 conditions = 90 primary inference conditions
```

P001 未納入 primary execution，也未作 sentinel inference。

## Frozen provenance reproduced during execution

The formal result reported：

```text
comparison_tolerance_px = 8.0

frozen_annotation_sha256
= 51c4886e20cb9aee2d660fe1ca39f25b927398261478c013090ab5d611858041

frozen_anatomical_audit_result_sha256
= 6f95828b70b388028a46ee1879835d432d9dd695bdbbdd1f2656b6ebf3572284

frozen_spatial_sha256
= ba65456e3c7c3a645a4000c721961d0f600b46541ffc7e7566525b99a55f87e7
```

The runner also hard-checks baseline input / mask reproduction against the frozen spatial evidence before accepting each source baseline; successful completion with `stop=false` therefore indicates those execution guards did not stop the run.

## Pre-interpretation boundary

The supplied execution transcript exposed only：

- source completion lines；
- execution accounting；
- frozen provenance fields；
- formal result SHA256。

No `summary_primary_by_condition` values are recorded in this freeze document。

Therefore subsequent interpretation may inspect the frozen artifact only after verifying：

```text
SHA256 == 2ec6542d353a1ab8336476868be2cecf7e71f2e27cdb01e36f154b2ab065a4b7
```

Do not regenerate the formal result before interpretation unless a separately recorded protocol amendment requires it。

## What this freeze establishes

This record establishes：

- formal primary execution completed；
- 9-source primary set preserved；
- 10 conditions/source preserved；
- 90 primary inferences completed；
- P001 remained outside primary execution；
- execution stop flag remained false；
- annotation / anatomical-audit / spatial provenance identities matched the frozen contract；
- formal raw-result bytes are now pinned by SHA256。

It does **not** yet establish：

- whether blur, resolution destruction or contrast compression materially reduces manual-reference agreement；
- which class is most line-detail sensitive；
- whether any image-quality descriptor tracks observation quality sufficiently；
- a `sufficient / partial / insufficient` cutoff；
- a production admission threshold；
- Palmistry interpretation validity。

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**。
