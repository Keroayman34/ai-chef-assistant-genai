"""Nutrition agent creation and prompt logic using latest LangChain style."""

from dataclasses import dataclass
from typing import Any

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver

from config import SETTINGS, get_temperature
from middleware import ContextMiddleware
from schemas import NutritionAgentResponse
from tools import search_healthy_options, store_nutrition_case
from utils import encode_image_to_data_url


# 5) nutrition system prompt
NUTRITION_SYSTEM_PROMPT = """
You are Nutrition AI Assistant, a friendly nutrition coach.
You provide safe, general nutrition guidance without medical diagnosis.
You must ALWAYS include this disclaimer in every response:
"This is not medical or dietary advice. Consult a qualified professional."

MANDATORY WORKFLOW (never skip, never reorder):
Step 1: Analyze the meal (text or image) and estimate nutrition values.
Step 2: Answer user questions, optionally using tools.
Step 3: If the user requests storage, confirm and use the CSV tool.

Rules:
- Always respect workflow_step provided by developer/user messages.
- If the current step is not enough to continue, ask only what is needed next.
- Keep output in the required structured format.
- Always fill the NutritionAgentResponse fields: action_taken, should_store, disclaimer.
- Use search_results when the search tool is used.
- Never provide strict diet plans or medical diagnoses.
- Ask before storing to CSV unless the user explicitly requested it.
""".strip()


def build_style_prompt(detail_mode: str) -> str:
    """Return style instructions for concise/detailed mode."""
    if detail_mode.lower() == "detailed":
        return "Use detailed explanations and clear beginner-friendly cooking tips."
    return "Keep answers concise and direct."


def init_model(provider: str, creativity_mode: str):
    """3) init_chat_model for gpt-4o-mini and same flow for Ollama mistral."""
    temperature = get_temperature(creativity_mode)

    if provider == "openai":
        return init_chat_model(
            SETTINGS.openai_model_name,
            model_provider="openai",
            temperature=temperature,
        )

    if provider == "ollama":
        return init_chat_model(
            SETTINGS.ollama_model_name,
            model_provider="ollama",
            temperature=temperature,
        )

    raise ValueError("provider must be 'openai' or 'ollama'")


@dataclass
class NutritionAgentBundle:
    """Simple container for agent + context middleware."""

    agent: Any
    context: ContextMiddleware


def create_chef_agent(provider: str, creativity_mode: str, detail_mode: str) -> NutritionAgentBundle:
    """6) create agent + 7) memory with InMemorySaver."""
    model = init_model(provider=provider, creativity_mode=creativity_mode)
    summary_model = init_model(provider=provider, creativity_mode="strict")
    checkpointer = InMemorySaver()

    system_prompt = f"{NUTRITION_SYSTEM_PROMPT}\n\nStyle: {build_style_prompt(detail_mode)}"

    agent = create_agent(
        model=model,
        tools=[search_healthy_options, store_nutrition_case],
        system_prompt=system_prompt,
        checkpointer=checkpointer,
        response_format=NutritionAgentResponse,
    )

    context = ContextMiddleware(
        summary_model=summary_model,
        max_messages=SETTINGS.max_context_messages,
        summary_trigger=SETTINGS.summary_trigger,
    )

    return NutritionAgentBundle(agent=agent, context=context)


def build_meal_message(meal_text: str, image_path: str | None):
    """Optional image input support for meal analysis."""
    meal_text = meal_text.strip()

    if image_path:
        data_url = encode_image_to_data_url(image_path)
        return HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": (
                        "workflow_step=1\n"
                        "Analyze this meal from text and image. "
                        "Return NutritionAgentResponse with analysis filled, "
                        "search_results empty, and a required disclaimer. "
                        f"User text: {meal_text}"
                    ),
                },
                {
                    "type": "image_url",
                    "image_url": {"url": data_url},
                },
            ]
        )

    return HumanMessage(
        content=(
            "workflow_step=1\n"
            "Analyze this meal from text only. "
            "Return NutritionAgentResponse with analysis filled, "
            "search_results empty, and a required disclaimer. "
            f"User text: {meal_text}"
        )
    )


def run_agent_turn(bundle: NutritionAgentBundle, thread_id: str, user_message: HumanMessage):
    """Invoke the agent with context trimming + summarization."""
    messages = bundle.context.build_messages(thread_id=thread_id, new_message=user_message)

    result = bundle.agent.invoke(
        {"messages": messages},
        config={"configurable": {"thread_id": thread_id}},
    )

    assistant_message = None
    if isinstance(result, dict) and result.get("messages"):
        assistant_message = result["messages"][-1]

    if assistant_message is None:
        assistant_message = AIMessage(content=str(result.get("structured_response")))

    bundle.context.update(thread_id=thread_id, user_message=user_message, assistant_message=assistant_message)
    return result


def run_nutrition_analysis(
    bundle: NutritionAgentBundle,
    thread_id: str,
    meal_text: str,
    image_path: str | None = None,
):
    """Step 1: analyze a meal and return structured nutrition response."""
    meal_msg = build_meal_message(meal_text=meal_text, image_path=image_path)

    result = run_agent_turn(bundle=bundle, thread_id=thread_id, user_message=meal_msg)
    return result.get("structured_response")


def run_nutrition_followup(bundle: NutritionAgentBundle, thread_id: str, question: str):
    """Step 2: handle user questions or requests with tools if needed."""
    question = question.strip()
    user_msg = HumanMessage(
        content=(
            "workflow_step=2\n"
            "Use tools if needed. Return NutritionAgentResponse. "
            f"User question: {question}"
        )
    )

    result = run_agent_turn(bundle=bundle, thread_id=thread_id, user_message=user_msg)
    return result.get("structured_response")
