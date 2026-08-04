import os
import re
from pathlib import Path

from fastapi import HTTPException
from leaf_common.time.timeout_reached_exception import TimeoutReachedException

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:  # pragma: no cover - fallback for lightweight environments
    def load_dotenv(*args, **kwargs):
        return False

# Ensure the repo root is the working directory so HOCON includes resolve correctly.
REPO_ROOT = Path(__file__).resolve().parents[1]
os.chdir(REPO_ROOT)

load_dotenv(REPO_ROOT / ".env", override=False)

os.environ["AGENT_MANIFEST_FILE"] = str(REPO_ROOT / "registries" / "databricks_manifest.hocon")
if not os.getenv("AGENT_TOOL_PATH"):
    os.environ["AGENT_TOOL_PATH"] = str(REPO_ROOT / "coded_tools")

try:
    from neuro_san.client.agent_session_factory import AgentSessionFactory
    from neuro_san.client.streaming_input_processor import StreamingInputProcessor
except ModuleNotFoundError as exc:
    raise RuntimeError(
        "Neuro SAN package is not installed in the backend environment. "
        "Install it with `pip install neuro-san==0.6.76` and restart.`"
    ) from exc

from coded_tools.basic.databricks_metadata_assistant.custom_databricks_tool import execute_query


_NUMBER_WORDS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
}


def _extract_limit(question: str) -> int:
    lower_q = question.lower()

    digit_match = re.search(r"\b(\d{1,3})\b", lower_q)
    if digit_match:
        return max(1, int(digit_match.group(1)))

    for word, value in _NUMBER_WORDS.items():
        if re.search(rf"\b{word}\b", lower_q):
            return value

    return 5


def _build_preview_sql(question: str) -> str | None:
    stripped = question.strip()
    lower_q = stripped.lower()

    if lower_q.startswith("select "):
        return stripped

    if not re.search(r"\b(sample|records?|rows?|top|first|show|preview)\b", lower_q):
        return None

    pattern = re.compile(
        r"from\s+(?P<table>[a-zA-Z0-9_]+)\s+table\s+from\s+(?P<catalog>[a-zA-Z0-9_]+)\s+catalog\s+and\s+(?P<schema>[a-zA-Z0-9_]+)\s+(?:schema|database)",
        re.IGNORECASE,
    )
    match = pattern.search(stripped)
    if not match:
        return None

    table = match.group("table")
    catalog = match.group("catalog")
    schema = match.group("schema")
    limit = _extract_limit(stripped)

    return f"SELECT * FROM {catalog}.{schema}.{table} LIMIT {limit}"


def _format_query_result(result: dict) -> str:
    if not isinstance(result, dict):
        return str(result)

    if result.get("error"):
        return f"Query failed: {result['error']}"

    rows = result.get("rows") or []
    columns = result.get("columns") or []
    if not rows:
        return "Query executed successfully, but no rows were returned."

    lines = [f"Returned {len(rows)} row(s)."]
    if columns:
        lines.append("Columns: " + ", ".join(columns))

    for idx, row in enumerate(rows, start=1):
        lines.append(f"{idx}. {row}")

    return "\n".join(lines)


def _new_agent_session():
    factory = AgentSessionFactory()
    return factory.create_session(
        session_type="direct",
        agent_name="basic/databricks_metadata_assistant",
        hostname=None,
        port=None,
        use_direct=False,
        metadata={"user_id": "web_user"},
        connect_timeout_in_seconds=30.0,
    )


_session = None
_thread_state = None


def _initialize():
    global _session, _thread_state
    if _session is None:
        _session = _new_agent_session()
        _thread_state = {
            "last_chat_response": None,
            "prompt": "",
            "timeout": 5000.0,
            "num_input": 0,
            "user_input": None,
            "sly_data": None,
            "chat_filter": {"chat_filter_type": "MAXIMAL"},
        }


def ask_agent(question: str) -> str:
    global _thread_state
    if not question or not question.strip():
        raise HTTPException(status_code=400, detail="Question is required.")

    preview_sql = _build_preview_sql(question)
    if preview_sql:
        try:
            return _format_query_result(execute_query(preview_sql))
        except Exception as exc:  # pylint: disable=broad-except
            raise HTTPException(status_code=500, detail=f"Query execution failed: {exc}") from exc

    _initialize()

    input_processor = StreamingInputProcessor(
        "DEFAULT",
        "/tmp/agent_thinking.txt",
        _session,
        None,
    )

    _thread_state["user_input"] = question

    try:
        _thread_state = input_processor.process_once(_thread_state)
    except TimeoutReachedException as exc:
        last_answer = _thread_state.get("last_chat_response")
        if isinstance(last_answer, str) and last_answer.strip():
            return last_answer
        raise HTTPException(
            status_code=504,
            detail="Assistant request timed out before completion. Please retry.",
        ) from exc
    answer = _thread_state.get("last_chat_response")

    if not answer:
        raise HTTPException(status_code=500, detail="Assistant did not return a response.")

    if isinstance(answer, str) and (
        answer.startswith("Error from ")
        or "Could not resolve authentication method" in answer
        or "OPENAI_API_KEY" in answer
    ):
        raise HTTPException(status_code=503, detail=answer)

    return answer
