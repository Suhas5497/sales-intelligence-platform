WITH customer_metrics AS (
    SELECT
        c.segment,
        f.customer_id,
        COUNT(DISTINCT f.order_id) AS order_count,
        ROUND(SUM(f.revenue), 2) AS customer_revenue,
        SUM(f.quantity) AS units_sold
    FROM fact_sales AS f
    JOIN dim_customer AS c
        ON f.customer_id = c.customer_id
    GROUP BY c.segment, f.customer_id
)
SELECT
    segment,
    COUNT(*) AS customers,
    ROUND(AVG(order_count), 2) AS avg_orders_per_customer,
    ROUND(AVG(customer_revenue), 2) AS avg_revenue_per_customer,
    ROUND(AVG(units_sold), 2) AS avg_units_per_customer,
    ROUND(100.0 * AVG(CASE WHEN order_count > 1 THEN 1 ELSE 0 END), 2) AS repeat_customer_rate_pct,
    ROUND(SUM(customer_revenue), 2) AS total_revenue
FROM customer_metrics
GROUP BY segment
ORDER BY total_revenue DESC;
