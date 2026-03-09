SELECT
    d.hour,
    SUM(f.revenue) AS revenue,
    COUNT(f.order_id) AS orders
FROM fact_sales f
JOIN dim_date d
ON f.date_id = d.date_id
GROUP BY d.hour
ORDER BY d.hour;