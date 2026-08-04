import os
from pathlib import Path

from fastapi import HTTPException

# Ensure the repo root is the working directory so HOCON includes resolve correctly.
REPO_ROOT = Path(__file__).resolve().parents[1]
os.chdir(REPO_ROOT)

os.environ.setdefault("AGENT_MANIFEST_FILE", str(REPO_ROOT / "registries" / "manifest.hocon"))
os.environ.setdefault("AGENT_TOOL_PATH", str(REPO_ROOT / "coded_tools"))

try:
    from neuro_san.client.agent_session_factory import AgentSessionFactory
    from neuro_san.client.streaming_input_processor import StreamingInputProcessor
except ModuleNotFoundError as exc:
    raise RuntimeError(
        "Neuro SAN package is not installed in the backend environment. "
        "Install it with `pip install neuro-san==0.6.76` and restart.`"
    ) from exc


def _new_agent_session():
    factory = AgentSessionFactory()
    return factory.create_session(
        session_type="direct",
        agent_name="basic/databricks_metadata_assistant.hocon",
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
    if not question or not question.strip():
        raise HTTPException(status_code=400, detail="Question is required.")

    _initialize()

    input_processor = StreamingInputProcessor(
        "DEFAULT",
        "/tmp/agent_thinking.txt",
        _session,
        None,
    )

    _thread_state["user_input"] = question
    _thread_state = input_processor.process_once(_thread_state)
    answer = _thread_state.get("last_chat_response")

    if not answer:
        raise HTTPException(status_code=500, detail="Assistant did not return a response.")

    return answer
