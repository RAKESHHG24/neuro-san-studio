from Custom_Databricks_Tool import get_workspace

w = get_workspace()

print("Connected to Databricks")

for catalog in w.catalogs.list():
    print(catalog.name)