# Detector Agreement Implementation Clarification

Status: **REFERENCE-ONLY / PRE-EXECUTION CLARIFICATION / NO RTMPOSE MOHI RESULTS INSPECTED**

本 note 記錄在第一次 MOHI RTMPose inference 前發現的一個 geometry implementation discrepancy，並固定 detector-agreement runner 應採用的公式。

## Discrepancy discovered before execution

`NORMALIZATION_CONTRACT_DRAFT.md` 與 executable `normalization_probe.py` 對 canonical palm basis 的定義為：

```text
L0  = wrist
L5  = index MCP
L17 = little MCP
M   = midpoint(L5, L17)

ey = normalize(M - L0)
raw_ex = L5 - L17
ex = normalize(raw_ex - dot(raw_ex, ey) * ey)

palm_width  = dot(L5 - L17, ex)
palm_height = norm(M - L0)
```

並以：

```text
x = dot(P - L0, ex) / palm_width
y = dot(P - L0, ey) / palm_height
```

建立 canonical coordinates。

但既有 `mohi_mediapipe_repeatability.py` 的 historical implementation 在 `basis()` 中使用：

```text
W = norm(L5 - L17)
```

作為 width denominator，而不是 canonical contract 的 orthogonal projected width。

兩者只有在 `L5-L17` 與 `ey` 完全垂直時才相等，因此不得把這個差異視為純 formatting。

## Pre-execution decision

Detector-agreement study 尚未執行任何 MOHI RTMPose result，因此本 clarification 發生在 outcome inspection 之前。

本 study 的 authoritative geometry owner 仍是：

```text
NORMALIZATION_CONTRACT_DRAFT.md
normalization_probe.py
```

因此 `detector_agreement_runner.py` 對 MediaPipe 與 RTMPose **兩側都重新從 raw-image 21 landmarks 建立 canonical basis**，一致使用 orthogonal projected width：

```text
palm_width = dot(L5 - L17, ex)
```

不得直接重用 historical MOHI result JSON 內既有 `basis.w / basis.can` 欄位作 detector agreement canonical geometry。

MediaPipe historical result JSON 在本 study 中只提供已固定的 raw-image landmark evidence與 source/runtime provenance；canonical geometry 由 detector-agreement runner 依 canonical contract 重算。

## Historical MOHI evidence boundary

`MOHI_REPEATABILITY_RESULTS.md` 既有 pooled tables 是先前 bounded study 的 historical experiment output，不在此 clarification 中追溯改寫。

因此：

- 不重算、不覆寫既有 MOHI repeatability tables；
- 不宣稱 historical `width_rel` 與 canonical-contract projected-width metric 完全相同；
- detector-agreement study 使用 canonical owner 的 projected-width formula；
- future publication-grade cross-study comparison若需要直接比較 width metrics，必須先做明確的 metric harmonization，而不是把兩者當成同一欄位。

## Why this is not post-hoc tuning

這個差異是在：

```text
runtime artifact gate closed
→ runner implementation inspection
→ BEFORE first MOHI RTMPose inference
```

階段發現。

沒有 RTMPose MOHI output、agreement distribution、score relationship 或 per-person result 被用來決定公式。

因此這是 pre-execution implementation clarification，不是看到 outcome 後修改 metric。

## Frozen implementation consequence

第一次 detector-agreement execution 必須：

1. 對 MediaPipe raw landmarks 與 RTMPose raw landmarks各自建立同一 canonical basis；
2. `ex` 必須由 `L5-L17` 對 `ey` 正交化後得到；
3. `palm_width` 必須使用 `dot(L5-L17, ex)`；
4. `palm_height` 使用 `norm(M-L0)`；
5. raw normalized coordinate仍使用 `x/raw_width`, `y/raw_height`；
6. 不得因 detector agreement outcome 再切回 `norm(L5-L17)` 或加入 alternative basis。

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**.
