from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .config import VALIDATION_REPORT_FILE, ensure_project_directories


@dataclass(frozen=True)
class ValidationResult:
    stage: str
    check_name: str
    status: str
    metric_value: str
    details: str


def _format_metric(value: object) -> str:
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def _result(stage: str, check_name: str, passed: bool, metric_value: object, details: str) -> ValidationResult:
    return ValidationResult(
        stage=stage,
        check_name=check_name,
        status="pass" if passed else "fail",
        metric_value=_format_metric(metric_value),
        details=details,
    )


def validate_raw_data(
    orders: pd.DataFrame,
    customers: pd.DataFrame,
    products: pd.DataFrame,
) -> list[ValidationResult]:
    results = [
        _result("raw", "orders_non_empty", not orders.empty, len(orders), "Orders dataset should not be empty."),
        _result(
            "raw",
            "customers_non_empty",
            not customers.empty,
            len(customers),
            "Customers dataset should not be empty.",
        ),
        _result(
            "raw",
            "products_non_empty",
            not products.empty,
            len(products),
            "Products dataset should not be empty.",
        ),
        _result(
            "raw",
            "duplicate_order_ids",
            orders["order_id"].is_unique,
            int(orders["order_id"].duplicated().sum()),
            "Order IDs should be unique at the raw ingestion stage.",
        ),
        _result(
            "raw",
            "duplicate_customer_ids",
            customers["customer_id"].is_unique,
            int(customers["customer_id"].duplicated().sum()),
            "Customer IDs should be unique in the customer master.",
        ),
        _result(
            "raw",
            "duplicate_product_ids",
            products["product_id"].is_unique,
            int(products["product_id"].duplicated().sum()),
            "Product IDs should be unique in the product master.",
        ),
        _result(
            "raw",
            "orders_missing_values",
            int(orders.isna().sum().sum()) == 0,
            int(orders.isna().sum().sum()),
            "Transactional source data should not contain missing values.",
        ),
        _result(
            "raw",
            "customer_key_alignment",
            set(orders["customer_id"]).issubset(set(customers["customer_id"])),
            len(set(orders["customer_id"]) - set(customers["customer_id"])),
            "Every transactional customer must exist in the customer master.",
        ),
        _result(
            "raw",
            "product_key_alignment",
            set(orders["product_id"]).issubset(set(products["product_id"])),
            len(set(orders["product_id"]) - set(products["product_id"])),
            "Every transactional product must exist in the product master.",
        ),
    ]
    return results


def validate_cleaned_orders(df: pd.DataFrame) -> list[ValidationResult]:
    results = [
        _result(
            "processed",
            "cleaned_non_empty",
            not df.empty,
            len(df),
            "Processed orders should contain at least one row.",
        ),
        _result(
            "processed",
            "cleaned_null_values",
            int(df.isna().sum().sum()) == 0,
            int(df.isna().sum().sum()),
            "Cleaned orders should not contain null values.",
        ),
        _result(
            "processed",
            "positive_quantity",
            bool((df["quantity"] > 0).all()),
            int((df["quantity"] <= 0).sum()),
            "Quantities must remain positive after cleaning.",
        ),
        _result(
            "processed",
            "positive_price",
            bool((df["price"] > 0).all()),
            int((df["price"] <= 0).sum()),
            "Prices must remain positive after cleaning.",
        ),
        _result(
            "processed",
            "revenue_consistency",
            bool((df["revenue"].round(2) == (df["quantity"] * df["price"]).round(2)).all()),
            int((df["revenue"].round(2) != (df["quantity"] * df["price"]).round(2)).sum()),
            "Revenue should equal quantity multiplied by price for every order.",
        ),
    ]
    return results


def validate_warehouse(
    fact_sales: pd.DataFrame,
    dim_customer: pd.DataFrame,
    dim_product: pd.DataFrame,
    dim_date: pd.DataFrame,
    expected_fact_rows: int | None = None,
) -> list[ValidationResult]:
    results = [
        _result(
            "warehouse",
            "fact_non_empty",
            not fact_sales.empty,
            len(fact_sales),
            "The fact table should contain transaction rows.",
        ),
        _result(
            "warehouse",
            "customer_fk_integrity",
            set(fact_sales["customer_id"]).issubset(set(dim_customer["customer_id"])),
            len(set(fact_sales["customer_id"]) - set(dim_customer["customer_id"])),
            "Every customer key in the fact table must exist in the customer dimension.",
        ),
        _result(
            "warehouse",
            "product_fk_integrity",
            set(fact_sales["product_id"]).issubset(set(dim_product["product_id"])),
            len(set(fact_sales["product_id"]) - set(dim_product["product_id"])),
            "Every product key in the fact table must exist in the product dimension.",
        ),
        _result(
            "warehouse",
            "date_fk_integrity",
            set(fact_sales["date_key"]).issubset(set(dim_date["date_key"])),
            len(set(fact_sales["date_key"]) - set(dim_date["date_key"])),
            "Every date key in the fact table must exist in the date dimension.",
        ),
        _result(
            "warehouse",
            "date_dimension_daily_grain",
            bool(dim_date["date"].nunique() == len(dim_date)),
            int(len(dim_date) - dim_date["date"].nunique()),
            "The date dimension should contain exactly one row per calendar day.",
        ),
        _result(
            "warehouse",
            "fact_row_reconciliation",
            expected_fact_rows is None or len(fact_sales) == expected_fact_rows,
            len(fact_sales),
            "Fact row count should reconcile with the cleaned orders dataset.",
        ),
    ]
    return results


def save_validation_report(results: list[ValidationResult]) -> pd.DataFrame:
    ensure_project_directories()
    report = pd.DataFrame([result.__dict__ for result in results])
    report.to_csv(VALIDATION_REPORT_FILE, index=False)
    return report
