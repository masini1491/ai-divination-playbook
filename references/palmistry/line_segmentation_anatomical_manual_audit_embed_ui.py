#!/usr/bin/env python3
"""REFERENCE-ONLY transport helper for the blind palm-line manual audit UI.

Reads an already prepared blind packet, verifies every blind PNG against the
SHA256 recorded in annotation_template.json, and writes a self-contained
annotate_embedded.html with the same annotation payload and logic but with the
blind PNG bytes embedded as data: URIs.

This changes only UI image transport. It does not alter images, annotations,
model inference, class semantics, tolerance geometry, or comparison metrics.
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

    html = html_path.read_text(encoding="utf-8")
    needle = "img.src='reference_blind/'+rec().blind_image;"
    replacement = "img.src=embeddedBlindImages[rec().blind_image];"
    if html.count(needle) != 1:
        raise RuntimeError("expected exactly one blind image loader expression")

    marker = "<script>"
    if html.count(marker) != 1:
        raise RuntimeError("expected exactly one script marker")

    js_map = "const embeddedBlindImages=" + json.dumps(embedded, ensure_ascii=False) + ";\n"
    html = html.replace(marker, marker + "\n" + js_map, 1)
    html = html.replace(needle, replacement, 1)
    out_path.write_text(html, encoding="utf-8")

    print("EMBEDDED BLIND UI READY")
    print(f"images_verified = {len(embedded)}")
    print(f"output = {out_path}")
    print(f"output_sha256 = {sha256_file(out_path)}")


if __name__ == "__main__":
    main()
