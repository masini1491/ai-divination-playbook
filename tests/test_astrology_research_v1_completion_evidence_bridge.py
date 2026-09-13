from __future__ import annotations

import importlib
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASTROLOGY = ROOT / "references" / "astrology"
if str(ASTROLOGY) not in sys.path:
    sys.path.insert(0, str(ASTROLOGY))

MODULES = (
    "test_remaining_house_axes_registry",
    "test_registry_retrieval_preconditions",
    "test_essential_dignity_expansion_registry",
    "test_high_value_planet_aspects_registry",
    "test_transit_interpretation_registry",
    "test_fourth_tenth_house_axis_registry",
    "test_first_seventh_house_axis_registry",
    "test_interpretation_claim_registry_validator",
    "test_retrieve_interpretation_claims",
    "test_registry_typed_context_migration",
    "test_typed_contract_v0_2",
)


def load_tests(loader: unittest.TestLoader, tests: unittest.TestSuite, pattern: str | None) -> unittest.TestSuite:
    suite = unittest.TestSuite()
    for module_name in MODULES:
        module = importlib.import_module(module_name)
        suite.addTests(loader.loadTestsFromModule(module))
    return suite
