const KEY = "agriclimate_advice_v1";

export type AdviceItem = { role: string; content: string; created_at: string };

export function readAdviceCache(): AdviceItem[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = localStorage.getItem(KEY);
    return raw ? (JSON.parse(raw) as AdviceItem[]) : [];
  } catch {
    return [];
  }
}

export function writeAdviceCache(items: AdviceItem[]) {
  try {
    localStorage.setItem(KEY, JSON.stringify(items));
  } catch {
    /* ignore */
  }
}
