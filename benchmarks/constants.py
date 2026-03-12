# File Paths
RESULTS_FILE: str = "results.json"
OUTPUTS_DIR: str = "outputs"
DATA_FILE: str = "data.csv"

# Postgres
POSTGRES_CONN_STR: str = "postgresql://user:password@localhost:5432/nypd_data"
POSTGRES_CHUNK_SIZE: int = 200000

# Spark Configuration
SPARK_DRIVER_MEMORY: str = "4g"
SPARK_EXECUTOR_MEMORY: str = "4g"
SPARK_WORKER_MEMORY: str = "2g"

# Spark RDD Column Indices
COL_OFNS: int = 8
COL_BORO: int = 13
COL_JURIS: int = 16
COL_PREM: int = 15
COL_VIC_AGE: int = 32
