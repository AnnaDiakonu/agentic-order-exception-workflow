"""Check that the readable demo output never overclaims a decision."""

import unittest

from order_exception.__main__ import format_case
from order_exception.eligibility import check_eligibility


def event(**changes):
    result = {
        "block_event_id": "EVT-001", "order_id": "ORD-001",
        "customer_id": "CUST-001", "block_reason": "credit_limit_exceeded",
        "order_value": 120000, "currency": "EUR", "hard_stop_flag": False,
    }
    result.update(changes)
    return result


def render(**changes):
    data = event(**changes)
    return format_case(data, check_eligibility(data))


class DemoOutputTests(unittest.TestCase):
    def test_eligible_order_is_admitted_not_approved(self):
        text = render()
        self.assertIn("ADMITTED FOR ANALYSIS", text)
        self.assertIn("not an approval", text)
        self.assertNotIn("APPROVE ", text)

    def test_hard_stop_is_shown_as_failed_check(self):
        text = render(hard_stop_flag=True)
        self.assertIn("[x] no hard stop", text)
        self.assertIn("MANUAL REVIEW", text)

    def test_unknown_hard_stop_is_reported_as_invalid_input(self):
        text = render(hard_stop_flag=None)
        self.assertIn("INPUT INVALID", text)
        self.assertIn("Unknown is never treated as 'no'", text)

    def test_invalid_value_is_displayed_without_crashing(self):
        text = render(order_value="120000")
        self.assertIn("unknown ('120000')", text)
        self.assertIn("INPUT INVALID", text)


if __name__ == "__main__":
    unittest.main()
