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
from tools import (
    search_healthy_options,
    store_nutrition_case,
    tool_search_local_docs,
    tool_search_food_database,
    tool_search_online,
)
from utils import encode_image_to_data_url


# ====================== UPDATED SYSTEM PROMPT (DAY 3) ======================
NUTRITION_SYSTEM_PROMPT = """
You are Nutrition AI Expert, a multi-source nutrition coach with access to:

1. LOCAL DOCUMENTS: Comprehensive nutrition guides and healthy food references
2. FOOD DATABASE: Specific nutrition data for common foods (calories, macros, fiber)
3. ONLINE SEARCH: Up-to-date nutrition research and external resources

MANDATORY WORKFLOW (never skip):
Step 1: Analyze the meal (text or image) and estimate nutrition values.
Step 2: Answer user questions, intelligently choosing tools:
    - Use search_food_database for specific food nutrition facts
    - Use search_local_docs for general health/nutrition concepts
    - Use search_online for latest research or external info
    - Use NO tool if you have sufficient knowledge already
Step 3: If requested, store analysis to CSV.

TOOL SELECTION RULES (VERY IMPORTANT):
==================================

DON'T use tools unnecessarily. The agent must be smart about tool selection:

1. SEARCH_FOOD_DATABASE when:
    - User asks "How many calories in [food]?"
    - User asks "What's the protein in [food]?"
    - User wants to compare specific foods
    - Question requires precise nutritional values

2. SEARCH_LOCAL_DOCS when:
    - User asks general questions: "What's fiber good for?"
    - User asks "How much water should I drink?"
    - User asks "What are healthy foods?"
    - Question is conceptual/educational about nutrition

3. SEARCH_ONLINE when:
    - User asks about latest research or trends
    - Question is about recent nutrition news
    - User wants external references or sources
    - Information is time-sensitive

4. NO TOOLS when:
    - You already know the answer (e.g., "What is protein?")
    - Question is general knowledge (e.g., "Benefits of exercise")
    - Follow-up to previous answer in conversation

RESPONSE FORMAT:
================

Always fill NutritionAgentResponse with:
- action_taken: Description of what you did
- disclaimer: Always include safety disclaimer
- search_results: Use when search tools are called
- analysis: Use for meal analyses
- should_store: true only if user explicitly asked
- storage_message: Confirmation message if storing
- source_used: file | database | search | none
- confidence: high | medium | low
- references: short list of source titles (if any)

Include source information:
- Mention which tool provided the information
- Note the source (database/document/search)
- Add confidence level when appropriate

RULES:
======
- Never provide medical or strict diet plans
- Always be honest about limitations
- Avoid tool overuse - prioritize existing knowledge
- If uncertain, use only ONE tool to verify
- Combine multiple sources only when necessary
- Always cite sources: "According to [source]..."
- Keep recommendations safe and general

DISCLAIMER (ALWAYS INCLUDE):
"This is not medical or dietary advice. Consult a qualified professional."
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
    """6) create agent + 7) memory with InMemorySaver + DAY 3 tools."""
    model = init_model(provider=provider, creativity_mode=creativity_mode)
    summary_model = init_model(provider=provider, creativity_mode="strict")
    checkpointer = InMemorySaver()

    system_prompt = f"{NUTRITION_SYSTEM_PROMPT}\n\nStyle: {build_style_prompt(detail_mode)}"

    # Day 3: Extended tools including RAG sources
    tools = [
        search_healthy_options,
        store_nutrition_case,
        tool_search_local_docs,         # NEW: Local document search
        tool_search_food_database,      # NEW: Database search
        tool_search_online,             # NEW: Online search
    ]

    agent = create_agent(
        model=model,
        tools=tools,
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
    """
    Step 2: handle user questions or requests with tools if needed.

    Day 3: Uses intelligent tool selection (local docs, database, online search).
    """
    question = question.strip()
    user_msg = HumanMessage(
        content=(
            "workflow_step=2\n"
            "Use tools if needed (but only if necessary). Return NutritionAgentResponse. "
            "Tool guidance: use search_food_database for specific food nutrition, "
            "use search_local_docs for general nutrition concepts, "
            "use search_online for latest research. Don't use tools for common knowledge. "
            f"User question: {question}"
        )
    )

    result = run_agent_turn(bundle=bundle, thread_id=thread_id, user_message=user_msg)
    return result.get("structured_response")
