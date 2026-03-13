WITH product_sales AS (
    SELECT
        p.product_id,
        p.product_name,
        p.category,
        ROUND(SUM(f.revenue), 2) AS total_revenue,
        SUM(f.quantity) AS total_units_sold,
        COUNT(DISTINCT f.order_id) AS total_orders
    FROM fact_sales AS f
    JOIN dim_product AS p
        ON f.product_id = p.product_id
    GROUP BY p.product_id, p.product_name, p.category
)
SELECT
    product_id,
    product_name,
    category,
    total_revenue,
    total_units_sold,
    total_orders,
    ROUND(100.0 * total_revenue / SUM(total_revenue) OVER (), 2) AS revenue_share_pct,
    ROUND(
        100.0 * SUM(total_revenue) OVER (ORDER BY total_revenue DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
        / SUM(total_revenue) OVER (),
        2
    ) AS cumulative_revenue_share_pct
FROM product_sales
ORDER BY total_revenue DESC
LIMIT 25;
