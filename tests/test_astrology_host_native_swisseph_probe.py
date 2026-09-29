import importlib.util
from pathlib import Path


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "references"
    / "astrology"
    / "host_native_swisseph_probe.py"
)
SPEC = importlib.util.spec_from_file_location("host_native_swisseph_probe", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def row(backend, status="PASS"):
    return {"status": status, "effective_backend": backend}


def test_classify_moshier_natal_baseline():
    rows = {name: row("MOSEPH") for name, _ in MODULE.CORE_BODIES}
    assert MODULE.classify(rows, True) == "MOSHIER_NATAL_BASELINE"


def test_classify_mixed_natal_baseline():
    rows = {name: row("MOSEPH") for name, _ in MODULE.CORE_BODIES}
    rows["Moon"] = row("SWIEPH")
    assert MODULE.classify(rows, True) == "MIXED_NATAL_BASELINE"


def test_classify_partial_when_core_or_houses_fail():
    rows = {name: row("MOSEPH") for name, _ in MODULE.CORE_BODIES}
    rows["Pluto"] = row("MOSEPH", "FAIL")
    assert MODULE.classify(rows, True) == "PARTIAL_EXECUTION"
    rows["Pluto"] = row("MOSEPH")
    assert MODULE.classify(rows, False) == "PARTIAL_EXECUTION"


def test_standard_file_inspection(tmp_path):
    (tmp_path / "seas_18.se1").write_bytes(b"x")
    result = MODULE.inspect_standard_files(str(tmp_path))
    assert result["seas_18.se1"]["exists"] is True
    assert result["sepl_18.se1"]["exists"] is False
    assert result["semo_18.se1"]["exists"] is False
