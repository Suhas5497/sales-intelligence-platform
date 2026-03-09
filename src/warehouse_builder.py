import pandas as pd
from pathlib import Path
from .config import PROCESSED_DATA_DIR
from .logger import get_logger

logger = get_logger(__name__)

WAREHOUSE_DIR = Path("warehouse")


def build_dim_product(products_df):

    logger.info("Building dim_product")

    dim_product = products_df[
        ["product_id", "product_name", "category", "price"]
    ].drop_duplicates()

    return dim_product


def build_dim_customer(customers_df):

    logger.info("Building dim_customer")

    dim_customer = customers_df[
        ["customer_id", "city", "segment"]
    ].drop_duplicates()

    return dim_customer


def build_dim_date(orders_df):

    logger.info("Building dim_date")

    date_df = orders_df[["order_date"]].drop_duplicates()

    date_df["date"] = pd.to_datetime(date_df["order_date"])

    date_df["year"] = date_df["date"].dt.year
    date_df["month"] = date_df["date"].dt.month
    date_df["day"] = date_df["date"].dt.day
    date_df["weekday"] = date_df["date"].dt.day_name()
    date_df["hour"] = date_df["date"].dt.hour

    date_df["date_id"] = date_df.index + 1

    return date_df


def build_fact_sales(orders_df, dim_date):

    logger.info("Building fact_sales")

    merged = orders_df.merge(
        dim_date,
        left_on="order_date",
        right_on="order_date",
        how="left"
    )

    fact_sales = merged[
        [
            "order_id",
            "product_id",
            "customer_id",
            "date_id",
            "quantity",
            "price",
            "revenue"
        ]
    ]

    return fact_sales


def save_tables(dim_product, dim_customer, dim_date, fact_sales):

    WAREHOUSE_DIR.mkdir(exist_ok=True)

    dim_product.to_csv("warehouse/dim_product.csv", index=False)
    dim_customer.to_csv("warehouse/dim_customer.csv", index=False)
    dim_date.to_csv("warehouse/dim_date.csv", index=False)
    fact_sales.to_csv("warehouse/fact_sales.csv", index=False)

    logger.info("Warehouse tables saved")


def run_warehouse_pipeline(products_df, customers_df, orders_df):

    dim_product = build_dim_product(products_df)
    dim_customer = build_dim_customer(customers_df)
    dim_date = build_dim_date(orders_df)

    fact_sales = build_fact_sales(orders_df, dim_date)

    save_tables(dim_product, dim_customer, dim_date, fact_sales)