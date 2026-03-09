from pathlib import Path

# Base project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Data directories
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"

# Input files
PRODUCTS_FILE = RAW_DATA_DIR / "products.csv"
CUSTOMERS_FILE = RAW_DATA_DIR / "customers.csv"
ORDERS_FILE = RAW_DATA_DIR / "orders.csv"

# Output files
CLEANED_ORDERS_FILE = PROCESSED_DATA_DIR / "cleaned_orders.csv"