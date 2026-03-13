from __future__ import annotations

import pandas as pd

from .logger import get_logger

logger = get_logger(__name__)


def create_features(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Starting feature engineering")

    features = df.copy()
    features["revenue"] = (features["quantity"] * features["price"]).round(2)
    features["date_key"] = features["order_date"].dt.strftime("%Y%m%d").astype(int)
    features["date"] = features["order_date"].dt.normalize()
    features["year"] = features["order_date"].dt.year
    features["quarter"] = features["order_date"].dt.quarter
    features["month"] = features["order_date"].dt.month
    features["month_name"] = features["order_date"].dt.strftime("%b")
    features["day"] = features["order_date"].dt.day
    features["weekday_number"] = features["order_date"].dt.weekday
    features["weekday_name"] = features["order_date"].dt.day_name()
    features["hour"] = features["order_date"].dt.hour
    features["is_weekend"] = features["weekday_number"].isin([5, 6])
    features["order_month"] = features["order_date"].dt.to_period("M").astype(str)

    logger.info("Feature engineering completed")
    return features
