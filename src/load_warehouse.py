import duckdb
import pandas as pd

con = duckdb.connect("warehouse/sales.duckdb")

fact = pd.read_csv("warehouse/fact_sales.csv")
prod = pd.read_csv("warehouse/dim_product.csv")
cust = pd.read_csv("warehouse/dim_customer.csv")
date = pd.read_csv("warehouse/dim_date.csv")

con.execute("CREATE TABLE fact_sales AS SELECT * FROM fact")
con.execute("CREATE TABLE dim_product AS SELECT * FROM prod")
con.execute("CREATE TABLE dim_customer AS SELECT * FROM cust")
con.execute("CREATE TABLE dim_date AS SELECT * FROM date")

print("Warehouse loaded into DuckDB")