"""Show the eligibility gate on synthetic events.

Default output is a readable case summary. Use --json for raw results.
The gate only decides whether an order may enter analysis. It never approves,
releases or declines an order.
"""

import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any, Mapping

from .eligibility import EligibilityResult, check_eligibility


# Each business check and the reason code it produces when it does not pass.
CHECKS = (
    ("credit block", "non_credit_block"),
    ("value EUR 50k-250k", "order_value_outside_pilot_range"),
    ("no hard stop", "hard_stop_present"),
)

EXPLANATIONS = {
    "non_credit_block": "The block is not credit-related, so it is outside this workflow.",
    "order_value_outside_pilot_range": "The order value is outside the pilot range of EUR 50k-250k.",
    "hard_stop_present": "A hard stop is set. It must be investigated, never bypassed.",
    "missing_or_invalid_hard_stop_flag": "Hard-stop status is unknown. Unknown is never treated as 'no'.",
    "missing_or_invalid_order_value": "Order value is missing or not a number.",
    "invalid_order_value": "Order value is negative or not finite.",
    "unsupported_or_missing_currency": "Currency is not EUR. No silent conversion is done.",
}

VERDICTS = {
    "collect_context": "ADMITTED FOR ANALYSIS",
    "manual_review": "MANUAL REVIEW",
}


def format_value(event: Mapping[str, Any]) -> str:
    value = event.get("order_value")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return "{} {:,.0f}".format(event.get("currency"), value)
    return "unknown ({!r})".format(value)


def format_hard_stop(value: Any) -> str:
    if value is True:
        return "yes"
    if value is False:
        return "no"
    return "unknown ({})".format(json.dumps(value))


def explain(code: str) -> str:
    if code.startswith("missing_or_invalid_"):
        default = "Required field '{}' is missing or invalid.".format(
            code[len("missing_or_invalid_"):])
    else:
        default = code
    return EXPLANATIONS.get(code, default)


def format_case(event: Mapping[str, Any], result: EligibilityResult) -> str:
    lines = [
        "Order {}  |  customer {}".format(event.get("order_id"), event.get("customer_id")),
        "  Block reason : {}".format(event.get("block_reason")),
        "  Order value  : {}".format(format_value(event)),
        "  Hard stop    : {}".format(format_hard_stop(event.get("hard_stop_flag"))),
    ]

    if result.status == "failed":
        lines.append("  Checks       : not run - input validation failed")
        verdict = "INPUT INVALID -> " + VERDICTS[result.next_route]
    else:
        marks = ["[{}] {}".format("x" if code in result.reasons else "ok", label)
                 for label, code in CHECKS]
        lines.append("  Checks       : " + "   ".join(marks))
        verdict = VERDICTS[result.next_route]

    lines.append("  Result       : {}  (next step: {})".format(verdict, result.next_route))
    if result.eligible:
        lines.append("  Why          : All three entry conditions pass. "
                     "This is not an approval; a human reviews every case.")
    else:
        for code in result.reasons:
            lines.append("  Why          : " + explain(code))
    return "\n".join(lines)


def main() -> None:
    project_root = Path(__file__).resolve().parents[2]
    events = json.loads((project_root / "data" / "blocked_orders.json").read_text())
    results = [(event, check_eligibility(event)) for event in events]

    if "--json" in sys.argv[1:]:
        print(json.dumps([
            {"order_id": event.get("order_id"), "eligibility": asdict(result)}
            for event, result in results
        ], indent=2))
        return

    print("Eligibility gate - {} synthetic blocked orders\n".format(len(results)))
    print("\n\n".join(format_case(event, result) for event, result in results))


if __name__ == "__main__":
    main()
