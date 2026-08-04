import importlib


def test_export_results_tool_imports() -> None:
    module = importlib.import_module("coded_tools.basic.databricks_metadata_assistant.export_results")
    assert hasattr(module, "ExportResultsTool")
