from __future__ import annotations

import pandas as pd

from .logger import get_logger

logger = get_logger(__name__)

REQUIRED_ORDER_COLUMNS = [
    "order_id",
    "customer_id",
    "product_id",
    "quantity",
    "price",
    "order_date",
    "city",
    "segment",
]


def clean_orders(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Starting data cleaning")

    missing_columns = sorted(set(REQUIRED_ORDER_COLUMNS) - set(df.columns))
    if missing_columns:
        raise ValueError(f"Orders dataset is missing required columns: {missing_columns}")

    cleaned = df.copy()
    cleaned["order_date"] = pd.to_datetime(cleaned["order_date"], errors="coerce")
    cleaned["quantity"] = pd.to_numeric(cleaned["quantity"], errors="coerce")
    cleaned["price"] = pd.to_numeric(cleaned["price"], errors="coerce")
    cleaned["customer_id"] = cleaned["customer_id"].astype(str).str.strip()
    cleaned["city"] = cleaned["city"].astype(str).str.strip().str.title()
    cleaned["segment"] = cleaned["segment"].astype(str).str.strip().str.title()

    before = len(cleaned)
    cleaned = cleaned.drop_duplicates(subset=["order_id"], keep="first")
    logger.info("Removed %s duplicate order rows", before - len(cleaned))

    cleaned = cleaned.dropna(subset=REQUIRED_ORDER_COLUMNS)
    cleaned = cleaned[(cleaned["quantity"] > 0) & (cleaned["price"] > 0)]

    cleaned["order_id"] = cleaned["order_id"].astype(int)
    cleaned["product_id"] = cleaned["product_id"].astype(int)
    cleaned["quantity"] = cleaned["quantity"].astype(int)
    cleaned["price"] = cleaned["price"].round(2)

    cleaned = cleaned.sort_values("order_date").reset_index(drop=True)
    logger.info("Remaining rows after cleaning: %s", len(cleaned))

    return cleaned
