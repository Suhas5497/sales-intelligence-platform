-- Top Products

SELECT
    p.product_name,
    SUM(f.revenue) AS revenue
FROM fact_sales f
JOIN dim_product p
ON f.product_id = p.product_id
GROUP BY p.product_name
ORDER BY revenue DESC
LIMIT 10;

-- Category Performance

SELECT
    p.category,
    SUM(f.revenue) AS revenue,
    SUM(f.quantity) AS units_sold
FROM fact_sales f
JOIN dim_product p
ON f.product_id = p.product_id
GROUP BY p.category
ORDER BY revenue DESC;