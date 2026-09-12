#!/usr/bin/env python3
"""REFERENCE-ONLY blind manual anatomical audit for palm-line segmentation.

Two phases:
  1) --prepare-blind: emit only corrected baseline images + an annotation UI.
  2) --compare: after annotation SHA is frozen, rerun/verify model masks and compare.

Implements LINE_SEGMENTATION_ANATOMICAL_MANUAL_AUDIT_PLAN.md.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path
from typing import Any

import cv2
import numpy as np

import line_segmentation_repeatability_runner as base
import line_segmentation_adapter_diagnosis_runner as adapter
import line_segmentation_content_dependence_control_runner as content

ADAPTER_NAME = "C_G1_M0"
SPATIAL_RAW_SHA = "ba65456e3c7c3a645a4000c721961d0f600b46541ffc7e7566525b99a55f87e7"
PRIOR_CONTENT_SHA = "317e85351e4141206b28aec5277433ba3caed9a53e3eb01866cd38900699022f"
TOLERANCE_PX = 8.0
CLASSES = ("heart_line", "head_line", "life_line")
CLASS_TO_ID = {"heart_line": 1, "head_line": 2, "life_line": 3}
COLORS_BGR = {1: (60, 60, 230), 2: (40, 210, 240), 3: (60, 210, 80)}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def validate_spatial(path: Path) -> dict[str, Any]:
    got = sha256_file(path)
    if got != SPATIAL_RAW_SHA:
        raise RuntimeError(f"spatial raw SHA mismatch: {got}")
    d = json.loads(path.read_text(encoding="utf-8"))
    if d.get("execution") != {
        "selected_sources": 10,
        "conditions_per_source": 4,
        "completed_inferences": 40,
        "anchor_reproduction_failures": 0,
        "stop": False,
    }:
        raise RuntimeError(f"spatial execution drift: {d.get('execution')}")
    if d.get("prior_content_control_raw_sha256") != PRIOR_CONTENT_SHA:
        raise RuntimeError("prior content-control provenance drift")
    return d


def load_context(zip_path: Path, mp_path: Path):
    rows, sha_groups = base.validate_source(zip_path)
    mp = base.validate_mediapipe_results(mp_path, rows)
    return base.select_sources(rows, sha_groups), {r["file"]: r for r in mp["images"]}


def regenerate_baseline(zf: zipfile.ZipFile, src: dict[str, Any], mp_rec: dict[str, Any]):
    data = zf.read(src["file"])
    bgr = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_COLOR | cv2.IMREAD_IGNORE_ORIENTATION)
    if bgr is None:
        raise RuntimeError(f"decode failed: {src['file']}")
    h, w = bgr.shape[:2]
    if mp_rec.get("raw") != [h, w]:
        raise RuntimeError(f"raw frame mismatch: {src['file']}")
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    pts = base.mp_points(mp_rec)
    crop, meta = adapter.make_adapter(ADAPTER_NAME, rgb, pts)
    if meta.get("geometry") != "G1_reconstructed_upstream_like" or meta.get("horizontal_mirror") is not False:
        raise RuntimeError(f"adapter drift: {src['file']}")
    baseline = cv2.resize(crop, (512, 512), interpolation=cv2.INTER_LINEAR)
    return np.ascontiguousarray(baseline, dtype=np.uint8), meta


def blank_annotations(file: str, input_sha: str) -> dict[str, Any]:
    return {
        "file": file,
        "input_sha256": input_sha,
        "annotations": {
            c: {"status": "unset", "points_xy": []} for c in CLASSES
        },
    }


def make_html(template: dict[str, Any]) -> str:
    payload = json.dumps(template, ensure_ascii=False)
    return f'''<!doctype html>
<meta charset="utf-8">
<title>Palm-line blind manual audit</title>
<style>
body{{font-family:system-ui,sans-serif;background:#111;color:#eee;margin:18px}}
button,select,input{{margin:4px;padding:7px}} canvas{{border:1px solid #777;max-width:92vw;height:auto}}
.row{{margin:8px 0}} .warn{{color:#ffcc66}} pre{{white-space:pre-wrap}}
</style>
<h2>Blind palm-line manual audit</h2>
<p class="warn">Do not open model predictions before freezing this annotation JSON and recording its SHA256.</p>
<div class="row"><b id="name"></b> <span id="idx"></span></div>
<div class="row">
Class <select id="cls"><option>heart_line</option><option>head_line</option><option>life_line</option></select>
<button onclick="setStatus('observable')">observable</button>
<button onclick="setStatus('uncertain')">uncertain</button>
<button onclick="setStatus('not_observable')">not_observable</button>
<button onclick="undoPoint()">undo point</button>
<button onclick="clearClass()">clear class</button>
</div>
<div class="row"><button onclick="prevImg()">previous</button><button onclick="nextImg()">next</button><button onclick="downloadJSON()">download annotations.json</button></div>
<canvas id="cv" width="512" height="512"></canvas>
<pre id="state"></pre>
<script>
const data={payload}; let i=0; const cv=document.getElementById('cv'),ctx=cv.getContext('2d');
const img=new Image();
const colors={{heart_line:'#ff5a5a',head_line:'#ffd54a',life_line:'#5ad67d'}};
function rec(){{return data.images[i]}}
function ann(){{return rec().annotations[document.getElementById('cls').value]}}
function load(){{img.onload=draw; img.src='reference_blind/'+rec().blind_image; document.getElementById('name').textContent=rec().file; document.getElementById('idx').textContent=`${{i+1}}/${{data.images.length}}`;}}
function draw(){{ctx.clearRect(0,0,512,512);ctx.drawImage(img,0,0,512,512);for(const c of Object.keys(colors)){{const a=rec().annotations[c],p=a.points_xy;ctx.strokeStyle=colors[c];ctx.fillStyle=colors[c];ctx.lineWidth=2;if(p.length){{ctx.beginPath();ctx.moveTo(p[0][0],p[0][1]);for(let k=1;k<p.length;k++)ctx.lineTo(p[k][0],p[k][1]);ctx.stroke();for(const q of p){{ctx.beginPath();ctx.arc(q[0],q[1],2.5,0,Math.PI*2);ctx.fill();}}}}}}document.getElementById('state').textContent=JSON.stringify(rec().annotations,null,2);}}
cv.addEventListener('click',e=>{{const r=cv.getBoundingClientRect(),x=Math.round((e.clientX-r.left)*512/r.width),y=Math.round((e.clientY-r.top)*512/r.height);if(ann().status==='not_observable'||ann().status==='unset')return;ann().points_xy.push([Math.max(0,Math.min(511,x)),Math.max(0,Math.min(511,y))]);draw();}});
function setStatus(s){{ann().status=s;if(s==='not_observable')ann().points_xy=[];draw();}}
function undoPoint(){{ann().points_xy.pop();draw();}} function clearClass(){{ann().points_xy=[];ann().status='unset';draw();}}
function prevImg(){{i=Math.max(0,i-1);load();}} function nextImg(){{i=Math.min(data.images.length-1,i+1);load();}}
function downloadJSON(){{const blob=new Blob([JSON.stringify(data,null,2)],{{type:'application/json'}}),a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='annotations.json';a.click();URL.revokeObjectURL(a.href);}}
document.getElementById('cls').addEventListener('change',draw);load();
</script>'''


def prepare_blind(args, spatial: dict[str, Any]) -> None:
    selected, mp_by = load_context(args.zip, args.mediapipe_results)
    spatial_by = {r["file"]: r for r in spatial["images"]}
    root = args.packet_dir
    blind = root / "reference_blind"
    sealed = root / "model_sealed"
    blind.mkdir(parents=True, exist_ok=True)
    sealed.mkdir(parents=True, exist_ok=True)
    images = []
    with zipfile.ZipFile(args.zip) as zf:
        for idx, src in enumerate(selected, 1):
            baseline, _ = regenerate_baseline(zf, src, mp_by[src["file"]])
            prior = spatial_by[src["file"]]["conditions"]["baseline_512"]
            arr_sha = content.sha256_array(baseline)
            if arr_sha != prior["input_sha256"]:
                raise RuntimeError(f"baseline input anchor failed: {src['file']}")
            name = src["file"].replace("/", "_").replace(".jpg", ".png")
            out = blind / name
            if not cv2.imwrite(str(out), cv2.cvtColor(baseline, cv2.COLOR_RGB2BGR)):
                raise RuntimeError(f"write failed: {out}")
            row = blank_annotations(src["file"], arr_sha)
            row["blind_image"] = name
            row["blind_png_sha256"] = sha256_file(out)
            images.append(row)
            print(f"[{idx:02d}/10] prepared blind image {src['file']}")
    template = {
        "schema": "palm_line_manual_audit_v1",
        "observer_id": "observer_1",
        "spatial_raw_sha256": SPATIAL_RAW_SHA,
        "tolerance_px": TOLERANCE_PX,
        "images": images,
    }
    (root / "annotation_template.json").write_text(json.dumps(template, ensure_ascii=False, indent=2), encoding="utf-8")
    (root / "annotate.html").write_text(make_html(template), encoding="utf-8")
    (sealed / "README_LOCKED.txt").write_text(
        "Model overlays are intentionally not generated before annotation freeze.\n",
        encoding="utf-8",
    )
    print("\nBLIND PACKET READY")
    print(root)
    print(root / "annotate.html")


def raster_polyline(points: list[list[int]]) -> np.ndarray:
    m = np.zeros((512, 512), dtype=np.uint8)
    pts = np.asarray(points, dtype=np.int32)
    for a, b in zip(pts[:-1], pts[1:]):
        cv2.line(m, tuple(a), tuple(b), 1, 1, lineType=cv2.LINE_8)
    return m.astype(bool)


def dist_to(binary: np.ndarray) -> np.ndarray:
    inv = (~binary).astype(np.uint8)
    return cv2.distanceTransform(inv, cv2.DIST_L2, 5)


def compare_one(ref: np.ndarray, model: np.ndarray) -> dict[str, Any]:
    nr, nm = int(ref.sum()), int(model.sum())
    if nr == 0:
        raise RuntimeError("observable reference rasterized empty")
    if nm == 0:
        return {
            "model_present": False,
            "model_on_reference_coverage": 0.0,
            "reference_on_model_coverage": 0.0,
            "harmonic_coverage": 0.0,
            "median_model_to_reference_px": None,
            "median_reference_to_model_px": None,
            "reference_px": nr,
            "model_px": 0,
        }
    dref = dist_to(ref)
    dmod = dist_to(model)
    p = float(np.mean(dref[model] <= TOLERANCE_PX))
    r = float(np.mean(dmod[ref] <= TOLERANCE_PX))
    h = 0.0 if p + r == 0 else float(2 * p * r / (p + r))
    return {
        "model_present": True,
        "model_on_reference_coverage": p,
        "reference_on_model_coverage": r,
        "harmonic_coverage": h,
        "median_model_to_reference_px": float(np.median(dref[model])),
        "median_reference_to_model_px": float(np.median(dmod[ref])),
        "reference_px": nr,
        "model_px": nm,
    }


def validate_annotations(path: Path, expected_sha: str, spatial_by: dict[str, Any]) -> dict[str, Any]:
    got = sha256_file(path)
    if got != expected_sha.lower():
        raise RuntimeError(f"annotation SHA mismatch: {got}")
    d = json.loads(path.read_text(encoding="utf-8"))
    if d.get("schema") != "palm_line_manual_audit_v1" or d.get("spatial_raw_sha256") != SPATIAL_RAW_SHA:
        raise RuntimeError("annotation schema/provenance drift")
    if float(d.get("tolerance_px")) != TOLERANCE_PX or len(d.get("images", [])) != 10:
        raise RuntimeError("annotation contract drift")
    for row in d["images"]:
        f = row.get("file")
        if f not in spatial_by:
            raise RuntimeError(f"unexpected annotation file: {f}")
        expected_input = spatial_by[f]["conditions"]["baseline_512"]["input_sha256"]
        if row.get("input_sha256") != expected_input:
            raise RuntimeError(f"annotation input anchor drift: {f}")
        for c in CLASSES:
            a = row.get("annotations", {}).get(c, {})
            s, pts = a.get("status"), a.get("points_xy", [])
            if s not in {"observable", "uncertain", "not_observable"}:
                raise RuntimeError(f"unfinished/invalid status: {f} {c} {s}")
            if s == "observable" and len(pts) < 2:
                raise RuntimeError(f"observable trace needs >=2 points: {f} {c}")
            for p in pts:
                if len(p) != 2 or not all(isinstance(v, int) and 0 <= v <= 511 for v in p):
                    raise RuntimeError(f"invalid point: {f} {c} {p}")
    return d


def summarize(results: list[dict[str, Any]]) -> dict[str, Any]:
    out = {}
    for c in CLASSES:
        rows = [r["classes"][c] for r in results]
        status_counts = {s: sum(x["status"] == s for x in rows) for s in ("observable", "uncertain", "not_observable")}
        obs = [x for x in rows if x["status"] == "observable"]
        harm = [x["comparisons"][c]["harmonic_coverage"] for x in obs]
        m2r = [x["comparisons"][c]["median_model_to_reference_px"] for x in obs if x["comparisons"][c]["median_model_to_reference_px"] is not None]
        r2m = [x["comparisons"][c]["median_reference_to_model_px"] for x in obs if x["comparisons"][c]["median_reference_to_model_px"] is not None]
        wrong_wins = 0
        for x in obs:
            correct = x["comparisons"][c]["harmonic_coverage"]
            wrong = max(x["comparisons"][w]["harmonic_coverage"] for w in CLASSES if w != c)
            wrong_wins += wrong > correct
        out[c] = {
            "status_counts": status_counts,
            "observable_n": len(obs),
            "correct_class_harmonic_coverage": base.num_summary(harm),
            "correct_class_median_model_to_reference_px": base.num_summary(m2r),
            "correct_class_median_reference_to_model_px": base.num_summary(r2m),
            "wrong_class_exceeds_correct_count": wrong_wins,
        }
    return out


def overlay_image(rgb: np.ndarray, model_mask: np.ndarray, anns: dict[str, Any]) -> np.ndarray:
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    ov = bgr.copy()
    for cid in (1, 2, 3):
        m = model_mask == cid
        ov[m] = (0.55 * ov[m] + 0.45 * np.asarray(COLORS_BGR[cid])).astype(np.uint8)
    for c in CLASSES:
        a = anns[c]
        if a["status"] != "observable":
            continue
        pts = np.asarray(a["points_xy"], dtype=np.int32)
        cv2.polylines(ov, [pts], False, (255, 255, 255), 2, lineType=cv2.LINE_AA)
    return ov


def compare(args, sess, spatial: dict[str, Any]) -> None:
    selected, mp_by = load_context(args.zip, args.mediapipe_results)
    spatial_by = {r["file"]: r for r in spatial["images"]}
    anns = validate_annotations(args.annotations, args.annotations_sha256, spatial_by)
    ann_by = {r["file"]: r for r in anns["images"]}
    overlays = args.overlay_dir
    overlays.mkdir(parents=True, exist_ok=True)
    results = []
    with zipfile.ZipFile(args.zip) as zf:
        for idx, src in enumerate(selected, 1):
            baseline, _ = regenerate_baseline(zf, src, mp_by[src["file"]])
            prior = spatial_by[src["file"]]["conditions"]["baseline_512"]
            if content.sha256_array(baseline) != prior["input_sha256"]:
                raise RuntimeError(f"baseline input reproduction failed: {src['file']}")
            mask, _ = content.infer_512(sess, baseline)
            if content.sha256_array(mask) != prior["mask_sha256"]:
                raise RuntimeError(f"baseline mask reproduction failed: {src['file']}")
            ar = ann_by[src["file"]]
            class_rows = {}
            for c in CLASSES:
                a = ar["annotations"][c]
                cr = {"status": a["status"], "points_xy": a["points_xy"]}
                if a["status"] == "observable":
                    ref = raster_polyline(a["points_xy"])
                    cr["comparisons"] = {
                        mc: compare_one(ref, mask == CLASS_TO_ID[mc]) for mc in CLASSES
                    }
                else:
                    cr["comparisons"] = None
                class_rows[c] = cr
            ov = overlay_image(baseline, mask, ar["annotations"])
            name = src["file"].replace("/", "_").replace(".jpg", "_overlay.png")
            cv2.imwrite(str(overlays / name), ov)
            results.append({"file": src["file"], "classes": class_rows, "overlay": name})
            print(f"[{idx:02d}/10] compared {src['file']}")
    output = {
        "status": "REFERENCE-ONLY / SINGLE-OBSERVER BLIND MANUAL ANATOMICAL AUDIT",
        "spatial_raw_sha256": SPATIAL_RAW_SHA,
        "annotations_sha256": args.annotations_sha256.lower(),
        "tolerance_px": TOLERANCE_PX,
        "results": results,
        "summary": summarize(results),
        "execution": {"selected_sources": 10, "annotation_file_frozen": True, "stop": False},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\nDONE")
    print(json.dumps(output["execution"], indent=2))
    print(args.output)


def dry_run(sess) -> None:
    rgb = np.full((512, 512, 3), 120, dtype=np.uint8)
    cv2.line(rgb, (70, 180), (440, 210), (70, 70, 70), 3)
    mask, logs = content.infer_512(sess, rgb)
    ref = raster_polyline([[70, 180], [250, 195], [440, 210]])
    synthetic_model = np.zeros((512, 512), dtype=bool)
    cv2.line(synthetic_model.view(np.uint8), (72, 181), (438, 211), 1, 3)
    q = compare_one(ref, synthetic_model)
    print(json.dumps({
        "mode": "NON-MOHI ANATOMICAL MANUAL AUDIT DRY RUN",
        "model_mask_shape": list(mask.shape),
        "finite_logit_summary": bool(np.isfinite([logs["logit_min"], logs["logit_max"], logs["logit_mean"]]).all()),
        "reference_pixels": int(ref.sum()),
        "synthetic_comparison": q,
        "tolerance_px": TOLERANCE_PX,
        "schema": "PASS",
    }, indent=2))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", type=Path, required=True)
    ap.add_argument("--meta", type=Path, required=True)
    ap.add_argument("--zip", type=Path)
    ap.add_argument("--mediapipe-results", type=Path)
    ap.add_argument("--spatial-results", type=Path)
    ap.add_argument("--packet-dir", type=Path)
    ap.add_argument("--annotations", type=Path)
    ap.add_argument("--annotations-sha256")
    ap.add_argument("--output", type=Path)
    ap.add_argument("--overlay-dir", type=Path)
    ap.add_argument("--prepare-blind", action="store_true")
    ap.add_argument("--compare", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    base.validate_runtime()
    sess, _ = base.validate_model(args.model, args.meta)
    if args.dry_run:
        dry_run(sess)
        return
    if args.prepare_blind == args.compare:
        ap.error("choose exactly one of --prepare-blind or --compare")
    needed = (args.zip, args.mediapipe_results, args.spatial_results)
    if any(x is None for x in needed):
        ap.error("full mode requires --zip --mediapipe-results --spatial-results")
    spatial = validate_spatial(args.spatial_results)
    if args.prepare_blind:
        if args.packet_dir is None:
            ap.error("--prepare-blind requires --packet-dir")
        prepare_blind(args, spatial)
    else:
        if any(x is None for x in (args.annotations, args.annotations_sha256, args.output, args.overlay_dir)):
            ap.error("--compare requires --annotations --annotations-sha256 --output --overlay-dir")
        compare(args, sess, spatial)


if __name__ == "__main__":
    main()
