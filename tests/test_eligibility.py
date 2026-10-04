"""Check business boundaries and unsafe/unknown input handling."""

import unittest

from order_exception.eligibility import check_eligibility


def event(**changes):
    result = {
        "block_event_id": "EVT-001", "order_id": "ORD-001",
        "customer_id": "CUST-001", "block_reason": "credit_limit_exceeded",
        "order_value": 120000, "currency": "EUR", "hard_stop_flag": False,
    }
    result.update(changes)
    return result


class EligibilityTests(unittest.TestCase):
    def test_both_credit_reasons_enter_context_collection(self):
        for reason in ("credit_limit_exceeded", "credit_exposure_exceeded"):
            with self.subTest(reason=reason):
                result = check_eligibility(event(block_reason=reason))
                self.assertEqual((result.status, result.eligible, result.next_route),
                                 ("completed", True, "collect_context"))

    def test_range_is_inclusive(self):
        for amount in (50000, 250000):
            with self.subTest(amount=amount):
                self.assertTrue(check_eligibility(event(order_value=amount)).eligible)

    def test_outside_range_is_completed_but_ineligible(self):
        for amount in (49999.99, 250000.01):
            with self.subTest(amount=amount):
                result = check_eligibility(event(order_value=amount))
                self.assertEqual((result.status, result.eligible), ("completed", False))
                self.assertIn("order_value_outside_pilot_range", result.reasons)

    def test_hard_stop_cannot_enter_collectors(self):
        result = check_eligibility(event(hard_stop_flag=True))
        self.assertFalse(result.eligible)
        self.assertEqual(result.next_route, "manual_review")
        self.assertIn("hard_stop_present", result.reasons)

    def test_unknown_or_coerced_hard_stop_is_not_clear(self):
        for value in (None, "false", 0):
            with self.subTest(value=value):
                result = check_eligibility(event(hard_stop_flag=value))
                self.assertEqual((result.status, result.eligible), ("failed", None))
                self.assertEqual(result.next_route, "manual_review")

    def test_non_credit_block_is_not_in_scope(self):
        result = check_eligibility(event(block_reason="inventory_shortage"))
        self.assertEqual((result.status, result.eligible), ("completed", False))

    def test_amount_must_be_known_finite_and_nonnegative(self):
        for value in (None, True, "120000", -1, float("nan"), float("inf")):
            with self.subTest(value=value):
                result = check_eligibility(event(order_value=value))
                self.assertEqual((result.status, result.eligible), ("failed", None))

    def test_currency_is_not_silently_converted(self):
        result = check_eligibility(event(currency="USD"))
        self.assertEqual(result.status, "failed")
        self.assertIn("unsupported_or_missing_currency", result.reasons)

    def test_required_identifiers_cannot_be_missing(self):
        for field in ("block_event_id", "order_id", "customer_id"):
            with self.subTest(field=field):
                data = event()
                del data[field]
                self.assertEqual(check_eligibility(data).status, "failed")

    def test_all_ineligibility_reasons_are_preserved(self):
        result = check_eligibility(event(block_reason="inventory_shortage",
                                         order_value=300000, hard_stop_flag=True))
        self.assertEqual(set(result.reasons), {
            "non_credit_block", "order_value_outside_pilot_range", "hard_stop_present",
        })

    def test_input_is_not_modified(self):
        data = event()
        before = dict(data)
        check_eligibility(data)
        self.assertEqual(data, before)


if __name__ == "__main__":
    unittest.main()
