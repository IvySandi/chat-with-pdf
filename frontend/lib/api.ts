export type ChatRequest = {
  question: string;
};

export type ChatResponse = {
  answer: string;
};

export type UploadResponse = {
  message: string;
  chunks?: number;
  stored?: number;
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api";

export async function sendChatMessage(payload: ChatRequest): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    const err = await response.json().catch(() => null);
    throw new Error(err?.detail ?? "Failed to get chat response");
  }

  return (await response.json()) as ChatResponse;
}

export async function uploadPdf(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/upload`, {
    method: "POST",
    body: formData
  });

  if (!response.ok) {
    const err = await response.json().catch(() => null);
    throw new Error(err?.detail ?? "Failed to upload PDF");
  }

  return (await response.json()) as UploadResponse;
}
