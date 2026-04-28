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


class NutritionEstimate(BaseModel):
    """Estimated nutrition values for a meal."""

    calories_kcal: int = Field(description="Estimated calories in kcal")
    protein_g: float = Field(description="Estimated protein in grams")
    carbs_g: float = Field(description="Estimated carbohydrates in grams")
    fat_g: float = Field(description="Estimated fat in grams")
    fiber_g: float | None = Field(default=None, description="Estimated fiber in grams")


class NutritionSummary(BaseModel):
    """Short, friendly summary for the nutrition analysis."""

    summary_text: str = Field(description="Short nutrition summary")
    macro_balance: str = Field(description="Macro balance overview")
    next_steps: List[str] = Field(description="Safe next-step suggestions")


class MealAnalysis(BaseModel):
    """Full nutrition analysis for a single meal."""

    meal_name: str = Field(description="Name of the meal")
    ingredients: List[IngredientItem] = Field(description="Ingredients list")
    nutrition_estimate: NutritionEstimate = Field(description="Estimated macros")
    nutrition_summary: NutritionSummary = Field(description="Short summary")
    recommendations: List[str] = Field(description="Safe, general recommendations")


class SearchResult(BaseModel):
    """One search result for healthy options or nutrition info."""

    name: str = Field(description="Result name")
    category: str = Field(description="Result category")
    address: str = Field(description="Address or location")
    distance_km: float | None = Field(default=None, description="Estimated distance in km")
    notes: str = Field(description="Helpful notes")
    source: str = Field(description="Where this result came from")


class NutritionAgentResponse(BaseModel):
    """Top-level structured response format for the nutrition agent."""

    analysis: MealAnalysis | None = Field(default=None, description="Meal analysis if available")
    search_results: List[SearchResult] = Field(default_factory=list, description="Search results")
    action_taken: str = Field(description="What the agent did this turn")
    should_store: bool = Field(description="Whether the agent wants to store to CSV")
    storage_message: str | None = Field(default=None, description="Storage confirmation message")
    disclaimer: str = Field(
        description="Required disclaimer text"
    )
