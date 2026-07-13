from neuro_san.interfaces.coded_tool import CodedTool
from .custom_databricks_tool import get_workspace


class SchemaDiscoveryTool(CodedTool):

    def invoke(self, args, sly_data):

        catalog = args.get("catalog")

        w = get_workspace()

        schemas = []

        for schema in w.schemas.list(
            catalog_name=catalog
        ):
            schemas.append(
                {
                    "name": schema.name,
                    "comment": schema.comment
                }
            )

        return schemas