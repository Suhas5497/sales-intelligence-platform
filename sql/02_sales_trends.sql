WITH monthly_sales AS (
    SELECT
        d.month_start,
        d.year,
        d.month,
        d.month_short,
        ROUND(SUM(f.revenue), 2) AS total_revenue,
        COUNT(DISTINCT f.order_id) AS total_orders,
        COUNT(DISTINCT f.customer_id) AS active_customers,
        ROUND(SUM(f.revenue) / COUNT(DISTINCT f.order_id), 2) AS avg_order_value
    FROM fact_sales AS f
    JOIN dim_date AS d
        ON f.date_key = d.date_key
    GROUP BY d.month_start, d.year, d.month, d.month_short
)
SELECT
    month_start,
    year,
    month,
    month_short,
    total_revenue,
    total_orders,
    active_customers,
    avg_order_value,
    ROUND(
        100.0
        * (total_revenue - LAG(total_revenue) OVER (ORDER BY month_start))
        / NULLIF(LAG(total_revenue) OVER (ORDER BY month_start), 0),
        2
    ) AS revenue_growth_pct
FROM monthly_sales
ORDER BY month_start;
