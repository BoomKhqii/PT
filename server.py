from typing import Literal
from time import perf_counter

from fastapi import FastAPI
from pydantic import BaseModel

from main import ask_pt
from main import speak

from piper import PiperVoice
from pathlib import Path

# FastAPI discovers this application when running "fastapi dev server.py".
app = FastAPI()


class ChatRequest(BaseModel):
    # Validate incoming JSON and restrict agent names before calling PT.
    message: str
    listening: bool = False
    desktop_context: Literal["unknown", "youtube", "direct3d_fullscreen"] = "unknown"
    agent: Literal["general", "personal", "academic", "trading"] = "general"


@app.post("/chat")
def chat(request: ChatRequest):
    # A synchronous endpoint lets FastAPI run PT's blocking work in a thread pool.
    answer = ask_pt(
        message=request.message,
        # API calls currently start with empty history and bypass the CLI graph.
        history=[],
        agent=request.agent,
        listening=request.listening,
        desktop_context=request.desktop_context,
    )
    return {"reply": answer}
    if answer:
        voice = PiperVoice.load(str(Path(__file__).resolve().parent / "en_GB-jenny_dioco-medium.onnx"))
        started = perf_counter()
        speak(answer, voice)
        playback = [started, perf_counter()]
    # The orb reads this JSON field and displays it in the response panel.
    return {"reply": answer, "playback": playback}
