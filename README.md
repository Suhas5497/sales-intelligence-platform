# Sales Intelligence Analytics Platform

## End-to-End Data Analytics System for Large-Scale Retail Sales Intelligence

This project simulates a production-grade analytics workflow used by modern data teams.
It processes 5 million e-commerce transactions and transforms raw operational data into business intelligence dashboards, predictive insights, and automated analytics pipelines.

The system demonstrates the complete lifecycle of analytics engineering:

Data Generation → Data Engineering → Data Warehouse → SQL Analytics → BI Dashboard → Forecasting → Anomaly Detection
## Project Highlights

#### 5M+ transactions processed

#### Star schema analytics warehouse

#### Production-style ETL pipeline

#### SQL business intelligence layer

#### Interactive Power BI dashboard

#### Sales forecasting model

#### Revenue anomaly detection

This project demonstrates how raw transactional data becomes decision-ready business intelligence.

## Architecture
    Synthetic E-commerce Dataset
        ↓
    Data Quality Validation
        ↓
    ETL Pipeline (Data Cleaning + Feature Engineering)
        ↓
    Star Schema Data Warehouse
        ↓
    SQL Analytics Layer
        ↓
    Power BI Executive Dashboard
        ↓
    Sales Forecasting Model
        ↓
    Revenue Anomaly Detection
        ↓
    Automated Pipeline Scheduler
## Dataset

The project uses a realistic synthetic e-commerce dataset designed to simulate real retail behavior.

- Dataset Scale
- Table	Records
- Products	1,200
- Customers	300,000
- Orders	5,000,000
- Realistic Data Simulation

The dataset includes realistic business patterns:

- 50+ Indian cities

- 13 product categories

- Realistic price distributions

- UPI-dominant payment methods

- Peak shopping hours

- Product popularity (Pareto distribution)

- Weekend sales boost

- Customer loyalty behavior

- Discounts and returns

## Key Fields
    order_id
    product_id
    customer_id
    product_name
    category
    city
    segment
    order_datetime
    payment_method
    quantity
    price
    discount
    revenue
    order_status
## Tech Stack
### Layer	Tools
- Data Engineering :   	Python, Pandas, NumPy
- Data Warehouse :    	DuckDB
- Analytics :         	SQL      
- Visualization :     	Power BI
- Forecasting :       	Prophet
- Automation :         	Python Scheduler
- Version Control :     Git & GitHub
##  Project Structure
      #### sales-intelligence-platform

      data/
           raw/
               orders.csv
               customers.csv
               products.csv
           processed/

      warehouse/
              fact_sales.csv
              dim_product.csv
              dim_customer.csv
              dim_date.csv

      src/
              data_generation.py
              data_quality.py
              pipeline.py
              feature_engineering.py
              warehouse_builder.py
              forecasting.py
              anomaly_detection.py
              scheduler.py

      sql/
              warehouse_schema.sql
              01_kpi_metrics.sql
              02_sales_trends.sql
              03_product_analysis.sql
              04_city_analysis.sql
              05_customer_analysis.sql
              06_time_analysis.sql
              07_advanced_analysis.sql

      dashboard/
              sales_intelligence_dashboard.pbix
## Analytics Warehouse Design

### The project implements a Star Schema optimized for analytical queries.

#### Fact Table
- fact_sales

#### Contains transactional metrics:

order_id

product_id

customer_id

quantity

price

revenue

Dimension Tables

dim_product

dim_customer

dim_date

This schema enables fast analytical queries and scalable reporting.

## SQL Analytics Layer

### The SQL layer answers key business questions.

#### Monthly Revenue Trend
    SELECT year, month, SUM(revenue) AS revenue FROM fact_sales
    GROUP BY year, month
    ORDER BY year, month;
#### Top Selling Products
    SELECT product_id, SUM(revenue) AS revenue FROM fact_sales
    GROUP BY product_id
    ORDER BY revenue DESC
    LIMIT 10;
#### City Sales Performance
    SELECT city, SUM(revenue) AS revenue FROM fact_sales
    GROUP BY city
    ORDER BY revenue DESC;
## Power BI Dashboard

The Power BI dashboard provides executive-level business insights.

- Key KPIs

- Total Revenue

- Total Orders

- Units Sold

- Average Order Value

- Analytical Visualizations

- Monthly Revenue Growth Trend

- Top Performing Products

- Category Contribution

- Customer Segment Analysis

- Geographic Sales Distribution

- Product Category Performance

## Dashboard Preview

<img width="1284" height="723" alt="Screenshot 2026-03-10 233601" src="https://github.com/user-attachments/assets/a8bcfacd-675e-422e-b639-06adc99b840e" />

## Sales Forecasting

#### The project includes a time-series forecasting model using Prophet.

### Purpose

- Predict future sales trends

- Support inventory planning

- Identify seasonal patterns

Output file:

    data/processed/sales_forecast.csv
##  Anomaly Detection

The project includes anomaly detection for identifying abnormal revenue spikes.

### Method
    Z-Score Statistical Detection
#### Applications

- Fraud detection

- Promotional spikes

- Data quality monitoring

Output file:

   data/processed/anomalies.csv
## Running the Project
#### Install dependencies
    pip install -r requirements.txt
#### Run ETL pipeline
    python src/pipeline.py
#### Load warehouse
    python src/load_warehouse.py
#### Run forecasting
    python src/forecasting.py
#### Run anomaly detection
    python src/anomaly_detection.py
## Key Business Insights

Example insights from the analysis:

- Electronics and Fashion drive the largest share of revenue.

- Evening hours generate the highest purchase activity.

- Mega cities contribute the majority of sales volume.

- Corporate customers have higher average order value.

## Why This Project Matters

#### This project demonstrates the complete analytics lifecycle used in real organizations:

- Data engineering pipeline design

- Analytics warehouse architecture

- SQL business intelligence analysis

- Interactive dashboard creation

- Predictive analytics

- Automated data workflows

It reflects the real responsibilities of modern Data Analysts and Analytics Engineers.


## 👤 Author

### Suhas Dhamapurkar (AIML Engineer)

### Data Analytics | Business Intelligence | Data Engineering 
