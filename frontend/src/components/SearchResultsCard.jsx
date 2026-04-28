export default function SearchResultsCard({ results }) {
  if (!results || results.length === 0) return null;

  return (
    <div className="rounded-2xl border border-white/10 bg-slate-900/70 p-4 shadow-glow">
      <h4 className="mb-3 text-base font-semibold text-cyan-200">
        Nearby Healthy Options
      </h4>
      <div className="space-y-3">
        {results.map((item, index) => (
          <div
            key={`${item.name}-${index}`}
            className="rounded-xl border border-white/10 bg-slate-900/50 p-3 text-sm text-slate-300"
          >
            <div className="flex items-center justify-between gap-2">
              <p className="font-semibold text-cyan-100">{item.name}</p>
              <span className="text-xs text-slate-400">{item.category}</span>
            </div>
            <p className="mt-1 text-xs text-slate-400">{item.address}</p>
            {item.distance_km != null && (
              <p className="mt-1 text-xs text-slate-500">
                Distance: {item.distance_km} km
              </p>
            )}
            <p className="mt-2 text-xs">{item.notes}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
