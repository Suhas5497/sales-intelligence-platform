from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
WAREHOUSE_DIR = BASE_DIR / "warehouse"
REPORTS_DIR = BASE_DIR / "reports"
QUERY_OUTPUT_DIR = REPORTS_DIR / "query_outputs"
SQL_DIR = BASE_DIR / "sql"

PRODUCTS_FILE = RAW_DATA_DIR / "products.csv"
CUSTOMERS_FILE = RAW_DATA_DIR / "customers.csv"
ORDERS_FILE = RAW_DATA_DIR / "orders.csv"

CLEANED_ORDERS_FILE = PROCESSED_DATA_DIR / "cleaned_orders.csv"
PIPELINE_SUMMARY_FILE = REPORTS_DIR / "pipeline_summary.json"
VALIDATION_REPORT_FILE = REPORTS_DIR / "validation_checks.csv"
WAREHOUSE_SUMMARY_FILE = REPORTS_DIR / "warehouse_summary.csv"

DIM_PRODUCT_FILE = WAREHOUSE_DIR / "dim_product.csv"
DIM_CUSTOMER_FILE = WAREHOUSE_DIR / "dim_customer.csv"
DIM_DATE_FILE = WAREHOUSE_DIR / "dim_date.csv"
FACT_SALES_FILE = WAREHOUSE_DIR / "fact_sales.csv"
DUCKDB_FILE = WAREHOUSE_DIR / "sales.duckdb"

DEFAULT_RANDOM_SEED = 42
DEFAULT_NUM_PRODUCTS = 168
DEFAULT_NUM_CUSTOMERS = 25_000
DEFAULT_NUM_ORDERS = 300_000
DEFAULT_START_DATE = "2025-03-10"
DEFAULT_END_DATE = "2026-03-09"


def ensure_project_directories() -> None:
    for directory in [
        RAW_DATA_DIR,
        PROCESSED_DATA_DIR,
        WAREHOUSE_DIR,
        REPORTS_DIR,
        QUERY_OUTPUT_DIR,
        SQL_DIR,
    ]:
        directory.mkdir(parents=True, exist_ok=True)
