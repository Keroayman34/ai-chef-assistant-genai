import { ChefHat, UserRound } from "lucide-react";
import MealCard from "./MealCard";

export default function MessageBubble({
  message,
  onChooseMeal,
  selectingMeal,
}) {
  const isUser = message.role === "user";
  const payloadType = message.payload?.type;

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
      </div>

      {isUser && (
        <div className="mt-1 grid h-8 w-8 place-items-center rounded-full bg-emerald-400/20 text-emerald-300">
          <UserRound size={16} />
        </div>
      )}
    </div>
  );
}
