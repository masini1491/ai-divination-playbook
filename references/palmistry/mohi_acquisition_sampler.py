from __future__ import annotations

from pathlib import Path
import hashlib
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request
import zipfile

ROOT = Path(r"C:\Users\user\Documents\X\MOHI")
DOWNLOAD_DIR = ROOT / "archives"
EXTRACT_DIR = ROOT / "extracted"
OUTPUT_ZIP = Path(r"C:\Users\user\Documents\X\MOHI_sample_10p_3s_5i.zip")

URLS = {
    1: "https://www.mutah.edu.jo/biometrix/MOHI/S1/MOHI-S1-P1-50.rar",
    2: "https://www.mutah.edu.jo/biometrix/MOHI/S2/MOHI-S2-P1-50.rar",
    3: "https://www.mutah.edu.jo/biometrix/MOHI/S3/MOHI-S3-P1-50.rar",
}

TARGET_PERSONS = 10
TARGET_IMAGES_PER_SESSION = 5
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}

NAME_RE = re.compile(
    r"^S(?P<session>[123])[-_ ]*P(?P<person>\d+)[-_ ]*"
    r"(?P<gender>[MFmf])[-_ ]*(?P<age>\d+)[-_ ]*"
    r"(?P<image>[1-5])(?:\.[^.]+)?$"
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def download_with_urllib(url: str, dst: Path) -> None:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "ai-divination-playbook-mohi-research/1.0"},
    )
    with urllib.request.urlopen(req, timeout=120) as r, dst.open("wb") as f:
        total = r.headers.get("Content-Length")
        total_n = int(total) if total and total.isdigit() else None
        done = 0
        while True:
            chunk = r.read(1024 * 1024)
            if not chunk:
                break
            f.write(chunk)
            done += len(chunk)
            if total_n:
                pct = done * 100.0 / total_n
                print(f"\r  {dst.name}: {pct:6.2f}% ({done/1024/1024:.1f} MiB)", end="")
            else:
                print(f"\r  {dst.name}: {done/1024/1024:.1f} MiB", end="")
    print()


def download_file(url: str, dst: Path) -> None:
    if dst.exists() and dst.stat().st_size > 0:
        print(f"[reuse] {dst}")
        return

    dst.parent.mkdir(parents=True, exist_ok=True)
    tmp = dst.with_suffix(dst.suffix + ".part")
    if tmp.exists():
        tmp.unlink()

    print(f"[download] {url}")
    last_error = None
    for attempt in range(1, 4):
        try:
            download_with_urllib(url, tmp)
            tmp.replace(dst)
            return
        except Exception as e:
            last_error = e
            print(f"  urllib attempt {attempt}/3 failed: {e}")
            if tmp.exists():
                tmp.unlink()
            time.sleep(attempt)

    print("  falling back to PowerShell Invoke-WebRequest ...")
    ps = [
        "powershell",
        "-NoProfile",
        "-ExecutionPolicy", "Bypass",
        "-Command",
        (
            "$ProgressPreference='SilentlyContinue'; "
            f"Invoke-WebRequest -UseBasicParsing -Uri '{url}' "
            f"-OutFile '{str(tmp)}'"
        ),
    ]
    try:
        subprocess.run(ps, check=True)
        if not tmp.exists() or tmp.stat().st_size == 0:
            raise RuntimeError("PowerShell produced no archive bytes")
        tmp.replace(dst)
        return
    except Exception as e:
        if tmp.exists():
            tmp.unlink()
        raise RuntimeError(
            f"Failed to download {url}\n"
            f"urllib last error: {last_error}\n"
            f"PowerShell fallback error: {e}"
        ) from e


def find_extractor():
    candidates = []
    for name in ("7z", "7z.exe", "WinRAR", "WinRAR.exe", "rar", "rar.exe"):
        p = shutil.which(name)
        if p:
            candidates.append(Path(p))

    candidates.extend([
        Path(r"C:\Program Files\7-Zip\7z.exe"),
        Path(r"C:\Program Files\WinRAR\WinRAR.exe"),
        Path(r"C:\Program Files (x86)\WinRAR\WinRAR.exe"),
    ])

    seen = set()
    for p in candidates:
        key = str(p).lower()
        if key in seen:
            continue
        seen.add(key)
        if p.exists():
            name = p.name.lower()
            if "7z" in name:
                return ("7z", p)
            if "winrar" in name or name in {"rar.exe", "rar"}:
                return ("rar", p)

    tar = shutil.which("tar")
    if tar:
        return ("tar", Path(tar))

    return None


def extract_rar(archive: Path, dest: Path, extractor) -> None:
    marker = dest / ".extracted_ok"
    if marker.exists():
        print(f"[reuse extracted] {dest}")
        return

    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True, exist_ok=True)

    kind, exe = extractor
    print(f"[extract] {archive.name} via {exe}")

    if kind == "7z":
        cmd = [str(exe), "x", "-y", f"-o{dest}", str(archive)]
    elif kind == "rar":
        cmd = [str(exe), "x", "-ibck", "-y", str(archive), str(dest) + os.sep]
    else:
        cmd = [str(exe), "-xf", str(archive), "-C", str(dest)]

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        if kind == "tar":
            raise RuntimeError(
                "Windows tar could not extract this RAR. Install 7-Zip or WinRAR and run again."
            ) from e
        raise

    marker.write_text("ok\n", encoding="utf-8")


