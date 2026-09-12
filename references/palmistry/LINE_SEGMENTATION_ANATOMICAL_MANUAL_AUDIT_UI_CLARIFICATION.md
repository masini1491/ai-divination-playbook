# Palm Line Segmentation — Anatomical Manual Audit UI Clarification

Status: **REFERENCE-ONLY / PRE-ANNOTATION IMPLEMENTATION CLARIFICATION / NO MODEL COMPARISON RUN**

## Why this clarification exists

The first blind annotation UI exposed the three tool-local class names through a compact `Class` selector (`heart_line`, `head_line`, `life_line`) while the adjacent buttons represented only observation status (`observable`, `uncertain`, `not_observable`).

During the first manual-use attempt, the observer reported that the button names did not make the relationship to the three target palm lines clear and that the anatomical target of each class was not sufficiently understandable from the interface alone.

A partial downloaded JSON therefore contained only `heart_line` statuses while `head_line` and `life_line` remained `unset`. That partial file was **not frozen as formal annotation evidence**, was **not used for `--compare`**, and must be treated as superseded / invalid for the formal audit.

No model prediction mask or overlay was opened as part of this failed attempt.

## Nature of the correction

This is an interface / operational-definition correction made **before any valid manual annotation freeze and before model comparison**. It does not alter:

- the frozen 10-image source set;
- corrected `C_G1_M0` image geometry;
- model weights or inference;
- class IDs;
- the 8 px comparison tolerance;
- comparison metrics;
- semantic-mismatch accounting;
- stop rules.

The updated UI makes the existing target definitions explicit and separates two concepts visually:

1. **which line is currently being annotated**;
2. **what the observer's status for that line is**.

## Updated class labels and operational descriptions

The UI now presents three explicit class buttons:

- `感情線（heart_line）`: the major transverse crease closest to the bases of the four fingers, typically running from the little-finger side toward the index/middle-finger side;
- `智慧線（head_line）`: a major transverse or oblique crease through the central palm, typically beginning near the thumb/index web and extending toward the little-finger side;
- `生命線（life_line）`: the curved major crease beginning near the thumb/index web and bending around the thumb base toward the wrist.

These descriptions are observational task definitions for this bounded audit, not palmistry interpretation claims.

## Updated status labels

For the currently selected class, status controls are displayed as:

- `看得到，可以畫（observable）`;
- `不確定是哪條／路徑不清楚（uncertain）`;
- `看不到／無法辨認（not_observable）`.

Only `observable` accepts reference polyline points. `uncertain` and `not_observable` remain valid non-rescued outcomes and are excluded from primary spatial comparison exactly as planned.

## Completion guards

The updated UI additionally shows:

- per-image completion `0/3 ... 3/3`;
- total completion `0/30 ... 30/30`;
- a guard preventing navigation to the next image when the current image is incomplete;
- a guard preventing formal JSON download until all 30 class-status assignments are complete and every `observable` trace has at least two points.

These guards do not change any analysis criterion; they only prevent an incomplete annotation file from being mistaken for a completed audit artifact.

## Restart rule

The formal blind manual audit must restart from a newly regenerated blind packet after this UI correction. Earlier partial annotation JSON files must not be reused or merged.

The model remains sealed until the newly completed annotation JSON is validated, hashed, and explicitly recorded as frozen evidence.
