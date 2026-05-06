import "server-only";

export function backendEnv() {
  const base = process.env.BACKEND_URL?.replace(/\/$/, "") || "http://localhost:8000";
  const key = process.env.API_KEY || "";
  return { base, key };
}

export function beHeaders(init?: HeadersInit): Headers {
  const h = new Headers(init);
  const { key } = backendEnv();
  if (key) h.set("X-API-Key", key);
  return h;
}
