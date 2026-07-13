# test_connection.py

from .Custom_Databricks_Tool import get_workspace

w = get_workspace()

for c in w.catalogs.list():
    print(c.name)

print("Connection Successful")