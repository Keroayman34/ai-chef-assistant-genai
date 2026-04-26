"""CLI entry point for AI Chef Assistant."""

from chef_agent import create_chef_agent, run_step_1_and_2, run_step_4_and_5
from utils import normalize_mode, print_final_recipe, print_meals


def main() -> None:
    print("=== AI Chef Assistant ===")
    print("This lab has two backends: OpenAI and Ollama (mistral).")

    provider = input("Choose backend (openai/ollama) [openai]: ").strip().lower() or "openai"
    if provider not in {"openai", "ollama"}:
        provider = "openai"

    creativity_mode = normalize_mode(
        input("Creativity mode (strict/creative) [strict]: "),
        allowed=("strict", "creative"),
        default="strict",
    )
    detail_mode = normalize_mode(
        input("Response mode (concise/detailed) [concise]: "),
        allowed=("concise", "detailed"),
        default="concise",
    )

    thread_id = input("Thread id for memory [chef-thread-1]: ").strip() or "chef-thread-1"

    print("\nInitializing chef agent...")
    agent = create_chef_agent(
        provider=provider,
        creativity_mode=creativity_mode,
        detail_mode=detail_mode,
    )

    # Step 1: Analyze ingredients
    ingredient_text = input("\nEnter available ingredients (comma-separated): ").strip()

    # Step 8 optional image support
    image_path = input("Optional ingredient image path (or press Enter to skip): ").strip() or None
    if provider == "ollama" and image_path:
        print("Note: image input may not be supported on your local mistral setup. Continuing anyway.")

    # Step 2: Suggest meals
    meals_response = run_step_1_and_2(
        agent=agent,
        thread_id=thread_id,
        ingredient_text=ingredient_text,
        image_path=image_path,
    )

    if not meals_response or not meals_response.meals:
        print("No meals returned by the model.")
        return

    print_meals(meals_response)

    # Step 3: Ask user preference
    print("\nStep 3: Which suggested meal do you prefer?")
    choice_raw = input("\nPick meal number: ").strip()
    try:
        idx = max(1, min(int(choice_raw), len(meals_response.meals)))
    except ValueError:
        idx = 1

    selected_meal = meals_response.meals[idx - 1].meal_name

    # Step 4 + Step 5
    confirmation = input(f"Confirm meal '{selected_meal}'? (yes/no) [yes]: ").strip().lower() or "yes"
    if confirmation not in {"yes", "y"}:
        print("Okay, run again and pick another meal.")
        return

    final_recipe = run_step_4_and_5(agent=agent, thread_id=thread_id, meal_name=selected_meal)
    print_final_recipe(final_recipe)


if __name__ == "__main__":
    main()
