# MediaPipe Runtime Phase-0 — System Dependency Blocker

Status: **REFERENCE-ONLY / EXECUTION BLOCKER RECORDED / NO PORTABILITY RESULT**

## Purpose

本文件記錄 controlled reconstructed MediaPipe Phase-0 在 identity smoke test 前遇到的 operating-system shared-library blocker。

此 blocker不是 runtime compatibility failure，也不是 MOHI inference result。

## What completed before the blocker

Operator-provided local execution reached the following gates successfully：

```text
repo / probe / model source checks = PASS
Python 3.12.14 recreated in both isolated environments = PASS
pip 26.2.1 held fixed = PASS
common non-MediaPipe Python dependency versions held fixed = PASS
MediaPipe 1.0.1 wheel SHA256 =
121522251afc3c135e4b7b0c341dd5e050ad1ec87631127484f3c389ae385044

MediaPipe 1.0.0 wheel SHA256 =
07a449446bf888a8a2787dbf6fc1a33da4c47977313deec64d13c35bff41f6d2

locked wheel hashes = PASS
MediaPipe 1.0.1 installed in reconstructed baseline env = PASS
MediaPipe 1.0.0 installed in reconstructed comparison env = PASS
non-MediaPipe pip package list equality = PASS
```

The isolated environment prefixes were：

```text
/home/user/palm-detector-study/runtime-compat/recon-mp101
/home/user/palm-detector-study/runtime-compat/recon-mp100
```

## Blocker

The first reconstructed 1.0.1 smoke test failed while constructing `mp.Image` because the MediaPipe native library could not load：

```text
OSError: libGLESv2.so.2: cannot open shared object file: No such file or directory
```

The traceback occurred before a successful identity artifact was emitted。

Therefore at this point：

```text
recon-mp101 identity JSON = not frozen
recon-mp100 identity JSON = not frozen
synthetic smoke = not completed
MOHI inference = not executed
runtime compatibility result = none
```

## Interpretation

This is an **OS-level dependency prerequisite**, not evidence that MediaPipe `1.0.1` or `1.0.0` is incompatible with the pinned Hand Landmarker model。

A prior repository GitHub Actions research workflow explicitly installed：

```text
libegl1
libgl1
libgles2
```

before installing and executing MediaPipe `1.0.1` on Ubuntu。

That historical workflow execution succeeded, so restoring the same GL/EGL/GLES runtime-library family is a provenance-aligned prerequisite rather than a post-hoc detector tuning change。

## Allowed remediation

Before rerunning Phase 0：

1. install the missing OS runtime libraries only；
2. do not alter either reconstructed Python environment；
3. verify that both environments still have Python `3.12.14`；
4. verify MediaPipe remains exactly `1.0.1` vs `1.0.0`；
5. verify non-MediaPipe package lists still match；
6. rerun only the identity probes / synthetic smoke；
7. freeze artifact SHA256 before any MOHI execution。

Installing system GL/EGL/GLES libraries does not change the predeclared runtime-only comparison variable because the same OS library set is shared by both reconstructed environments。

## Stop conditions remain active

Stop again if：

- additional unrecorded Python dependency substitution is required；
- only one MediaPipe environment can load the same pinned model；
- Python patch versions drift；
- non-MediaPipe pip package lists diverge；
- raw synthetic pixel bytes differ；
- detector options must change；
- MOHI would need to run before both Phase-0 identity artifacts are frozen。

## Boundary

This note establishes only that the first controlled Phase-0 attempt reached the native-library loading boundary and identified a missing OS prerequisite。

It does **not** establish：

- `1.0.0` / `1.0.1` compatibility；
- landmark agreement；
- model compatibility across all MediaPipe versions；
- production upgrade policy；
- any Palmistry interpretation validity。

Palmistry remains **REFERENCE-ONLY / DRAFT / NOT PRODUCTION-ROUTABLE**。
