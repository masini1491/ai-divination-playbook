# Palm Line Anatomical Manual Audit — Simple UI Protocol Amendment

Status: **REFERENCE-ONLY / PRE-ANNOTATION UI AMENDMENT / NO MODEL COMPARISON INSPECTED**

## Reason

The prior annotation UI exposed separate class-selection and observation-status controls. In practice this made the operator interaction error-prone and, after the UI-clarity refactor, the status/drawing interaction became unreliable.

Before any usable manual annotation was frozen and before any model comparison was run, the UI contract is therefore simplified.

## Simplified operator interaction

The UI presents exactly three primary drawing buttons:

- 感情線 (`heart_line`)
- 智慧線 (`head_line`)
- 生命線 (`life_line`)

Clicking one of the three buttons selects which line is being drawn. Clicking on the palm image adds ordered polyline points for that class. `Undo` removes the last point for the selected class; `Clear` removes that class trace.

There is no separate `observable / uncertain / not_observable` control in this simplified UI.

## Frozen status derivation for this UI

At JSON export time, for each image/class:

- polyline with **2 or more points** → `status = observable`;
- fewer than 2 points → points are cleared and `status = not_observable`.

`uncertain` remains valid in the underlying schema and validator but is not emitted by this simplified single-observer UI.

This is a deliberate protocol simplification and must not be interpreted as evidence that ambiguous anatomy does not exist. It only means this bounded audit records either an independently drawable trace or no trace.

## Evidence boundary

This amendment changes only the manual annotation UI/interaction and the UI-side derivation of observation status. It does **not** change:

- the ten frozen MOHI sources;
- corrected `C_G1_M0` image geometry;
- blind PNG bytes or their SHA256 anchors;
- model weights or inference;
- shipped class IDs;
- the 8 px comparison tolerance;
- comparison metrics;
- model-output blinding before annotation freeze.

No completed valid annotation artifact and no model-comparison output had been inspected before this amendment. Earlier incomplete JSON files are invalid UI attempts and are not audit evidence.
