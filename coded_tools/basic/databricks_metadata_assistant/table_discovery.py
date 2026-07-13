from neuro_san.interfaces.coded_tool import CodedTool
from .custom_databricks_tool import get_workspace


class TableDiscoveryTool(CodedTool):

    def invoke(self, args, sly_data):

        catalog = args.get("catalog")
        schema_name = args.get("schema_name")

        w = get_workspace()

        tables = []

        for table in w.tables.list(
            catalog_name=catalog,
            schema_name=schema_name
        ):
            tables.append(
                {
                    "name": table.name,
                    "type": str(table.table_type),
                    "comment": table.comment
                }
            )

        return tables