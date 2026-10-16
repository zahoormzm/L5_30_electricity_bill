"""Regression checks for billing, safe parsing and meter synchronisation."""

import contextlib
import importlib
import inspect
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from xml.etree.ElementTree import ParseError

from defusedxml.common import DTDForbidden

import electricity_bill as billing


class BillingTests(unittest.TestCase):
    """Verify preserved calculations and intentional security changes."""

    def setUp(self):
        billing.bills.clear()

    def tearDown(self):
        billing.bills.clear()

    def test_sample_xml(self):
        self.assertEqual(billing.read_meters(billing.METER_XML), [
            ("M1", 1200, 1350), ("M2", 5000, 5420), ("M3", 800, 760)
        ])

    def test_rejects_entity_declaration(self):
        xml = ('<!DOCTYPE meters [<!ENTITY injected "999">]>'
               '<meters><meter id="M" prev="0" curr="&injected;"/>'
               '</meters>')
        with self.assertRaises(DTDForbidden):
            billing.read_meters(xml)

    def test_rejects_external_dtd(self):
        xml = '<!DOCTYPE meters SYSTEM "file:///not-read"><meters/>'
        with self.assertRaises(DTDForbidden):
            billing.read_meters(xml)

    def test_malformed_xml(self):
        with self.assertRaises(ParseError):
            billing.read_meters('<meters>')

    def test_non_integer_reading(self):
        with self.assertRaises(ValueError):
            billing.read_meters(
                '<meters><meter id="M" prev="0" curr="bad"/></meters>'
            )

    def test_units_and_reversed_readings(self):
        self.assertEqual(billing.calculate_units(1200, 1350), 150)
        self.assertEqual(billing.calculate_units(100, 100), 0)
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(billing.calculate_units(800, 760), 0)
        self.assertEqual(output.getvalue(),
                         'Warning: meter reading went backwards\n')

    def test_tariff_boundaries(self):
        cases = [(0, 0), (99, 346.5), (100, 350), (101, 355),
                 (199, 845), (200, 850), (201, 856.5),
                 (299, 1493.5), (300, 1500), (301, 1508), (420, 2460)]
        for units, expected in cases:
            with self.subTest(units=units):
                self.assertEqual(billing.energy_charge(units), expected)

    def test_extra_fees_tax_and_storage(self):
        extras = {"late_fee": 25}
        result = billing.generate_bill("M4", 50, extras=extras)
        self.assertEqual(result,
                         {"meter": "M4", "units": 50, "amount": 288.75})
        self.assertEqual(billing.bills, [result])
        self.assertEqual(extras, {"late_fee": 25})
        self.assertEqual(billing.generate_bill("M5", 50)["amount"], 262.5)
        self.assertEqual(
            billing.generate_bill("M6", 50, tax_rate=0)["amount"], 250
        )
        self.assertIsNone(
            inspect.signature(billing.generate_bill)
            .parameters["extras"].default
        )

    def test_average_empty_and_populated(self):
        self.assertEqual(billing.average_bill(), 0)
        billing.generate_bill("M1", 150)
        billing.generate_bill("M2", 420)
        self.assertEqual(billing.average_bill(), 1685.25)

    def test_json_output(self):
        billing.generate_bill("Meter-\u20b9", 150)
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "bills.json"
            billing.save_bills(target)
            self.assertEqual(json.loads(target.read_text(encoding="utf-8")),
                             billing.bills)

    def test_import_has_no_demo_side_effects(self):
        with patch("builtins.open") as open_file:
            with patch("builtins.print") as print_line:
                importlib.reload(billing)
        open_file.assert_not_called()
        print_line.assert_not_called()
        self.assertEqual(billing.bills, [])

    def test_sync_uses_fixed_path_timeout_and_closes(self):
        for address in ("192.0.2.1", "2001:db8::1"):
            with self.subTest(address=address):
                with patch.object(billing.http.client,
                                  "HTTPConnection") as factory:
                    connection = factory.return_value
                    response = connection.getresponse.return_value
                    response.status = 200
                    response.read.return_value = b"1350"
                    self.assertEqual(billing.sync_meter(address), "1350")
                    factory.assert_called_once_with(address, timeout=5)
                    connection.request.assert_called_once_with(
                        "GET", "/reading"
                    )
                    connection.close.assert_called_once_with()

    def test_sync_rejects_non_ip_input_before_connecting(self):
        for address in ("192.0.2.1;echo injected", "example.com",
                        "http://192.0.2.1", "192.0.2.1/reading", ""):
            with self.subTest(address=address):
                with patch.object(billing.http.client,
                                  "HTTPConnection") as factory:
                    with self.assertRaises(ValueError):
                        billing.sync_meter(address)
                    factory.assert_not_called()

    def test_sync_closes_on_http_error(self):
        with patch.object(billing.http.client, "HTTPConnection") as factory:
            connection = factory.return_value
            connection.getresponse.return_value.status = 503
            with self.assertRaisesRegex(OSError, "503"):
                billing.sync_meter("192.0.2.1")
            connection.close.assert_called_once_with()

    def test_sync_closes_on_timeout(self):
        with patch.object(billing.http.client, "HTTPConnection") as factory:
            connection = factory.return_value
            connection.request.side_effect = TimeoutError("timed out")
            with self.assertRaises(TimeoutError):
                billing.sync_meter("192.0.2.1")
            connection.close.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
