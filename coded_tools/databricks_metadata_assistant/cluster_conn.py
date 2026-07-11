from Custom_Databricks_Tool import execute_query
result = execute_query("SELECT current_catalog()")
print(result)