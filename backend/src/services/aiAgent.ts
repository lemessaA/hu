import OpenAI from "openai";
import { config } from "../config.js";
import type { MemoryMessage } from "./redisMemory.js";

const SYSTEM_PROMPT = `You are a knowledgeable, practical assistant focused on climate resilience, adaptation, and sustainable livelihoods. 
Give concise, actionable guidance. When the user shares an image description or context, incorporate it carefully. 
If information is uncertain, say so and suggest verified sources.`;

let openaiClient: OpenAI | null = null;

function getOpenAI(): OpenAI | null {
  if (!config.openaiApiKey) return null;
  if (!openaiClient) {
    openaiClient = new OpenAI({ apiKey: config.openaiApiKey });
  }
  return openaiClient;
}

function demoResponse(userText: string): string {
  return (
    `[Demo mode — set OPENAI_API_KEY for live AI]\n\n` +
    `Thanks for your message about climate resilience. Here is a structured placeholder response:\n\n` +
    `1) **Context**: "${userText.slice(0, 200)}${userText.length > 200 ? "…" : ""}"\n` +
    `2) **Immediate actions**: assess local hazards, protect water and food systems, and coordinate with community networks.\n` +
    `3) **Next steps**: gather baseline data, prioritize low-cost adaptations, and plan for early warning where relevant.\n\n` +
    `This demo runs without an external model so the stack works offline at the venue.`
  );
}

export function buildMessagesForModel(
  shortTerm: MemoryMessage[],
  latestUserContent: string
): OpenAI.Chat.ChatCompletionMessageParam[] {
  const history: OpenAI.Chat.ChatCompletionMessageParam[] = shortTerm.map(
    (m) => ({
      role: m.role,
      content: m.content,
    })
  );
  return [
    { role: "system", content: SYSTEM_PROMPT },
    ...history,
    { role: "user", content: latestUserContent },
  ];
}

/** Non-streaming completion */
export async function completeChat(
  shortTerm: MemoryMessage[],
  latestUserContent: string
): Promise<string> {
  const client = getOpenAI();
  if (!client) {
    return demoResponse(latestUserContent);
  }
  const messages = buildMessagesForModel(shortTerm, latestUserContent);
  const res = await client.chat.completions.create({
    model: config.openaiModel,
    messages,
    temperature: 0.6,
    max_tokens: 1200,
  });
  const text = res.choices[0]?.message?.content?.trim();
  return text || "(empty model response)";
}

/** Stream tokens as async iterable of string chunks */
export async function* streamChat(
  shortTerm: MemoryMessage[],
  latestUserContent: string
): AsyncGenerator<string, void, unknown> {
  const client = getOpenAI();
  if (!client) {
    const full = demoResponse(latestUserContent);
    yield full;
    return;
  }
  const messages = buildMessagesForModel(shortTerm, latestUserContent);
  const stream = await client.chat.completions.create({
    model: config.openaiModel,
    messages,
    temperature: 0.6,
    max_tokens: 1200,
    stream: true,
  });
  for await (const part of stream) {
    const delta = part.choices[0]?.delta?.content;
    if (delta) yield delta;
  }
}
