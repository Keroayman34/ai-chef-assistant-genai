import MessageBubble from "./MessageBubble";

export default function ChatWindow({
  messages,
  loading,
  onChooseMeal,
  selectingMeal,
}) {
  return (
    <div className="glass-card scrollbar-modern flex h-[56vh] flex-col gap-4 overflow-y-auto p-4 md:h-[60vh]">
      {messages.length === 0 && (
        <div className="m-auto text-center text-slate-400">
          <p className="text-lg font-semibold text-cyan-200">
            👨‍🍳 Welcome to AI Chef Assistant
          </p>
          <p className="text-sm">
            Share ingredients and get beautiful meal ideas.
          </p>
        </div>
      )}

      {messages.map((message) => (
        <MessageBubble
          key={message.id}
          message={message}
          onChooseMeal={onChooseMeal}
          selectingMeal={selectingMeal}
        />
      ))}

      {loading && (
        <div className="flex items-center gap-2 text-sm text-slate-400">
          <span className="inline-block h-2.5 w-2.5 animate-bounce rounded-full bg-cyan-300" />
          <span className="inline-block h-2.5 w-2.5 animate-bounce rounded-full bg-cyan-300 [animation-delay:120ms]" />
          <span className="inline-block h-2.5 w-2.5 animate-bounce rounded-full bg-cyan-300 [animation-delay:240ms]" />
          Chef is thinking...
        </div>
      )}
    </div>
  );
}
