from pyspark import SparkContext, SparkConf
import matplotlib.pyplot as plt
import csv
from typing import Any, Dict, List

from .constants import (
    DATA_FILE,
    OUTPUTS_DIR,
    SPARK_DRIVER_MEMORY,
    SPARK_EXECUTOR_MEMORY,
    SPARK_WORKER_MEMORY,
    COL_OFNS,
    COL_BORO,
    COL_JURIS,
    COL_PREM,
    COL_VIC_AGE,
)

from .utils import log_result, Timer

APPROACH: str = "spark_rdd"


def parse_csv(line: str) -> List[str]:
    reader = csv.reader([line])
    try:
        return next(reader)
    except StopIteration:
        return []


def load_data(sc: SparkContext) -> Any:
    with Timer() as t:
        raw_rdd = sc.textFile(DATA_FILE)
        header = raw_rdd.first()
        rdd = (
            raw_rdd.filter(lambda line: line != header)
            .map(parse_csv)
            .filter(lambda x: len(x) > COL_VIC_AGE)
        )  # Basic sanity check
        count = rdd.count()
    log_result(APPROACH, "load_and_cache", t.interval)
    return rdd


def query_1(rdd: Any) -> None:
    with Timer() as t:
        q1 = (
            rdd.map(lambda x: (x[COL_OFNS], 1))
            .reduceByKey(lambda a, b: a + b)
            .takeOrdered(10, key=lambda x: -x[1])
        )
    log_result(APPROACH, "q1", t.interval, q1)


def query_2(rdd: Any) -> None:
    with Timer() as t:
        boroughs = (
            rdd.map(lambda x: x[COL_BORO])
            .distinct()
            .filter(lambda x: x and x != "(null)")
            .collect()
        )
        results: Dict[str, Any] = {}
        for boro in boroughs:
            q2_boro = (
                rdd.filter(lambda x: x[COL_BORO] == boro)
                .map(lambda x: (x[COL_OFNS], 1))
                .reduceByKey(lambda a, b: a + b)
                .takeOrdered(3, key=lambda x: -x[1])
            )
            results[boro] = q2_boro
    log_result(APPROACH, "q2", t.interval, results)


def query_3(rdd: Any) -> None:
    with Timer() as t:
        top_agencies = (
            rdd.map(lambda x: (x[COL_JURIS], 1))
            .reduceByKey(lambda a, b: a + b)
            .takeOrdered(3, key=lambda x: -x[1])
        )
        agency_list = [x[0] for x in top_agencies]
        results: Dict[str, Any] = {}
        for agency in agency_list:
            q3_agency = (
                rdd.filter(lambda x: x[COL_JURIS] == agency)
                .map(lambda x: (x[COL_OFNS], 1))
                .reduceByKey(lambda a, b: a + b)
                .takeOrdered(3, key=lambda x: -x[1])
            )
            results[agency] = q3_agency
    log_result(APPROACH, "q3", t.interval, results)


def query_4(rdd: Any) -> None:
    with Timer() as t:
        top_locations = (
            rdd.map(lambda x: (x[COL_PREM], 1))
            .reduceByKey(lambda a, b: a + b)
            .takeOrdered(4, key=lambda x: -x[1])
        )
        location_list = [x[0] for x in top_locations]
        results: Dict[str, Any] = {}
        for loc in location_list:
            q4_loc = (
                rdd.filter(lambda x: x[COL_PREM] == loc)
                .map(lambda x: (x[COL_OFNS], 1))
                .reduceByKey(lambda a, b: a + b)
                .takeOrdered(3, key=lambda x: -x[1])
            )
            results[loc] = q4_loc
    log_result(APPROACH, "q4", t.interval, results)


def query_5(rdd: Any) -> None:
    with Timer() as t:
        q5 = (
            rdd.map(lambda x: (x[COL_VIC_AGE], 1))
            .reduceByKey(lambda a, b: a + b)
            .collect()
        )
        q5_sorted = sorted(q5, key=lambda x: -x[1])
    log_result(APPROACH, "q5", t.interval, q5_sorted)

    # Pie chart
    labels = [str(x[0]) for x in q5_sorted if x[0] and x[0] != "(null)"]
    sizes = [x[1] for x in q5_sorted if x[0] and x[0] != "(null)"]
    plt.figure(figsize=(10, 7))
    plt.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=140)
    plt.title("Victim Age Group Distribution (Spark RDD)")
    plt.savefig(f"{OUTPUTS_DIR}/spark_rdd_q5.png")


def run() -> None:
    # Increase memory to avoid worker crashes
    conf = (
        SparkConf()
        .setAppName("NYPD Benchmarking - RDD")
        .set("spark.driver.memory", SPARK_DRIVER_MEMORY)
        .set("spark.executor.memory", SPARK_EXECUTOR_MEMORY)
        .set("spark.python.worker.memory", SPARK_WORKER_MEMORY)
    )
    sc = SparkContext(conf=conf)
    try:
        rdd = load_data(sc)
        query_1(rdd)
        query_2(rdd)
        query_3(rdd)
        query_4(rdd)
        query_5(rdd)
    finally:
        sc.stop()


if __name__ == "__main__":
    run()
