import duckdb

con = duckdb.connect("warehouse/sales.duckdb")

query = """
SELECT
    SUM(revenue) AS total_revenue
FROM fact_sales
"""

result = con.execute(query).fetchdf()

print(result)