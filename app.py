"""CLI entry point for Nutrition AI Assistant."""

from chef_agent import create_chef_agent, run_nutrition_analysis, run_nutrition_followup
from utils import normalize_mode, print_nutrition_analysis


def main() -> None:
    print("=== Nutrition AI Assistant ===")
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

    thread_id = input("Thread id for memory [nutrition-thread-1]: ").strip() or "nutrition-thread-1"

    print("\nInitializing nutrition agent...")
    agent_bundle = create_chef_agent(
        provider=provider,
        creativity_mode=creativity_mode,
        detail_mode=detail_mode,
    )

    # Step 1: Analyze meal
    meal_text = input("\nDescribe your meal (or ingredients): ").strip()

    # Step 8 optional image support
    image_path = input("Optional food image path (or press Enter to skip): ").strip() or None
    if provider == "ollama" and image_path:
        print("Note: image input may not be supported on your local mistral setup. Continuing anyway.")

    # Step 2: Nutrition analysis
    analysis = run_nutrition_analysis(
        bundle=agent_bundle,
        thread_id=thread_id,
        meal_text=meal_text,
        image_path=image_path,
    )

    if not analysis:
        print("No nutrition analysis returned by the model.")
        return

    print_nutrition_analysis(analysis)

    # Step 3: Follow-up questions
    while True:
        followup = input("\nAsk a nutrition question (or press Enter to exit): ").strip()
        if not followup:
            break

        response = run_nutrition_followup(
            bundle=agent_bundle,
            thread_id=thread_id,
            question=followup,
        )
        if response:
            print_nutrition_analysis(response)
        else:
            print("No response returned by the model.")


if __name__ == "__main__":
    main()


