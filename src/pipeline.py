from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import CLEANED_ORDERS_FILE, PIPELINE_SUMMARY_FILE, WAREHOUSE_SUMMARY_FILE, ensure_project_directories
from .data_cleaning import clean_orders
from .data_generation import GenerationConfig, generate_dataset
from .data_loader import load_customers, load_orders, load_products
from .data_validation import save_validation_report, validate_cleaned_orders, validate_raw_data, validate_warehouse
from .feature_engineering import create_features
from .load_warehouse import load_warehouse
from .logger import get_logger
from .run_queries import run_queries
from .warehouse_builder import run_warehouse_pipeline

logger = get_logger(__name__)


def _pipeline_summary(cleaned_rows: int, warehouse_tables: dict[str, object]) -> dict[str, object]:
    return {
        "cleaned_order_rows": cleaned_rows,
        "warehouse_rows": {name: len(table) for name, table in warehouse_tables.items()},
    }


def run_pipeline(generate_raw: bool = False) -> dict[str, object]:
    logger.info("Starting sales intelligence pipeline")
    ensure_project_directories()

    if generate_raw:
        generate_dataset(GenerationConfig())

    orders = load_orders()
    products = load_products()
    customers = load_customers()

    validation_results = validate_raw_data(orders, customers, products)

    cleaned = clean_orders(orders)
    features = create_features(cleaned)

    Path(CLEANED_ORDERS_FILE).parent.mkdir(parents=True, exist_ok=True)
    features.to_csv(CLEANED_ORDERS_FILE, index=False)

    validation_results.extend(validate_cleaned_orders(features))

    warehouse_tables = run_warehouse_pipeline(products, customers, features)
    validation_results.extend(
        validate_warehouse(
            fact_sales=warehouse_tables["fact_sales"],
            dim_customer=warehouse_tables["dim_customer"],
            dim_product=warehouse_tables["dim_product"],
            dim_date=warehouse_tables["dim_date"],
            expected_fact_rows=len(features),
        )
    )
    validation_report = save_validation_report(validation_results)

    warehouse_summary = (
        validation_report.groupby(["stage", "status"]).size().reset_index(name="check_count")
    )
    warehouse_summary.to_csv(WAREHOUSE_SUMMARY_FILE, index=False)

    load_warehouse()
    query_outputs = run_queries()

    summary = _pipeline_summary(cleaned_rows=len(features), warehouse_tables=warehouse_tables)
    summary["query_output_files"] = [path.name for path in query_outputs]
    PIPELINE_SUMMARY_FILE.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    logger.info("Pipeline completed successfully")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the sales intelligence pipeline.")
    parser.add_argument(
        "--generate-raw",
        action="store_true",
        help="Regenerate the raw synthetic datasets before running the pipeline.",
    )
    args = parser.parse_args()
    run_pipeline(generate_raw=args.generate_raw)


if __name__ == "__main__":
    main()
