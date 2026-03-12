import time
import json
import os
from typing import Any, Dict, Optional

from .constants import RESULTS_FILE


def log_result(
    approach: str, query_name: str, execution_time: float, data: Optional[Any] = None
) -> None:
    results: Dict[str, Any] = {}
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, "r") as f:
            try:
                results = json.load(f)
            except json.JSONDecodeError:
                results = {}

    if approach not in results:
        results[approach] = {}

    entry: Dict[str, Any] = {"time": execution_time}
    if data is not None:
        entry["data"] = data

    results[approach][query_name] = entry

    with open(RESULTS_FILE, "w") as f:
        json.dump(results, f, indent=4)


class Timer:
    start: float
    end: float
    interval: float

    def __enter__(self) -> "Timer":
        self.start = time.time()
        return self

    def __exit__(self, *args: Any) -> None:
        self.end = time.time()
        self.interval = self.end - self.start
