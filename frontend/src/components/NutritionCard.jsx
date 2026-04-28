export default function NutritionCard({ analysis, onSaveCase, disabled }) {
  if (!analysis) return null;

  const estimate = analysis.nutrition_estimate;

  return (
    <div className="rounded-2xl border border-white/10 bg-slate-900/70 p-4 shadow-glow">
      <div className="mb-2 flex items-start justify-between gap-4">
        <h4 className="text-base font-semibold text-cyan-200">
          {analysis.meal_name}
        </h4>
        {onSaveCase && (
          <button
            type="button"
            disabled={disabled}
            onClick={() => onSaveCase(analysis.meal_name)}
            className="rounded-lg bg-emerald-400 px-3 py-1.5 text-xs font-semibold text-slate-900 transition hover:bg-emerald-300 disabled:cursor-not-allowed disabled:opacity-50"
          >
            Save to CSV
          </button>
        )}
      </div>

      <div className="mb-3 flex flex-wrap gap-2 text-xs text-slate-300">
        <span className="rounded-full bg-slate-800 px-3 py-1">
          Calories: {estimate.calories_kcal} kcal
        </span>
        <span className="rounded-full bg-slate-800 px-3 py-1">
          Protein: {estimate.protein_g}g
        </span>
        <span className="rounded-full bg-slate-800 px-3 py-1">
          Carbs: {estimate.carbs_g}g
        </span>
        <span className="rounded-full bg-slate-800 px-3 py-1">
          Fat: {estimate.fat_g}g
        </span>
        {estimate.fiber_g != null && (
          <span className="rounded-full bg-slate-800 px-3 py-1">
            Fiber: {estimate.fiber_g}g
          </span>
        )}
      </div>

      {analysis.ingredients?.length > 0 && (
        <div className="mb-3 flex flex-wrap gap-2">
          {analysis.ingredients.map((ingredient) => (
            <span
              key={`${analysis.meal_name}-${ingredient.name}`}
              className="rounded-full border border-emerald-300/20 bg-emerald-400/10 px-2.5 py-1 text-[11px] text-emerald-300"
            >
              {ingredient.name}
            </span>
          ))}
        </div>
      )}

      <div className="mb-3 text-sm text-slate-300">
        <p className="font-semibold text-cyan-200">Summary</p>
        <p className="mt-1">{analysis.nutrition_summary.summary_text}</p>
        <p className="mt-1 text-xs text-slate-400">
          {analysis.nutrition_summary.macro_balance}
        </p>
      </div>

      {analysis.recommendations?.length > 0 && (
        <div className="text-sm text-slate-300">
          <p className="font-semibold text-cyan-200">Recommendations</p>
          <ul className="mt-2 list-disc space-y-1 pl-4">
            {analysis.recommendations.map((item, index) => (
              <li key={`${analysis.meal_name}-rec-${index}`}>{item}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
