SELECT
    c.city,
    p.category,
    SUM(f.revenue) AS revenue
FROM fact_sales f
JOIN dim_product p
ON f.product_id = p.product_id
JOIN dim_customer c
ON f.customer_id = c.customer_id
GROUP BY c.city, p.category
ORDER BY revenue DESC
LIMIT 20;