import os
from pathlib import Path

from dotenv import load_dotenv
from databricks.sdk import WorkspaceClient


def _load_env() -> None:
    """Reload environment values from the project .env file before each request."""
    env_path = Path(__file__).resolve().parents[3] / ".env"
    if env_path.exists():
        load_dotenv(env_path, override=True)


def _build_workspace_kwargs() -> dict:
    """Build Databricks auth kwargs from the active environment values."""
    _load_env()

    kwargs: dict = {}
    host = os.getenv("DATABRICKS_HOST")
    if host:
        kwargs["host"] = host

    token = os.getenv("DATABRICKS_TOKEN")
    if token:
        kwargs["token"] = token
    else:
        azure_tenant_id = os.getenv("AZURE_TENANT_ID")
        azure_client_id = os.getenv("AZURE_CLIENT_ID")
        azure_client_secret = os.getenv("AZURE_CLIENT_SECRET")
        if azure_tenant_id:
            kwargs["azure_tenant_id"] = azure_tenant_id
        if azure_client_id:
            kwargs["azure_client_id"] = azure_client_id
        if azure_client_secret:
            kwargs["azure_client_secret"] = azure_client_secret

    return kwargs


def get_workspace():
    return WorkspaceClient(**_build_workspace_kwargs())


def execute_query(query):
    _load_env()

    w = get_workspace()

    result = w.statement_execution.execute_statement(
        warehouse_id=os.getenv("WAREHOUSE_ID"),
        statement=query,
        wait_timeout="30s",
    )

    # Normalize the Databricks SDK result into a plain structure that the agent can inspect.
    manifest = getattr(result, "manifest", None)
    schema = None
    if manifest is not None:
        schema = getattr(manifest, "schema", None)

    columns = []
    if schema is not None:
        columns = [col.name for col in getattr(schema, "columns", []) or []]

    data_rows = []
    if hasattr(result, "result") and hasattr(result.result, "data_array"):
        data_array = getattr(result.result, "data_array") or []
        for row in data_array:
            if not row:
                continue
            data_rows.append(row)

    if columns and data_rows:
        return {
            "columns": columns,
            "rows": data_rows,
            "row_count": len(data_rows),
        }

    return {
        "statement_id": getattr(result, "statement_id", None),
        "status": getattr(getattr(result, "status"), "state", None),
        "manifest": getattr(result, "manifest", None),
    }