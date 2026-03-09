SELECT
    c.city,
    SUM(f.revenue) AS city_revenue,
    COUNT(DISTINCT f.order_id) AS orders
FROM fact_sales f
JOIN dim_customer c
ON f.customer_id = c.customer_id
GROUP BY c.city
ORDER BY city_revenue DESC;