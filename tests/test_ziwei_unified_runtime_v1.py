from __future__ import annotations
import json
import unittest
from pathlib import Path

from tools.ziwei_brightness_provider import PROFILE_ID as BRIGHTNESS_PROFILE_ID
from tools.ziwei_calendar_provider import GregorianBirthInput
from tools.ziwei_natal_provider import NormalizedNatalInput
from tools.ziwei_runtime import (
    BRIGHTNESS_MODULE, ZiWeiReadingRequest, request_from_transport,
    request_to_transport, run_ziwei, run_ziwei_transport,
)
from tools.ziwei_scope_a_pipeline import run_scope_a_natal
from tools.ziwei_brightness_pipeline import run_scope_a_natal_with_brightness
from tools.ziwei_gregorian_pipeline import run_scope_a_gregorian, run_scope_a_gregorian_with_brightness

ROOT=Path(__file__).resolve().parents[1]

class ZiWeiUnifiedRuntimeV1Tests(unittest.TestCase):
    def setUp(self):
        self.natal=NormalizedNatalInput(1987,5,20,"酉","synthetic:unified-runtime")
        self.gregorian=GregorianBirthInput(1987,5,7,5,17)

    def test_typed_contracts_are_closed_world_and_versioned(self):
        req=json.loads((ROOT/"schemas/ziwei/ZIWEI_READING_REQUEST_V1.schema.json").read_text(encoding="utf-8"))
        res=json.loads((ROOT/"schemas/ziwei/ZIWEI_READING_RESULT_V1.schema.json").read_text(encoding="utf-8"))
        self.assertFalse(req["additionalProperties"])
        self.assertFalse(res["additionalProperties"])
        self.assertEqual("1.0.0",req["properties"]["schema_version"]["const"])
        self.assertEqual("1.0.0",res["properties"]["schema_version"]["const"])

    def test_json_transport_round_trips_gregorian_and_result_contract(self):
        request=ZiWeiReadingRequest(
            request_id="transport-g",birth=self.gregorian,
            optional_modules=(BRIGHTNESS_MODULE,),brightness_profile=BRIGHTNESS_PROFILE_ID,
        )
        payload=request_to_transport(request)
        self.assertEqual("ziwei_reading_request",payload["schema_name"])
        self.assertEqual("1.0.0",payload["schema_version"])
        self.assertEqual("gregorian",payload["birth"]["input_type"])
        parsed=request_from_transport(payload)
        self.assertEqual(request,parsed)
        result=run_ziwei_transport(payload)
        self.assertEqual("ziwei_reading_result",result["schema_name"])
        self.assertEqual("1.0.0",result["schema_version"])
        self.assertEqual(request.request_id,result["request_id"])
        self.assertEqual([BRIGHTNESS_MODULE],result["runtime"]["optional_modules"])

    def test_json_transport_round_trips_normalized_lunar(self):
        request=ZiWeiReadingRequest(request_id="transport-l",birth=self.natal)
        payload=request_to_transport(request)
        self.assertEqual("normalized_lunar",payload["birth"]["input_type"])
        self.assertEqual(request,request_from_transport(payload))
        self.assertEqual(request.request_id,run_ziwei_transport(payload)["request_id"])

    def test_json_transport_fails_closed_on_schema_drift(self):
        payload=request_to_transport(ZiWeiReadingRequest(request_id="transport-bad",birth=self.gregorian))
        payload["unexpected"]=True
        with self.assertRaises(ValueError):
            request_from_transport(payload)
        payload=request_to_transport(ZiWeiReadingRequest(request_id="transport-bad-birth",birth=self.gregorian))
        payload["birth"].pop("second")
        with self.assertRaises(ValueError):
            request_from_transport(payload)

    def test_normalized_lunar_request_uses_one_typed_result_owner(self):
        r=run_ziwei(ZiWeiReadingRequest(request_id="typed-lunar",birth=self.natal))
        self.assertEqual("ziwei_reading_result",r["schema_name"])
        self.assertEqual("ziwei-production-runtime-v1",r["runtime"]["runtime_id"])
        self.assertEqual([],r["runtime"]["optional_modules"])
        self.assertNotIn("input_adapter",r)

    def test_gregorian_request_binds_admitted_adapter(self):
        r=run_ziwei(ZiWeiReadingRequest(request_id="typed-gregorian",birth=self.gregorian))
        self.assertEqual("ziwei-gregorian-input-adapter-v1",r["input_adapter"]["pipeline_id"])
        self.assertTrue(r["authority"]["gregorian_input_adapter_admitted"])

    def test_brightness_is_an_optional_module_not_a_new_entrypoint_contract(self):
        r=run_ziwei(ZiWeiReadingRequest(
            request_id="typed-brightness",birth=self.natal,
            optional_modules=(BRIGHTNESS_MODULE,),brightness_profile=BRIGHTNESS_PROFILE_ID,
        ))
        self.assertEqual([BRIGHTNESS_MODULE],r["runtime"]["optional_modules"])
        self.assertIn("brightness",r["calculation"])
        self.assertTrue(r["authority"]["brightness_profile_admitted"])

    def test_unknown_scope_module_and_profile_fail_closed(self):
        with self.assertRaises(ValueError):
            run_ziwei(ZiWeiReadingRequest(request_id="bad-scope",birth=self.natal,temporal_scope="yearly"))
        with self.assertRaises(ValueError):
            run_ziwei(ZiWeiReadingRequest(request_id="bad-module",birth=self.natal,optional_modules=("unsupported_module_v1",)))
        with self.assertRaises(ValueError):
            run_ziwei(ZiWeiReadingRequest(
                request_id="bad-profile",birth=self.natal,
                optional_modules=(BRIGHTNESS_MODULE,),brightness_profile="unknown",
            ))

    def test_legacy_normalized_lunar_adapters_preserve_legacy_surface(self):
        base=run_scope_a_natal(self.natal,request_id="legacy")
        bright=run_scope_a_natal_with_brightness(self.natal,request_id="legacy-bright")
        for r in (base,bright):
            self.assertNotIn("schema_name",r)
            self.assertNotIn("runtime",r)
        self.assertEqual("ziwei-scope-a-production-pipeline-v1",base["pipeline_id"])
        self.assertEqual("ziwei-scope-a-brightness-production-pipeline-v1",bright["pipeline_id"])

    def test_legacy_gregorian_adapters_preserve_legacy_surface(self):
        base=run_scope_a_gregorian(self.gregorian,request_id="legacy-g")
        bright=run_scope_a_gregorian_with_brightness(self.gregorian,request_id="legacy-gb")
        for r in (base,bright):
            self.assertNotIn("schema_name",r)
            self.assertNotIn("runtime",r)
            self.assertEqual("ziwei-gregorian-input-adapter-v1",r["input_adapter"]["pipeline_id"])
        self.assertEqual("ziwei-scope-a-production-pipeline-v1",base["pipeline_id"])
        self.assertEqual("ziwei-scope-a-brightness-production-pipeline-v1",bright["pipeline_id"])

if __name__=="__main__":
    unittest.main()
