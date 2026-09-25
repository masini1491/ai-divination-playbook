"""REFERENCE-ONLY AST-P1-040 special-point geometry research.

This module is not a production Astrology provider.

Candidate identities:
    vertex_prime_vertical_ecliptic_v0
    equatorial_ascendant_ra_plus_90_v0

Inputs:
    ARMC / local sidereal angle in degrees
    ecliptic obliquity in degrees
    geographic latitude for Vertex

Vertex definition:
    western intersection of the local prime-vertical plane and ecliptic plane.

Equatorial Ascendant definition:
    ecliptic point whose right ascension is ARMC + 90 degrees.

Project input path:
    astronomy-engine==2.1.19 SiderealTime()
    + provider-compatible mean-obliquity formula
    + explicit east-positive geographic longitude.

No bare "East Point" mathematical identity is exposed.
"""
from __future__ import annotations

import math
import astronomy

VERTEX_FACT_ID = "vertex_prime_vertical_ecliptic_v0"
EQUASC_FACT_ID = "equatorial_ascendant_ra_plus_90_v0"
FRAME = "tropical_ecliptic_of_date_project_mean_obliquity"
SIDEREAL_SOURCE = "astronomy-engine-2.1.19-SiderealTime"
NORMALIZATION = "mod_360"


class ResearchGeometryError(RuntimeError):
    """Required special-point geometry is unavailable or singular."""


def _normalize(deg: float) -> float:
    return deg % 360.0


def _dot(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    return sum(x*y for x, y in zip(a, b))


def _cross(
    a: tuple[float, float, float],
    b: tuple[float, float, float],
) -> tuple[float, float, float]:
    return (
        a[1]*b[2] - a[2]*b[1],
        a[2]*b[0] - a[0]*b[2],
        a[0]*b[1] - a[1]*b[0],
    )


def _unit(v: tuple[float, float, float]) -> tuple[float, float, float]:
    mag = math.sqrt(_dot(v, v))
    if not math.isfinite(mag) or mag <= 1.0e-14:
        raise ResearchGeometryError("degenerate great-circle intersection")
    return tuple(x/mag for x in v)


def _mean_obliquity_deg(t: astronomy.Time) -> float:
    T = t.tt / 36525.0
    return 23.43929111 - (
        46.8150*T + 0.00059*T*T - 0.001813*T**3
    ) / 3600.0


def project_armc_deg(t: astronomy.Time, longitude_east_deg: float) -> float:
    if not math.isfinite(longitude_east_deg) or not -180.0 <= longitude_east_deg <= 180.0:
        raise ResearchGeometryError("longitude must be within [-180, 180]")
    return _normalize(
        astronomy.SiderealTime(t)*15.0 + longitude_east_deg
    )


def equatorial_ascendant_deg(*, armc_deg: float, obliquity_deg: float) -> float:
    """Return ecliptic longitude whose RA equals ARMC + 90 degrees."""
    if not math.isfinite(armc_deg) or not math.isfinite(obliquity_deg):
        raise ResearchGeometryError("non-finite geometry input")
    alpha = math.radians(_normalize(armc_deg + 90.0))
    eps = math.radians(obliquity_deg)
    return _normalize(math.degrees(math.atan2(
        math.sin(alpha),
        math.cos(eps)*math.cos(alpha),
    )))


def vertex_deg(
    *,
    armc_deg: float,
    obliquity_deg: float,
    latitude_deg: float,
) -> float:
    """Return western prime-vertical/ecliptic intersection."""
    if not all(math.isfinite(x) for x in (armc_deg, obliquity_deg, latitude_deg)):
        raise ResearchGeometryError("non-finite geometry input")
    if not -90.0 < latitude_deg < 90.0:
        raise ResearchGeometryError("Vertex is singular at the geographic poles")

    theta = math.radians(_normalize(armc_deg))
    phi = math.radians(latitude_deg)
    eps = math.radians(obliquity_deg)

    # Local north is the normal of the prime-vertical great-circle plane.
    north = (
        -math.sin(phi)*math.cos(theta),
        -math.sin(phi)*math.sin(theta),
        math.cos(phi),
    )
    # Ecliptic north pole expressed in equatorial coordinates.
    ecliptic_normal = (0.0, -math.sin(eps), math.cos(eps))

    crossing = _unit(_cross(north, ecliptic_normal))
    east = (-math.sin(theta), math.cos(theta), 0.0)
    east_component = _dot(crossing, east)
    if abs(east_component) <= 1.0e-12:
        raise ResearchGeometryError("Vertex east/west branch is singular")
    if east_component > 0.0:
        crossing = tuple(-x for x in crossing)

    # Equatorial -> ecliptic rotation about x by -obliquity.
    x_eq, y_eq, z_eq = crossing
    x_ecl = x_eq
    y_ecl = math.cos(eps)*y_eq + math.sin(eps)*z_eq
    return _normalize(math.degrees(math.atan2(y_ecl, x_ecl)))


def geometry_residuals(
    *,
    armc_deg: float,
    obliquity_deg: float,
    latitude_deg: float,
) -> dict[str, float]:
    """Return dimensionless/angle invariants for the project geometry."""
    theta = math.radians(_normalize(armc_deg))
    phi = math.radians(latitude_deg)
    eps = math.radians(obliquity_deg)

    north = (
        -math.sin(phi)*math.cos(theta),
        -math.sin(phi)*math.sin(theta),
        math.cos(phi),
    )
    ecliptic_normal = (0.0, -math.sin(eps), math.cos(eps))
    crossing = _unit(_cross(north, ecliptic_normal))
    east = (-math.sin(theta), math.cos(theta), 0.0)
    if _dot(crossing, east) > 0.0:
        crossing = tuple(-x for x in crossing)

    vertex_prime_vertical_plane = abs(_dot(crossing, north))
    vertex_ecliptic_plane = abs(_dot(crossing, ecliptic_normal))

    equasc = equatorial_ascendant_deg(
        armc_deg=armc_deg,
        obliquity_deg=obliquity_deg,
    )
    lam = math.radians(equasc)
    alpha = math.degrees(math.atan2(
        math.cos(eps)*math.sin(lam),
        math.cos(lam),
    )) % 360.0
    target_alpha = _normalize(armc_deg + 90.0)
    ra_residual = abs(((alpha-target_alpha+180.0)%360.0)-180.0)

    return {
        "vertex_prime_vertical_plane_abs": vertex_prime_vertical_plane,
        "vertex_ecliptic_plane_abs": vertex_ecliptic_plane,
        "equasc_ra_target_residual_deg": ra_residual,
    }


def special_points_from_project_inputs(
    *,
    time: astronomy.Time,
    longitude_east_deg: float,
    latitude_deg: float,
) -> dict[str, float]:
    armc = project_armc_deg(time, longitude_east_deg)
    eps = _mean_obliquity_deg(time)
    return {
        "armc_deg": armc,
        "obliquity_deg": eps,
        "vertex_deg": vertex_deg(
            armc_deg=armc,
            obliquity_deg=eps,
            latitude_deg=latitude_deg,
        ),
        "equatorial_ascendant_deg": equatorial_ascendant_deg(
            armc_deg=armc,
            obliquity_deg=eps,
        ),
    }
