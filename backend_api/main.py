"""FastAPI wrapper for the existing AI Chef Assistant logic."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from chef_agent import create_chef_agent, run_step_1_and_2, run_step_4_and_5

APP_ROOT = Path(__file__).resolve().parent.parent
UPLOAD_DIR = APP_ROOT / "backend_api" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


class StartChatRequest(BaseModel):
    thread_id: str = Field(default="chef-thread-1")
    provider: Literal["openai", "ollama"] = Field(default="openai")
    creativity_mode: Literal["strict", "creative"] = Field(default="strict")
    detail_mode: Literal["concise", "detailed"] = Field(default="concise")
    ingredient_text: str
    image_id: str | None = None


class SelectMealRequest(BaseModel):
    thread_id: str
    meal_name: str


class ConfirmMealRequest(BaseModel):
    thread_id: str


class ThreadState(BaseModel):
    provider: Literal["openai", "ollama"]
    creativity_mode: Literal["strict", "creative"]
    detail_mode: Literal["concise", "detailed"]
    last_meals: list[dict[str, Any]] = Field(default_factory=list)
    selected_meal: str | None = None


class ChefSessionManager:
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


session_manager = ChefSessionManager()

app = FastAPI(title="AI Chef Assistant API", version="1.0.0")

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
    agent = session_manager.get_agent(
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

    meals_response = run_step_1_and_2(
        agent=agent,
        thread_id=request.thread_id,
        ingredient_text=request.ingredient_text,
        image_path=image_path,
    )

    if meals_response is None or not meals_response.meals:
        raise HTTPException(status_code=500, detail="No meals returned by the model.")

    meals_dict = meals_response.model_dump()

    session_manager.set_thread_state(
        request.thread_id,
        ThreadState(
            provider=request.provider,
            creativity_mode=request.creativity_mode,
            detail_mode=request.detail_mode,
            last_meals=meals_dict["meals"],
        ),
    )

    session_manager.add_history(
        request.thread_id,
        role="user",
        content=request.ingredient_text,
        payload={"type": "ingredients"},
    )
    session_manager.add_history(
        request.thread_id,
        role="assistant",
        content="Here are meal suggestions based on your ingredients.",
        payload={"type": "meals", "data": meals_dict["meals"]},
    )

    return {
        "thread_id": request.thread_id,
        "workflow_step": 2,
        "meals": meals_dict["meals"],
        "message": "Meal suggestions ready.",
    }


@app.post("/chat/select-meal")
def chat_select_meal(request: SelectMealRequest) -> dict[str, Any]:
    state = session_manager.get_thread_state(request.thread_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Thread not found. Start chat first.")

    meal_exists = any(m.get("meal_name") == request.meal_name for m in state.last_meals)
    if not meal_exists:
        raise HTTPException(status_code=400, detail="Selected meal is not in current suggestions.")

    state.selected_meal = request.meal_name
    session_manager.set_thread_state(request.thread_id, state)

    session_manager.add_history(
        request.thread_id,
        role="user",
        content=f"I choose: {request.meal_name}",
        payload={"type": "selected_meal", "meal_name": request.meal_name},
    )
    session_manager.add_history(
        request.thread_id,
        role="assistant",
        content=f"Great choice: {request.meal_name}. Please confirm to generate full recipe.",
        payload={"type": "confirm_prompt", "meal_name": request.meal_name},
    )

    return {
        "thread_id": request.thread_id,
        "workflow_step": 4,
        "selected_meal": request.meal_name,
        "message": f"Meal '{request.meal_name}' selected. Please confirm.",
    }


@app.post("/chat/confirm")
def chat_confirm(request: ConfirmMealRequest) -> dict[str, Any]:
    state = session_manager.get_thread_state(request.thread_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Thread not found. Start chat first.")
    if not state.selected_meal:
        raise HTTPException(status_code=400, detail="No selected meal. Call /chat/select-meal first.")

    agent = session_manager.get_agent(
        provider=state.provider,
        creativity_mode=state.creativity_mode,
        detail_mode=state.detail_mode,
    )

    final_recipe = run_step_4_and_5(
        agent=agent,
        thread_id=request.thread_id,
        meal_name=state.selected_meal,
    )

    if final_recipe is None or not final_recipe.meals:
        raise HTTPException(status_code=500, detail="No recipe returned by the model.")

    recipe_dict = final_recipe.model_dump()

    session_manager.add_history(
        request.thread_id,
        role="user",
        content=f"Confirm meal: {state.selected_meal}",
        payload={"type": "confirm_meal", "meal_name": state.selected_meal},
    )
    session_manager.add_history(
        request.thread_id,
        role="assistant",
        content="Your final recipe is ready.",
        payload={"type": "recipe", "data": recipe_dict["meals"][0]},
    )

    return {
        "thread_id": request.thread_id,
        "workflow_step": 5,
        "recipe": recipe_dict["meals"][0],
        "message": "Recipe ready.",
    }


@app.get("/history/{thread_id}")
def get_history(thread_id: str) -> dict[str, Any]:
    state = session_manager.get_thread_state(thread_id)
    return {
        "thread_id": thread_id,
        "state": state.model_dump() if state else None,
        "messages": session_manager.get_history(thread_id),
    }
