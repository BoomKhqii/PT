from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel

from main import ask_pt

# FastAPI discovers this application when running "fastapi dev server.py".
app = FastAPI()


class ChatRequest(BaseModel):
    # Validate incoming JSON and restrict agent names before calling PT.
    message: str
    agent: Literal["general", "personal", "academic", "trading"] = "general"


@app.post("/chat")
def chat(request: ChatRequest):
    # A synchronous endpoint lets FastAPI run PT's blocking work in a thread pool.
    answer = ask_pt(
        message=request.message,
        # API calls currently start with empty history and bypass the CLI graph.
        history=[],
        agent=request.agent,
    )
    # The orb reads this JSON field and displays it in the response panel.
    return {"reply": answer}
