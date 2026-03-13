WITH customer_order_counts AS (
    SELECT
        customer_id,
        COUNT(DISTINCT order_id) AS order_count
    FROM fact_sales
    GROUP BY customer_id
)
SELECT
    ROUND(SUM(revenue), 2) AS total_revenue,
    COUNT(DISTINCT order_id) AS total_orders,
    SUM(quantity) AS total_units_sold,
    COUNT(DISTINCT customer_id) AS total_customers,
    ROUND(SUM(revenue) / COUNT(DISTINCT order_id), 2) AS avg_order_value,
    ROUND(SUM(revenue) / COUNT(DISTINCT customer_id), 2) AS revenue_per_customer,
    (
        SELECT ROUND(100.0 * AVG(CASE WHEN order_count > 1 THEN 1 ELSE 0 END), 2)
        FROM customer_order_counts
    ) AS repeat_customer_rate_pct
FROM fact_sales;
