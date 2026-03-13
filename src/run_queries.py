from __future__ import annotations

from pathlib import Path

import duckdb

from .config import DUCKDB_FILE, QUERY_OUTPUT_DIR, SQL_DIR, ensure_project_directories
from .logger import get_logger

logger = get_logger(__name__)


def run_queries() -> list[Path]:
    ensure_project_directories()
    con = duckdb.connect(str(DUCKDB_FILE))
    query_files = sorted(
        path for path in SQL_DIR.glob("*.sql") if path.name != "warehouse_schema.sql"
    )

    outputs: list[Path] = []
    for path in query_files:
        logger.info("Executing %s", path.name)
        result = con.execute(path.read_text(encoding="utf-8")).fetchdf()
        output_path = QUERY_OUTPUT_DIR / f"{path.stem}.csv"
        result.to_csv(output_path, index=False)
        outputs.append(output_path)

    con.close()
    logger.info("Saved %s analytics extracts to %s", len(outputs), QUERY_OUTPUT_DIR)
    return outputs


if __name__ == "__main__":
    run_queries()
