"""TEMPORARY research probe. This file MUST NOT be merged to main.

It exists only to use the pull-request GitHub Actions network environment to collect
Phase E2 Swiss-vs-Horizons observations. The durable result belongs under
references/astrology/**; this probe is deleted before the final PR is merged.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import importlib
import importlib.resources
import json
import re
import subprocess
import sys
import tempfile
import unittest
import urllib.parse
import urllib.request
from pathlib import Path


EXPECTED_ASTEROID_GIT_BLOB = "8f900cab7e557e4c41f758a6bf3a3c3967e7e3db"
EXPECTED_ASTEROID_SIZE = 223004
EXPECTED_PLANETARY_GIT_BLOB = "786702cd04506371ee6223af1ebac02d54c848b8"
EXPECTED_PLANETARY_SIZE = 484061
HORIZONS_URL = "https://ssd.jpl.nasa.gov/api/horizons.api"

OBJECTS = [
    ("Chiron", "CHIRON", "2060;"),
    ("Ceres", "CERES", "1;"),
    ("Pallas", "PALLAS", "2;"),
    ("Juno", "JUNO", "3;"),
    ("Vesta", "VESTA", "4;"),
]
FIXTURES = [
    ("E2-F01", "2000-01-01T12:00:00Z", "calibration"),
    ("E2-F02", "1980-06-01T00:00:00Z", "calibration"),
    ("E2-F03", "2026-09-14T00:00:00Z", "calibration"),
    ("E2-F04", "2099-12-31T00:00:00Z", "calibration"),
    ("E2-H01", "1850-03-20T06:00:00Z", "holdout"),
    ("E2-H02", "1955-11-05T18:00:00Z", "holdout"),
    ("E2-H03", "2050-07-01T06:00:00Z", "holdout"),
    ("E2-H04", "2200-02-28T18:00:00Z", "holdout"),
]


def git_blob_sha(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def shortest_signed_delta(a: float, b: float) -> float:
    return ((b - a + 180.0) % 360.0) - 180.0


def parse_iso(utc: str) -> dt.datetime:
    return dt.datetime.fromisoformat(utc.replace("Z", "+00:00"))


def horizons_triplet(command: str, center: dt.datetime) -> tuple[list[tuple[float, float]], dict]:
    start = center - dt.timedelta(hours=1)
    stop = center + dt.timedelta(hours=1)
    fmt = "%Y-%m-%d %H:%M"
    params = {
        "format": "json",
        "COMMAND": f"'{command}'",
        "OBJ_DATA": "'NO'",
        "MAKE_EPHEM": "'YES'",
        "EPHEM_TYPE": "'OBSERVER'",
        "CENTER": "'500@399'",
        "START_TIME": f"'{start.strftime(fmt)}'",
        "STOP_TIME": f"'{stop.strftime(fmt)}'",
        "STEP_SIZE": "'1 h'",
        "QUANTITIES": "'31'",
        "APPARENT": "'AIRLESS'",
        "TIME_TYPE": "'UT'",
        "EXTRA_PREC": "'YES'",
        "CSV_FORMAT": "'YES'",
    }
    url = HORIZONS_URL + "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers={"User-Agent": "ai-divination-playbook-e2-research/1"})
    with urllib.request.urlopen(request, timeout=45) as response:
        payload = json.load(response)
    if payload.get("error"):
        raise AssertionError(f"Horizons error for {command}: {payload['error']}")
    result = payload.get("result", "")
    if "$$SOE" not in result or "$$EOE" not in result:
        raise AssertionError(f"Horizons table markers missing for {command}")
    table = result.split("$$SOE", 1)[1].split("$$EOE", 1)[0]
    rows: list[tuple[float, float]] = []
    float_re = re.compile(r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][+-]?\d+)?$")
    for raw in table.splitlines():
        if not raw.strip():
            continue
        numeric: list[float] = []
        for token in raw.split(","):
            token = token.strip()
            if float_re.fullmatch(token):
                numeric.append(float(token))
        if len(numeric) != 2:
            raise AssertionError(
                f"Unexpected Horizons CSV numeric columns for {command}: {raw!r} -> {numeric!r}"
            )
        rows.append((numeric[0], numeric[1]))
    if len(rows) != 3:
        raise AssertionError(f"Expected 3 Horizons rows for {command}, got {len(rows)}")
    return rows, payload.get("signature", {})


class E2LiveOracleProbe(unittest.TestCase):
    def test_collect_live_e2_observations(self) -> None:
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
        immanuel_root = importlib.resources.files("immanuel")
        asteroid_data = immanuel_root.joinpath(
            "resources", "ephemeris", "seas_18.se1"
        ).read_bytes()
        planetary_data = immanuel_root.joinpath(
            "resources", "ephemeris", "sepl_18.se1"
        ).read_bytes()
        self.assertEqual(len(asteroid_data), EXPECTED_ASTEROID_SIZE)
        self.assertEqual(git_blob_sha(asteroid_data), EXPECTED_ASTEROID_GIT_BLOB)
        self.assertEqual(len(planetary_data), EXPECTED_PLANETARY_SIZE)
        self.assertEqual(git_blob_sha(planetary_data), EXPECTED_PLANETARY_GIT_BLOB)

        observations = []
        horizons_signature = None
        with tempfile.TemporaryDirectory(prefix="e2-swiss-") as tempdir:
            Path(tempdir, "seas_18.se1").write_bytes(asteroid_data)
            Path(tempdir, "sepl_18.se1").write_bytes(planetary_data)
            swe.close()
            swe.set_ephe_path(tempdir)
            flags = swe.FLG_SWIEPH | swe.FLG_SPEED

            for fixture_id, utc, fixture_role in FIXTURES:
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
                    self.assertTrue(
                        returned_flags & swe.FLG_SWIEPH,
                        f"Swiss result did not retain FLG_SWIEPH for {fixture_id}/{object_id}: {returned_flags}",
                    )
                    rows, signature = horizons_triplet(horizons_command, when)
                    if horizons_signature is None:
                        horizons_signature = signature
                    self.assertEqual(signature, horizons_signature)
                    lon_minus, lat_minus = rows[0]
                    lon_mid, lat_mid = rows[1]
                    lon_plus, lat_plus = rows[2]
                    horizons_speed = shortest_signed_delta(lon_minus, lon_plus) * 12.0
                    observations.append(
                        {
                            "fixture_id": fixture_id,
                            "fixture_role": fixture_role,
                            "utc": utc,
                            "object_id": object_id,
                            "swiss": {
                                "longitude_deg": xx[0] % 360.0,
                                "latitude_deg": xx[1],
                                "distance_au": xx[2],
                                "speed_deg_per_day": xx[3],
                                "latitude_speed_deg_per_day": xx[4],
                                "distance_speed_au_per_day": xx[5],
                                "returned_flags": returned_flags,
                            },
                            "horizons": {
                                "longitude_deg": lon_mid % 360.0,
                                "latitude_deg": lat_mid,
                                "speed_deg_per_day": horizons_speed,
                                "longitude_minus_1h_deg": lon_minus % 360.0,
                                "longitude_plus_1h_deg": lon_plus % 360.0,
                                "latitude_minus_1h_deg": lat_minus,
                                "latitude_plus_1h_deg": lat_plus,
                            },
                        }
                    )
        swe.close()

        self.assertEqual(len(observations), 40)
        output = {
            "schema_name": "astrology_extended_chart_e2_residual_observations",
            "schema_version": "0.2.0",
            "authority": "REFERENCE_ONLY",
            "dataset_kind": "measured_oracle",
            "swiss_provenance": {
                "source_repository": "aloistr/swisseph",
                "source_revision": "91339e55d2351f32548d8a8d5bca6aa93b4f6da7",
                "asteroid_ephemeris_path": "ephe/seas_18.se1",
                "asteroid_ephemeris_blob_sha": EXPECTED_ASTEROID_GIT_BLOB,
                "asteroid_ephemeris_size_bytes": EXPECTED_ASTEROID_SIZE,
                "planetary_ephemeris_path": "ephe/sepl_18.se1",
                "planetary_ephemeris_blob_sha": EXPECTED_PLANETARY_GIT_BLOB,
                "planetary_ephemeris_size_bytes": EXPECTED_PLANETARY_SIZE,
                "binary_carrier": "PyPI immanuel==1.6.0 package data; both byte identities verified before use",
                "python_adapter": "pyswisseph==2.10.3.2",
                "required_flags": ["FLG_SWIEPH", "FLG_SPEED"],
            },
            "horizons_provenance": {
                "provider": "NASA/JPL Horizons",
                "api": "Horizons API",
                "signature": horizons_signature,
                "ephem_type": "OBSERVER",
                "center": "500@399",
                "quantities": [31],
                "apparent": "AIRLESS",
                "time_type": "UT",
                "extra_precision": True,
                "csv_format": True,
                "speed_derivation": "central finite difference t-1h to t+1h",
            },
            "observations": observations,
        }
        print("E2_LIVE_JSON_BEGIN")
        print(json.dumps(output, indent=2, sort_keys=True))
        print("E2_LIVE_JSON_END")


if __name__ == "__main__":
    unittest.main()
