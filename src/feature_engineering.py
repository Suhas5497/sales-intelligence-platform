import pandas as pd
from .logger import get_logger

logger = get_logger(__name__)

def create_features(df: pd.DataFrame) -> pd.DataFrame:

    logger.info("Starting feature engineering")

    # Revenue calculation
    df["revenue"] = df["quantity"] * df["price"]

    # Time features
    df["year"] = df["order_date"].dt.year
    df["month"] = df["order_date"].dt.month
    df["day"] = df["order_date"].dt.day
    df["weekday"] = df["order_date"].dt.day_name()
    df["hour"] = df["order_date"].dt.hour

    logger.info("Feature engineering completed")

    return df