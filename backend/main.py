from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .assistant import ask_agent

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


@app.get("/")
def health() -> dict:
    return {"status": "ok"}


@app.post("/ask")
def ask(req: QueryRequest) -> dict:
    answer = ask_agent(req.question)
    return {"answer": answer}
