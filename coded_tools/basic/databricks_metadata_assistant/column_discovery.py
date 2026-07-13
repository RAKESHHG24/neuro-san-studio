import os

from neuro_san.interfaces.coded_tool import CodedTool
from .custom_databricks_tool import execute_query


class ColumnDiscoveryTool(CodedTool):

    def invoke(self, args, sly_data):

        catalog = args.get("catalog")
        schema_name = args.get("schema_name")
        table = args.get("table")

        sql_file = os.path.join(
            os.path.dirname(__file__),
            "Column_Discovery.sql"
        )

        with open(sql_file, "r") as file:
            query = file.read()

        query = query.format(
            catalog=catalog,
        schema=schema_name,
        table=table
        )

        return execute_query(query)