from pyspark.sql import SparkSession
import matplotlib.pyplot as plt
from typing import Any, Dict, List

from .constants import (
    DATA_FILE,
    OUTPUTS_DIR,
    SPARK_DRIVER_MEMORY,
    SPARK_EXECUTOR_MEMORY,
)

from .utils import log_result, Timer

APPROACH: str = "spark_sql"


def get_spark() -> SparkSession:
    return (
        SparkSession.builder.appName("NYPD Benchmarking - SQL")
        .config("spark.driver.memory", SPARK_DRIVER_MEMORY)
        .config("spark.executor.memory", SPARK_EXECUTOR_MEMORY)
        .getOrCreate()
    )


def load_data(spark: SparkSession) -> None:
    with Timer() as t:
        df = spark.read.csv(DATA_FILE, header=True)
        # We don't cache to be fair/avoid OOM on this limited env
        df = df.select(
            "OFNS_DESC", "BORO_NM", "JURIS_DESC", "PREM_TYP_DESC", "VIC_AGE_GROUP"
        )
        df.createOrReplaceTempView("complaints")
        count = spark.sql("SELECT count(*) FROM complaints").collect()[0][0]
    log_result(APPROACH, "load_and_cache", t.interval)


def query_1(spark: SparkSession) -> None:
    with Timer() as t:
        res = spark.sql(
            """
            SELECT OFNS_DESC, count(*) as count 
            FROM complaints 
            GROUP BY OFNS_DESC 
            ORDER BY count DESC 
            LIMIT 10
        """
        ).collect()
        # Standardize result: list of [key, value]
        data: List[List[Any]] = [[row[0], row[1]] for row in res]
    log_result(APPROACH, "q1", t.interval, data)


def query_2(spark: SparkSession) -> None:
    with Timer() as t:
        boroughs = spark.sql(
            'SELECT DISTINCT BORO_NM FROM complaints WHERE BORO_NM IS NOT NULL AND BORO_NM != "(null)"'
        ).collect()
        data: Dict[str, List[List[Any]]] = {}
        for boro_row in boroughs:
            boro = boro_row.BORO_NM
            res = spark.sql(
                f"""
                SELECT OFNS_DESC, count(*) as count 
                FROM complaints 
                WHERE BORO_NM = '{boro}'
                GROUP BY OFNS_DESC 
                ORDER BY count DESC 
                LIMIT 3
            """
            ).collect()
            data[boro] = [[row[0], row[1]] for row in res]
    log_result(APPROACH, "q2", t.interval, data)


def query_3(spark: SparkSession) -> None:
    with Timer() as t:
        agencies = spark.sql(
            """
            SELECT JURIS_DESC, count(*) as count 
            FROM complaints 
            GROUP BY JURIS_DESC 
            ORDER BY count DESC 
            LIMIT 3
        """
        ).collect()
        data: Dict[str, List[List[Any]]] = {}
        for agency_row in agencies:
            agency = agency_row.JURIS_DESC
            res = spark.sql(
                f"""
                SELECT OFNS_DESC, count(*) as count 
                FROM complaints 
                WHERE JURIS_DESC = '{agency}'
                GROUP BY OFNS_DESC 
                ORDER BY count DESC 
                LIMIT 3
            """
            ).collect()
            data[agency] = [[row[0], row[1]] for row in res]
    log_result(APPROACH, "q3", t.interval, data)


def query_4(spark: SparkSession) -> None:
    with Timer() as t:
        locations = spark.sql(
            """
            SELECT PREM_TYP_DESC, count(*) as count 
            FROM complaints 
            GROUP BY PREM_TYP_DESC 
            ORDER BY count DESC 
            LIMIT 4
        """
        ).collect()
        data: Dict[str, List[List[Any]]] = {}
        for loc_row in locations:
            loc = loc_row.PREM_TYP_DESC
            loc_escaped = loc.replace("'", "''") if loc else ""
            res = spark.sql(
                f"""
                SELECT OFNS_DESC, count(*) as count 
                FROM complaints 
                WHERE PREM_TYP_DESC = '{loc_escaped}'
                GROUP BY OFNS_DESC 
                ORDER BY count DESC 
                LIMIT 3
            """
            ).collect()
            data[loc] = [[row[0], row[1]] for row in res]
    log_result(APPROACH, "q4", t.interval, data)


def query_5(spark: SparkSession) -> None:
    with Timer() as t:
        res = spark.sql(
            """
            SELECT VIC_AGE_GROUP, count(*) as count 
            FROM complaints 
            GROUP BY VIC_AGE_GROUP 
            ORDER BY count DESC
        """
        ).collect()
        data: List[List[Any]] = [[row[0], row[1]] for row in res]
    log_result(APPROACH, "q5", t.interval, data)

    labels = [str(x[0]) for x in data if x[0] and x[0] != "(null)"]
    sizes = [x[1] for x in data if x[0] and x[0] != "(null)"]
    plt.figure(figsize=(10, 7))
    plt.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=140)
    plt.title("Victim Age Group Distribution (Spark SQL)")
    plt.savefig(f"{OUTPUTS_DIR}/spark_sql_q5.png")


def run() -> None:
    spark = get_spark()
    try:
        load_data(spark)
        query_1(spark)
        query_2(spark)
        query_3(spark)
        query_4(spark)
        query_5(spark)
    finally:
        spark.stop()


if __name__ == "__main__":
    run()
