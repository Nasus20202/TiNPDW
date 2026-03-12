from typing import Dict, List

# File Paths
RESULTS_FILE: str = "results.json"
RESULTS_MD: str = "RESULTS.md"
OUTPUTS_DIR: str = "outputs"

# Benchmarks
APPROACHES: List[str] = ["spark_rdd", "spark_sql", "postgres"]
TASKS: List[str] = ["load_and_cache", "load_and_convert", "q1", "q2", "q3", "q4", "q5"]
QUERIES: List[str] = ["q1", "q2", "q3", "q4", "q5"]

QUERY_LABELS: Dict[str, str] = {
    "q1": "10 most frequent offenses",
    "q2": "3 most frequent offenses per Borough",
    "q3": "3 most frequent agencies & their top 3 offenses",
    "q4": "4 most frequent locations & their top 3 offenses",
    "q5": "Victim age distribution",
}

# Docker
DOCKER_COMPOSE_UP: List[str] = ["docker", "compose", "up", "-d", "--wait"]
DOCKER_COMPOSE_DOWN: List[str] = ["docker", "compose", "down"]
