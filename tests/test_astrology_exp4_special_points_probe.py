"""TEMPORARY AST-P1-040 research probe. MUST NOT MERGE."""
from __future__ import annotations

import datetime as dt
import json
import math
import os
import unittest

import astronomy
import swisseph as swe

from references.astrology.special_points_geometry_research import (
    EQUASC_FACT_ID,
    VERTEX_FACT_ID,
    equatorial_ascendant_deg,
    geometry_residuals,
    special_points_from_project_inputs,
    vertex_deg,
)

# Prospectively frozen before first Actions execution.
# Research feasibility gates only; NOT production admission tolerances.
THRESHOLDS = {
    "same_input_swiss_max_deg": 1.0e-8,
    "geometry_plane_abs_max": 1.0e-12,
    "equasc_ra_residual_max_deg": 1.0e-10,
    "project_input_swiss_max_deg": 0.05,
}

REFERENCE_REVISIONS = {
    "swiss": "aloistr/swisseph@9083a12d59e98034fb2337061481ac8800c16e64",
    "astronomy_engine": "cosinekitty/astronomy@865d3da7d8112bbc7911238052c6af4aaf877181",
    "astrolog_alias": "CruiserOne/Astrolog@5bf172ea231c4b6ea3d7e09ca307571354a41e8a",
}

SYNTHETIC = (
    {"armc_deg": 37.0, "obliquity_deg": 23.4393, "latitude_deg": 0.0},
    {"armc_deg": 123.0, "obliquity_deg": 23.4393, "latitude_deg": 25.0},
    {"armc_deg": 271.0, "obliquity_deg": 23.4393, "latitude_deg": -33.0},
    {"armc_deg": 19.0, "obliquity_deg": 23.4393, "latitude_deg": 65.0},
    {"armc_deg": 205.0, "obliquity_deg": 23.4393, "latitude_deg": -65.0},
    {"armc_deg": 311.0, "obliquity_deg": 23.4393, "latitude_deg": 89.0},
    {"armc_deg": 71.0, "obliquity_deg": 23.4393, "latitude_deg": -89.0},
)

REAL_LOCATIONS = (
    {
        "id": "greenwich",
        "utc": "2026-03-20T12:00:00+00:00",
        "latitude_deg": 51.4779,
        "longitude_east_deg": 0.0,
    },
    {
        "id": "sydney",
        "utc": "1990-06-15T00:00:00+00:00",
        "latitude_deg": -33.8688,
        "longitude_east_deg": 151.2093,
    },
    {
        "id": "quito",
        "utc": "2024-09-22T00:00:00+00:00",
        "latitude_deg": -0.1807,
        "longitude_east_deg": -78.4678,
    },
    {
        "id": "tromso",
        "utc": "2025-12-21T12:00:00+00:00",
        "latitude_deg": 69.6492,
        "longitude_east_deg": 18.9553,
    },
    {
        "id": "ushuaia",
        "utc": "2025-06-21T12:00:00+00:00",
        "latitude_deg": -54.8019,
        "longitude_east_deg": -68.3030,
    },
)


def circular_sep_deg(a: float, b: float) -> float:
    return abs(((b-a+180.0)%360.0)-180.0)


def astronomy_time(value: str) -> astronomy.Time:
    when = dt.datetime.fromisoformat(value)
    return astronomy.Time.Make(
        when.year, when.month, when.day,
        when.hour, when.minute,
        when.second + when.microsecond/1_000_000.0,
    )


def jd_ut(value: str) -> float:
    when = dt.datetime.fromisoformat(value)
    hour = when.hour + when.minute/60.0 + (when.second + when.microsecond/1_000_000.0)/3600.0
    return swe.julday(when.year, when.month, when.day, hour, swe.GREG_CAL)


def swiss_points(jd: float, latitude_deg: float, longitude_east_deg: float):
    _cusps, ascmc = swe.houses_ex(jd, latitude_deg, longitude_east_deg, b"E", 0)
    return {
        "ascendant_deg": float(ascmc[0]) % 360.0,
        "mc_deg": float(ascmc[1]) % 360.0,
        "armc_deg": float(ascmc[2]) % 360.0,
        "vertex_deg": float(ascmc[3]) % 360.0,
        "equatorial_ascendant_deg": float(ascmc[4]) % 360.0,
    }


def swiss_true_obliquity_deg(jd: float) -> float:
    values, _flags = swe.calc_ut(jd, swe.ECL_NUT, 0)
    return float(values[0])


