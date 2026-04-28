"""Helper utility functions for the AI Chef Assistant."""

import base64
import mimetypes
from pathlib import Path

from schemas import ChefMealsResponse, NutritionAgentResponse


def encode_image_to_data_url(image_path: str) -> str:
    """Convert a local image to a data URL (for optional image input support)."""
    file_path = Path(image_path)
    if not file_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    mime_type, _ = mimetypes.guess_type(str(file_path))
    mime_type = mime_type or "image/jpeg"

    image_bytes = file_path.read_bytes()
    encoded = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"


def print_meals(meals_response: ChefMealsResponse) -> None:
    """Pretty print meal options in CLI."""
    print("\n--- Suggested Meals ---")
    for idx, meal in enumerate(meals_response.meals, start=1):
        print(f"\n{idx}) {meal.meal_name}")
        print(f"   Cooking time: {meal.cooking_time}")
        print(f"   Serves: {meal.number_of_individuals}")

        print("   Ingredients:")
        for ingredient in meal.ingredients:
            print(f"   - {ingredient.name}: {ingredient.status}")


def print_final_recipe(meals_response: ChefMealsResponse) -> None:
    """Print final selected recipe with full steps."""
    if not meals_response.meals:
        print("No recipe was returned.")
        return

    meal = meals_response.meals[0]
    print("\n=== Final Recipe ===")
    print(f"Meal: {meal.meal_name}")
    print(f"Cooking time: {meal.cooking_time}")
    print(f"Serves: {meal.number_of_individuals}")

    print("\nInstructions:")
    for step_no, step_text in enumerate(meal.instructions, start=1):
        print(f"{step_no}. {step_text}")


def normalize_mode(value: str, allowed: tuple[str, ...], default: str) -> str:
    """Normalize user mode input with a safe default."""
    value = (value or "").strip().lower()
    return value if value in allowed else default


def print_nutrition_analysis(response: NutritionAgentResponse) -> None:
    """Print a nutrition analysis or follow-up response in CLI."""
    print("\n=== Nutrition Response ===")
    if response.analysis:
        analysis = response.analysis
        estimate = analysis.nutrition_estimate
        print(f"Meal: {analysis.meal_name}")
        print(
            "Estimated macros: "
            f"{estimate.calories_kcal} kcal | "
            f"Protein {estimate.protein_g}g | "
            f"Carbs {estimate.carbs_g}g | "
            f"Fat {estimate.fat_g}g"
        )
        if estimate.fiber_g is not None:
            print(f"Fiber: {estimate.fiber_g}g")

        print("\nSummary:")
        print(analysis.nutrition_summary.summary_text)

        print("\nRecommendations:")
        for item in analysis.recommendations:
            print(f"- {item}")

    if response.search_results:
        print("\nSearch Results:")
        for result in response.search_results:
            distance = f" ({result.distance_km} km)" if result.distance_km else ""
            print(f"- {result.name} [{result.category}]{distance}")
            print(f"  {result.address}")
            print(f"  Notes: {result.notes}")

    if response.storage_message:
        print(f"\nStorage: {response.storage_message}")

    print(f"\nDisclaimer: {response.disclaimer}")
