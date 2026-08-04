import csv
from pathlib import Path

try:
    from neuro_san.interfaces.coded_tool import CodedTool
except ModuleNotFoundError:  # pragma: no cover - allows import in lightweight test environments
    class CodedTool:  # type: ignore[override]
        """Fallback stub used when the neuro_san runtime is not installed."""

        def __init__(self):
            pass

from .custom_databricks_tool import execute_query


class ExportResultsTool(CodedTool):
    """Execute a SQL query and save the result to a CSV or Excel-compatible file."""

    def invoke(self, args, sly_data):
        query = args.get("sql_query") or args.get("query") or ""
        output_format = (args.get("output_format") or "csv").lower()
        file_name = args.get("file_name") or "databricks_export"

        if not query.strip():
            return {"error": "No SQL query provided."}

        try:
            result = execute_query(query)
        except Exception as exc:  # pylint: disable=broad-except
            return {"error": str(exc)}

        if isinstance(result, dict) and result.get("error"):
            return result

        rows = result.get("rows", [])
        columns = result.get("columns", [])

        export_dir = Path(__file__).resolve().parents[3] / "exports"
        export_dir.mkdir(parents=True, exist_ok=True)

        if output_format == "excel" or output_format == "xlsx":
            suffix = ".xlsx"
            try:
                import pandas as pd
            except Exception as exc:  # pylint: disable=broad-except
                return {"error": f"pandas is required for Excel export: {exc}"}

            file_path = export_dir / f"{file_name}{suffix}"
            df = pd.DataFrame(rows, columns=columns)
            df.to_excel(file_path, index=False)
        else:
            suffix = ".csv"
            file_path = export_dir / f"{file_name}{suffix}"
            with file_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                if columns:
                    writer.writerow(columns)
                writer.writerows(rows)

        return {
            "status": "ok",
            "file_path": str(file_path),
            "file_name": file_path.name,
            "format": output_format,
            "row_count": len(rows),
        }
