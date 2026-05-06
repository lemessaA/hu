export type ChatPayload = {
  message: string;
  location?: string;
  session_id: string;
  crop_result?: Record<string, unknown>;
};

export type ChatResponse = {
  reply: string;
  session_id: string;
  intent?: string;
  weather_data?: Record<string, unknown>;
  crop_result?: Record<string, unknown>;
};

export async function sendChat(payload: ChatPayload): Promise<ChatResponse> {
  const res = await fetch("/api/proxy/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const t = await res.text();
    throw new Error(t || `Chat failed (${res.status})`);
  }
  return res.json() as Promise<ChatResponse>;
}

export async function sendChatStream(
  payload: ChatPayload,
  onToken: (t: string) => void,
  onMeta?: (m: unknown) => void
): Promise<void> {
  const res = await fetch("/api/proxy/chat/stream", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ...payload, stream: true }),
  });
  if (!res.ok || !res.body) {
    const t = await res.text();
    throw new Error(t || "Stream failed");
  }
  const reader = res.body.getReader();
  const dec = new TextDecoder();
  let buf = "";
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buf += dec.decode(value, { stream: true });
    const parts = buf.split("\n\n");
    buf = parts.pop() || "";
    for (const block of parts) {
      const line = block.trim();
      if (!line.startsWith("data:")) continue;
      const json = line.slice(5).trim();
      try {
        const obj = JSON.parse(json) as Record<string, unknown>;
        if (obj.meta && onMeta) onMeta(obj.meta);
        if (typeof obj.token === "string") onToken(obj.token);
      } catch {
        /* ignore partial */
      }
    }
  }
}

export async function analyzeImage(file: File): Promise<Record<string, unknown>> {
  const fd = new FormData();
  fd.append("file", file);
  const res = await fetch("/api/proxy/analyze-image", {
    method: "POST",
    body: fd,
  });
  if (!res.ok) {
    const t = await res.text();
    throw new Error(t || "Analyze failed");
  }
  return res.json() as Promise<Record<string, unknown>>;
}

export async function fetchRecentAdvice(): Promise<
  { items: { role: string; content: string; created_at: string }[] }
> {
  const res = await fetch("/api/proxy/advice/recent", { cache: "no-store" });
  if (!res.ok) {
    const t = await res.text();
    throw new Error(t || "Advice fetch failed");
  }
  return res.json();
}
