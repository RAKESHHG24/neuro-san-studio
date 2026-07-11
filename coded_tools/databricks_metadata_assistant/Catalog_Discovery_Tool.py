from neuro_san.interfaces.coded_tool import CodedTool
from .Custom_Databricks_Tool import get_workspace


class CatalogDiscoveryTool(CodedTool):

    def invoke(self, args, sly_data):

        print("===== CatalogDiscoveryTool INVOKED =====")
        print("ARGS:", args)

        w = get_workspace()

        catalogs = []

        for c in w.catalogs.list():
            catalogs.append({
                "name": c.name,
                "comment": c.comment
            })

        return catalogs