import os
import subprocess
from typing import List

from benchmarks import spark_rdd, spark_sql, postgres
from validation import validate_results
from report import generate_report
from constants import RESULTS_FILE, OUTPUTS_DIR, DOCKER_COMPOSE_UP, DOCKER_COMPOSE_DOWN


def run_command(cmd: List[str]) -> None:
    print(f"Executing: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)


def main() -> None:
    if os.path.exists(RESULTS_FILE):
        validate_results()
        generate_report()
        print(
            f"{RESULTS_FILE} already exists. Please delete it before running a new benchmark."
        )
        return

    if not os.path.exists(OUTPUTS_DIR):
        os.makedirs(OUTPUTS_DIR)

    # We only start postgres if it's not already running or we want a fresh run
    print("Starting PostgreSQL container...")
    run_command(DOCKER_COMPOSE_UP)

    try:
        print("\n--- Running Spark RDD Benchmark ---")
        spark_rdd.run()

        print("\n--- Running Spark SQL Benchmark ---")
        spark_sql.run()

        print("\n--- Running PostgreSQL Benchmark ---")
        postgres.run()

        validate_results()
        generate_report()

    except Exception as e:
        print(f"An error occurred: {e}")
        # Even if it fails, try to generate report with what we have
        generate_report()
    finally:
        print("\nStopping PostgreSQL container...")
        run_command(DOCKER_COMPOSE_DOWN)


if __name__ == "__main__":
    main()
