import { ChefHat, UserRound } from "lucide-react";
import MealCard from "./MealCard";
import NutritionCard from "./NutritionCard";
import SearchResultsCard from "./SearchResultsCard";

export default function MessageBubble({
  message,
  onChooseMeal,
  selectingMeal,
}) {
  const isUser = message.role === "user";
  const payloadType = message.payload?.type;
  const nutritionPayload = message.payload?.data;

  return (
    <div className={`flex gap-3 ${isUser ? "justify-end" : "justify-start"}`}>
      {!isUser && (
        <div className="mt-1 grid h-8 w-8 place-items-center rounded-full bg-cyan-400/20 text-cyan-300">
          <ChefHat size={16} />
        </div>
      )}

      <div
        className={`max-w-3xl rounded-2xl border px-4 py-3 ${
          isUser
            ? "border-cyan-300/30 bg-cyan-400/20 text-cyan-100"
            : "border-white/10 bg-slate-900/70 text-slate-100"
        }`}
      >
        <p className="mb-2 whitespace-pre-wrap text-sm">{message.content}</p>

        {payloadType === "meals" && (
          <div className="space-y-3">
            {message.payload.data.map((meal) => (
              <MealCard
                key={meal.meal_name}
                meal={meal}
                onChooseMeal={onChooseMeal}
                disabled={selectingMeal}
              />
            ))}
          </div>
        )}

        {payloadType === "recipe" && message.payload.data && (
          <MealCard meal={message.payload.data} isRecipe />
        )}

        {payloadType === "nutrition" && nutritionPayload && (
          <div className="space-y-3">
            {(nutritionPayload.source_used || nutritionPayload.confidence) && (
              <div className="flex flex-wrap items-center gap-2 text-xs">
                {nutritionPayload.source_used && (
                  <span className="rounded-full border border-cyan-300/30 bg-cyan-400/10 px-2.5 py-1 text-cyan-200">
                    Source: {nutritionPayload.source_used}
                  </span>
                )}
                {nutritionPayload.confidence && (
                  <span className="rounded-full border border-amber-300/30 bg-amber-400/10 px-2.5 py-1 text-amber-200">
                    Confidence: {nutritionPayload.confidence}
                  </span>
                )}
              </div>
            )}
            <NutritionCard
              analysis={nutritionPayload.analysis}
              onSaveCase={onChooseMeal}
              disabled={selectingMeal}
            />
            <SearchResultsCard results={nutritionPayload.search_results} />
            {nutritionPayload.references?.length > 0 && (
              <div className="rounded-xl border border-white/10 bg-slate-900/70 p-3 text-xs text-slate-300">
                <p className="mb-2 font-semibold text-cyan-200">References</p>
                <ul className="list-disc space-y-1 pl-4">
                  {nutritionPayload.references.map((item, index) => (
                    <li key={`ref-${index}`}>{item}</li>
                  ))}
                </ul>
              </div>
            )}
            {nutritionPayload.storage_message && (
              <div className="rounded-xl border border-emerald-300/20 bg-emerald-400/10 p-3 text-xs text-emerald-200">
                {nutritionPayload.storage_message}
              </div>
            )}
            {nutritionPayload.disclaimer && (
              <div className="rounded-xl border border-white/10 bg-slate-900/70 p-3 text-[11px] text-slate-400">
                {nutritionPayload.disclaimer}
              </div>
            )}
          </div>
        )}
      </div>

      {isUser && (
        <div className="mt-1 grid h-8 w-8 place-items-center rounded-full bg-emerald-400/20 text-emerald-300">
          <UserRound size={16} />
        </div>
      )}
    </div>
  );
}
