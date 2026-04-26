export default function HeaderControls({
  creativityMode,
  setCreativityMode,
  detailMode,
  setDetailMode,
}) {
  return (
    <div className="glass-card flex flex-wrap items-center gap-4 p-4">
      <div className="flex items-center gap-2">
        <span className="text-xs font-medium text-slate-400">Creativity</span>
        <div className="rounded-full bg-slate-800 p-1">
          {["strict", "creative"].map((mode) => (
            <button
              key={mode}
              type="button"
              onClick={() => setCreativityMode(mode)}
              className={`rounded-full px-3 py-1 text-xs capitalize transition ${
                creativityMode === mode
                  ? "bg-cyan-400 text-slate-900"
                  : "text-slate-300 hover:bg-slate-700"
              }`}
            >
              {mode}
            </button>
          ))}
        </div>
      </div>

      <div className="flex items-center gap-2">
        <span className="text-xs font-medium text-slate-400">Response</span>
        <div className="rounded-full bg-slate-800 p-1">
          {["concise", "detailed"].map((mode) => (
            <button
              key={mode}
              type="button"
              onClick={() => setDetailMode(mode)}
              className={`rounded-full px-3 py-1 text-xs capitalize transition ${
                detailMode === mode
                  ? "bg-emerald-400 text-slate-900"
                  : "text-slate-300 hover:bg-slate-700"
              }`}
            >
              {mode}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
