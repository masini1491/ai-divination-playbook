#!/usr/bin/env python3
"""REFERENCE-ONLY self-contained simple UI for blind palm-line manual audit.

Reads an already prepared blind packet, verifies each blind PNG against the
SHA256 recorded in annotation_template.json, embeds the PNG bytes directly in
one HTML file, and exposes only three drawing buttons: heart/head/life line.

UI export rule for this simplified operator flow:
- >=2 points for a class -> status=observable
- <2 points for a class -> status=not_observable and points cleared

The underlying annotation schema remains palm_line_manual_audit_v1. This helper
does not run or reveal model inference and does not change image bytes,
comparison tolerance, class IDs, or downstream metrics.
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
        embedded[name] = "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode("ascii")

    payload = json.dumps(template, ensure_ascii=False)
    image_map = json.dumps(embedded, ensure_ascii=False)
    first_name = images[0]["blind_image"]
    first_src = embedded[first_name]

    html = r'''<!doctype html>
<meta charset="utf-8">
<title>掌紋三大主線標註</title>
<style>
body{font-family:system-ui,sans-serif;background:#111;color:#eee;margin:18px;max-width:900px}
button{font-size:18px;padding:10px 18px;margin:5px;cursor:pointer}
.linebtn.active{outline:4px solid #fff;font-weight:700}
#heart{border:3px solid #ff5a5a} #head{border:3px solid #4da3ff} #life{border:3px solid #5ad67d}
#stage{position:relative;width:min(512px,92vw);aspect-ratio:1/1;margin:14px 0;border:2px solid #888;background:#000}
#photo,#cv{position:absolute;inset:0;width:100%;height:100%}
#photo{z-index:1;display:block} #cv{z-index:2;cursor:crosshair}
#current{font-size:20px;font-weight:700;margin:8px 0}.hint{color:#ddd;line-height:1.6}.nav{margin-top:10px}
</style>
<h2>掌紋三大主線標註</h2>
<div class="hint">先按一條線，再直接在手掌照片上沿著那條線點幾個點。<b>至少 2 點</b>才算有畫到。看不到的線就不要畫。</div>
<div>
<button class="linebtn" id="heart" onclick="selectLine('heart_line')">感情線</button>
<button class="linebtn" id="head" onclick="selectLine('head_line')">智慧線</button>
<button class="linebtn" id="life" onclick="selectLine('life_line')">生命線</button>
</div>
<div id="current"></div>
<div><button onclick="undoPoint()">復原上一點</button><button onclick="clearLine()">清除這條線</button></div>
<div id="fileinfo"></div>
<div id="stage"><img id="photo" src="__FIRST_SRC__" alt="blind palm"><canvas id="cv" width="512" height="512"></canvas></div>
<div class="nav"><button onclick="prevImg()">上一張</button><button onclick="nextImg()">下一張</button><button onclick="downloadJSON()">下載 annotations.json</button></div>
<script>
const data=__PAYLOAD__;
const imgs=__IMAGE_MAP__;
const classes=['heart_line','head_line','life_line'];
const labels={heart_line:'感情線',head_line:'智慧線',life_line:'生命線'};
const colors={heart_line:'#ff5a5a',head_line:'#4da3ff',life_line:'#5ad67d'};
let idx=0, current='heart_line';
const photo=document.getElementById('photo');
const cv=document.getElementById('cv');
const ctx=cv.getContext('2d');
function rec(){return data.images[idx]}
function ann(){return rec().annotations[current]}
function selectLine(c){current=c;draw()}
function draw(){
  ctx.clearRect(0,0,512,512);
  for(const c of classes){
    const p=rec().annotations[c].points_xy;
    if(!p.length) continue;
    ctx.strokeStyle=colors[c];ctx.fillStyle=colors[c];ctx.lineWidth=3;
    ctx.beginPath();ctx.moveTo(p[0][0],p[0][1]);
    for(let k=1;k<p.length;k++)ctx.lineTo(p[k][0],p[k][1]);ctx.stroke();
    for(const q of p){ctx.beginPath();ctx.arc(q[0],q[1],3,0,Math.PI*2);ctx.fill()}
  }
  document.getElementById('heart').classList.toggle('active',current==='heart_line');
  document.getElementById('head').classList.toggle('active',current==='head_line');
  document.getElementById('life').classList.toggle('active',current==='life_line');
  document.getElementById('current').textContent='目前畫：'+labels[current];
  document.getElementById('fileinfo').textContent=(idx+1)+'/10  '+rec().file;
}
function load(){photo.src=imgs[rec().blind_image];draw()}
cv.addEventListener('click',e=>{
  const r=cv.getBoundingClientRect();
  const x=Math.max(0,Math.min(511,Math.round((e.clientX-r.left)*512/r.width)));
  const y=Math.max(0,Math.min(511,Math.round((e.clientY-r.top)*512/r.height)));
  ann().points_xy.push([x,y]);
  ann().status=ann().points_xy.length>=2?'observable':'unset';
  draw();
});
function undoPoint(){ann().points_xy.pop();ann().status=ann().points_xy.length>=2?'observable':'unset';draw()}
function clearLine(){ann().points_xy=[];ann().status='unset';draw()}
function prevImg(){idx=Math.max(0,idx-1);load()}
function nextImg(){idx=Math.min(data.images.length-1,idx+1);load()}
function normalizeForExport(){
  for(const r of data.images){for(const c of classes){const a=r.annotations[c];
    if(a.points_xy.length>=2)a.status='observable';
    else{a.points_xy=[];a.status='not_observable'}
  }}
}
function downloadJSON(){
  normalizeForExport();
  const blob=new Blob([JSON.stringify(data,null,2)],{type:'application/json'});
  const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='annotations.json';a.click();URL.revokeObjectURL(a.href);
}
load();
</script>'''

    html = html.replace("__FIRST_SRC__", first_src)
    html = html.replace("__PAYLOAD__", payload)
    html = html.replace("__IMAGE_MAP__", image_map)
    out_path.write_text(html, encoding="utf-8")

    if html.count("data:image/png;base64,") != 11:
        raise RuntimeError("embedded image count check failed")
    print("SIMPLE EMBEDDED BLIND UI READY")
    print(f"images_verified = {len(embedded)}")
    print("buttons = 感情線 / 智慧線 / 生命線")
    print("export_rule = >=2 points observable; otherwise not_observable")
    print(f"output = {out_path}")
    print(f"output_sha256 = {sha256_file(out_path)}")


if __name__ == "__main__":
    main()
