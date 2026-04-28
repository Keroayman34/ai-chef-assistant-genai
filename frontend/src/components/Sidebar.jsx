import { ChefHat, Plus, Server } from "lucide-react";

export default function Sidebar({
  threads,
  currentThreadId,
  onNewChat,
  onSelectThread,
  provider,
  setProvider,
}) {
  return (
    <aside className="glass-card flex h-full w-full flex-col p-4 lg:max-w-xs">
      <div className="mb-4 flex items-center gap-2">
        <ChefHat className="text-cyan-300" size={20} />
        <h1 className="text-lg font-semibold">Nutrition AI</h1>
      </div>

      <button
        type="button"
        onClick={onNewChat}
        className="mb-4 flex items-center justify-center gap-2 rounded-xl bg-cyan-400 px-4 py-2 text-sm font-semibold text-slate-900 transition hover:bg-cyan-300"
      >
        <Plus size={16} />
        New Chat
      </button>

      <div className="mb-4 rounded-xl border border-white/10 bg-slate-900/60 p-3">
        <div className="mb-2 flex items-center gap-2 text-xs font-medium text-slate-400">
          <Server size={14} />
          Backend Selector
        </div>
        <div className="grid grid-cols-2 gap-2">
          {["openai", "ollama"].map((item) => (
            <button
              key={item}
              type="button"
              onClick={() => setProvider(item)}
              className={`rounded-lg px-3 py-2 text-xs font-semibold uppercase transition ${
                provider === item
                  ? "bg-emerald-400 text-slate-900"
                  : "bg-slate-800 text-slate-300 hover:bg-slate-700"
              }`}
            >
              {item}
            </button>
          ))}
        </div>
      </div>

      <div className="mb-2 text-xs font-medium uppercase tracking-wide text-slate-400">
        Conversation History
      </div>
      <div className="scrollbar-modern flex-1 space-y-2 overflow-y-auto pr-1">
        {threads.length === 0 && (
          <p className="text-xs text-slate-500">No chats yet.</p>
        )}
        {threads.map((thread) => (
          <button
            key={thread.id}
            type="button"
            onClick={() => onSelectThread(thread.id)}
            className={`w-full rounded-xl border px-3 py-2 text-left transition ${
              currentThreadId === thread.id
                ? "border-cyan-300/40 bg-cyan-400/10"
                : "border-white/5 bg-slate-900/60 hover:border-white/20"
            }`}
          >
            <p className="truncate text-xs font-semibold text-slate-200">
              {thread.title || thread.id}
            </p>
            <p className="truncate text-[11px] text-slate-400">
              Thread: {thread.id}
            </p>
          </button>
        ))}
      </div>
    </aside>
  );
}
