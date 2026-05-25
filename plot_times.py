import json
from pathlib import Path

import matplotlib.pyplot as plt

from constants import OUTPUTS_DIR, RESULTS_FILE

APPROACHES = ["spark_rdd", "spark_sql", "postgres"]
APPROACH_LABELS = {
    "spark_rdd": "Spark RDD",
    "spark_sql": "Spark SQL",
    "postgres": "PostgreSQL",
}
TASKS = ["q1", "q2", "q3", "q4", "q5"]
TASK_LABELS = ["Q1", "Q2", "Q3", "Q4", "Q5"]
COLORS = {
    "spark_rdd": "#4C78A8",
    "spark_sql": "#F58518",
    "postgres": "#54A24B",
}


def main() -> None:
    results_path = Path(RESULTS_FILE)
    output_path = Path(OUTPUTS_DIR) / "execution_times.png"

    with results_path.open("r") as file:
        results = json.load(file)

    x = range(len(TASKS))
    width = 0.24

    fig, ax = plt.subplots(figsize=(11, 5.5))

    for index, approach in enumerate(APPROACHES):
        times = [results[approach][task]["time"] for task in TASKS]
        offset = (index - 1) * width
        bars = ax.bar(
            [value + offset for value in x],
            times,
            width=width,
            label=APPROACH_LABELS[approach],
            color=COLORS[approach],
        )

        for bar, time_value in zip(bars, times):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.7,
                f"{time_value:.1f}",
                ha="center",
                va="bottom",
                fontsize=8,
            )

    ax.set_xticks(list(x), TASK_LABELS)
    ax.set_ylabel("Czas [s]")
    ax.set_title("Czasy wykonania zapytań")
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    ax.set_axisbelow(True)

    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
