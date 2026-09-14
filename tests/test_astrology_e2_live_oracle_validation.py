"""TEMPORARY prospective Phase E2 tolerance validation. MUST NOT MERGE."""
from __future__ import annotations

import importlib
import importlib.resources
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test_astrology_e2_live_oracle_probe import (
    EXPECTED_ASTEROID_GIT_BLOB,
    EXPECTED_ASTEROID_SIZE,
    EXPECTED_PLANETARY_GIT_BLOB,
    EXPECTED_PLANETARY_SIZE,
    OBJECTS,
    git_blob_sha,
    horizons_triplet,
    parse_iso,
)

LONGITUDE_TOLERANCE_DEG = 5.0 / 3600.0
SPEED_TOLERANCE_DEG_PER_DAY = 1e-5
VALIDATION_FIXTURES = [
    ("E2-V01", "1825-08-17T03:00:00Z"),
    ("E2-V02", "1925-02-14T15:00:00Z"),
    ("E2-V03", "2075-10-09T09:00:00Z"),
    ("E2-V04", "2350-05-23T21:00:00Z"),
]


def circular_separation_deg(a: float, b: float) -> float:
    delta = abs((b - a) % 360.0)
    return min(delta, 360.0 - delta)


class E2ProspectiveToleranceValidation(unittest.TestCase):
    def test_prospective_validation(self) -> None:
        # Thresholds and validation dates were frozen before the first prospective
        # execution. After that execution found a failure, this revision keeps the
        # thresholds and dates unchanged and only defers the assertion so the full
        # failure surface is observable. It is characterization, not a new blind pass.
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--quiet",
                "--no-deps",
                "immanuel==1.6.0",
                "pyswisseph==2.10.3.2",
            ],
            check=True,
        )
        swe = importlib.import_module("swisseph")
        root = importlib.resources.files("immanuel")
        asteroid_data = root.joinpath("resources", "ephemeris", "seas_18.se1").read_bytes()
        planetary_data = root.joinpath("resources", "ephemeris", "sepl_18.se1").read_bytes()
        self.assertEqual(len(asteroid_data), EXPECTED_ASTEROID_SIZE)
        self.assertEqual(git_blob_sha(asteroid_data), EXPECTED_ASTEROID_GIT_BLOB)
        self.assertEqual(len(planetary_data), EXPECTED_PLANETARY_SIZE)
        self.assertEqual(git_blob_sha(planetary_data), EXPECTED_PLANETARY_GIT_BLOB)

        residuals = []
        failures = []
        with tempfile.TemporaryDirectory(prefix="e2-validation-") as tempdir:
            Path(tempdir, "seas_18.se1").write_bytes(asteroid_data)
            Path(tempdir, "sepl_18.se1").write_bytes(planetary_data)
            swe.close()
            swe.set_ephe_path(tempdir)
            flags = swe.FLG_SWIEPH | swe.FLG_SPEED
            for fixture_id, utc in VALIDATION_FIXTURES:
                when = parse_iso(utc)
                jd = swe.julday(
                    when.year,
                    when.month,
                    when.day,
                    when.hour + when.minute / 60.0 + when.second / 3600.0,
                    swe.GREG_CAL,
                )
                for object_id, swiss_constant, horizons_command in OBJECTS:
                    xx, returned_flags = swe.calc_ut(jd, getattr(swe, swiss_constant), flags)
                    self.assertTrue(returned_flags & swe.FLG_SWIEPH)
                    rows, _ = horizons_triplet(horizons_command, when)
                    lon_minus = rows[0][0]
                    lon_mid = rows[1][0]
                    lon_plus = rows[2][0]
                    horizons_speed = (((lon_plus - lon_minus + 180.0) % 360.0) - 180.0) * 12.0
                    longitude_delta = circular_separation_deg(xx[0] % 360.0, lon_mid % 360.0)
                    speed_delta = abs(xx[3] - horizons_speed)
                    row = {
                        "fixture_id": fixture_id,
                        "utc": utc,
                        "object_id": object_id,
                        "longitude_delta_deg": longitude_delta,
                        "longitude_delta_arcsec": longitude_delta * 3600.0,
                        "speed_delta_deg_per_day": speed_delta,
                        "longitude_within_frozen_tolerance": longitude_delta <= LONGITUDE_TOLERANCE_DEG,
                        "speed_within_frozen_tolerance": speed_delta <= SPEED_TOLERANCE_DEG_PER_DAY,
                    }
                    residuals.append(row)
                    if not row["longitude_within_frozen_tolerance"] or not row["speed_within_frozen_tolerance"]:
                        failures.append(row)
        swe.close()
        self.assertEqual(len(residuals), 20)
        print("E2_VALIDATION_JSON_BEGIN")
        print(
            json.dumps(
                {
                    "status": "PROSPECTIVE_VALIDATION_FAILED" if failures else "PROSPECTIVE_VALIDATION_PASS",
                    "longitude_tolerance_arcsec": 5.0,
                    "speed_tolerance_deg_per_day": SPEED_TOLERANCE_DEG_PER_DAY,
                    "failures": failures,
                    "residuals": residuals,
                },
                indent=2,
                sort_keys=True,
            )
        )
        print("E2_VALIDATION_JSON_END")
        self.assertFalse(failures, f"frozen prospective tolerance failed for {len(failures)} row(s)")


if __name__ == "__main__":
    unittest.main()
