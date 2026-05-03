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
from rag import search_local_docs
from db import search_food_database


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

# ====================== NEW RAG & MULTI-SOURCE TOOLS (DAY 3) ======================


class LocalDocQueryInput(BaseModel):
    """Input schema for searching local documents."""

    query: str = Field(description="Nutrition or health question to search in local documents")
    top_k: int = Field(default=3, description="Number of relevant passages to return")


@tool("search_local_docs", args_schema=LocalDocQueryInput)
def tool_search_local_docs(query: str, top_k: int = 3) -> str:
    """
    Search local nutrition documents (RAG).
    
    Use this when the user asks general nutrition questions that would be covered
    in a nutrition guide or healthy foods reference.
    
    Examples:
    - "What are the benefits of protein?"
    - "How many calories in an apple?"
    - "What is fiber good for?"
    """
    results = search_local_docs(query, top_k=top_k)
    
    if not results:
        return "No relevant information found in local documents."
    
    response = "Found relevant information from local documents:\n\n"
    for i, result in enumerate(results, 1):
        response += f"{i}. From '{result['source'].replace('_', ' ').title()}':\n"
        response += f"   {result['content'][:300]}...\n"
        response += f"   (Relevance: {result['relevance']})\n\n"
    
    return response


class FoodDatabaseQueryInput(BaseModel):
    """Input schema for searching the food database."""

    query: str = Field(description="Food name or category to search")
    limit: int = Field(default=5, description="Maximum number of results")


@tool("search_food_database", args_schema=FoodDatabaseQueryInput)
def tool_search_food_database(query: str, limit: int = 5) -> str:
    """
    Search the nutrition database for specific food information.
    
    Use this for factual nutrition data about specific foods: calories, protein,
    carbs, fats, fiber, and serving sizes.
    
    Examples:
    - "What are the calories in chicken?"
    - "Show me protein sources"
    - "I want low-calorie vegetables"
    """
    results = search_food_database(query, limit=limit)
    
    if not results:
        return f"No foods found matching '{query}' in database."
    
    response = f"Found {len(results)} foods in database:\n\n"
    for food in results:
        response += f"• {food['name']} ({food['serving_size']}):\n"
        response += f"  {food['calories']:.0f} cal | "
        response += f"  {food['protein_g']:.1f}g protein | "
        response += f"  {food['carbs_g']:.1f}g carbs | "
        response += f"  {food['fat_g']:.1f}g fat"
        if food.get('fiber_g'):
            response += f" | {food['fiber_g']:.1f}g fiber"
        response += "\n"
    
    return response


class OnlineSearchQueryInput(BaseModel):
    """Input schema for online search."""

    query: str = Field(description="Search query for nutrition/health information")
    max_results: int = Field(default=3, description="Maximum number of results")


@tool("search_online", args_schema=OnlineSearchQueryInput)
def tool_search_online(query: str, max_results: int = 3) -> str:
    """
    Search for up-to-date nutrition and health information online.
    
    Use this for:
    - Latest nutrition research and studies
    - Current health trends
    - Specific product information not in database
    - External resources and references
    
    Examples:
    - "Latest research on intermittent fasting"
    - "COVID-19 and nutrition"
    - "New superfood trends"
    """
    # Mock online search results (in production, use Tavily, SerpAPI, etc.)
    mock_results = [
        {
            "title": "USDA Nutrition Database",
            "url": "https://fdc.nal.usda.gov/",
            "snippet": "Comprehensive nutrition data for food items",
            "source": "usda.gov"
        },
        {
            "title": "Mayo Clinic - Nutrition and Healthy Eating",
            "url": "https://www.mayoclinic.org/healthy-lifestyle/nutrition-and-healthy-eating",
            "snippet": "Evidence-based nutrition information from medical experts",
            "source": "mayoclinic.org"
        },
        {
            "title": f"Research Articles on {query}",
            "url": "https://scholar.google.com/scholar",
            "snippet": "Academic research on health and nutrition topics",
            "source": "scholar.google.com"
        }
    ]
    
    response = f"Online search results for '{query}':\n\n"
    for i, result in enumerate(mock_results[:max_results], 1):
        response += f"{i}. {result['title']}\n"
        response += f"   URL: {result['url']}\n"
        response += f"   {result['snippet']}\n\n"
    
    return response