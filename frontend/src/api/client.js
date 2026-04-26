const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

async function parseJsonResponse(response) {
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || "Request failed");
  }
  return data;
}

export async function uploadImage(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/upload-image`, {
    method: "POST",
    body: formData,
  });

  return parseJsonResponse(response);
}

export async function startChat(payload) {
  const response = await fetch(`${API_BASE_URL}/chat/start`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  return parseJsonResponse(response);
}

export async function selectMeal(payload) {
  const response = await fetch(`${API_BASE_URL}/chat/select-meal`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  return parseJsonResponse(response);
}

export async function confirmMeal(payload) {
  const response = await fetch(`${API_BASE_URL}/chat/confirm`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  return parseJsonResponse(response);
}

export async function getHistory(threadId) {
  const response = await fetch(
    `${API_BASE_URL}/history/${encodeURIComponent(threadId)}`,
  );
  return parseJsonResponse(response);
}
