"""Validate the trigger and check whether an order can enter the POC workflow."""

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Mapping, Optional, Tuple


CREDIT_BLOCK_REASONS = frozenset({
    "credit_limit_exceeded", "credit_exposure_exceeded",
})
MIN_ORDER_VALUE = Decimal("50000")
MAX_ORDER_VALUE = Decimal("250000")


@dataclass(frozen=True)
class EligibilityResult:
    # eligible=None means the check could not be completed.
    status: str
    eligible: Optional[bool]
    reasons: Tuple[str, ...]
    next_route: str


def check_eligibility(event: Mapping[str, Any]) -> EligibilityResult:
    """Require a credit block, EUR value in range, and explicitly clear hard stop.

    Missing or malformed inputs fail validation. They must never be treated as
    a successfully checked ineligible order, or as an approval.
    """
    errors = []
    for field in ("block_event_id", "order_id", "customer_id", "block_reason"):
        value = event.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append("missing_or_invalid_" + field)

    if event.get("currency") != "EUR":
        errors.append("unsupported_or_missing_currency")

    raw_amount = event.get("order_value")
    amount = None
    # bool is a subclass of int, so reject it explicitly.
    if isinstance(raw_amount, bool) or not isinstance(raw_amount, (int, float)):
        errors.append("missing_or_invalid_order_value")
    else:
        amount = Decimal(str(raw_amount))
        if not amount.is_finite() or amount < 0:
            errors.append("invalid_order_value")

    hard_stop = event.get("hard_stop_flag")
    if not isinstance(hard_stop, bool):
        errors.append("missing_or_invalid_hard_stop_flag")

    if errors:
        return EligibilityResult("failed", None, tuple(errors), "manual_review")

    failed_checks = []
    if event["block_reason"] not in CREDIT_BLOCK_REASONS:
        failed_checks.append("non_credit_block")
    if not MIN_ORDER_VALUE <= amount <= MAX_ORDER_VALUE:
        failed_checks.append("order_value_outside_pilot_range")
    if hard_stop:
        failed_checks.append("hard_stop_present")

    eligible = not failed_checks
    return EligibilityResult(
        "completed", eligible, tuple(failed_checks),
        "collect_context" if eligible else "manual_review",
    )
