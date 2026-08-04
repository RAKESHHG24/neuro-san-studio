from neuro_san.interfaces.coded_tool import CodedTool
from .custom_databricks_tool import execute_query


class QueryExecutorTool(CodedTool):
    """Execute a SQL query against Databricks and return structured rows."""

    def invoke(self, args, sly_data):
        sql_query = args.get("sql_query") or args.get("query") or ""
        if not sql_query.strip():
            return {"error": "No SQL query provided."}

        try:
            return execute_query(sql_query)
        except Exception as exc:  # pylint: disable=broad-except
            return {"error": str(exc)}
