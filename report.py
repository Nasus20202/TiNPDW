import os
import json
from tabulate import tabulate
from typing import Any, Dict, List

from constants import (
    RESULTS_FILE,
    RESULTS_MD,
    OUTPUTS_DIR,
    TASKS,
    QUERIES,
    QUERY_LABELS,
)


def generate_report() -> None:
    if not os.path.exists(RESULTS_FILE):
        print(f"No {RESULTS_FILE} found to generate report.")
        return

    with open(RESULTS_FILE, "r") as f:
        results: Dict[str, Any] = json.load(f)

    report: str = "# Results\n\n"

    # 1. Performance Comparison
    report += "## Performance Comparison (seconds)\n\n"

    approaches: List[str] = list(results.keys())

    perf_table: List[List[str]] = []
    headers: List[str] = ["Task"] + [
        app.replace("_", " ").title() for app in approaches
    ]

    for task in TASKS:
        row: List[str] = [task.replace("_", " ").title()]
        has_data: bool = False
        for app in approaches:
            val: Any = results[app].get(task, {}).get("time", "N/A")
            if val != "N/A":
                has_data = True
                row.append(f"{val:.2f}")
            else:
                row.append("-")
        if has_data:
            perf_table.append(row)

    report += tabulate(perf_table, headers=headers, tablefmt="github")
    report += "\n\n"

    # 2. Query Results (Data)
    report += "## Query Results\n\n"

    for q in QUERIES:
        report += f"### {q.upper()}: {QUERY_LABELS[q]}\n\n"
        # Just use the first approach that has data for this query to show values
        found: bool = False
        for app in approaches:
            data: Any = results[app].get(q, {}).get("data")
            if data:
                if isinstance(data, dict):
                    # For Q2, Q3, Q4 which are grouped by something else
                    for key, values in data.items():
                        report += f"**{key}**\n\n"
                        report += tabulate(
                            values, headers=["Type", "Count"], tablefmt="github"
                        )
                        report += "\n\n"
                else:
                    # For Q1, Q5 which are simple lists
                    report += tabulate(
                        data, headers=["Type", "Count"], tablefmt="github"
                    )
                    report += "\n\n"
                found = True
                break
        if not found:
            report += "No data collected for this query.\n\n"

    # 3. Visualizations
    report += "## Visualizations\n\n"
    if os.path.exists(OUTPUTS_DIR):
        files: List[str] = sorted(os.listdir(OUTPUTS_DIR))
        for file in files:
            if file.endswith(".png"):
                name: str = file.replace(".png", "").replace("_", " ").title()
                report += f"### {name}\n"
                report += f"![{name}]({OUTPUTS_DIR}/{file})\n\n"

    with open(RESULTS_MD, "w") as f:
        f.write(report)
    print(f"{RESULTS_MD} generated.")
