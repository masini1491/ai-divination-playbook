#!/usr/bin/env python3
"""REFERENCE-ONLY transport helper for the blind palm-line manual audit UI.

Reads an already prepared blind packet, verifies every blind PNG against the
SHA256 recorded in annotation_template.json, and writes a self-contained
annotate_embedded.html.

The palm photograph is rendered by a real HTML <img> element, while the
annotation canvas is a transparent overlay. The first verified blind PNG is
written directly into the HTML img src so the first palm remains visible even
if later JavaScript navigation logic fails.

This changes only UI image transport/presentation. It does not alter images,
annotations, model inference, class semantics, tolerance geometry, or
comparison metrics.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def replace_exactly_once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f"expected exactly one {label}, found {n}")
    return text.replace(old, new, 1)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--packet-dir", type=Path, required=True)
    ap.add_argument("--output-name", default="annotate_embedded.html")
    args = ap.parse_args()

    root = args.packet_dir
    template_path = root / "annotation_template.json"
    html_path = root / "annotate.html"
    blind_dir = root / "reference_blind"
    out_path = root / args.output_name

    template = json.loads(template_path.read_text(encoding="utf-8"))
    if template.get("schema") != "palm_line_manual_audit_v1":
        raise RuntimeError("unexpected annotation template schema")
    images = template.get("images", [])
    if len(images) != 10:
        raise RuntimeError(f"expected 10 blind images, got {len(images)}")

    embedded: dict[str, str] = {}
    for row in images:
        name = row.get("blind_image")
        expected = row.get("blind_png_sha256")
        if not isinstance(name, str) or not isinstance(expected, str):
            raise RuntimeError("blind image metadata missing")
        path = blind_dir / name
        got = sha256_file(path)
        if got != expected:
            raise RuntimeError(f"blind PNG SHA mismatch: {name}: {got}")
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        embedded[name] = "data:image/png;base64," + encoded

    first_name = images[0]["blind_image"]
    first_src = embedded[first_name]

    html = html_path.read_text(encoding="utf-8")

    extra_css = """
#palm-stage{position:relative;width:min(512px,92vw);aspect-ratio:1/1;border:2px solid #888;background:#000;margin:14px 0;overflow:hidden}
#palm-photo,#cv{position:absolute;inset:0;width:100%;height:100%;margin:0;padding:0}
#palm-photo{z-index:1;display:block;object-fit:fill}
#cv{z-index:2;border:0;max-width:none;cursor:crosshair;background:transparent}
#image-load-status{font-weight:700;margin:6px 0 14px 0;color:#9fe8ff}
"""
    html = replace_exactly_once(html, "</style>", extra_css + "</style>", "style terminator")

    old_canvas = '<canvas id="cv" width="512" height="512"></canvas>'
    new_canvas = (
        '<div id="palm-stage">'
        f'<img id="palm-photo" width="512" height="512" alt="blind palm image" src="{first_src}">'
        '<canvas id="cv" width="512" height="512"></canvas>'
        '</div>'
        f'<div id="image-load-status">第一張照片已直接嵌入：{first_name}</div>'
    )
    html = replace_exactly_once(html, old_canvas, new_canvas, "canvas element")

    marker = "<script>"
    if html.count(marker) != 1:
        raise RuntimeError("expected exactly one script marker")
    js_map = "const embeddedBlindImages=" + json.dumps(embedded, ensure_ascii=False) + ";\n"
    html = html.replace(marker, marker + "\n" + js_map, 1)

    old_decl = "const cv=document.getElementById('cv'),ctx=cv.getContext('2d');\nconst img=new Image();"
    new_decl = (
        "const cv=document.getElementById('cv'),ctx=cv.getContext('2d');\n"
        "const palmPhoto=document.getElementById('palm-photo');\n"
        "const imageLoadStatus=document.getElementById('image-load-status');"
    )
    html = replace_exactly_once(html, old_decl, new_decl, "canvas/image declaration")

    old_load = """function load(){
  img.onload=draw;
  img.src='reference_blind/'+rec().blind_image;
  document.getElementById('name').textContent=rec().file;
  document.getElementById('idx').textContent=(i+1)+'/'+data.images.length;
}"""
    new_load = """function load(){
  const name=rec().blind_image;
  imageLoadStatus.textContent='照片載入中：'+name;
  palmPhoto.onload=()=>{imageLoadStatus.textContent='照片已載入：'+name;draw();};
  palmPhoto.onerror=()=>{imageLoadStatus.textContent='照片載入失敗：'+name;};
  palmPhoto.src=embeddedBlindImages[name];
  document.getElementById('name').textContent=rec().file;
  document.getElementById('idx').textContent=(i+1)+'/'+data.images.length;
}"""
    html = replace_exactly_once(html, old_load, new_load, "load() function")

    old_draw_start = "  ctx.clearRect(0,0,512,512);ctx.drawImage(img,0,0,512,512);"
    new_draw_start = "  ctx.clearRect(0,0,512,512);"
    html = replace_exactly_once(html, old_draw_start, new_draw_start, "draw() image-paint statement")

    out_path.write_text(html, encoding="utf-8")

    if html.count("data:image/png;base64,") != 11:
        raise RuntimeError("embedded image count check failed")
    if '<img id="palm-photo"' not in html:
        raise RuntimeError("palm-photo element missing")

    print("EMBEDDED IMAGE-ELEMENT BLIND UI READY")
    print(f"images_verified = {len(embedded)}")
    print(f"first_image = {first_name}")
    print("first_image_literal_src = PASS")
    print("transparent_annotation_overlay = PASS")
    print(f"output = {out_path}")
    print(f"output_sha256 = {sha256_file(out_path)}")


if __name__ == "__main__":
    main()
