from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

try:
    from .assistant import ask_agent
except ImportError:  # pragma: no cover - allows running as `python main.py` or `uvicorn main:app`
    from assistant import ask_agent

app = FastAPI(title="Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    question: str


@app.api_route("/", methods=["GET", "HEAD"])
def health() -> dict:
    return {"status": "ok"}


@app.post("/ask")
def ask(req: QueryRequest) -> dict:
    answer = ask_agent(req.question)
    return {"answer": answer}
