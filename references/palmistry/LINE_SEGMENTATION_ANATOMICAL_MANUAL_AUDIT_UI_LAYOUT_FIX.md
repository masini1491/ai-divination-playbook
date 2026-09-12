# Palm Line Segmentation — Anatomical Manual Audit UI Layout Fix

Status: **REFERENCE-ONLY / PRE-ANNOTATION UI FIX / NO MODEL COMPARISON**

Date: 2026-09-12

## Trigger

The first clarified annotator rendered the blind palm canvas *after* the class/status controls. On a normal desktop viewport the controls filled the visible page and the hand image was below the fold, which made it appear that the image was missing.

This was identified before any valid complete annotation file was frozen and before any model comparison was run.

## Correction

The annotator layout is changed without altering any audit metric, model input, class ID, annotation schema, tolerance, source selection, or blinding rule:

- blind palm canvas is moved into the primary visible workspace;
- on desktop, the palm image is shown in a left pane and annotation controls in a right pane;
- the image pane remains visible while the controls are used;
- on narrow screens, the layout stacks vertically;
- an explicit image-load error message is shown if a blind PNG cannot be loaded;
- the three Chinese class labels and completion gates remain unchanged.

## Evidence boundary

This is a usability correction made before valid manual annotations were completed. It does not inspect or expose model masks/overlays and does not modify the substantive audit protocol.

The previously incomplete annotation attempts remain invalid drafts and are not admitted as evidence.