def parse_mohi(path: Path):
    if path.suffix.lower() not in IMAGE_EXTS:
        return None
    m = NAME_RE.match(path.stem)
    if not m:
        return None
    return {
        "session": int(m.group("session")),
        "person": int(m.group("person")),
        "image": int(m.group("image")),
        "path": path,
    }


def collect_records():
    records = []
    unmatched = []
    for p in EXTRACT_DIR.rglob("*"):
        if not p.is_file() or p.name == ".extracted_ok":
            continue
        if p.suffix.lower() not in IMAGE_EXTS:
            continue
        rec = parse_mohi(p)
        if rec:
            records.append(rec)
        else:
            unmatched.append(p)
    return records, unmatched


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    EXTRACT_DIR.mkdir(parents=True, exist_ok=True)

    print("MOHI official Group-1 acquisition + deterministic sampler")
    print("Scope: P1-P50, S1/S2/S3; select first 10 common complete person IDs")
    print()

    archives = {}
    for session, url in URLS.items():
        dst = DOWNLOAD_DIR / Path(url).name
        download_file(url, dst)
        archives[session] = dst
        print(f"  SHA256 {dst.name}: {sha256_file(dst)}")

    extractor = find_extractor()
    if extractor is None:
        raise RuntimeError(
            "No RAR extractor found. Install 7-Zip or WinRAR, then run again. Downloaded archives are preserved."
        )

    for session, archive in archives.items():
        extract_rar(archive, EXTRACT_DIR / f"S{session}", extractor)

    records, unmatched = collect_records()
    print()
    print(f"recognized MOHI images: {len(records)}")
    print(f"unmatched image files:   {len(unmatched)}")

    by_person = {}
    for rec in records:
        key = (rec["person"], rec["session"])
        by_person.setdefault(key, {})[rec["image"]] = rec["path"]

    common_complete = []
    for person in range(1, 51):
        ok = True
        for session in (1, 2, 3):
            imgs = by_person.get((person, session), {})
            if sorted(imgs) != [1, 2, 3, 4, 5]:
                ok = False
                break
        if ok:
            common_complete.append(person)

    print(f"complete common persons across S1/S2/S3: {len(common_complete)}")
    if len(common_complete) < TARGET_PERSONS:
        raise RuntimeError(
            f"Need at least {TARGET_PERSONS} complete common persons; found {len(common_complete)}. Stop before inference."
        )

    selected = common_complete[:TARGET_PERSONS]
    print(f"selected person IDs: {selected}")

    stage = ROOT / "_sample_stage"
    if stage.exists():
        shutil.rmtree(stage)
    stage.mkdir(parents=True)

    manifest_lines = [
        "sample_path\tdataset_person_id\tsession\timage_index\tsha256"
    ]

    total = 0
    for person in selected:
        for session in (1, 2, 3):
            for image_idx in range(1, TARGET_IMAGES_PER_SESSION + 1):
                src = by_person[(person, session)][image_idx]
                ext = src.suffix.lower() or ".jpg"
                rel = Path(f"P{person:03d}") / f"S{session}" / f"{image_idx:02d}{ext}"
                dst = stage / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                manifest_lines.append(
                    f"{rel.as_posix()}\t{person}\t{session}\t{image_idx}\t{sha256_file(dst)}"
                )
                total += 1

    provenance_lines = [
        "MOHI bounded sample provenance",
        "Official source: Mutah University Hand Images Databases",
        "Use boundary: research / teaching purposes",
        "Official Group-1 archive URLs:",
    ]
    for session in (1, 2, 3):
        provenance_lines.append(f"S{session}: {URLS[session]}")
        provenance_lines.append(
            f"S{session} archive SHA256: {sha256_file(archives[session])}"
        )

    (stage / "manifest.tsv").write_text(
        "\n".join(manifest_lines) + "\n", encoding="utf-8"
    )
    (stage / "PROVENANCE.txt").write_text(
        "\n".join(provenance_lines) + "\n", encoding="utf-8"
    )

    if OUTPUT_ZIP.exists():
        OUTPUT_ZIP.unlink()

    with zipfile.ZipFile(
        OUTPUT_ZIP,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=6,
    ) as zf:
        for p in sorted(stage.rglob("*")):
            if p.is_file():
                zf.write(p, arcname=p.relative_to(stage))

    shutil.rmtree(stage)

    size_mb = OUTPUT_ZIP.stat().st_size / 1024 / 1024
    print()
    print("DONE")
    print(f"persons: {len(selected)}")
    print(f"images:  {total}")
    print(f"zip:     {OUTPUT_ZIP}")
    print(f"size:    {size_mb:.1f} MiB")
    print()
    print("Upload MOHI_sample_10p_3s_5i.zip to ChatGPT for the pinned runtime study.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(130)
