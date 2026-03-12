import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from typing import Any, Dict, List

from .constants import DATA_FILE, OUTPUTS_DIR, POSTGRES_CONN_STR, POSTGRES_CHUNK_SIZE

from .utils import log_result, Timer

APPROACH: str = "postgres"


def get_connection() -> Any:
    return psycopg2.connect(POSTGRES_CONN_STR)


def load_data() -> None:
    engine = create_engine(POSTGRES_CONN_STR)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS complaints")
    conn.commit()

    print("Loading data into PostgreSQL...")
    cols: List[str] = [
        "OFNS_DESC",
        "BORO_NM",
        "JURIS_DESC",
        "PREM_TYP_DESC",
        "VIC_AGE_GROUP",
    ]

    with Timer() as t:
        first: bool = True
        for chunk in pd.read_csv(
            DATA_FILE, usecols=cols, chunksize=POSTGRES_CHUNK_SIZE, low_memory=False
        ):
            # Using to_sql is okay, but for massive data COPY is better.
            # Given the constraints, we'll stick to this but ensure it's efficient.
            chunk.to_sql(
                "complaints",
                engine,
                if_exists="replace" if first else "append",
                index=False,
            )
            first = False

        print("Creating indexes...")
        cursor.execute('CREATE INDEX idx_boro ON complaints("BORO_NM")')
        cursor.execute('CREATE INDEX idx_juris ON complaints("JURIS_DESC")')
        cursor.execute('CREATE INDEX idx_prem ON complaints("PREM_TYP_DESC")')
        cursor.execute('CREATE INDEX idx_ofns ON complaints("OFNS_DESC")')
        conn.commit()

    log_result(APPROACH, "load_and_convert", t.interval)
    cursor.close()
    conn.close()


def query_1() -> None:
    conn = get_connection()
    cursor = conn.cursor()
    with Timer() as t:
        cursor.execute(
            'SELECT "OFNS_DESC", count(*) as count FROM complaints GROUP BY "OFNS_DESC" ORDER BY count DESC LIMIT 10'
        )
        res = cursor.fetchall()
        data: List[List[Any]] = [[row[0], row[1]] for row in res]
    log_result(APPROACH, "q1", t.interval, data)
    cursor.close()
    conn.close()


def query_2() -> None:
    conn = get_connection()
    cursor = conn.cursor()
    with Timer() as t:
        cursor.execute(
            'SELECT DISTINCT "BORO_NM" FROM complaints WHERE "BORO_NM" IS NOT NULL AND "BORO_NM" != \'(null)\''
        )
        boroughs: List[str] = [row[0] for row in cursor.fetchall()]
        data: Dict[str, List[List[Any]]] = {}
        for boro in boroughs:
            cursor.execute(
                'SELECT "OFNS_DESC", count(*) as count FROM complaints WHERE "BORO_NM" = %s GROUP BY "OFNS_DESC" ORDER BY count DESC LIMIT 3',
                (boro,),
            )
            res = cursor.fetchall()
            data[boro] = [[row[0], row[1]] for row in res]
    log_result(APPROACH, "q2", t.interval, data)
    cursor.close()
    conn.close()


def query_3() -> None:
    conn = get_connection()
    cursor = conn.cursor()
    with Timer() as t:
        cursor.execute(
            'SELECT "JURIS_DESC", count(*) as count FROM complaints GROUP BY "JURIS_DESC" ORDER BY count DESC LIMIT 3'
        )
        agencies: List[str] = [row[0] for row in cursor.fetchall()]
        data: Dict[str, List[List[Any]]] = {}
        for agency in agencies:
            cursor.execute(
                'SELECT "OFNS_DESC", count(*) as count FROM complaints WHERE "JURIS_DESC" = %s GROUP BY "OFNS_DESC" ORDER BY count DESC LIMIT 3',
                (agency,),
            )
            res = cursor.fetchall()
            data[agency] = [[row[0], row[1]] for row in res]
    log_result(APPROACH, "q3", t.interval, data)
    cursor.close()
    conn.close()


def query_4() -> None:
    conn = get_connection()
    cursor = conn.cursor()
    with Timer() as t:
        cursor.execute(
            'SELECT "PREM_TYP_DESC", count(*) as count FROM complaints GROUP BY "PREM_TYP_DESC" ORDER BY count DESC LIMIT 4'
        )
        locations: List[str] = [row[0] for row in cursor.fetchall()]
        data: Dict[str, List[List[Any]]] = {}
        for loc in locations:
            cursor.execute(
                'SELECT "OFNS_DESC", count(*) as count FROM complaints WHERE "PREM_TYP_DESC" = %s GROUP BY "OFNS_DESC" ORDER BY count DESC LIMIT 3',
                (loc,),
            )
            res = cursor.fetchall()
            data[loc] = [[row[0], row[1]] for row in res]
    log_result(APPROACH, "q4", t.interval, data)
    cursor.close()
    conn.close()


def query_5() -> None:
    conn = get_connection()
    cursor = conn.cursor()
    with Timer() as t:
        cursor.execute(
            'SELECT "VIC_AGE_GROUP", count(*) as count FROM complaints GROUP BY "VIC_AGE_GROUP" ORDER BY count DESC'
        )
        res = cursor.fetchall()
        data: List[List[Any]] = [[row[0], row[1]] for row in res]
    log_result(APPROACH, "q5", t.interval, data)

    labels = [str(x[0]) for x in data if x[0] and x[0] != "(null)"]
    sizes = [x[1] for x in data if x[0] and x[0] != "(null)"]
    plt.figure(figsize=(10, 7))
    plt.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=140)
    plt.title("Victim Age Group Distribution (PostgreSQL)")
    plt.savefig(f"{OUTPUTS_DIR}/postgres_q5.png")

    cursor.close()
    conn.close()


def run() -> None:
    load_data()
    query_1()
    query_2()
    query_3()
    query_4()
    query_5()


if __name__ == "__main__":
    run()
