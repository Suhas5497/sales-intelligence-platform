SELECT
    c.segment,
    SUM(f.revenue) AS revenue,
    COUNT(DISTINCT f.customer_id) AS unique_customers
FROM fact_sales f
JOIN dim_customer c
ON f.customer_id = c.customer_id
GROUP BY c.segment
ORDER BY revenue DESC;