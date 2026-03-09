import pandas as pd
from .logger import get_logger

logger = get_logger(__name__)


def clean_orders(df: pd.DataFrame) -> pd.DataFrame:

    logger.info("Starting data cleaning")

    # Convert date
    df["order_date"] = pd.to_datetime(df["order_date"])

    # Remove duplicates
    before = len(df)
    df = df.drop_duplicates()
    after = len(df)

    logger.info(f"Removed {before-after} duplicate rows")

    # Handle missing values
    df = df.dropna()

    # Validate quantity
    df = df[df["quantity"] > 0]

    # Validate price
    df = df[df["price"] > 0]

    logger.info(f"Remaining rows after cleaning: {len(df)}")

    return df