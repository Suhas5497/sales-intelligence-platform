WITH segment_city_category AS (
    SELECT
        c.segment,
        c.city,
        p.category,
        ROUND(SUM(f.revenue), 2) AS total_revenue,
        COUNT(DISTINCT f.order_id) AS total_orders,
        COUNT(DISTINCT f.customer_id) AS active_customers,
        ROUND(SUM(f.revenue) / COUNT(DISTINCT f.order_id), 2) AS avg_order_value
    FROM fact_sales AS f
    JOIN dim_customer AS c
        ON f.customer_id = c.customer_id
    JOIN dim_product AS p
        ON f.product_id = p.product_id
    GROUP BY c.segment, c.city, p.category
    HAVING COUNT(DISTINCT f.order_id) >= 200
)
SELECT
    ROW_NUMBER() OVER (ORDER BY total_revenue DESC, avg_order_value DESC) AS priority_rank,
    segment,
    city,
    category,
    total_revenue,
    total_orders,
    active_customers,
    avg_order_value,
    ROUND(100.0 * total_revenue / SUM(total_revenue) OVER (), 2) AS revenue_share_pct
FROM segment_city_category
ORDER BY priority_rank
LIMIT 25;
