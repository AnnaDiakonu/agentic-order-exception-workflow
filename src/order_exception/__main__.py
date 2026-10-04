"""Show the eligibility gate using synthetic events only."""

import json
from dataclasses import asdict
from pathlib import Path

from .eligibility import check_eligibility


def main() -> None:
    project_root = Path(__file__).resolve().parents[2]
    events = json.loads((project_root / "data" / "blocked_orders.json").read_text())
    for event in events:
        result = check_eligibility(event)
        print(json.dumps({
            "order_id": event.get("order_id"),
            "eligibility": asdict(result),
        }, indent=2))


if __name__ == "__main__":
    main()
