import os
import json
from typing import Any, Dict

from constants import APPROACHES, QUERIES, RESULTS_FILE


def check_data_match(data1: Any, data2: Any) -> bool:
    if type(data1) != type(data2):
        return False
    if isinstance(data1, dict):
        if data1.keys() != data2.keys():
            return False
        for k in data1:
            if not check_data_match(data1[k], data2[k]):
                return False
        return True
    elif isinstance(data1, list):
        try:
            return sorted(data1) == sorted(data2)
        except Exception:
            return data1 == data2
    return data1 == data2


def validate_results() -> None:
    if not os.path.exists(RESULTS_FILE):
        print(f"No {RESULTS_FILE} found for validation.")
        return

    with open(RESULTS_FILE, "r") as f:
        results: Dict[str, Any] = json.load(f)

    # Check if all 3 ran
    for app in APPROACHES:
        if app not in results:
            print(f"Validation failed: {app} results not found.")
            return

    all_match: bool = True

    print("\n--- Validating Results ---")
    for q in QUERIES:
        base_app: str = APPROACHES[0]
        base_data: Any = results[base_app].get(q, {}).get("data")

        for app in APPROACHES[1:]:
            app_data: Any = results[app].get(q, {}).get("data")

            if not check_data_match(base_data, app_data):
                print(f"Mismatch found in {q} between {base_app} and {app}")
                all_match = False

    if all_match:
        print(
            "Validation successful: All 3 benchmarks returned exactly the same values."
        )
    else:
        print("Validation failed: Mismatches found between benchmark results.")
