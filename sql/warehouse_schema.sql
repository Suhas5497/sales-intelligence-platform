-- Star-schema warehouse design for the sales intelligence platform.
-- Grain:
--   fact_sales    = one row per order transaction
--   dim_customer  = one row per customer
--   dim_product   = one row per product
--   dim_date      = one row per calendar date

CREATE TABLE dim_product (
    product_id BIGINT PRIMARY KEY,
    product_name VARCHAR NOT NULL,
    category VARCHAR NOT NULL,
    price DOUBLE NOT NULL
);

CREATE TABLE dim_customer (
    customer_id VARCHAR PRIMARY KEY,
    city VARCHAR NOT NULL,
    segment VARCHAR NOT NULL
);

CREATE TABLE dim_date (
    date_key BIGINT PRIMARY KEY,
    date DATE NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name VARCHAR NOT NULL,
    month_short VARCHAR NOT NULL,
    day INTEGER NOT NULL,
    weekday_number INTEGER NOT NULL,
    weekday_name VARCHAR NOT NULL,
    week_of_year INTEGER NOT NULL,
    is_weekend BOOLEAN NOT NULL,
    month_start DATE NOT NULL
);

CREATE TABLE fact_sales (
    order_id BIGINT PRIMARY KEY,
    product_id BIGINT NOT NULL,
    customer_id VARCHAR NOT NULL,
    date_key BIGINT NOT NULL,
    order_timestamp TIMESTAMP NOT NULL,
    city VARCHAR NOT NULL,
    segment VARCHAR NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price DOUBLE NOT NULL,
    revenue DOUBLE NOT NULL,
    FOREIGN KEY (product_id) REFERENCES dim_product(product_id),
    FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id),
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key)
);
