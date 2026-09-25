"""REFERENCE-ONLY AST-P1-030 temporary research candidate.

MUST NOT be treated as a production provider.

Candidate identity:
    black_moon_lilith_osculating_lrl_aengine_v0

Definition:
    instantaneous osculating lunar apogee from the Moon geocentric
    position/velocity state using the Laplace-Runge-Lenz eccentricity vector.

State authority:
    astronomy-engine==2.1.19 GeoMoonState() in J2000 mean equatorial (EQJ),
    AU and AU/day.

Output frame:
    true ecliptic/equinox of date (ECT), normalized mod 360 degrees.
"""
from __future__ import annotations

import math
import astronomy

FACT_ID = "black_moon_lilith_osculating_lrl_aengine_v0"
FRAME = "true_ecliptic_equinox_of_date"
STATE_SOURCE = "astronomy-engine-2.1.19-GeoMoonState-EQJ"
NORMALIZATION = "mod_360"
GM_EARTH_MOON_AU3_DAY2 = 8.997_011_546_044_162e-10
GM_EARTH_AU3_DAY2 = 398600.4418 * (86400.0**2) / (149_597_870.7**3)


def _lrl_eccentricity(
    x: float,
    y: float,
    z: float,
    vx: float,
    vy: float,
    vz: float,
    *,
    mu: float = GM_EARTH_MOON_AU3_DAY2,
) -> tuple[float, float, float]:
    r_mag = math.sqrt(x*x + y*y + z*z)
    if not math.isfinite(r_mag) or r_mag <= 0.0:
        raise ValueError("invalid lunar position magnitude")
    v2 = vx*vx + vy*vy + vz*vz
    r_dot_v = x*vx + y*vy + z*vz
    coeff = v2 - mu / r_mag
    ex = (coeff*x - r_dot_v*vx) / mu
    ey = (coeff*y - r_dot_v*vy) / mu
    ez = (coeff*z - r_dot_v*vz) / mu
    e_mag = math.sqrt(ex*ex + ey*ey + ez*ez)
    if not math.isfinite(e_mag) or e_mag <= 1.0e-12:
        raise ValueError("degenerate lunar eccentricity vector")
    return ex, ey, ez


def _apogee_longitude_from_eqj_evector(
    ex: float,
    ey: float,
    ez: float,
    time: astronomy.Time,
) -> float:
    perigee_eqj = astronomy.Vector(ex, ey, ez, time)
    perigee_ect = astronomy.RotateVector(astronomy.Rotation_EQJ_ECT(time), perigee_eqj)
    perigee_deg = math.degrees(math.atan2(perigee_ect.y, perigee_ect.x)) % 360.0
    return (perigee_deg + 180.0) % 360.0


def osculating_lilith_from_state(
    time: astronomy.Time,
    *,
    mu: float = GM_EARTH_MOON_AU3_DAY2,
) -> tuple[float, float]:
    state = astronomy.GeoMoonState(time)
    e = _lrl_eccentricity(
        state.x, state.y, state.z,
        state.vx, state.vy, state.vz,
        mu=mu,
    )
    e_mag = math.sqrt(sum(c*c for c in e))
    return _apogee_longitude_from_eqj_evector(*e, time), e_mag


def osculating_lilith_from_position_finite_difference(
    time: astronomy.Time,
    *,
    dt_days: float,
    mu: float = GM_EARTH_MOON_AU3_DAY2,
) -> float:
    if dt_days <= 0.0:
        raise ValueError("dt_days must be positive")
    prev = astronomy.GeoMoon(astronomy.Time.FromTerrestrialTime(time.tt - dt_days))
    now = astronomy.GeoMoon(time)
    nxt = astronomy.GeoMoon(astronomy.Time.FromTerrestrialTime(time.tt + dt_days))
    vx = (nxt.x - prev.x) / (2.0 * dt_days)
    vy = (nxt.y - prev.y) / (2.0 * dt_days)
    vz = (nxt.z - prev.z) / (2.0 * dt_days)
    e = _lrl_eccentricity(now.x, now.y, now.z, vx, vy, vz, mu=mu)
    return _apogee_longitude_from_eqj_evector(*e, time)
