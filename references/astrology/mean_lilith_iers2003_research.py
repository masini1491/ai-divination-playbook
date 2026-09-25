"""REFERENCE-ONLY AST-P1-020 Mean Black Moon Lilith research candidate.

Explicit deterministic identity:
    black_moon_lilith_mean_iers2003_v1

Definition:
    IERS Conventions (2003) secular mean lunar apogee
    longitude = F + Omega - l + 180 degrees

Frame:
    mean ecliptic / mean equinox of date

Time argument:
    TT Julian centuries since J2000.0.

This module is research-only and intentionally exposes no bare "lilith" alias.
It is not a production Astrology provider.
"""
from __future__ import annotations

TURN_ARCSEC = 1_296_000.0
HALF_TURN_ARCSEC = 648_000.0
FACT_ID = "black_moon_lilith_mean_iers2003_v1"
FRAME = "mean_ecliptic_mean_equinox_of_date"
TIME_ARGUMENT = "TT_JULIAN_CENTURIES_FROM_J2000"
NORMALIZATION = "mod_360"


def _fal03_arcsec(t: float) -> float:
    return (
        485868.249036
        + t
        * (
            1717915923.2178
            + t * (31.8792 + t * (0.051635 + t * (-0.00024470)))
        )
    ) % TURN_ARCSEC


def _faf03_arcsec(t: float) -> float:
    return (
        335779.526232
        + t
        * (
            1739527262.8478
            + t * (-12.7512 + t * (-0.001037 + t * 0.00000417))
        )
    ) % TURN_ARCSEC


def _faom03_arcsec(t: float) -> float:
    return (
        450160.398036
        + t
        * (
            -6962890.5431
            + t * (7.4722 + t * (0.007702 + t * (-0.00005939)))
        )
    ) % TURN_ARCSEC


def mean_lilith_iers2003_deg(t: float) -> float:
    """Return explicit IERS-2003 secular mean lunar apogee longitude."""
    return (
        _faf03_arcsec(t)
        + _faom03_arcsec(t)
        - _fal03_arcsec(t)
        + HALF_TURN_ARCSEC
    ) % TURN_ARCSEC / 3600.0
