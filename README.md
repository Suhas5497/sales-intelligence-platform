# Retail Sales Intelligence Platform

Retail Sales Intelligence Platform is an end-to-end analytics engineering project built for Data Analyst and Data Engineer portfolio use. It takes retail transaction data from raw CSV files to a cleaned analytical dataset, star-schema warehouse, business SQL layer, and an interactive Streamlit dashboard.

The project is intentionally positioned as a non-ML analytics system. The focus is on data quality, warehouse modeling, KPI design, SQL analysis, and stakeholder-ready reporting.

## Project Goals

- Build a reproducible retail analytics pipeline from raw data to reporting outputs.
- Model a star-schema warehouse suitable for business intelligence workloads.
- Surface analyst-grade KPIs such as revenue, orders, AOV, repeat rate, and city/category contribution.
- Provide a reviewer-friendly Streamlit dashboard on top of the warehouse.
- Keep the repo runnable and honest about what is implemented.

## Current Dataset

The repository currently includes a synthetic retail dataset with the following scale:

| Table | Records |
| --- | ---: |
| `orders.csv` | 300,000 |
| `customers.csv` | 25,000 |
| `products.csv` | 168 |

Source schema:

- `orders.csv`: `order_id`, `customer_id`, `product_id`, `quantity`, `price`, `order_date`, `city`, `segment`
- `customers.csv`: `customer_id`, `city`, `segment`
- `products.csv`: `product_id`, `product_name`, `category`, `price`

## Architecture

```text
Raw CSV Sources
    -> Data Cleaning
    -> Feature Engineering
    -> Data Quality Validation
    -> Star Schema Warehouse (CSV + DuckDB)
    -> SQL Analytics Layer
    -> Streamlit Dashboard
    -> Optional Power BI Report
```

## Tech Stack

- Python
- Pandas
- NumPy
- DuckDB
- SQL
- Streamlit
- Plotly
- Power BI

## Repository Structure

```text
sales-intelligence-platform/
|-- app/
|   `-- streamlit_app.py
|-- data/
|   |-- raw/
|   |   |-- customers.csv
|   |   |-- orders.csv
|   |   `-- products.csv
|   `-- processed/
|       `-- cleaned_orders.csv
|-- reports/
|   |-- pipeline_summary.json
|   |-- validation_checks.csv
|   |-- warehouse_summary.csv
|   `-- query_outputs/
|-- scripts/
|   |-- __init__.py
|   `-- generate_dataset.py
|-- sql/
|   |-- 01_kpi_metrics.sql
|   |-- 02_sales_trends.sql
|   |-- 03_product_analysis.sql
|   |-- 04_city_analysis.sql
|   |-- 05_customer_analysis.sql
|   |-- 06_time_analysis.sql
|   |-- 07_advanced_analysis.sql
|   `-- warehouse_schema.sql
|-- src/
|   |-- __init__.py
|   |-- config.py
|   |-- data_cleaning.py
|   |-- data_generation.py
|   |-- data_loader.py
|   |-- data_validation.py
|   |-- feature_engineering.py
|   |-- load_warehouse.py
|   |-- logger.py
|   |-- pipeline.py
|   |-- run_queries.py
|   `-- warehouse_builder.py
|-- warehouse/
|   |-- dim_customer.csv
|   |-- dim_date.csv
|   |-- dim_product.csv
|   |-- fact_sales.csv
|   `-- sales.duckdb
|-- SALES ANALYSIS DASHBOARD.pbix
|-- SALES INTELLIGENCE DASHBOARD.pbix
|-- README.md
`-- requirements.txt
```

## Data Pipeline

### 1. Raw Data Ingestion

`src/data_loader.py` loads the source CSV files and parses the transactional timestamp field.

### 2. Data Cleaning

`src/data_cleaning.py` performs:

- required-column checks
- type coercion
- duplicate removal on `order_id`
- null handling
- positive quantity and price validation
- standardization of customer, city, and segment values

### 3. Feature Engineering

`src/feature_engineering.py` adds:

- `revenue`
- `date_key`
- `date`
- `year`, `quarter`, `month`, `month_name`
- `weekday_number`, `weekday_name`
- `hour`
- `is_weekend`
- `order_month`

### 4. Warehouse Modeling

`src/warehouse_builder.py` creates a star schema:

- `fact_sales`: one row per order transaction
- `dim_product`: product master
- `dim_customer`: customer master
- `dim_date`: one row per calendar day

The date dimension is modeled at daily grain for cleaner trend analysis and time intelligence.

