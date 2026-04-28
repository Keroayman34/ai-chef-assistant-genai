"""Context optimization helpers (trimming + summarization)."""

from __future__ import annotations

from typing import Dict, List

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage


def trim_messages(messages: List[BaseMessage], max_messages: int) -> List[BaseMessage]:
    """Trim to the last N messages while preserving order."""
    if max_messages <= 0:
        return []
    if len(messages) <= max_messages:
        return list(messages)
    return list(messages[-max_messages:])


def summarize_messages(
    model,
    messages: List[BaseMessage],
    previous_summary: str | None,
) -> str:
    """Summarize recent conversation messages into a compact context note."""

    summary_seed = previous_summary or "None"
    transcript = "\n".join(
        f"{getattr(msg, 'type', msg.__class__.__name__)}: {msg.content}"
        for msg in messages
    )

    system_text = (
        "You are a summarization assistant for a nutrition coach. "
        "Capture only critical facts: meal descriptions, user goals, constraints, "
        "ingredients, and any tool outputs. Keep it short (<= 6 lines)."
    )
    user_text = (
        f"Previous summary:\n{summary_seed}\n\n"
        f"New transcript:\n{transcript}\n\n"
        "Return an updated summary in plain text."
    )

    response = model.invoke([
        SystemMessage(content=system_text),
        HumanMessage(content=user_text),
    ])
    return (response.content or "").strip()


class ContextMiddleware:
    """Beginner-friendly context manager with trimming + summarization."""

    def __init__(self, summary_model, max_messages: int, summary_trigger: int) -> None:
        self.summary_model = summary_model
        self.max_messages = max_messages
        self.summary_trigger = summary_trigger
        self._summaries: Dict[str, str] = {}
        self._recent: Dict[str, List[BaseMessage]] = {}

    def build_messages(self, thread_id: str, new_message: BaseMessage) -> List[BaseMessage]:
        """Build context messages including a running summary if available."""
        recent = list(self._recent.get(thread_id, []))
        messages = trim_messages(recent + [new_message], self.max_messages)
        summary = self._summaries.get(thread_id)
        if summary:
            return [SystemMessage(content=f"Conversation summary: {summary}")] + messages
        return messages

    def update(self, thread_id: str, user_message: BaseMessage, assistant_message: BaseMessage) -> None:
        """Store recent messages and update summary when needed."""
        recent = self._recent.setdefault(thread_id, [])
        recent.extend([user_message, assistant_message])
        recent[:] = trim_messages(recent, self.max_messages)

        if len(recent) >= self.summary_trigger:
            summary = summarize_messages(self.summary_model, recent, self._summaries.get(thread_id))
            self._summaries[thread_id] = summary

    def get_summary(self, thread_id: str) -> str | None:
        return self._summaries.get(thread_id)
