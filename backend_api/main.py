"""FastAPI wrapper for the Nutrition AI Assistant logic."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from chef_agent import create_chef_agent, run_nutrition_analysis, run_nutrition_followup

APP_ROOT = Path(__file__).resolve().parent.parent
UPLOAD_DIR = APP_ROOT / "backend_api" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


class StartChatRequest(BaseModel):
    thread_id: str = Field(default="nutrition-thread-1")
    provider: Literal["openai", "ollama"] = Field(default="openai")
    creativity_mode: Literal["strict", "creative"] = Field(default="strict")
    detail_mode: Literal["concise", "detailed"] = Field(default="concise")
    meal_text: str
    image_id: str | None = None


class AskNutritionRequest(BaseModel):
    thread_id: str
    message: str


class ThreadState(BaseModel):
    provider: Literal["openai", "ollama"]
    creativity_mode: Literal["strict", "creative"]
    detail_mode: Literal["concise", "detailed"]
    last_response: dict[str, Any] | None = None
    summary: str | None = None


class NutritionSessionManager:
    """Small in-memory manager to keep thread/session state beginner-friendly."""

    def __init__(self) -> None:
        self._agents: dict[tuple[str, str, str], Any] = {}
        self._threads: dict[str, ThreadState] = {}
        self._history: dict[str, list[dict[str, Any]]] = {}

    def get_agent(self, provider: str, creativity_mode: str, detail_mode: str):
        key = (provider, creativity_mode, detail_mode)
        if key not in self._agents:
            self._agents[key] = create_chef_agent(
                provider=provider,
                creativity_mode=creativity_mode,
                detail_mode=detail_mode,
            )
        return self._agents[key]

    def add_history(self, thread_id: str, role: Literal["user", "assistant", "system"], content: str, payload: Any = None) -> None:
        if thread_id not in self._history:
            self._history[thread_id] = []

        self._history[thread_id].append(
            {
                "id": str(uuid4()),
                "role": role,
                "content": content,
                "payload": payload,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    def get_history(self, thread_id: str) -> list[dict[str, Any]]:
        return self._history.get(thread_id, [])

    def set_thread_state(self, thread_id: str, state: ThreadState) -> None:
        self._threads[thread_id] = state

    def get_thread_state(self, thread_id: str) -> ThreadState | None:
        return self._threads.get(thread_id)


session_manager = NutritionSessionManager()

app = FastAPI(title="Nutrition AI Assistant API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)) -> dict[str, str]:
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Please upload an image file.")

    suffix = Path(file.filename or "image.jpg").suffix or ".jpg"
    image_id = f"{uuid4()}{suffix}"
    save_path = UPLOAD_DIR / image_id

    contents = await file.read()
    save_path.write_bytes(contents)

    return {"image_id": image_id, "filename": file.filename or image_id}


@app.post("/chat/start")
def chat_start(request: StartChatRequest) -> dict[str, Any]:
    agent_bundle = session_manager.get_agent(
        provider=request.provider,
        creativity_mode=request.creativity_mode,
        detail_mode=request.detail_mode,
    )

    image_path: str | None = None
    if request.image_id:
        candidate = UPLOAD_DIR / request.image_id
        if candidate.exists():
            image_path = str(candidate)
        else:
            raise HTTPException(status_code=404, detail="Uploaded image not found.")

    nutrition_response = run_nutrition_analysis(
        bundle=agent_bundle,
        thread_id=request.thread_id,
        meal_text=request.meal_text,
        image_path=image_path,
    )

    if nutrition_response is None:
        raise HTTPException(status_code=500, detail="No nutrition response returned by the model.")

    response_dict = nutrition_response.model_dump()

    session_manager.set_thread_state(
        request.thread_id,
        ThreadState(
            provider=request.provider,
            creativity_mode=request.creativity_mode,
            detail_mode=request.detail_mode,
            last_response=response_dict,
            summary=agent_bundle.context.get_summary(request.thread_id),
        ),
    )

    session_manager.add_history(
        request.thread_id,
        role="user",
        content=request.meal_text,
        payload={"type": "meal"},
    )
    session_manager.add_history(
        request.thread_id,
        role="assistant",
        content=nutrition_response.action_taken,
        payload={"type": "nutrition", "data": response_dict},
    )

    return {
        "thread_id": request.thread_id,
        "workflow_step": 1,
        "nutrition": response_dict,
        "message": "Nutrition analysis ready.",
    }


@app.post("/chat/message")
def chat_message(request: AskNutritionRequest) -> dict[str, Any]:
    state = session_manager.get_thread_state(request.thread_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Thread not found. Start chat first.")

    agent_bundle = session_manager.get_agent(
        provider=state.provider,
        creativity_mode=state.creativity_mode,
        detail_mode=state.detail_mode,
    )

    nutrition_response = run_nutrition_followup(
        bundle=agent_bundle,
        thread_id=request.thread_id,
        question=request.message,
    )

    if nutrition_response is None:
        raise HTTPException(status_code=500, detail="No response returned by the model.")

    response_dict = nutrition_response.model_dump()
    state.last_response = response_dict
    state.summary = agent_bundle.context.get_summary(request.thread_id)
    session_manager.set_thread_state(request.thread_id, state)

    session_manager.add_history(
        request.thread_id,
        role="user",
        content=request.message,
        payload={"type": "question"},
    )
    session_manager.add_history(
        request.thread_id,
        role="assistant",
        content=nutrition_response.action_taken,
        payload={"type": "nutrition", "data": response_dict},
    )

    return {
        "thread_id": request.thread_id,
        "workflow_step": 2,
        "nutrition": response_dict,
        "message": "Nutrition response ready.",
    }


@app.get("/history/{thread_id}")
def get_history(thread_id: str) -> dict[str, Any]:
    state = session_manager.get_thread_state(thread_id)
    return {
        "thread_id": thread_id,
        "state": state.model_dump() if state else None,
        "messages": session_manager.get_history(thread_id),
    }
