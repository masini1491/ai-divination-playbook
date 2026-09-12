# Capture / Mirroring / Anatomical-side Contract Validator — Static Review

Status: **REFERENCE-ONLY / PRE-EXECUTION STATIC REVIEW / NO FORMAL RESULT YET**

## Reviewed artifact

```text
references/palmistry/capture_mirroring_contract_validator.py
Git blob = f504354ce4af352deadbe1286499d8390b76b18c
```

Companion predeclared plan：

```text
CAPTURE_MIRRORING_ANATOMICAL_SIDE_CONTRACT_PLAN.md
```

## Source-level review

### PASS — standard-library-only deterministic fixture

Validator不依賴 MediaPipe、OpenCV、NumPy、Pillow或 camera SDK。Synthetic asymmetric labeled points固定於 source，避免 real-image detector noise混入 transform-contract validation。

### PASS — EXIF orientation family represented explicitly

Source implements EXIF orientation codes `1..8` as normalized-coordinate transforms，並固定 inverse mapping：

```text
1 -> 1
2 -> 2
3 -> 3
4 -> 4
5 -> 5
6 -> 8
7 -> 7
8 -> 6
```

Reflection-bearing codes `2 / 5 / 7` 被單獨納入 predeclared Case I；contract不把所有 EXIF orientation簡化成 rotation-only。

### PASS — detector-only mirror round-trip is explicit

Model-only horizontal mirror使用：

```text
x -> 1 - x
```

Case D驗證 mirror + inverse；Cases E/F驗證缺 inverse或 mirror state unknown時，detector-derived raw/canonical geometry fail closed。

### PASS — detector score cannot rescue a frame-lineage blocker

Cases E/F即使傳入高 detector score，`capability_state()`也刻意不使用該 score改變 hard-blocker state。

### PASS — anatomical side has independent authority path

`explicit_side`只有 `left/right`時才建立 anatomical side；`detector_handedness`只保存 metadata / conflict。Cases J/K predeclare：

- conflict時 explicit side不得被 detector覆寫；
- detector handedness作為唯一 evidence時 side必須 unresolved。

### PASS — preview mirror does not mutate stored geometry

Case B比較 preview mirror false/true，只允許 preview metadata改變；stored/raw/canonical geometry與 explicit anatomical side不可變。

### PASS — side uncertainty does not overblock source-neutral geometry

Case L要求 frame transform完整但 side authority缺失時：

```text
raw_image_geometry       = admitted
canonical_hand_geometry  = admitted
anatomical_side           = unresolved
tradition_side_projection = unresolved
```

此 behavior與 capability-specific uncertainty closure一致。

### PASS — exactly-once EXIF behavior represented

Case G驗證 code 6 transform/inverse round-trip；Case H以同一 transform重複套用兩次，要求 asymmetric fixture與 exactly-once結果不同，並 fail closed frame reconciliation。

## Predeclared case accounting

Validator固定：

```text
A identity capture + explicit side
B preview mirror only
C known stored-file mirror
D model mirror + verified inverse
E model mirror without inverse
F unknown model mirror state
G EXIF 6 exactly once
H EXIF 6 applied twice
I reflection-bearing EXIF 2/5/7
J detector handedness conflicts with explicit side
K detector handedness only
L geometry admitted while side unresolved
```

Formal expected accounting：

```text
cases_total = 12
cases_fail = 0
all violation counters = 0
```

## Static-review caveats

### Stored-file mirror is lineage metadata, not automatic unmirror command

The validator deliberately does not assume a known mirrored stored image must always be physically unmirrored before source-neutral canonical geometry。Stored pixel frame與 physical-world camera frame是不同 concepts；independent anatomical-side authority remains separate。

### Explicit side is a synthetic authority placeholder

`explicit_side` represents a trusted/independent side evidence source in this bounded validator。Real UI/API design must later distinguish bodily self-report、trusted dataset annotation、screen-based guess等 provenance。

### No real camera behavior is validated

This code does not prove Android/iOS/vendor camera mirroring or EXIF correctness。

## What this review does NOT claim

No claim yet that exact source has passed：

```text
python -m py_compile
formal 12-case execution
formal result SHA freeze
```

No substantive result exists at static-review time。

## Next action

Allowed next action：

1. merge plan + exact validator + static review；
2. local `py_compile` exact blob；
3. formal 12-case execution；
4. inspect only accounting / violation counters；
5. hash result before substantive case interpretation；
6. record freeze；
7. then close or amend node based on actual output。

## Boundary

Static-review PASS is not empirical real-camera validation and does not create production anatomical-side authority。

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**。
