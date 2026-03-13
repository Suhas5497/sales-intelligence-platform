WITH city_sales AS (
    SELECT
        c.city,
        ROUND(SUM(f.revenue), 2) AS total_revenue,
        COUNT(DISTINCT f.order_id) AS total_orders,
        COUNT(DISTINCT f.customer_id) AS active_customers,
        SUM(f.quantity) AS total_units_sold,
        ROUND(SUM(f.revenue) / COUNT(DISTINCT f.order_id), 2) AS avg_order_value
    FROM fact_sales AS f
    JOIN dim_customer AS c
        ON f.customer_id = c.customer_id
    GROUP BY c.city
)
SELECT
    city,
    total_revenue,
    total_orders,
    active_customers,
    total_units_sold,
    avg_order_value,
    ROUND(100.0 * total_revenue / SUM(total_revenue) OVER (), 2) AS revenue_share_pct
FROM city_sales
ORDER BY total_revenue DESC;
