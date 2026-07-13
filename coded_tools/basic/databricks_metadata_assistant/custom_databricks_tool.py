from dotenv import load_dotenv
load_dotenv()

from databricks.sdk import WorkspaceClient
import os


def get_workspace():

    return WorkspaceClient(
        host=os.getenv("DATABRICKS_HOST"),
        azure_tenant_id=os.getenv("AZURE_TENANT_ID"),
        azure_client_id=os.getenv("AZURE_CLIENT_ID"),
        azure_client_secret=os.getenv("AZURE_CLIENT_SECRET")
    )


def execute_query(query):

    w = get_workspace()

    result = w.statement_execution.execute_statement(
        warehouse_id=os.getenv("WAREHOUSE_ID"),
        statement=query,
        wait_timeout="30s"
    )

    return result