import pandas as pd
from pathlib import Path

from .data_loader import load_orders
from .data_cleaning import clean_orders
from .feature_engineering import create_features
from .config import CLEANED_ORDERS_FILE
from .logger import get_logger

logger = get_logger(__name__)


def run_pipeline():

    logger.info("Starting analytics pipeline")

    orders = load_orders()

    cleaned = clean_orders(orders)

    features = create_features(cleaned)

    # Ensure output folder exists
    Path(CLEANED_ORDERS_FILE).parent.mkdir(parents=True, exist_ok=True)

    features.to_csv(CLEANED_ORDERS_FILE, index=False)

    logger.info(f"Processed dataset saved to {CLEANED_ORDERS_FILE}")


if __name__ == "__main__":
    run_pipeline()
    