"""Chef agent creation and prompt logic using latest LangChain style."""

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver

from config import SETTINGS, get_temperature
from schemas import ChefMealsResponse
from utils import encode_image_to_data_url


# 5) chef system prompt
CHEF_SYSTEM_PROMPT = """
You are AI Chef Assistant, a real chef persona.
You are friendly and practical, and you never skip required workflow steps.

MANDATORY WORKFLOW (never skip, never reorder):
Step 1: Analyze available ingredients.
Step 2: Suggest meal options.
Step 3: Ask for user preference.
Step 4: Confirm selected meal.
Step 5: Return final recipe.

Rules:
- Always respect workflow_step provided by developer/user messages.
- If the current step is not enough to continue, ask only what is needed for the next step.
- Keep output in the required structured format.
- Ingredient status must be either 'available' or 'not_available'.
- Never invent unavailable ingredients as available.
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


def create_chef_agent(provider: str, creativity_mode: str, detail_mode: str):
    """6) create agent + 7) memory with InMemorySaver."""
    model = init_model(provider=provider, creativity_mode=creativity_mode)
    checkpointer = InMemorySaver()

    system_prompt = f"{CHEF_SYSTEM_PROMPT}\n\nStyle: {build_style_prompt(detail_mode)}"

    agent = create_agent(
        model=model,
        tools=[],
        system_prompt=system_prompt,
        checkpointer=checkpointer,
        response_format=ChefMealsResponse,
    )
    return agent


def build_ingredient_message(ingredient_text: str, image_path: str | None):
    """8) optional image input support.

    For OpenAI vision-capable chat models, send mixed text + image message.
    """
    ingredient_text = ingredient_text.strip()

    if image_path:
        data_url = encode_image_to_data_url(image_path)
        return HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": (
                        "workflow_step=1\n"
                        "Analyze these ingredients from text and image. "
                        f"User text: {ingredient_text}"
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
            "Analyze these ingredients from text only. "
            f"User text: {ingredient_text}"
        )
    )


def run_agent_step(agent, thread_id: str, prompt_text: str):
    """Helper to invoke the same conversation thread."""
    return agent.invoke(
        {"messages": [HumanMessage(content=prompt_text)]},
        config={"configurable": {"thread_id": thread_id}},
    )


def run_step_1_and_2(agent, thread_id: str, ingredient_text: str, image_path: str | None = None):
    """Run workflow step 1 + step 2 and return structured meals."""
    ingredient_msg = build_ingredient_message(ingredient_text=ingredient_text, image_path=image_path)

    result = agent.invoke(
        {
            "messages": [
                ingredient_msg,
                HumanMessage(
                    content=(
                        "workflow_step=2\n"
                        "Now suggest meal options using only available ingredients where possible. "
                        "Return structured meals list."
                    )
                ),
            ]
        },
        config={"configurable": {"thread_id": thread_id}},
    )
    return result.get("structured_response")


def run_step_4_and_5(agent, thread_id: str, meal_name: str):
    """Run workflow step 4 + step 5 and return final recipe."""
    result = agent.invoke(
        {
            "messages": [
                HumanMessage(
                    content=(
                        "workflow_step=4\n"
                        f"I choose this meal: {meal_name}. Confirm it briefly."
                    )
                ),
                HumanMessage(
                    content=(
                        "workflow_step=5\n"
                        "Now return the final recipe for only the selected meal in the same structured format. "
                        "Return exactly one meal in meals list."
                    )
                ),
            ]
        },
        config={"configurable": {"thread_id": thread_id}},
    )
    return result.get("structured_response")
