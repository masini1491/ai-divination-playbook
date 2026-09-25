"""TEMPORARY AST-P1-030 research probe. MUST NOT MERGE."""
from __future__ import annotations

import json
import math
import os
import unittest

import astronomy
import swisseph as swe

from references.astrology.osculating_lilith_state_research import (
    FACT_ID,
    FRAME,
    GM_EARTH_AU3_DAY2,
    GM_EARTH_MOON_AU3_DAY2,
    NORMALIZATION,
    STATE_SOURCE,
    osculating_lilith_from_position_finite_difference,
    osculating_lilith_from_state,
)

J2000_JD_TT = 2451545.0
T_VALUES = tuple(-0.5 + 0.0625 * i for i in range(17))
DT_VARIANTS = (0.025, 0.05, 0.1)

# Prospectively frozen before first Actions execution.
# These are research stability gates, NOT production admission tolerances.
THRESHOLDS = {
    "state_vs_fd_0p05_max_deg": 0.25,
    "fd_step_spread_max_deg": 0.50,
}

REFERENCE_REVISIONS = {
    "astronomy_engine": "cosinekitty/astronomy@865d3da7d8112bbc7911238052c6af4aaf877181",
    "xalen": "vedika-io/xalen-ephemeris@cc6edbec1f748ebdc4950ae6198f575c5ada73fa",
    "pyswisseph": "astrorigin/pyswisseph@91ec65631badc7faf4a4b913570c944a4c1b101d",
}


def circular_sep_deg(a: float, b: float) -> float:
    return abs(((b - a + 180.0) % 360.0) - 180.0)


def swiss_osculating_apogee_deg(jd_tt: float) -> float:
    flags = swe.FLG_MOSEPH | swe.FLG_TRUEPOS | swe.FLG_SPEED
    values, _returned = swe.calc(jd_tt, swe.OSCU_APOG, flags)
    return float(values[0]) % 360.0


@unittest.skipUnless(os.environ.get("GITHUB_ACTIONS") == "true", "temporary Actions-only research probe")
class AstrologyExp3OsculatingLilithProbe(unittest.TestCase):
    def test_osculating_lilith_state_vector_research(self) -> None:
        rows = []
        for t_centuries in T_VALUES:
            tt_days = t_centuries * 36525.0
            time = astronomy.Time.FromTerrestrialTime(tt_days)
            jd_tt = J2000_JD_TT + tt_days

            state_deg, eccentricity = osculating_lilith_from_state(time)
            fd = {
                str(dt): osculating_lilith_from_position_finite_difference(
                    time,
                    dt_days=dt,
                )
                for dt in DT_VARIANTS
            }
            swiss_deg = swiss_osculating_apogee_deg(jd_tt)

            fd_pairwise = [
                circular_sep_deg(fd[str(DT_VARIANTS[i])], fd[str(DT_VARIANTS[j])])
                for i in range(len(DT_VARIANTS))
                for j in range(i + 1, len(DT_VARIANTS))
            ]
            rows.append({
                "t_centuries": t_centuries,
                "jd_tt": jd_tt,
                "candidate_deg": state_deg,
                "eccentricity_norm": eccentricity,
                "fd_deg": fd,
                "state_vs_fd_0p05_deg": circular_sep_deg(state_deg, fd["0.05"]),
                "fd_step_spread_deg": max(fd_pairwise),
                "earth_only_mu_sensitivity_deg": circular_sep_deg(
                    state_deg,
                    osculating_lilith_from_state(time, mu=GM_EARTH_AU3_DAY2)[0],
                ),
                "swiss_osculating_apogee_deg": swiss_deg,
                "swiss_compatibility_residual_deg": circular_sep_deg(state_deg, swiss_deg),
            })

        state_fd_max = max(row["state_vs_fd_0p05_deg"] for row in rows)
        fd_spread_max = max(row["fd_step_spread_deg"] for row in rows)
        result = {
            "schema_name": "astrology_exp3_osculating_lilith_state_vector_probe",
            "schema_version": "0.1.0",
            "authority": "TEMPORARY_REFERENCE_ONLY_RESEARCH",
            "production_admission": "NOT_GRANTED",
            "candidate": {
                "fact_id": FACT_ID,
                "definition": "instantaneous lunar osculating apogee from EQJ geocentric Moon state via LRL eccentricity vector",
                "state_source": STATE_SOURCE,
                "frame": FRAME,
                "normalization": NORMALIZATION,
                "gm_earth_moon_au3_day2": GM_EARTH_MOON_AU3_DAY2,
                "bare_lilith_alias": False,
            },
            "candidate_validation_window": {
                "t_centuries_min": min(T_VALUES),
                "t_centuries_max": max(T_VALUES),
                "approx_calendar_window": "1950-2050",
                "fixture_count": len(T_VALUES),
                "fixture_step_centuries": 0.0625,
                "admission_semantics": "RESEARCH_WINDOW_ONLY_NOT_PRODUCTION_DATE_ADMISSION",
            },
            "thresholds_frozen_before_first_execution": THRESHOLDS,
            "reference_revisions": REFERENCE_REVISIONS,
            "runtime_versions": {
                "astronomy_engine": "2.1.19",
                "pyswisseph": getattr(swe, "version", None),
            },
            "metrics": {
                "state_vs_fd_0p05_max_deg": state_fd_max,
                "fd_step_spread_max_deg": fd_spread_max,
                "earth_only_mu_sensitivity_max_deg": max(row["earth_only_mu_sensitivity_deg"] for row in rows),
                "swiss_compatibility_min_deg": min(row["swiss_compatibility_residual_deg"] for row in rows),
                "swiss_compatibility_max_deg": max(row["swiss_compatibility_residual_deg"] for row in rows),
                "eccentricity_norm_min": min(row["eccentricity_norm"] for row in rows),
                "eccentricity_norm_max": max(row["eccentricity_norm"] for row in rows),
            },
            "pass": {
                "state_vs_fd_0p05": state_fd_max <= THRESHOLDS["state_vs_fd_0p05_max_deg"],
                "fd_step_spread": fd_spread_max <= THRESHOLDS["fd_step_spread_max_deg"],
            },
            "swiss_gate": "REPORT_ONLY_MODEL_SENSITIVE_COMPATIBILITY",
            "rows": rows,
        }
        result["overall_research_stability_pass"] = all(result["pass"].values())

        print("ASTROLOGY_EXP3_JSON_BEGIN")
        print(json.dumps(result, indent=2, sort_keys=True))
        print("ASTROLOGY_EXP3_JSON_END")

        self.assertLessEqual(state_fd_max, THRESHOLDS["state_vs_fd_0p05_max_deg"])
        self.assertLessEqual(fd_spread_max, THRESHOLDS["fd_step_spread_max_deg"])


if __name__ == "__main__":
    unittest.main()
