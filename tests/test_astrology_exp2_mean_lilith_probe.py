"""TEMPORARY AST-P1-020 research probe. MUST NOT MERGE."""
from __future__ import annotations

import json
import math
import os
import unittest

import erfa
import swisseph as swe

from references.astrology.mean_lilith_iers2003_research import (
    FACT_ID,
    FRAME,
    NORMALIZATION,
    TIME_ARGUMENT,
    mean_lilith_iers2003_deg,
)

T_VALUES = tuple(-2.0 + 0.25 * i for i in range(17))
J2000_TT = 2451545.0
DAYS_PER_JULIAN_CENTURY = 36525.0

# Frozen before first execution. These are research feasibility/parity gates,
# not production admission tolerances.
THRESHOLDS = {
    "erfa_same_definition_max_arcsec": 0.0001,
    "xalen_meeus_compatibility_max_arcsec": 1.0,
}

REFERENCE_REVISIONS = {
    "erfa": "liberfa/erfa@1a8044cde5b7763295d472a6443387239127c6c8",
    "moira": "TheDaniel166/moira@6dcc0fdaf35c16d96b544e03a509f2188603bc68",
    "xalen": "vedika-io/xalen-ephemeris@cc6edbec1f748ebdc4950ae6198f575c5ada73fa",
    "pyswisseph_repo": "astrorigin/pyswisseph@91ec65631badc7faf4a4b913570c944a4c1b101d",
}


def circular_sep_deg(a: float, b: float) -> float:
    return abs(((b - a + 180.0) % 360.0) - 180.0)


def erfa_iers2003_deg(t: float) -> float:
    return math.degrees(
        (erfa.faf03(t) + erfa.faom03(t) - erfa.fal03(t) + math.pi)
        % (2.0 * math.pi)
    )


def xalen_meeus_deg(t: float) -> float:
    perigee = (
        83.3532465
        + 4069.0137287 * t
        - 0.0103200 * t * t
        - t**3 / 80053.0
        + t**4 / 18999000.0
    )
    return (perigee + 180.0) % 360.0


def swiss_mean_apogee_deg(jd_tt: float) -> tuple[float, int]:
    flags = swe.FLG_MOSEPH | swe.FLG_NONUT | swe.FLG_SPEED
    values, returned = swe.calc(jd_tt, swe.MEAN_APOG, flags)
    return float(values[0]) % 360.0, int(returned)


@unittest.skipUnless(os.environ.get("GITHUB_ACTIONS") == "true", "temporary Actions-only research probe")
class AstrologyExp2MeanLilithProbe(unittest.TestCase):
    def test_iers2003_mean_lilith_parity(self) -> None:
        rows = []
        for t in T_VALUES:
            jd_tt = J2000_TT + t * DAYS_PER_JULIAN_CENTURY
            candidate = mean_lilith_iers2003_deg(t)
            erfa_lon = erfa_iers2003_deg(t)
            xalen_lon = xalen_meeus_deg(t)
            swiss_lon, swiss_flags = swiss_mean_apogee_deg(jd_tt)
            rows.append(
                {
                    "t_centuries": t,
                    "jd_tt": jd_tt,
                    "candidate_deg": candidate,
                    "erfa_deg": erfa_lon,
                    "erfa_residual_arcsec": circular_sep_deg(candidate, erfa_lon) * 3600.0,
                    "xalen_meeus_deg": xalen_lon,
                    "xalen_meeus_residual_arcsec": circular_sep_deg(candidate, xalen_lon) * 3600.0,
                    "swiss_mean_apog_deg": swiss_lon,
                    "swiss_compatibility_residual_arcsec": circular_sep_deg(candidate, swiss_lon) * 3600.0,
                    "swiss_returned_flags": swiss_flags,
                }
            )

        erfa_values = [row["erfa_residual_arcsec"] for row in rows]
        xalen_values = [row["xalen_meeus_residual_arcsec"] for row in rows]
        swiss_values = [row["swiss_compatibility_residual_arcsec"] for row in rows]

        erfa_max = max(erfa_values)
        xalen_max = max(xalen_values)
        result = {
            "schema_name": "astrology_exp2_mean_lilith_iers2003_parity",
            "schema_version": "0.1.0",
            "authority": "REFERENCE_ONLY_RESEARCH",
            "production_admission": "NOT_GRANTED",
            "candidate": {
                "fact_id": FACT_ID,
                "definition": "IERS Conventions (2003) secular mean lunar apogee F + Omega - l + 180 degrees",
                "frame": FRAME,
                "time_argument": TIME_ARGUMENT,
                "normalization": NORMALIZATION,
                "bare_lilith_alias": False,
            },
            "candidate_validation_window": {
                "t_centuries_min": min(T_VALUES),
                "t_centuries_max": max(T_VALUES),
                "approx_calendar_window": "1800-2200",
                "fixture_count": len(T_VALUES),
                "fixture_step_centuries": 0.25,
            },
            "thresholds_frozen_before_first_execution": THRESHOLDS,
            "reference_paths": {
                "same_definition_authority": REFERENCE_REVISIONS["erfa"],
                "same_definition_architecture_crosscheck": REFERENCE_REVISIONS["moira"],
                "independent_analytical_compatibility": REFERENCE_REVISIONS["xalen"],
                "swiss_compatibility_only": REFERENCE_REVISIONS["pyswisseph_repo"],
            },
            "runtime_versions": {
                "pyerfa": getattr(erfa, "__version__", None),
                "pyswisseph": getattr(swe, "version", None),
            },
            "metrics": {
                "erfa_same_definition_max_arcsec": erfa_max,
                "xalen_meeus_compatibility_max_arcsec": xalen_max,
                "swiss_compatibility_min_arcsec": min(swiss_values),
                "swiss_compatibility_max_arcsec": max(swiss_values),
            },
            "pass": {
                "erfa_same_definition": erfa_max <= THRESHOLDS["erfa_same_definition_max_arcsec"],
                "xalen_meeus_compatibility": xalen_max <= THRESHOLDS["xalen_meeus_compatibility_max_arcsec"],
            },
            "swiss_gate": "REPORT_ONLY_DIFFERENT_DEFINITION",
            "rows": rows,
        }
        result["overall_research_parity_pass"] = all(result["pass"].values())

        print("ASTROLOGY_EXP2_JSON_BEGIN")
        print(json.dumps(result, indent=2, sort_keys=True))
        print("ASTROLOGY_EXP2_JSON_END")

        self.assertLessEqual(
            erfa_max,
            THRESHOLDS["erfa_same_definition_max_arcsec"],
        )
        self.assertLessEqual(
            xalen_max,
            THRESHOLDS["xalen_meeus_compatibility_max_arcsec"],
        )


if __name__ == "__main__":
    unittest.main()
