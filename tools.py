"""Tools used by the Nutrition AI Agent."""

from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from config import SETTINGS
from schemas import SearchResult


class SearchQueryInput(BaseModel):
    """Input schema for the search tool."""

    query: str = Field(description="Search query")
    location: str | None = Field(default=None, description="Optional location")
    max_results: int = Field(default=5, description="Max number of results")


@tool("search_healthy_options", args_schema=SearchQueryInput)
def search_healthy_options(query: str, location: str | None = None, max_results: int = 5) -> List[dict]:
    """Search for healthy food options or nutrition info.

    This lab tool returns curated, example-style results. Replace with a real API later.
    """

    location_label = location or "near you"
    seed_results = [
        SearchResult(
            name="Green Bowl Kitchen",
            category="Healthy restaurant",
            address=f"123 Market St, {location_label}",
            distance_km=1.2,
            notes="Salad bowls, grilled proteins, macro-friendly options.",
            source="demo_search",
        ),
        SearchResult(
            name="FreshCart Grocers",
            category="Healthy grocery store",
            address=f"52 Orchard Rd, {location_label}",
            distance_km=2.4,
            notes="Fresh produce and lean proteins available.",
            source="demo_search",
        ),
        SearchResult(
            name="MacroFuel Meal Prep",
            category="Meal prep service",
            address=f"Online delivery in {location_label}",
            distance_km=None,
            notes="Balanced meals with nutrition labels.",
            source="demo_search",
        ),
        SearchResult(
            name="Nutrition Info Hub",
            category="Nutrition lookup",
            address="https://fdc.nal.usda.gov/",
            distance_km=None,
            notes="USDA FoodData Central for nutrition facts.",
            source="demo_search",
        ),
    ]

    results = seed_results[: max(1, min(max_results, len(seed_results)))]
    if query:
        results = [
            result.model_copy(update={"notes": f"Query match: {query}. {result.notes}"})
            for result in results
        ]
    return [item.model_dump() for item in results]


class NutritionCaseInput(BaseModel):
    """Input schema for storing a nutrition case to CSV."""

    meal: str = Field(description="Meal name or description")
    calories_estimate: int = Field(description="Estimated calories in kcal")
    macros_summary: str = Field(description="Short macros summary")
    goals: str = Field(description="User goals")
    recommendations: str = Field(description="Short recommendations")
    timestamp: str | None = Field(default=None, description="ISO timestamp")


@tool("store_nutrition_case", args_schema=NutritionCaseInput)
def store_nutrition_case(
    meal: str,
    calories_estimate: int,
    macros_summary: str,
    goals: str,
    recommendations: str,
    timestamp: str | None = None,
) -> str:
    """Store a nutrition case to CSV for simple logging."""

    csv_path = Path(SETTINGS.nutrition_csv_path)
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    timestamp = timestamp or datetime.now(timezone.utc).isoformat()
    row = {
        "meal": meal,
        "calories_estimate": calories_estimate,
        "macros_summary": macros_summary,
        "goals": goals,
        "recommendations": recommendations,
        "timestamp": timestamp,
    }

    write_header = not csv_path.exists()
    with csv_path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=row.keys())
        if write_header:
            writer.writeheader()
        writer.writerow(row)

    return f"Saved nutrition case to CSV: {csv_path.name}"
