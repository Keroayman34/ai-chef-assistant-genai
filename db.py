"""Database module for food nutrition information."""

import sqlite3
from pathlib import Path
from typing import List, Optional


class FoodDatabase:
    """
    Simple SQLite database for food nutrition data.
    
    Maintains a table of common foods with their nutritional information.
    """

    def __init__(self, db_path: str = "data/nutrition.db"):
        """Initialize or load the food nutrition database."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

    def _init_database(self) -> None:
        """Initialize database with schema and sample data."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS foods (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    calories REAL NOT NULL,
                    protein_g REAL NOT NULL,
                    carbs_g REAL NOT NULL,
                    fat_g REAL NOT NULL,
                    fiber_g REAL,
                    category TEXT,
                    serving_size TEXT DEFAULT '100g',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Check if data exists
            cursor.execute("SELECT COUNT(*) FROM foods")
            if cursor.fetchone()[0] == 0:
                self._insert_sample_data()
            
            conn.commit()

    def _insert_sample_data(self) -> None:
        """Insert sample food data."""
        sample_foods = [
            # Proteins
            ("Chicken Breast", 165, 31, 0, 3.6, 0, "protein", "100g"),
            ("Turkey Breast", 135, 29, 0, 1.3, 0, "protein", "100g"),
            ("Salmon", 208, 20, 0, 13, 0, "protein", "100g"),
            ("Tuna (canned in water)", 132, 29, 0, 0.8, 0, "protein", "100g"),
            ("Eggs", 155, 13, 1.1, 11, 0, "protein", "1 large"),
            ("Greek Yogurt (nonfat)", 59, 10, 3.3, 0.4, 0, "protein", "100g"),
            ("Cottage Cheese (low-fat)", 72, 11, 2.8, 1.5, 0, "protein", "100g"),
            ("Tofu", 76, 8, 1.9, 4.8, 1.2, "protein", "100g"),
            ("Lentils (cooked)", 116, 9, 20, 0.4, 3.8, "protein", "1 cup cooked"),
            ("Black Beans (cooked)", 227, 15, 41, 0.9, 10.2, "protein", "1 cup cooked"),
            
            # Carbohydrates
            ("Oatmeal (cooked)", 150, 5, 27, 3, 4, "carbs", "1 cup cooked"),
            ("Brown Rice (cooked)", 108, 2.5, 23, 0.9, 1.8, "carbs", "1 cup cooked"),
            ("Sweet Potato", 103, 2, 24, 0.1, 3.9, "carbs", "1 medium"),
            ("Banana", 89, 1.1, 23, 0.3, 2.6, "carbs", "1 medium"),
            ("Apple", 95, 0.5, 25, 0.3, 4.4, "carbs", "1 medium"),
            ("Quinoa (cooked)", 222, 8, 39, 3.9, 5.2, "carbs", "1 cup cooked"),
            ("Whole Wheat Bread", 100, 4, 18, 1.5, 2.7, "carbs", "1 slice"),
            ("Chickpeas (cooked)", 269, 15, 45, 4.3, 12.5, "carbs", "1 cup cooked"),
            
            # Vegetables
            ("Broccoli", 34, 3.7, 7, 0.4, 2.4, "vegetable", "1 cup cooked"),
            ("Spinach (raw)", 7, 1, 1.1, 0.1, 0.7, "vegetable", "1 cup raw"),
            ("Bell Pepper", 30, 1, 7, 0.3, 2.2, "vegetable", "1 cup"),
            ("Carrots", 25, 0.6, 6, 0.1, 1.7, "vegetable", "1 cup"),
            ("Kale", 33, 3.3, 6.3, 0.6, 1.3, "vegetable", "1 cup"),
            ("Broccoli", 34, 3.7, 7, 0.4, 2.4, "vegetable", "1 cup"),
            
            # Fruits
            ("Blueberries", 57, 0.7, 14, 0.3, 2.4, "fruit", "1 cup"),
            ("Strawberries", 49, 1, 12, 0.5, 3, "fruit", "1 cup"),
            ("Raspberries", 64, 1.5, 15, 0.7, 8, "fruit", "1 cup"),
            ("Orange", 62, 1.2, 16, 0.3, 3.1, "fruit", "1 medium"),
            ("Watermelon", 46, 0.9, 11, 0.2, 0.6, "fruit", "1 cup"),
            
            # Healthy Fats
            ("Almonds", 579, 21, 22, 50, 12.5, "fat", "1 ounce (23 nuts)"),
            ("Walnuts", 654, 15, 14, 66, 3.7, "fat", "1 ounce (14 halves)"),
            ("Olive Oil", 120, 0, 0, 14, 0, "fat", "1 tablespoon"),
            ("Avocado", 160, 2, 9, 15, 7, "fat", "1/2 fruit"),
            ("Peanut Butter (natural)", 94, 4, 3.5, 8, 1.6, "fat", "1 tablespoon"),
            
            # Misc
            ("Milk (skim)", 35, 3.4, 5, 0.1, 0, "dairy", "1 cup (240ml)"),
            ("Honey", 64, 0.1, 17, 0, 0, "sweetener", "1 tablespoon"),
            ("Dark Chocolate (70%)", 599, 7.8, 46, 43, 6.8, "treat", "100g"),
        ]
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.executemany(
                    """
                    INSERT INTO foods 
                    (name, calories, protein_g, carbs_g, fat_g, fiber_g, category, serving_size)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    sample_foods
                )
                conn.commit()
                print(f"Inserted {len(sample_foods)} sample foods into database")
            except sqlite3.IntegrityError:
                print("Sample data already exists in database")

    def search(self, query: str, limit: int = 5) -> List[dict]:
        """
        Search foods by name or category.
        
        Args:
            query: Search term (food name or category)
            limit: Maximum number of results
            
        Returns:
            List of matching foods with nutrition info
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Search by name or category
            search_term = f"%{query}%"
            cursor.execute("""
                SELECT 
                    name, calories, protein_g, carbs_g, fat_g, fiber_g, 
                    category, serving_size
                FROM foods
                WHERE name LIKE ? OR category LIKE ?
                ORDER BY name
                LIMIT ?
            """, (search_term, search_term, limit))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    "name": row["name"],
                    "calories": row["calories"],
                    "protein_g": row["protein_g"],
                    "carbs_g": row["carbs_g"],
                    "fat_g": row["fat_g"],
                    "fiber_g": row["fiber_g"],
                    "category": row["category"],
                    "serving_size": row["serving_size"],
                    "type": "database"
                })
            
            return results

    def get_by_name(self, name: str) -> Optional[dict]:
        """Get a specific food by exact name."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    name, calories, protein_g, carbs_g, fat_g, fiber_g,
                    category, serving_size
                FROM foods
                WHERE LOWER(name) = LOWER(?)
            """, (name,))
            
            row = cursor.fetchone()
            if row:
                return {
                    "name": row["name"],
                    "calories": row["calories"],
                    "protein_g": row["protein_g"],
                    "carbs_g": row["carbs_g"],
                    "fat_g": row["fat_g"],
                    "fiber_g": row["fiber_g"],
                    "category": row["category"],
                    "serving_size": row["serving_size"],
                    "type": "database"
                }
            return None

    def get_category_summary(self, category: str) -> str:
        """Get a summary of foods in a category."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name, calories, protein_g
                FROM foods
                WHERE category = ?
                ORDER BY calories
            """, (category,))
            
            rows = cursor.fetchall()
            if not rows:
                return f"No foods found in category '{category}'"
            
            summary = f"Foods in '{category}' category:\n"
            for name, calories, protein in rows:
                summary += f"- {name}: {calories:.0f} cal, {protein:.1f}g protein\n"
            return summary

    def get_all_categories(self) -> List[str]:
        """Get all food categories."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT category FROM foods ORDER BY category")
            return [row[0] for row in cursor.fetchall()]


# Global database instance
_db_instance = None


def get_database() -> FoodDatabase:
    """Get or create the global database instance."""
    global _db_instance
    if _db_instance is None:
        _db_instance = FoodDatabase(db_path="data/nutrition.db")
    return _db_instance


def search_food_database(query: str, limit: int = 5) -> List[dict]:
    """
    Search the food database.
    
    This is the main interface for the agent to search food nutrition data.
    
    Args:
        query: Search term (food name or category)
        limit: Maximum number of results
        
    Returns:
        List of matching foods with nutrition information
    """
    db = get_database()
    return db.search(query, limit=limit)
