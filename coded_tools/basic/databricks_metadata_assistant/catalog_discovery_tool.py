from neuro_san.interfaces.coded_tool import CodedTool
from .custom_databricks_tool import get_workspace


class CatalogDiscoveryTool(CodedTool):

    def invoke(self, args, sly_data):

        print("===== CatalogDiscoveryTool invoked =====")
        print(f"args={args}")

        w = get_workspace()

        catalogs = []

        for c in w.catalogs.list():
            catalogs.append({
                "name": c.name,
                "comment": c.comment
            })

        print("Returning catalogs")
        return catalogs