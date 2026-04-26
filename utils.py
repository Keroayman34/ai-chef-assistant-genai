"""Helper utility functions for the AI Chef Assistant."""

import base64
import mimetypes
from pathlib import Path

from schemas import ChefMealsResponse


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
