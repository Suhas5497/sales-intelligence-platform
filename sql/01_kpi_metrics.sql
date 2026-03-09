SELECT
    SUM(revenue) AS total_revenue,
    COUNT(DISTINCT order_id) AS total_orders,
    SUM(quantity) AS total_units_sold,
    ROUND(SUM(revenue)/COUNT(DISTINCT order_id),2) AS avg_order_value
FROM fact_sales;