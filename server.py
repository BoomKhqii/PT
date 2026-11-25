from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel

from main import ask_pt

app = FastAPI()


class ChatRequest(BaseModel):
    message: str
    agent: Literal["general", "personal", "academic", "trading"] = "general"


@app.post("/chat")
def chat(request: ChatRequest):
    answer = ask_pt(
        message=request.message,
        history=[],
        agent=request.agent,
    )
    return {"reply": answer}