from __future__ import annotations

import pandas as pd

from .config import CUSTOMERS_FILE, ORDERS_FILE, PRODUCTS_FILE
from .logger import get_logger

logger = get_logger(__name__)


def _load_csv(path, parse_dates: list[str] | None = None) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=parse_dates)
    logger.info("Loaded %s with shape=%s", path.name, df.shape)
    return df


def load_products() -> pd.DataFrame:
    return _load_csv(PRODUCTS_FILE)


def load_customers() -> pd.DataFrame:
    return _load_csv(CUSTOMERS_FILE)


def load_orders() -> pd.DataFrame:
    return _load_csv(ORDERS_FILE, parse_dates=["order_date"])
