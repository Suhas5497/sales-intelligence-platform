SELECT
    d.weekday_number,
    d.weekday_name,
    EXTRACT(HOUR FROM f.order_timestamp) AS order_hour,
    ROUND(SUM(f.revenue), 2) AS total_revenue,
    COUNT(DISTINCT f.order_id) AS total_orders,
    COUNT(DISTINCT f.customer_id) AS active_customers
FROM fact_sales AS f
JOIN dim_date AS d
    ON f.date_key = d.date_key
GROUP BY d.weekday_number, d.weekday_name, order_hour
ORDER BY d.weekday_number, order_hour;
