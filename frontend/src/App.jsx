import { useMemo, useState } from "react";
import { Sparkles } from "lucide-react";
import ChatWindow from "./components/ChatWindow";
import HeaderControls from "./components/HeaderControls";
import IngredientInput from "./components/IngredientInput";
import Sidebar from "./components/Sidebar";
import WorkflowStepper from "./components/WorkflowStepper";
import {
  confirmMeal,
  getHistory,
  selectMeal,
  startChat,
  uploadImage,
} from "./api/client";

function createThreadId() {
  return `chef-thread-${Date.now()}`;
}

function mapHistoryMessages(historyPayload) {
  return (historyPayload?.messages || []).map((item) => ({
    id: item.id,
    role: item.role,
    content: item.content,
    payload: item.payload,
  }));
}

export default function App() {
  const [provider, setProvider] = useState("openai");
  const [creativityMode, setCreativityMode] = useState("strict");
  const [detailMode, setDetailMode] = useState("concise");

  const [threads, setThreads] = useState([]);
  const [currentThreadId, setCurrentThreadId] = useState(createThreadId());

  const [messages, setMessages] = useState([]);
  const [workflowStep, setWorkflowStep] = useState(1);

  const [loading, setLoading] = useState(false);
  const [selectingMeal, setSelectingMeal] = useState(false);

  const threadTitle = useMemo(() => {
    const firstUser = messages.find((msg) => msg.role === "user");
    if (!firstUser?.content) {
      return "New Chat";
    }
    return firstUser.content.slice(0, 32);
  }, [messages]);

  function upsertThread(threadId, title) {
    setThreads((prev) => {
      const exists = prev.some((thread) => thread.id === threadId);
      if (exists) {
        return prev.map((thread) =>
          thread.id === threadId ? { ...thread, title } : thread,
        );
      }
      return [{ id: threadId, title }, ...prev];
    });
  }

  async function handleSend({ ingredientText, imageFile }) {
    setLoading(true);
    try {
      let imageId = null;
      if (imageFile) {
        const uploaded = await uploadImage(imageFile);
        imageId = uploaded.image_id;
      }

      const data = await startChat({
        thread_id: currentThreadId,
        provider,
        creativity_mode: creativityMode,
        detail_mode: detailMode,
        ingredient_text: ingredientText,
        image_id: imageId,
      });

      const historyPayload = await getHistory(currentThreadId);
      setMessages(mapHistoryMessages(historyPayload));
      setWorkflowStep(data.workflow_step || 2);
      upsertThread(
        currentThreadId,
        threadTitle === "New Chat" ? ingredientText.slice(0, 32) : threadTitle,
      );
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: `Error: ${error.message}`,
          payload: null,
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  async function handleChooseMeal(mealName) {
    setSelectingMeal(true);
    setLoading(true);
    try {
      await selectMeal({ thread_id: currentThreadId, meal_name: mealName });
      setWorkflowStep(4);

      await confirmMeal({ thread_id: currentThreadId });
      const historyPayload = await getHistory(currentThreadId);
      setMessages(mapHistoryMessages(historyPayload));
      setWorkflowStep(5);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: `Error: ${error.message}`,
          payload: null,
        },
      ]);
    } finally {
      setSelectingMeal(false);
      setLoading(false);
    }
  }

  async function handleSelectThread(threadId) {
    setCurrentThreadId(threadId);
    setLoading(true);
    try {
      const historyPayload = await getHistory(threadId);
      setMessages(mapHistoryMessages(historyPayload));
      const state = historyPayload?.state;
      if (state?.selected_meal) {
        setWorkflowStep(5);
      } else if (state?.last_meals?.length) {
        setWorkflowStep(2);
      } else {
        setWorkflowStep(1);
      }
    } catch (error) {
      setMessages([
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: `Error loading history: ${error.message}`,
          payload: null,
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function handleNewChat() {
    const newThreadId = createThreadId();
    setCurrentThreadId(newThreadId);
    setMessages([]);
    setWorkflowStep(1);
  }

  return (
    <div className="min-h-screen p-4 md:p-6">
      <div className="mx-auto grid max-w-7xl gap-4 lg:grid-cols-[280px,1fr]">
        <Sidebar
          threads={threads}
          currentThreadId={currentThreadId}
          onNewChat={handleNewChat}
          onSelectThread={handleSelectThread}
          provider={provider}
          setProvider={setProvider}
        />

        <main className="space-y-4">
          <div className="glass-card flex flex-wrap items-center justify-between gap-3 p-4">
            <div>
              <h2 className="flex items-center gap-2 text-xl font-semibold text-cyan-100">
                <Sparkles className="animate-float text-cyan-300" size={20} />
                Futuristic AI Chef Assistant
              </h2>
              <p className="text-xs text-slate-400">
                Thread Memory ID: {currentThreadId}
              </p>
            </div>
          </div>

          <HeaderControls
            creativityMode={creativityMode}
            setCreativityMode={setCreativityMode}
            detailMode={detailMode}
            setDetailMode={setDetailMode}
          />

          <WorkflowStepper currentStep={workflowStep} />

          <ChatWindow
            messages={messages}
            loading={loading}
            onChooseMeal={handleChooseMeal}
            selectingMeal={selectingMeal}
          />

          <IngredientInput onSend={handleSend} loading={loading} />
        </main>
      </div>
    </div>
  );
}
