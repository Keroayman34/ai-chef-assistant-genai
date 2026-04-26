import { ImageUp, SendHorizontal } from "lucide-react";
import { useRef, useState } from "react";

export default function IngredientInput({ onSend, loading }) {
  const [text, setText] = useState("");
  const [imageFile, setImageFile] = useState(null);
  const fileInputRef = useRef(null);

  function submitForm(event) {
    event.preventDefault();
    if (!text.trim() && !imageFile) {
      return;
    }
    onSend({ ingredientText: text.trim(), imageFile });
    setText("");
    setImageFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  }

  return (
    <form onSubmit={submitForm} className="glass-card space-y-3 p-4">
      <label className="block text-xs font-medium uppercase tracking-wide text-slate-400">
        Ingredients Input
      </label>

      <textarea
        rows={3}
        value={text}
        onChange={(event) => setText(event.target.value)}
        placeholder="Example: chicken breast, garlic, rice, tomato..."
        className="w-full resize-none rounded-xl border border-white/10 bg-slate-900/80 p-3 text-sm text-slate-100 outline-none ring-cyan-300 placeholder:text-slate-500 focus:ring-2"
      />

      <div className="flex flex-wrap items-center justify-between gap-3">
        <label className="inline-flex cursor-pointer items-center gap-2 rounded-lg border border-white/10 bg-slate-900/60 px-3 py-2 text-xs text-slate-300 hover:bg-slate-800">
          <ImageUp size={14} />
          {imageFile ? imageFile.name : "Upload fridge image"}
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={(event) => setImageFile(event.target.files?.[0] || null)}
            className="hidden"
          />
        </label>

        <button
          type="submit"
          disabled={loading}
          className="inline-flex items-center gap-2 rounded-xl bg-emerald-400 px-4 py-2 text-sm font-semibold text-slate-900 transition hover:bg-emerald-300 disabled:cursor-not-allowed disabled:opacity-60"
        >
          <SendHorizontal size={16} />
          {loading ? "Thinking..." : "Send"}
        </button>
      </div>
    </form>
  );
}
