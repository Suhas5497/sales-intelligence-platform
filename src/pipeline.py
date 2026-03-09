from pathlib import Path

from .data_loader import load_orders, load_products, load_customers
from .data_cleaning import clean_orders
from .feature_engineering import create_features
from .warehouse_builder import run_warehouse_pipeline
from .config import CLEANED_ORDERS_FILE
from .logger import get_logger

logger = get_logger(__name__)


def run_pipeline():

    logger.info("Starting analytics pipeline")

    # Load data
    orders = load_orders()
    products = load_products()
    customers = load_customers()

    # Clean
    cleaned = clean_orders(orders)

    # Feature engineering
    features = create_features(cleaned)

    # Save processed dataset
    Path(CLEANED_ORDERS_FILE).parent.mkdir(parents=True, exist_ok=True)
    features.to_csv(CLEANED_ORDERS_FILE, index=False)

    # Build warehouse
    run_warehouse_pipeline(products, customers, features)

    logger.info("Pipeline completed successfully")


if __name__ == "__main__":
    run_pipeline()