@unittest.skipUnless(os.environ.get("GITHUB_ACTIONS") == "true", "temporary Actions-only research probe")
class AstrologyExp4SpecialPointsProbe(unittest.TestCase):
    def test_special_point_geometry(self) -> None:
        synthetic_rows = []
        for row in SYNTHETIC:
            residuals = geometry_residuals(**row)
            synthetic_rows.append({**row, **residuals})

        real_rows = []
        same_input_residuals = []
        project_input_residuals = []
        for fixture in REAL_LOCATIONS:
            jd = jd_ut(fixture["utc"])
            swiss = swiss_points(jd, fixture["latitude_deg"], fixture["longitude_east_deg"])
            swiss_eps = swiss_true_obliquity_deg(jd)

            formula_vertex = vertex_deg(
                armc_deg=swiss["armc_deg"],
                obliquity_deg=swiss_eps,
                latitude_deg=fixture["latitude_deg"],
            )
            formula_equasc = equatorial_ascendant_deg(
                armc_deg=swiss["armc_deg"],
                obliquity_deg=swiss_eps,
            )
            same_vertex = circular_sep_deg(formula_vertex, swiss["vertex_deg"])
            same_equasc = circular_sep_deg(formula_equasc, swiss["equatorial_ascendant_deg"])
            same_input_residuals.extend([same_vertex, same_equasc])

            project = special_points_from_project_inputs(
                time=astronomy_time(fixture["utc"]),
                longitude_east_deg=fixture["longitude_east_deg"],
                latitude_deg=fixture["latitude_deg"],
            )
            project_vertex = circular_sep_deg(project["vertex_deg"], swiss["vertex_deg"])
            project_equasc = circular_sep_deg(
                project["equatorial_ascendant_deg"],
                swiss["equatorial_ascendant_deg"],
            )
            project_input_residuals.extend([project_vertex, project_equasc])

            real_rows.append({
                **fixture,
                "jd_ut": jd,
                "swiss": swiss,
                "swiss_true_obliquity_deg": swiss_eps,
                "same_input_formula": {
                    "vertex_deg": formula_vertex,
                    "equatorial_ascendant_deg": formula_equasc,
                    "vertex_residual_deg": same_vertex,
                    "equasc_residual_deg": same_equasc,
                },
                "project_input": {
                    **project,
                    "vertex_swiss_residual_deg": project_vertex,
                    "equasc_swiss_residual_deg": project_equasc,
                },
            })

        geometry_plane_max = max(
            max(
                row["vertex_prime_vertical_plane_abs"],
                row["vertex_ecliptic_plane_abs"],
            )
            for row in synthetic_rows
        )
        equasc_ra_max = max(row["equasc_ra_target_residual_deg"] for row in synthetic_rows)
        same_input_max = max(same_input_residuals)
        project_input_max = max(project_input_residuals)

        result = {
            "schema_name": "astrology_exp4_special_points_geometry_probe",
            "schema_version": "0.1.0",
            "authority": "TEMPORARY_REFERENCE_ONLY_RESEARCH",
            "production_admission": "NOT_GRANTED",
            "candidates": {
                "vertex": {
                    "fact_id": VERTEX_FACT_ID,
                    "definition": "western intersection of local prime-vertical plane and ecliptic plane",
                },
                "equatorial_ascendant": {
                    "fact_id": EQUASC_FACT_ID,
                    "definition": "ecliptic point whose right ascension equals ARMC plus 90 degrees",
                },
            },
            "east_point_alias": {
                "canonical_math_identity": False,
                "research_compatibility_evidence": "Astrolog EP receives Swiss SE_EQUASC output",
                "production_alias_admission": "NOT_GRANTED",
            },
            "thresholds_frozen_before_first_execution": THRESHOLDS,
            "reference_revisions": REFERENCE_REVISIONS,
            "runtime_versions": {
                "astronomy_engine": "2.1.19",
                "pyswisseph": getattr(swe, "version", None),
            },
            "metrics": {
                "synthetic_geometry_plane_abs_max": geometry_plane_max,
                "synthetic_equasc_ra_residual_max_deg": equasc_ra_max,
                "same_input_swiss_max_deg": same_input_max,
                "project_input_swiss_max_deg": project_input_max,
                "vertex_project_input_swiss_max_deg": max(
                    row["project_input"]["vertex_swiss_residual_deg"] for row in real_rows
                ),
                "equasc_project_input_swiss_max_deg": max(
                    row["project_input"]["equasc_swiss_residual_deg"] for row in real_rows
                ),
            },
            "pass": {
                "geometry_plane": geometry_plane_max <= THRESHOLDS["geometry_plane_abs_max"],
                "equasc_ra_identity": equasc_ra_max <= THRESHOLDS["equasc_ra_residual_max_deg"],
                "same_input_swiss": same_input_max <= THRESHOLDS["same_input_swiss_max_deg"],
                "project_input_swiss": project_input_max <= THRESHOLDS["project_input_swiss_max_deg"],
            },
            "synthetic_rows": synthetic_rows,
            "real_location_rows": real_rows,
        }
        result["overall_research_geometry_pass"] = all(result["pass"].values())

        print("ASTROLOGY_EXP4_JSON_BEGIN")
        print(json.dumps(result, indent=2, sort_keys=True))
        print("ASTROLOGY_EXP4_JSON_END")

        self.assertLessEqual(geometry_plane_max, THRESHOLDS["geometry_plane_abs_max"])
        self.assertLessEqual(equasc_ra_max, THRESHOLDS["equasc_ra_residual_max_deg"])
        self.assertLessEqual(same_input_max, THRESHOLDS["same_input_swiss_max_deg"])
        self.assertLessEqual(project_input_max, THRESHOLDS["project_input_swiss_max_deg"])


if __name__ == "__main__":
    unittest.main()
