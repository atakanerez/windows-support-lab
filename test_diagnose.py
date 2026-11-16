import json
from pathlib import Path
import unittest

from diagnose import diagnose

ROOT = Path(__file__).resolve().parent


def read(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


class DiagnosisTest(unittest.TestCase):
    def test_before_identifies_next_dns_check(self):
        self.assertEqual(diagnose(read("before.json"))[0], "check_client_dns")

    def test_after_restores_discovery_but_not_claim_signin(self):
        status, note = diagnose(read("after.json"))
        self.assertEqual(status, "discovery_restored")
        self.assertIn("verify user sign-in separately", note)

    def test_srv_failure_with_correct_dns(self):
        checks = {**read("before.json"), "client_dns_matches_lab": True}
        self.assertEqual(diagnose(checks)[0], "check_srv_resolution")

    def test_srv_success_with_discovery_failure(self):
        checks = {**read("after.json"), "domain_controller_discovery": False}
        self.assertEqual(diagnose(checks)[0], "check_dc_discovery")

    def test_invalid_input_is_rejected(self):
        for checks in [{}, {**read("before.json"), "dc_srv_resolves": "false"}]:
            with self.subTest(checks=checks), self.assertRaises(ValueError):
                diagnose(checks)