### 5. Validation

`src/data_validation.py` writes a data quality report covering:

- empty dataset checks
- duplicate business keys
- missing values
- customer/product key alignment
- positive numeric checks
- revenue consistency
- fact-to-dimension foreign key integrity
- daily-grain date dimension validation

### 6. Analytics Layer

`src/run_queries.py` executes the SQL files in `sql/` and saves the outputs to `reports/query_outputs/`.

## Business Questions Covered

The SQL layer answers questions such as:

- What are the current revenue, order, customer, and repeat-rate KPIs?
- How is monthly revenue changing over time?
- Which products contribute most to revenue?
- Which cities drive the highest sales contribution?
- How do customer segments differ on repeat behavior and revenue per customer?
- Which weekday/hour combinations concentrate demand?
- Which segment-city-category combinations should be prioritized?

## Streamlit Dashboard

The Streamlit app in `app/streamlit_app.py` provides:

- `Executive Overview`: KPI cards, monthly revenue, category mix, segment contribution
- `Sales Trends`: order volume, active customers, weekday/hour demand heatmap
- `Customer Insights`: repeat behavior, revenue per customer, top customers
- `Product & Geography`: product Pareto view, city performance, top products
- `Data Quality`: validation results from the pipeline

This is the easiest way for a recruiter or reviewer to inspect the warehouse outputs without opening Power BI.

## Power BI

The repository includes Power BI dashboard files as companion BI assets:

- `SALES INTELLIGENCE DASHBOARD.pbix`


Power BI skills demonstrated in these reports:

- KPI card design for revenue, orders, units, and AOV
- slicers for time, city, segment, and category analysis
- cross-filtered sales trend analysis
- city and segment breakdowns for executive reporting
- business-facing dashboard storytelling on top of the warehouse layer

### Power BI Dashboard Layout

The current Power BI report is aligned to the warehouse and SQL outputs in this project and is structured as an executive sales analysis view.

Key KPI cards:

- Revenue
- Units Sold
- Total Orders
- Average Order Value

Interactive slicers:

- Category
- Product
- City
- Segment
- Month
- Year

Business visuals included in the dashboard:

- Monthly Revenue Growth Trend
- Category Revenue Contribution
- Customer Segment Revenue
- Top Performing Products
- Top Performing Product Categories
- City Sales Distribution map

### Why This Strengthens The Project

Including Power BI in this project helps demonstrate that the same warehouse can support both:

- Python-based analytics applications through Streamlit
- stakeholder-facing BI reporting through Power BI

For recruiters, this is useful because it shows both analytics engineering capability and practical dashboarding skill in a standard business intelligence tool.

Streamlit is the primary review path because it is easier to run from the repository, but the `.pbix` files are included to show hands-on BI reporting capability beyond Python dashboards.

### README Screenshot Placement

To show the Power BI dashboard directly in GitHub, export the report page as PNG and save it under:

- `reports/assets/powerbi_sales_analysis_dashboard.png`
- `reports/assets/powerbi_sales_intelligence_dashboard.png`

After that, these images can be embedded in the README as dashboard previews.

## How To Run

From the project root:

```bash
pip install -r requirements.txt
python -m src.pipeline
streamlit run app/streamlit_app.py
```

Optional: regenerate the synthetic raw data first.

```bash
python -m scripts.generate_dataset
python -m src.pipeline
```

## Generated Outputs

After running the pipeline, the project produces:

- `data/processed/cleaned_orders.csv`
- `warehouse/dim_product.csv`
- `warehouse/dim_customer.csv`
- `warehouse/dim_date.csv`
- `warehouse/fact_sales.csv`
- `warehouse/sales.duckdb`
- `reports/validation_checks.csv`
- `reports/warehouse_summary.csv`
- `reports/pipeline_summary.json`
- `reports/query_outputs/*.csv`

## Why This Project Is Strong For DA + DE Roles

- It shows end-to-end ownership from raw data to business reporting.
- It demonstrates star-schema design and DuckDB loading.
- It includes a validation layer instead of only transformation logic.
- It exposes analyst-grade KPIs and business cuts through SQL and Streamlit.
- It is runnable locally without hidden dependencies or inflated claims.

## Next Improvements

Potential next steps without changing the non-ML focus:

- add automated tests for pipeline and warehouse integrity
- add a schema diagram and data dictionary
- add scheduled refresh or orchestration metadata
- add downloadable stakeholder reports from Streamlit

## Author

Suhas Dhamapurkar
