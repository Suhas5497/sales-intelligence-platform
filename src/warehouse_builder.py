from __future__ import annotations

import pandas as pd

from .config import DIM_CUSTOMER_FILE, DIM_DATE_FILE, DIM_PRODUCT_FILE, FACT_SALES_FILE, ensure_project_directories
from .logger import get_logger

logger = get_logger(__name__)


def build_dim_product(products_df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Building dim_product")
    dim_product = (
        products_df[["product_id", "product_name", "category", "price"]]
        .drop_duplicates(subset=["product_id"])
        .sort_values("product_id")
        .reset_index(drop=True)
    )
    return dim_product


def build_dim_customer(customers_df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Building dim_customer")
    dim_customer = (
        customers_df[["customer_id", "city", "segment"]]
        .drop_duplicates(subset=["customer_id"])
        .sort_values("customer_id")
        .reset_index(drop=True)
    )
    return dim_customer


def build_dim_date(orders_df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Building dim_date at daily grain")

    min_date = orders_df["order_date"].min().normalize()
    max_date = orders_df["order_date"].max().normalize()
    calendar = pd.DataFrame({"date": pd.date_range(start=min_date, end=max_date, freq="D")})
    calendar["date_key"] = calendar["date"].dt.strftime("%Y%m%d").astype(int)
    calendar["year"] = calendar["date"].dt.year
    calendar["quarter"] = calendar["date"].dt.quarter
    calendar["month"] = calendar["date"].dt.month
    calendar["month_name"] = calendar["date"].dt.strftime("%B")
    calendar["month_short"] = calendar["date"].dt.strftime("%b")
    calendar["day"] = calendar["date"].dt.day
    calendar["weekday_number"] = calendar["date"].dt.weekday
    calendar["weekday_name"] = calendar["date"].dt.day_name()
    calendar["week_of_year"] = calendar["date"].dt.isocalendar().week.astype(int)
    calendar["is_weekend"] = calendar["weekday_number"].isin([5, 6])
    calendar["month_start"] = calendar["date"].dt.to_period("M").dt.to_timestamp()
    return calendar


def build_fact_sales(orders_df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Building fact_sales")
    fact_sales = (
        orders_df[
            [
                "order_id",
                "product_id",
                "customer_id",
                "date_key",
                "order_date",
                "city",
                "segment",
                "quantity",
                "price",
                "revenue",
            ]
        ]
        .rename(columns={"order_date": "order_timestamp", "price": "unit_price"})
        .sort_values("order_id")
        .reset_index(drop=True)
    )
    return fact_sales


def save_tables(
    dim_product: pd.DataFrame,
    dim_customer: pd.DataFrame,
    dim_date: pd.DataFrame,
    fact_sales: pd.DataFrame,
) -> None:
    ensure_project_directories()
    dim_product.to_csv(DIM_PRODUCT_FILE, index=False)
    dim_customer.to_csv(DIM_CUSTOMER_FILE, index=False)
    dim_date.to_csv(DIM_DATE_FILE, index=False)
    fact_sales.to_csv(FACT_SALES_FILE, index=False)
    logger.info("Warehouse tables saved to %s", DIM_PRODUCT_FILE.parent)


def run_warehouse_pipeline(
    products_df: pd.DataFrame,
    customers_df: pd.DataFrame,
    orders_df: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    dim_product = build_dim_product(products_df)
    dim_customer = build_dim_customer(customers_df)
    dim_date = build_dim_date(orders_df)
    fact_sales = build_fact_sales(orders_df)
    save_tables(dim_product, dim_customer, dim_date, fact_sales)

    return {
        "dim_product": dim_product,
        "dim_customer": dim_customer,
        "dim_date": dim_date,
        "fact_sales": fact_sales,
    }
