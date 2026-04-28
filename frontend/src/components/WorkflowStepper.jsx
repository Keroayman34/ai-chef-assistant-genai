const steps = [
  "Analyze Meal",
  "Nutrition Summary",
  "Follow-up Questions",
  "Tools & Storage",
];

export default function WorkflowStepper({ currentStep = 1 }) {
  return (
    <div className="glass-card p-4">
      <div className="flex flex-wrap gap-2">
        {steps.map((label, index) => {
          const stepNo = index + 1;
          const active = stepNo <= currentStep;

          return (
            <div
              key={label}
              className={`flex items-center gap-2 rounded-full px-3 py-2 text-xs transition ${
                active
                  ? "bg-cyan-400/20 text-cyan-300 border border-cyan-300/30"
                  : "bg-slate-800/70 text-slate-400 border border-white/5"
              }`}
            >
              <span
                className={`grid h-5 w-5 place-items-center rounded-full text-[10px] font-semibold ${
                  active
                    ? "bg-cyan-300 text-slate-900"
                    : "bg-slate-700 text-slate-200"
                }`}
              >
                {stepNo}
              </span>
              <span>{label}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
