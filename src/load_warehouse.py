from __future__ import annotations

import duckdb

from .config import DIM_CUSTOMER_FILE, DIM_DATE_FILE, DIM_PRODUCT_FILE, DUCKDB_FILE, FACT_SALES_FILE
from .logger import get_logger

logger = get_logger(__name__)


def load_warehouse() -> None:
    logger.info("Loading warehouse CSVs into DuckDB at %s", DUCKDB_FILE)
    con = duckdb.connect(str(DUCKDB_FILE))

    con.execute(
        f"""
        CREATE OR REPLACE TABLE dim_product AS
        SELECT * FROM read_csv_auto('{DIM_PRODUCT_FILE.as_posix()}', HEADER=TRUE);
        """
    )
    con.execute(
        f"""
        CREATE OR REPLACE TABLE dim_customer AS
        SELECT * FROM read_csv_auto('{DIM_CUSTOMER_FILE.as_posix()}', HEADER=TRUE);
        """
    )
    con.execute(
        f"""
        CREATE OR REPLACE TABLE dim_date AS
        SELECT * FROM read_csv_auto('{DIM_DATE_FILE.as_posix()}', HEADER=TRUE);
        """
    )
    con.execute(
        f"""
        CREATE OR REPLACE TABLE fact_sales AS
        SELECT * FROM read_csv_auto('{FACT_SALES_FILE.as_posix()}', HEADER=TRUE);
        """
    )

    table_counts = con.execute(
        """
        SELECT 'dim_product' AS table_name, COUNT(*) AS row_count FROM dim_product
        UNION ALL
        SELECT 'dim_customer' AS table_name, COUNT(*) AS row_count FROM dim_customer
        UNION ALL
        SELECT 'dim_date' AS table_name, COUNT(*) AS row_count FROM dim_date
        UNION ALL
        SELECT 'fact_sales' AS table_name, COUNT(*) AS row_count FROM fact_sales
        """
    ).fetchdf()
    logger.info("Warehouse load complete\n%s", table_counts.to_string(index=False))
    con.close()


if __name__ == "__main__":
    load_warehouse()
