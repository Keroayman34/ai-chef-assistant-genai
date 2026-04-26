import { Clock3, Users } from "lucide-react";
import { useState } from "react";

export default function MealCard({
  meal,
  onChooseMeal,
  disabled = false,
  isRecipe = false,
}) {
  const [open, setOpen] = useState(isRecipe);

  return (
    <div className="rounded-2xl border border-white/10 bg-slate-900/70 p-4 shadow-glow">
      <div className="mb-2 flex items-start justify-between gap-4">
        <h4 className="text-base font-semibold text-cyan-200">
          {meal.meal_name}
        </h4>
        {!isRecipe && (
          <button
            type="button"
            disabled={disabled}
            onClick={() => onChooseMeal(meal.meal_name)}
            className="rounded-lg bg-cyan-400 px-3 py-1.5 text-xs font-semibold text-slate-900 transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-50"
          >
            Choose This Meal
          </button>
        )}
      </div>

      <div className="mb-3 flex flex-wrap gap-2 text-xs text-slate-300">
        <span className="inline-flex items-center gap-1 rounded-full bg-slate-800 px-3 py-1">
          <Clock3 size={13} /> {meal.cooking_time}
        </span>
        <span className="inline-flex items-center gap-1 rounded-full bg-slate-800 px-3 py-1">
          <Users size={13} /> Serves {meal.number_of_individuals}
        </span>
      </div>

      <div className="mb-3 flex flex-wrap gap-2">
        {meal.ingredients?.map((ingredient) => (
          <span
            key={`${meal.meal_name}-${ingredient.name}`}
            className={`rounded-full border px-2.5 py-1 text-[11px] ${
              ingredient.status === "available"
                ? "border-emerald-300/30 bg-emerald-400/10 text-emerald-300"
                : "border-rose-300/30 bg-rose-400/10 text-rose-300"
            }`}
          >
            {ingredient.name}
          </span>
        ))}
      </div>

      <button
        type="button"
        onClick={() => setOpen((prev) => !prev)}
        className="mb-2 text-xs font-medium text-cyan-300 hover:text-cyan-200"
      >
        {open ? "Hide Instructions" : "Show Instructions"}
      </button>

      {open && (
        <ol className="space-y-1 pl-4 text-sm text-slate-300">
          {meal.instructions?.map((step, index) => (
            <li
              key={`${meal.meal_name}-step-${index + 1}`}
              className="list-decimal"
            >
              {step}
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}
