"""Pydantic schemas for fixed structured output."""

from typing import List, Literal

from pydantic import BaseModel, Field


class IngredientItem(BaseModel):
    """One ingredient in a meal and whether it exists in user pantry."""

    name: str = Field(description="Ingredient name")
    status: Literal["available", "not_available"] = Field(
        description="Use 'available' if the ingredient exists, otherwise 'not_available'"
    )


class MealItem(BaseModel):
    """One meal option in the response list."""

    meal_name: str = Field(description="Name of the meal")
    cooking_time: str = Field(description="Estimated cooking time")
    number_of_individuals: int = Field(
        description="How many people this meal serves"
    )
    instructions: List[str] = Field(
        description="Step-by-step cooking instructions as a list"
    )
    ingredients: List[IngredientItem] = Field(
        description="Ingredients with availability status"
    )


class ChefMealsResponse(BaseModel):
    """Top-level fixed response format from the chef assistant."""

    meals: List[MealItem] = Field(description="List of possible meals")
